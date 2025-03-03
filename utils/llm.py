from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import RateLimitError, BadRequestError, APIConnectionError
from langchain.llms import Ollama
from create_utils import create_agent, create_tongyi_react_agent
from base_prompt import get_base_prompt
from langchain_community.document_loaders import PyMuPDFLoader
###----------------------------
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
import dashscope
dashscope.api_key="sk-6c9bdfd143444b928397274a8c4fe2d5"
os.environ['DASHSCOPE_API_KEY'] = dashscope.api_key

class PDFQuery:
    def __init__(self, openai_api_key = None,model="gpt-4o") -> None:
        #openai没钱了
        #self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        #mxbai为部署到本地的embedding，切换时要选择对应向量数据文件夹
        #self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.embeddings = HuggingFaceEmbeddings(model_name='moka-ai/m3e-base')
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        self.model=model
        if self.model=="gpt-4o":
            #self.llm = ChatOpenAI(api_key=openai_api_key,model="gpt-4o", temperature=0.5,streaming=True)
            self.llm = Ollama(model="glm4:9b", temperature=0.5, num_ctx=50000)
        elif self.model=="qwen-max":
            self.llm = ChatOpenAI(
            api_key=dashscope.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # DashScope base_url
            model="qwen-max"
            )
        self.chain = None
        self.db = None
        self.system_prompt=get_base_prompt()

    def ask(self, question: str,chat_history: str) -> str:
        try:
            if self.model=="gpt-4o":
                #流式输出
                res=self.chain.stream({
                    "chat_history": chat_history,
                    "input": question
                })
                for chunk in res:
                    if isinstance(chunk, dict) and 'answer' in chunk:
                        # 检查chunk是否具有二级answer结构,筛选最终结果输出
                        query_text = chunk["answer"]
                        yield query_text
                output=''
            elif self.model=="qwen-max":
                response = self.chain.invoke(
                    {
                        "input": question,
                        "prompt": get_base_prompt(),
                        # chat_history is a string
                        "chat_history": chat_history,
                    }
                )
                output = response["output"]
        except RateLimitError :
            output="系统繁忙，请稍后重试！"
        except BadRequestError :
            output="答案内容过长，请尝试精简你的问题！"
        except APIConnectionError:
            output="服务器网络异常，请稍后重试！"
        except :
            output="系统繁忙，请重新输入"
        yield output

    # def ingest(self, file_path: os.PathLike,agent_name="计算机组成与体系结构") -> None:
    #     base_path="./local_db/"
    #     db_path=f"{base_path}{agent_name}"
    #     if agent_name=="Uploaded_db":
    #         # loader = PyMuPDFLoader(file_path)
    #         loader = PyPDFLoader(file_path)
    #         documents = loader.load()
    #         splitted_documents = self.text_splitter.split_documents(documents)
    #         self.db = Chroma.from_documents(splitted_documents, self.embeddings).as_retriever(search_type="mmr", search_kwargs={"k": 6, "fetch_k": 10})
    #         # db.persist()
    #     else:
    #         #self.db = Chroma(persist_directory=db_path, embedding_function=self.embeddings).as_retriever(search_type="similarity", search_kwargs={"k": 6})
    #         self.db = Chroma(persist_directory=db_path, embedding_function=self.embeddings).as_retriever(search_type="mmr", search_kwargs={"k": 6,"fetch_k": 10})


    def ingest(self, file_path: os.PathLike,agent_name="数字逻辑与微处理器") -> None:
        base_path="./local_db/"
        db_path=f"{base_path}{agent_name}"
        if agent_name=="Uploaded_db":
            # loader = PyMuPDFLoader(file_path)
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            splitted_documents = self.text_splitter.split_documents(documents)
            db= Chroma.from_documents(splitted_documents, self.embeddings,persist_directory=db_path)
            db.persist()
        self.db = Chroma(persist_directory=db_path, embedding_function=self.embeddings).as_retriever(search_type="similarity", search_kwargs={"k": 10})

    def summarize(self, input: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system","""
            针对第三步关联知识点解析中的内容，思考可能会针对这些内容进一步提出的问题。直接输出问题内容，严禁‘用户可能会进一步提出’类似的表述，且只有一个问题，不超过50字。 
            错误例子：用户可能会进一步提出：摩尔定律是否仍然适用于当今的计算机硬件发展？
            正确例子：摩尔定律是否仍然适用于当今的计算机硬件发展？"""
             ),
            ("user", "{input}")
        ])
        chain = prompt | self.llm| StrOutputParser()
        summary=chain.invoke({"input": input})
        return summary

    def create_prompt(self, prompt_input) -> None:
        if self.model == "gpt-4o":
            retriever_prompt = ChatPromptTemplate.from_messages([
                # MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                ("user",
                 "Generate a search query to look up to get information relevant to the input.")
            ])
            retriever_chain = create_history_aware_retriever(llm=self.llm, retriever=self.db, prompt=retriever_prompt)
            context_prompt = ChatPromptTemplate.from_messages([
                ("system", """
            [Role] You are a professional AI learning assistant whose main responsibility is to analyze the educational materials retrieved from searches, based on the questions provided by students, in order to generate in-depth and comprehensive answers.

            [Output Structure] You must strictly follow the following three steps to answer the question, while bolding and wrapping the title of each step:
            一、问题分析
            （Summarize the key points of the problem and what knowledge should be answered）
            二、问题回答
            （Provide the answer to the question）
            三、关联知识点解析
            （Summarize the knowledge test points involved in the problem）

            [Rules]
            1.Use $$latex$$ format when outputting formulas.
            2.Ensure that the answer to the second step(问题回答) is no less than 1000 words.
            3.Please translate the answer into Chinese.

            [information retrieved]Below is the specific textbook content obtained from the search:
            """ + "\n\n{context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ])
            document_chain = create_stuff_documents_chain(self.llm, context_prompt)
            retriever_chain = create_retrieval_chain(retriever_chain, document_chain)
            self.chain = retriever_chain
        elif self.model == "qwen-max":
            self.chain = create_tongyi_react_agent(retriever=self.db, llm=self.llm)

    def forget(self) -> None:
        self.db = None
        self.chain = None
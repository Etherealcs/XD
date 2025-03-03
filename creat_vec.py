import os
import openai
import sys

# sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key = 'sk-proj-8WDPTIBAZyUIpTcc7XDXT3BlbkFJk49DFk0x8C4oZVDkYwgv'


from langchain_community.document_loaders import PyPDFLoader


loaders = [PyPDFLoader('./数据结构.pdf')]

docs = []

for loader in loaders:
    docs.extend(loader.load())


from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1500,chunk_overlap = 150)
splits = text_splitter.split_documents(docs)

from langchain_openai import OpenAIEmbeddings
embedding = OpenAIEmbeddings(openai_api_key = openai.api_key)


from langchain_community.vectorstores import Chroma
persist_directory = 'local_db/数据结构'

vectordb = Chroma.from_documents(
    documents = splits,
    embedding = embedding,
    persist_directory = persist_directory
)
vectordb.persist()
question = "介绍一下栈"

docs = vectordb.max_marginal_relevance_search(question,k=3,fetch_k=9)

print(len(docs))

for i in docs:
    print(i.page_content)
import os
import tempfile
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_chat import message
from llm import PDFQuery
from langchain_core.prompts import ChatPromptTemplate
from streamlit_extras.switch_page_button import switch_page

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from create_utils import create_agent
from langchain.llms import Ollama

st.set_page_config(page_title="AI导师",layout="wide")

##用来显示聊天消息，它通过遍历 st.session_state["messages"] 列表中的每一项来实现，每一项都是一个包含消息文本和一个布尔值（表示消息是否由用户发送）的元组。
def display_messages():
    for i, (msg, is_user) in enumerate(st.session_state["tutor_messages"]):
        message(msg, is_user=is_user, key=str(i))
    ##表明系统正在思考
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
        ##检查输入的有效性，通过 strip() 方法移除字符串首尾的空白字符，确保输入是有效的。
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        ##获取当前聊天历史，全存在st.session_state["chat_history"]里面了
        tutor_chat_history = st.session_state["tutor_chat_history"]
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            ##
            query_text = ask(user_text,tutor_chat_history)

        st.session_state["tutor_chat_history"].append(HumanMessage(content=user_text))
        st.session_state["tutor_chat_history"].append(AIMessage(content=query_text))

        st.session_state["tutor_messages"].append((user_text, True))
        st.session_state["tutor_messages"].append((query_text, False))

# def new_chat():
#     st.session_state["tutor_messages"] = []
#     st.session_state["tutor_chat_history"] = []
#     st.session_state["tutor_messages"].append(("你好，很高兴遇见你！我是你的AI学习助手，请告诉我你的问题。", False))



def initialize():
    if "tutor_init" not in st.session_state:
        #st.session_state["OPENAI_API_KEY"] ="sk-proj-OcFdOCZ4m9bJd7KyWZUCT3BlbkFJ4ao6vB3ZqDdpDCgp87TP"

        st.session_state["tutor_messages"] = []
        st.session_state["tutor_chat_history"] = []
        st.session_state["tutor_messages"].append(("你好，很高兴遇见你！我是你的AI学习助手，请告诉我你的问题，我可以为你提出建议。", False))
        st.session_state["tutor_init"] = "ok"

def logout():
    st.session_state["authentication_status"] = None
    st.session_state["authentication_status_teacher"] = None
    st.session_state["authentication_status_student"] = None
    st.session_state["name"] = None
    st.session_state["email"] = None
    st.rerun()

def ask(input, context):
    #llm = ChatOpenAI(api_key=st.session_state["OPENAI_API_KEY"], temperature=0)
    llm = Ollama(model="glm4:ctx50k", temperature=0.5, num_ctx=50000)
    prompt = ChatPromptTemplate.from_template("""
        你是一个专为大学生设计的AI导师助手。你的主要任务是帮助中国大学生掌握他们感兴趣的学科。当学生询问如何学习特定学科时，
        你需要根据该学科的学习要求、基本知识、核心内容和进阶资源给出具体的学习建议。你的回答应包括学习策略、推荐的学习材料和可能的学习路径。
        推荐学习材料中的学习平台一定要是中国的学习平台！！！！而不是MIT OpenCourseWare等在线课程资源这类外国的
        回答内容要在七百字以上！！！！！！！


        ### 功能描述
        - **说明前置课程**：基于学生提出的学科，告诉学生学习这门课之前还需要学习什么课程。
        - **理解学科要求**：基于学生提出的学科，解释该学科的基本要求和学习目标。
        - **提供学习策略**：给出有效的学习方法和技巧，帮助学生高效学习。
        - **推荐学习资源**：推荐书籍、
        - **建议学习路径**：根据学生的当前水平，规划初级到高级的学习步骤和课程。

        ### 交互示例
        - 学生提问：“我想掌握计算机科学，应该从哪里开始？”
        - 你的回答应该包括：
        - 计算机科学的基础知识介绍。
        - 推荐的入门书籍。
        - 学习编程的基本技巧和常用工具。
        - 进阶学习资源，如高级编程、算法和数据结构等。

        ### 专业性和准确性
        - 在给出建议时，确保信息的专业性和准确性。
        

        请始终确保你的回答全面、实用，并且鼓励学生积极探索和深入学习。

    通过以下对话记录来满足对方的期望:
    <context>
    {context}
    </context>
    Request: {input}
    """)

    chain = prompt | llm
    response = chain.invoke({
        "input": input,
        "context": context
    })
    return response
    # 检查 response 类型并正确访问 content 属性
    #if isinstance(response, AIMessage):

    #    return response.content  # 访问 content 属性来获取回答
    #else:
    #    return "无法生成答案，请重试。"  # 处理异常情况或返回错误消息


def main():

    initialize()
    st.subheader("📝 AI学习助手")
    st.caption("🚀 基于大语言模型的AI学习导师")
    display_messages()
    for i in range(5):
        st.write(" ")
    st.divider()
    st.chat_input("请输入你的问题", key="user_input",on_submit=process_input)




if __name__ == "__main__":
    st.sidebar.subheader(f"欢迎您, {st.session_state.get('name')}同学")
    if "authentication_status" not in st.session_state \
        or st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        ##一直不显示，回头再看看
        st.warning("请先进行登录")
        switch_page("login")

    elif st.session_state["authentication_status"]:
        if st.sidebar.button("登出"):
            logout()
            st.experimental_rerun()        
        main()





import json
import os
from llm import PDFQuery
from PaperSearch import Trigger
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_extras.switch_page_button import switch_page
import time
def new_chat():
    st.session_state["search_chat_history"] = []
    st.session_state["detail_ask"] = False
    st.session_state["query"] = ''

def detail_ask():
    st.session_state["detail_ask"]=True

def initialize(model:str):
    if "search_init" not in st.session_state:
        st.session_state["search_init"] = "ok"
        new_chat()

st.set_page_config(page_title="AI学习助手",layout="wide")
def main():
    #初始化
    model = "gpt-4o"
    initialize(model)

    #侧边栏选项
    with st.sidebar:
        st.sidebar.subheader(f"欢迎您, {st.session_state.get('name')}同学")
        st.title(":blue[📝 文献随心读]")
        st.button("开始新对话", key="new_chat_button", on_click=new_chat)
    st.subheader("📝 文献随心读")
    st.caption("🚀 基于大语言模型的文献阅读助手")

    with st.chat_message("assistant"):
        st.write(
            '您好，很高兴遇见您！您希望阅读什么领域的文献呢？请使用英文直接输入希望阅读的文献类别标签，如：llm、rag等。')

    #展示历史记录
    for message in st.session_state["search_chat_history"]:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)
    #输入文本框
    user_input = st.chat_input("请在此处输入")
    input=str(user_input)
    # 创建trigger对象
    web = "https://export.arxiv.org/api/query?search_query=" + input +"&sortBy=submittedDate&sortOrder=descending&max_results=3"
    trigger = Trigger(websites=web)
    #显示输入信息并生成回答
    if user_input is not None and user_input != (" " * len(user_input)):
        #显示输入信息
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            st.write("正在为您全速搜索论文中，请耐心等待。")
        #输出回答
        with st.chat_message("assistant"):
            # 搜索获取论文简介（list）
            # 定义最大重试次数和重试间隔
            MAX_RETRIES = 3
            RETRY_INTERVAL = 0.5  # 单位为秒
            for attempt in range(MAX_RETRIES):
                try:
                    summary_raw_output = trigger.get_summary()
                    break  # 成功获取后跳出循环
                except :
                    if attempt < MAX_RETRIES - 1:  # 如果不是最后一次尝试
                        time.sleep(RETRY_INTERVAL)
                    else:
                        raise Exception("未找到该类相关文献，请尝试更换文献标签,使用英文直接输入希望阅读的文献类别标签，以获得正确结果！")

            #print("summary:",summary_raw_output)
            st.write("已为您搜索到相关文献，下面我将按照 id、title、introduction、recommend_reason、pdflink 的顺序依次为您介绍它们。\n\n")
            ai_output="已为您搜索到相关文献，下面我将按照 id、title、introduction、recommend_reason、pdflink 的顺序依次为您介绍它们。\n\n"
            # summary_raw_output列表包含多篇文章信息，遍历列表中对应的每篇文章字典，提取信息转化为文本输出
            summaries = ""
            for paper in summary_raw_output:
                for key, value in paper.items():
                    # 将键和值转换为字符串，并添加到summaries中
                    summaries += f"**{key}**: {value}  \n"
                summaries +="\n\n"
            st.write(summaries)
            ai_output += summaries
        #记录聊天记录
        st.session_state["search_chat_history"].append(HumanMessage(user_input))
        st.session_state["search_chat_history"].append(AIMessage(ai_output))

        st.session_state["query"]=summary_raw_output
        st.button("点击此处一键阅读总结文献信息！", key="detail_ask",on_click=detail_ask)

    query = st.session_state["query"]
    if st.session_state["detail_ask"] == True and query != '':
        input = "帮我自动总结论文信息！"
        with st.chat_message("user"):
            st.write(input)
        with st.chat_message("assistant"):
            st.write("正在为您全速阅读论文中，请耐心等待。")
        with st.chat_message("assistant"):
            ai_output = st.write_stream(trigger.get_paperdata(summary=query))
            #st.write(ai_output)
        st.session_state["search_chat_history"].append(HumanMessage(input))
        st.session_state["search_chat_history"].append(AIMessage(ai_output))
        st.session_state["detail_ask"] = False

if __name__ == "__main__":
    if "authentication_status" not in st.session_state \
            or st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:

        st.warning("请先进行登录")
        switch_page("login")
    elif st.session_state["authentication_status"]:
        main()
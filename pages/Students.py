import os
import tempfile

import streamlit as st
from PIL import Image
import base64
from langchain_core.messages import HumanMessage, AIMessage
from llm import PDFQuery
from base_prompt import get_base_prompt
import time
from streamlit_extras.switch_page_button import switch_page
from openai import OpenAI
import torch
 
st.set_page_config(page_title="AI学习助手",layout="wide")

def create_agent(agent_name:str):
    if "create" not in st.session_state:
        file_path = "  "
        st.session_state["pdfquery"].ingest(file_path,agent_name)
        base_prompt = get_base_prompt()
        st.session_state["pdfquery"].create_prompt(base_prompt)
        st.session_state["create"]="ok"
        new_chat()
def create_new_agent():
    base_prompt = get_base_prompt()
    st.session_state["pdfquery"].create_prompt(base_prompt)
    st.session_state["create"] = "ok"
    st.session_state["embed_tip"]="🎉文档嵌入成功!"
def delete_agent():
    del st.session_state["create"]
def delete_init():
    del st.session_state["init"]
    del st.session_state["create"]
def reaskset():
    st.session_state["reask"] = "True"
def read_and_save_file():
    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        st.session_state["pdfquery"].ingest(file_path,"Uploaded_db")
        os.remove(file_path)

def new_chat():
    st.session_state["chat_history"] = []
    st.session_state["query"]=[]
    st.session_state["reask"] = "False"

def initialize(model:str):
    if "init" not in st.session_state:
        st.session_state["OPENAI_API_KEY"] = "sk-proj-8WDPTIBAZyUIpTcc7XDXT3BlbkFJk49DFk0x8C4oZVDkYwgv"
        st.session_state["pdfquery"] = PDFQuery(st.session_state["OPENAI_API_KEY"],model)
        new_chat()
        st.session_state["init"] = "ok"

# 模拟文件上传进度
def fake_file_upload():
    placeholder = st.sidebar.empty()
    progress_bar = placeholder.progress(0)
    for percent_complete in range(100):
        time.sleep(0.05)  # 模拟上传的延迟
        progress_bar.progress(percent_complete + 1)
    placeholder.success("文件上传成功")
    placeholder.empty()


# 定义处理图片的函数并使用缓存
@st.cache_data(show_spinner=False)
def process_image(img_bytes):
    img_base = base64.b64encode(img_bytes).decode('utf-8')
    #client = ZhipuAI(api_key="a8285262398bd2ceb3ea50a32476f0f8.7UanZsyNvOpHbyIk")
    client = OpenAI(
    base_url='http://localhost:11434/v1/',
    # required but ignored
    api_key='ollama',
    )
    response = client.chat.completions.create(
        model="minicpm-v",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64,"+img_base
                        }
                    },
                    {
                        "type": "text",
                        "text":" 请提取所有信息！"
                    }
                ]
            }
        ]
    )

    return "图中的信息是:" + response.choices[0].message.content

def main():
    os.environ['LANGCHAIN_TRACING_V2'] = "true"
    os.environ['LANGCHAIN_API_KEY'] = "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"
    with st.sidebar:
        st.sidebar.subheader(f"欢迎您, {st.session_state.get('name')}同学")
        st.title(":blue[📝 AI学习助手]")
        base_model="gpt-4o"
        # 创建一个开关按钮
        #enabled = st.checkbox('选择启用代码增强模型', value=False,on_change=delete_init)
        # 显示开关状态
        #if enabled:
        #    st.caption('👨‍💻代码增强模型已启用！')
        #    base_model="qwen2.5-coder:7b"
        #else:
        #    base_model="gpt-4o"
        initialize(base_model)
        content = st.selectbox(
            '选择课程',
            (
            '数字逻辑与微处理器','计算机组成与体系结构','数据结构'),on_change=delete_agent)
        create_agent(content)
        
        st.subheader("上传文件")
        st.sidebar.file_uploader(
            "Upload document",
            type=["pdf"],
            key="file_uploader",
            on_change=read_and_save_file,
            label_visibility="collapsed",
            accept_multiple_files=True,
        )
        st.button("嵌入文档", key="new_agent", on_click=create_new_agent)
        if "embed_tip" in st.session_state:
            st.caption(st.session_state["embed_tip"])
            del st.session_state["embed_tip"]

        ###image
        st.subheader("上传图片")
        uploaded_img = st.sidebar.file_uploader("上传图片", type=["jpeg", "jpg", "png"],label_visibility="collapsed")
        if uploaded_img is not None:
            #fake_file_upload()
            # 打开上传的图片
            image = Image.open(uploaded_img).convert("RGB")
                # 在侧边栏中显示图片
            st.sidebar.image(image, caption="上传的图片", use_column_width=True)
                # 将文件指针重置到开头
            # uploaded_img.seek(0)

            img_bytes = uploaded_img.getvalue()
            st.session_state["img_res"] = process_image(img_bytes)


        st.button("开始新对话", key="new_chat_button", on_click=new_chat)
    st.subheader("📝 AI学习助手")
    st.caption("🚀 基于大语言模型的学习助手")

    #展示历史记录
    with st.chat_message("assistant"):
        st.write('您好，很高兴遇见您！我是您的AI学习助手，请告诉我您在课程中遇到的问题。')
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)

    #st.chat_input("请输入你的问题", key="user_input", on_submit=process_input)
    user_input = st.chat_input("请输入你的问题")

    if "img_res" not in st.session_state:
        st.session_state["img_res"] = None
    if st.session_state["img_res"] or user_input:
        all_input = (user_input or "") + (st.session_state["img_res"] or "")

    if user_input is not None and user_input != (" " * len(user_input)):
        with st.chat_message("user"):
            st.write(user_input)
        #流式输出回答
        with st.chat_message("assistant"):
            ai_output = st.write_stream(st.session_state["pdfquery"].ask(all_input, st.session_state.chat_history[-4:]))
            st.session_state["img_res"] = None
        st.session_state["chat_history"].append(HumanMessage(user_input))
        st.session_state["chat_history"].append(AIMessage(ai_output))
        #聊天记录截断
        # if len(st.session_state.chat_history) >= 16:
        #     st.session_state.chat_history = st.session_state.chat_history[-10:]

        # GPT生成用户可能问的问题
        query = st.session_state["pdfquery"].summarize(ai_output)
        st.session_state["query"] = query
        st.button(query + "     >", key="reask", on_click=reaskset)

    #追问
    query=st.session_state["query"]
    if st.session_state["reask"] == "True" and query!='':
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            ai_output = st.write_stream(st.session_state["pdfquery"].ask(query, st.session_state.chat_history))

        # 聊天记录
        st.session_state["chat_history"].append(HumanMessage(query))
        st.session_state["chat_history"].append(AIMessage(ai_output))


if __name__ == "__main__":
    if "authentication_status" not in st.session_state \
        or st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:

        st.warning("请先进行登录")
        switch_page("login")
    elif st.session_state["authentication_status"]:
        main()
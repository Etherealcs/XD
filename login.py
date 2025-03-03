import streamlit as st
from utils.OAuthClientLib import *
from utils.auth_functions import *
from streamlit_extras.switch_page_button import switch_page
def main():
    app_header()

    st.markdown("""

    ---
    **西安电子科技大学课程AI学习助手** 旨在为我们的学生提供一个先进的学习平台，利用最新的人工智能技术，以支持和增强您的学术研究和学习体验。无论您是深入研究特定领域的研究者，还是在寻求广泛知识的学习者，本平台都将成为您最可靠的助手。

    #### 功能特点：

    - **个性化学习建议**：根据您的学习历史和偏好，提供定制的学习资源和建议。
    - **智能问答系统**：无论何时您有任何学术问题，我们的AI助手都能提供即时的帮助和解答。
    - **资源丰富**：链接到海量的学术资源和文献，支持您的学习和研究需要。
    - **交互式学习体验**：通过互动问答和智能测验，提高学习的互动性和效果。
    - **研究项目支持**：助力您的研究项目，从文献搜集到数据分析，提供全方位的技术支持。

    #### 使命：

    我们致力于通过集成创新的教育技术，优化学习路径，使每一位西电的学子都能够在学术追求中达到最佳表现。课程AI学习助手是您通向学术卓越的桥梁。

    ---
    #### 提问建议：           

    1. **具体明确**：
            请尽量具体描述您的问题，如果问题涉及到特定的课本章节或概念，请一并提供。这有助于我们提供更准确的答案。

    2. **提供上下文**：
            如果您的问题是基于特定的学习背景或例子，提供这些信息将帮助我们更好地理解您的需求。

    3. **分步提问**：
            对于复杂的问题，尝试分解成若干小问题逐个提问，这样可以帮助您更系统地理解问题的各个部分。

    4. **使用关键词**：
            在提问时，清晰地标明相关的专业术语或关键词，如特定的理论、公式名等。



    
    ### 开始探索

    现在，开始您的学习之旅吧！如果您有任何问题，随时使用我们的问答系统寻求帮助，或浏览我们丰富的资源库来深化您的知识。课程AI学习助手，伴您每一步学术旅程。
    """)


    st.image('./images/research-assistant-gpt-01.jpg', width=600)
    st.markdown("---")
    st.markdown("AI Assistant   © 2024. All Rights Reserved.")

def app_header():
    st.image('./images/xidian_logo.jpg', width=100)
    st.markdown("# 登录界面")
    st.markdown("### 欢迎来到课程AI学习助手!")
    st.markdown("探索知识的新视界，开启你的学习之旅。")

def get_db_connection_student():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn
def get_db_connection_teacher():
    conn = sqlite3.connect('teachers.db')
    conn.row_factory = sqlite3.Row
    return conn


def login_student():
    with st.form("login_form"):
        st.subheader("学生登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit_button = st.form_submit_button("登录")

        if submit_button:
            if check_student(username, password):
                st.success('Logged In as {}'.format(username))
                st.session_state["authentication_status_student"] = True
                st.session_state["authentication_status"] = True
                st.session_state["name"] = username
                switch_page("Students")
                st.rerun()
            else:
                st.warning('用户名或密码错误')
def login_teacher():
    with st.form("login_form"):
        st.subheader("教师登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit_button = st.form_submit_button("登录")

        if submit_button:
            if check_teacher(username, password):
                st.success('Logged In as {}'.format(username))
                st.session_state["authentication_status_teacher"] = True
                st.session_state["authentication_status"] = True

                st.session_state["name"] = username
                switch_page("Teachers")
                st.rerun()
            else:
                st.warning('用户名或密码错误')
        # if st.session_state["authentication_status_teacher"]:
        #     switch_page("Teachers")



def check_student(username, password):
    conn = get_db_connection_student()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    if user and user['password'] == hash_password(password):
        return True
    return False
def check_teacher(username, password):
    conn = get_db_connection_teacher()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    if user and user['password'] == hash_password(password):
        return True
    return False


def register_student():
    with st.form("Register User Form"):
        st.subheader("学生用户注册")
        username = st.text_input("用户名*")
        password = st.text_input("账户密码*", type="password")
        repeated_password = st.text_input("重复密码*", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            if create_student(username, password):
                st.success('You have successfully created a valid account')
                st.info('Go to Login Menu to login')
            else:
                st.warning('Username already exists')
            return True
    return False
def register_teacher():
    with st.form("Register User Form"):
        st.subheader("教师用户注册")
        username = st.text_input("用户名*")
        password = st.text_input("账户密码*", type="password")
        repeated_password = st.text_input("重复密码*", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            if create_teacher(username, password):
                st.success('You have successfully created a valid account')
                st.info('Go to Login Menu to login')
            else:
                st.warning('Username already exists')
            return True
    return False



def create_student(username, password):
    conn = get_db_connection_student()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cur.fetchone():
        return False
    cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True
def create_teacher(username, password):
    conn = get_db_connection_teacher()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cur.fetchone():
        return False
    cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    st.set_page_config(page_title="课程AI学习助手", layout="wide", page_icon="🏠")

    # Initialize session state for authentication
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "authentication_status_student" not in st.session_state:
        st.session_state["authentication_status_student"] = None
    if "authentication_status_teacher" not in st.session_state:
        st.session_state["authentication_status_teacher"] = None

    # Sidebar for logout
    if st.session_state.get("authentication_status_teacher"):
        st.sidebar.subheader(f"欢迎您, {st.session_state.get('name')}老师")
        if st.sidebar.button("登出"):
            logout()
            st.experimental_rerun()
    if st.session_state.get("authentication_status_student"):
        st.sidebar.subheader(f"欢迎您, {st.session_state.get('name')}同学")
        if st.sidebar.button("登出"):
            logout()
            st.experimental_rerun()

    # Authentication (Login/SignUp) options
    # st.session_state["authentication_status_flag"] = True
    if st.session_state["authentication_status"]:
        main()
    # if st.session_state["authentication_status_teacher"] and st.session_state["authentication_status_flag"]:
    #     switch_page("Teachers")
    #     st.session_state["authentication_status_flag"] = None
    # if st.session_state["authentication_status_student"] and st.session_state["authentication_status_flag"]:
    #     switch_page("Students")
    #     st.session_state["authentication_status_flag"] = None
    else:
        with st.container():
            col1, col2, col3 = st.columns([3,3,1])
            with col1:
                app_header()
            with col2:  
                st.markdown("""
                    <style>
                    div.row-widget.stRadio > div{flex-direction:row;} 
                    </style>
                    """, unsafe_allow_html=True)


                choice = st.selectbox("请选择登录或注册:", ["登录", "注册"], index=0)

                if choice == "登录":
                    st.markdown("如果您没有账号，请选择注册来创建一个新账号。")
                    login_student()
                        # switch_page("Students")
                elif choice == "注册":
                    register_student()
                        


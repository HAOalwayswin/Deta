import pandas as pd
from deta import Deta
import bcrypt
import streamlit as st

deta = Deta(deta_key)
deta1= Deta(deta1_key)
db = deta.Base("database")
db1 = deta1.Base("posts")
post_db=db1


st.set_page_config(
    page_title='Deta DB 활용한 로그인',
    page_icon='🧊',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'http://www.example.com',
        'Report a bug': None,
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
#--------------계정 로그인------------------------------------------
# Deta 프로젝트 키 설정

# Deta Base 초기화 (여기서 "users"는 사용자 정보를 저장하는 Deta Base의 이름입니다)

def verify_user(username, password):
    user = db.get(username)  # 'username'을 키로 사용하여 사용자를 검색합니다.
    if user:
        # 데이터베이스에 저장된 해시된 비밀번호를 bytes로 변환합니다.
        stored_password = user.get("password")
        if isinstance(stored_password, int):  # 비밀번호가 정수로 저장된 경우, 이는 잘못된 것입니다.
            st.error(f"Stored password for '{username}' is not hashed correctly in the database.")
            return False
        stored_password = stored_password.encode('utf-8')

        # 사용자가 입력한 비밀번호를 bytes로 변환합니다.
        password = password.encode('utf-8')

        # 비밀번호를 확인합니다.
        if bcrypt.checkpw(password, stored_password):
            return True
        else:
            st.error("입력된 패스워드는 잘못되었습니다.")
            return False
    else:
        st.error(f"아이디 '{username}' 를 찾지 못하였습니다.")
        return False

def login_user():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("로그인")

        if submit_button:
            if verify_user(username, password):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.success("로그인 했습니다.")
                return username  # 로그인에 성공한 username을 반환합니다.
            else:
                st.error("아이디 또는 비밀번호를 확인하세요.")
                return None  # 로그인에 실패한 경우 None을 반환합니다.



#-------------post DB를 별도로 분리----------------------
def create_post(username, title, content):
    """
    Create a new post and save it to the Deta Base.
    """
    post_key = f"{username}:{title}"  # 각 포스트에 대해 고유한 키를 생성합니다.
    post = {
        "key": post_key,
        "title": title,
        "content": content,
        "author": username
    }
    posts_db.put(post)  # DB에 포스트를 저장합니다.


def post_form(username):
    with st.form("post_form"):
        title = st.text_input("제목")
        content = st.text_area("내용")
        submit_post = st.form_submit_button("저장하기")

        if submit_post and title and content:
            # 게시글을 DB에 저장합니다.
            create_post(username, title, content)
            # 성공 메시지를 표시합니다.
            st.success("게시글이 성공적으로 저장되었습니다!")
            records = db1.fetch().items
            df = pd.DataFrame(records)
            st.dataframe(df,use_container_width=True)


#----------------메인 실행함수-------------------------------------
def main():
    # 세션 상태의 'authenticated'와 'username'이 초기화되지 않았다면 기본값으로 설정합니다.
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    # 로그인 폼을 보여주고 로그인을 시도합니다.
    # 로그인에 성공하면 username을 반환받습니다.
    username = login_user() if not st.session_state['authenticated'] else st.session_state['username']

    # 인증된 사용자가 있을 경우에만 게시글 작성 폼을 보여줍니다.
    if st.session_state['authenticated'] and username:
        st.header("Create a new post")
        post_form(username)



if __name__ == "__main__":
    main()

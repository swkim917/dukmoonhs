import streamlit as st


if "login_id" not in st.session_state:
    st.session_state.login_id = None


def login():
    st.title("스마트 기기 대여 관리 앱")
    st.divider()
    
    st.header("관리자 계정 로그인")

    with st.form(key="login_form"):
        userid = st.text_input("아이디를 입력하세요")
        passwd = st.text_input("비밀번호를 입력하세요", type="password")
        
        submit_button = st.form_submit_button(label="로그인")

    if submit_button:
        # Create the SQL connection to dmgh_db as specified in your secrets file.
        conn = st.connection('dmgh_db', type='sql')
        df_user = conn.query(
            "select userid, passwd, name from users where userid = :userid",
            ttl=3600,
            params={"userid": userid})
        
        if df_user['userid'].count() == 1:
            db_passwd = df_user.iloc[0]['passwd']
            
            if passwd == db_passwd:
                st.session_state.login_id = userid
                st.session_state.login_name = df_user.iloc[0]['name']
                st.rerun()
            else:
                st.error("비밀번호가 일치하지 않습니다.")
        else: # df_user['userid'].count() == 0
            st.error("존재하지 않는 아이디 입니다.")
        

def logout():
    st.session_state.login_id = None
    st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
tablet_manager_page = st.Page("tablet_manager.py", title="스마트 기기 대여 관리")

account_pages = [tablet_manager_page, logout_page]

if st.session_state.login_id:
    pg = st.navigation(account_pages)
    st.sidebar.text(f"{st.session_state.login_name}({st.session_state.login_id})님 로그인됨.")
else:
    pg = st.navigation([login_page])

# --- SHARED ON ALL PAGES ---
st.logo("images/myLogo.png")
st.sidebar.text("Made with ❤ by Sangwoo")

pg.run()

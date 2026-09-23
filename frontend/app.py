import streamlit as st
import requests

API_URL = f"http://localhost:8000"

st.set_page_config(
    page_title="Text2SQL Agent",
    page_icon="✨",
    layout="wide"
)

# ---------------- Session State Init ----------------
if 'page' not in st.session_state:
    st.session_state.page = 'login'      # which auth screen to show
if 'token' not in st.session_state:
    st.session_state.token = None        # None = not logged in
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'login_error' not in st.session_state:
    st.session_state.login_error = None
if 'register_error' not in st.session_state:
    st.session_state.register_error = None
if 'register_success' not in st.session_state:
    st.session_state.register_success = None

# ----------------- Chat state init -------------------
if 'selected_chat_id' not in st.session_state:
    st.session_state.selected_chat_id = None
if 'history_error' not in st.session_state:
    st.session_state.history_error = None
if 'detail_error' not in st.session_state:
    st.session_state.detail_error = None
if 'delete_error' not in st.session_state:
    st.session_state.delete_error = None
if 'delete_success' not in st.session_state:
    st.session_state.delete_success = None
if 'new_chat_error' not in st.session_state:
    st.session_state.new_chat_error = None
if 'response_error' not in st.session_state:
    st.session_state.response_error = None

# ---------------- Auth Header ----------------
def auth_headers() -> dict:
    return {
        'Authorization': f'Bearer {st.session_state.token}'
    }

def go_to(page: str) -> None:
    st.session_state.page = page

# ---------------- Login Callback ----------------
def do_login():
    username = st.session_state.login_username
    password = st.session_state.login_password

    if not username or not password:
        st.session_state.login_error = "Please enter the appropriate detail above."
        return

    resp = requests.post(
        f"{API_URL}/login",
        data={'username': username, 'password': password}
    )

    if resp.ok:
        data = resp.json()
        st.session_state.token = data['access_token']
        st.session_state.username = username
        st.session_state.login_error = None
        st.session_state.page = 'main'
    else:
        st.session_state.login_error = "Internal Server Error"

# ---------------- Register Callback ----------------
def do_register():
    username = st.session_state.reg_username
    password = st.session_state.reg_password
    
    if len(username) < 3:
        st.session_state.register_error = 'Username must be at least 3 characters long.'
        st.session_state.register_success = None
        return

    if len(password) < 8:
        st.session_state.register_error = "Password must be at least 8 characters long."
        st.session_state.register_success = None
        return

    resp = requests.post(
        f"{API_URL}/register",
        json={"username": username, "password": password}
    )

    if resp.ok:
        st.session_state.register_error = None
        st.session_state.register_success = f"Account created for '{username}'. Please log in."
        st.session_state.page = "login"
    else:
        st.session_state.register_error = resp.json().get("detail", "Registration failed.")
        st.session_state.register_success = None

# ---------------- new_chat callback ----------------
def create_new_chat(question: str):
    resp = requests.post(
        f"{API_URL}/ask/new_chat" , 
        headers=auth_headers(),
        data={'payload': question}
    )

    if resp.ok:
        return resp.json()
    else:
        st.session_state.new_chat_error = resp.json().get("detail", "Could not initiate new chat.")
        return []
    
# ---------------- history callback ----------------
def fetch_history() -> list[dict]:
    resp = requests.get(f"{API_URL}/history" , headers=auth_headers())

    if resp.ok:
        return resp.json()
    else:
        st.session_state.history_error = resp.json().get("detail", "Could not load history.")
        return []

# ---------------- select chat callback ----------------
def select_chat(thread_id: int) -> None:
    st.session_state.selected_chat_id = thread_id

# ---------------- new chat dashboard callback ----------------
def new_chat_dashboard() -> None:
    st.session_state.selected_chat_id = None

# ---------------- fetch chat callback ----------------
def fetch_chat_detail(thread_id: int) -> dict | None:
    resp = requests.get(
        f"{API_URL}/fetch_chat/{thread_id}",
        headers=auth_headers()
    )

    if resp.ok:
        return resp.json()
    else:
        st.session_state.detail_error = "Could not load chat."
        return None

# ---------------- ask chat callback ----------------
def ask_chat(thread_id: int, question: str):
    resp = requests.post(
        f"{API_URL}/ask/{thread_id}",
        headers=auth_headers(),
        data={'payload': question}
    )

    if resp.ok:
        st.session_state.response_error = None
    else:
        st.session_state.response_error = resp.json().get("detail", "Response failed.")

# ---------------- delete callback ----------------
def do_delete(thread_id: int):
    resp = requests.delete(
        f"{API_URL}/chat/{thread_id}",
        headers=auth_headers()
    )

    if resp.ok:
        st.session_state.selected_chat_id = None
        st.session_state.delete_success = 'Your document is deleted successfully.'
    else:
        st.session_state.delete_error = resp.json().get('details', 'Failed to delete.')

# ---------------- logout callback ----------------
def do_logout():
    st.session_state.page = 'login'
    st.session_state.token = None
    st.session_state.username = ''
    st.session_state.uploader_version = 0
    st.session_state.selected_doc_id = None

# ---------------- Register Page ----------------
def register_page():
    with st.container(border=True):
        st.subheader("Register")
        st.text_input("Username", key="reg_username")
        st.text_input("Password", type="password", key="reg_password", help="Must be at least 8 characters.")
        st.button("Create account", key="reg_submit", on_click=do_register)

        if st.session_state.register_error:
            st.error(st.session_state.register_error)

    st.markdown("Already a user?")
    st.button("Login", key="to_login", on_click=go_to, args=("login",))


# ---------------- Login Page ----------------
def login_page():
    if st.session_state.register_success:
        st.success(st.session_state.register_success)
        st.session_state.register_success = None
        
    with st.container(border=True):
        st.subheader("Login")
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        st.button("Login", key="login_submit", on_click=do_login)

        if st.session_state.login_error:
            st.error(st.session_state.login_error)
            st.session_state.login_error = None

    st.markdown("Not a user?")
    st.button("Register", key="to_register", on_click=go_to, args=("register",))


# ---------------- Main App (logged in) ----------------
def main_page():
    with st.sidebar:
        st.text_input("Username", value=st.session_state.get('username', ''), disabled=True)
        st.button("⏻ Logout", key="logout_button", on_click=do_logout)
        st.markdown("---")

        st.button("📤 New Chat", key="upload_button", on_click=new_chat_dashboard)

        st.markdown("---")

        st.markdown("**Previous Chats:**")

        st.session_state.history_error = None
        history = fetch_history()

        if st.session_state.history_error:
            st.error(st.session_state.history_error)

        if not history:
            st.caption("No Chats yet.")
        else:
            for chat in history:
                label = f"{chat['name']})"
                st.button(
                    label,
                    key=f"doc_{chat['id']}",
                    on_click=select_chat,
                    args=(chat['id'],)
                )

    render_main_pane()

# ---------------- Render main pane ----------------
def render_main_pane():
    if st.session_state.selected_chat_id is None:
        st.title("WELCOME TO Text2SQL Agent")
        st.markdown("*select your chat from the history to regain all the previous conversation history*")
        if st.session_state.delete_success:
            st.error(st.session_state.delete_success)
            st.session_state.delete_success = None

        st.text_input("New chat", key="new_chat_bar")
        return

    st.session_state.detail_error = None
    chat = fetch_chat_detail(st.session_state.selected_chat_id)

    if st.session_state.detail_error:
        st.error(st.session_state.detail_error)
        return

    st.subheader(chat['name'])


# ---------------- Router ----------------
if st.session_state.token is None:
    if st.session_state.page == 'register':
        register_page()
    else:
        login_page()
else:
    main_page()
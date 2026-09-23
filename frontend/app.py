from __future__ import annotations

import json
from typing import Any

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 120  # agent can take a while

st.set_page_config(
    page_title="Text-To-SQL Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
_DEFAULTS: dict[str, Any] = {
    "page": "login",
    "token": None,
    "username": "",
    "user_id": None,
    "login_error": None,
    "register_error": None,
    "register_success": None,
    "selected_chat_id": None,
    "history_cache": None,          # list[dict] | None
    "history_error": None,
    "detail_error": None,
    "delete_error": None,
    "delete_success": None,
    "ask_error": None,
    "ask_loading": False,
    "pending_question": None,       # question waiting to be sent
}


def _init_state() -> None:
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_state()

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return {"detail": resp.text or f"HTTP {resp.status_code}"}


def _handle_http_error(resp: requests.Response, fallback: str) -> str:
    """Turn a failed response into a user-friendly message."""
    if resp.status_code == 401:
        # Token expired / invalid → force re-login
        st.session_state.token = None
        st.session_state.page = "login"
        return "Session expired. Please log in again."
    if resp.status_code == 429:
        return "Rate limit exceeded. Please wait a moment and try again."
    if resp.status_code == 404:
        return "Resource not found."
    if resp.status_code >= 500:
        body = _safe_json(resp)
        detail = body.get("detail") if isinstance(body, dict) else str(body)
        return f"Server error: {detail or fallback}"
    body = _safe_json(resp)
    if isinstance(body, dict):
        return str(body.get("detail") or body.get("message") or fallback)
    return fallback


def api_post_json(path: str, payload: dict, *, auth: bool = True) -> tuple[bool, Any]:
    try:
        headers = auth_headers() if auth else {}
        resp = requests.post(
            f"{API_URL}{path}",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if resp.ok:
            return True, resp.json()
        return False, _handle_http_error(resp, "Request failed.")
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the backend. Is the API running on port 8000?"
    except requests.exceptions.Timeout:
        return False, "Request timed out. The agent may still be working — try refreshing."
    except Exception as exc:
        return False, f"Unexpected error: {exc}"


def api_post_form(path: str, data: dict, *, auth: bool = False) -> tuple[bool, Any]:
    try:
        headers = auth_headers() if auth else {}
        resp = requests.post(
            f"{API_URL}{path}",
            data=data,
            headers=headers,
            timeout=30,
        )
        if resp.ok:
            return True, resp.json()
        return False, _handle_http_error(resp, "Request failed.")
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the backend. Is the API running on port 8000?"
    except requests.exceptions.Timeout:
        return False, "Request timed out."
    except Exception as exc:
        return False, f"Unexpected error: {exc}"


def api_get(path: str) -> tuple[bool, Any]:
    try:
        resp = requests.get(
            f"{API_URL}{path}",
            headers=auth_headers(),
            timeout=30,
        )
        if resp.ok:
            return True, resp.json()
        return False, _handle_http_error(resp, "Could not load data.")
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the backend. Is the API running on port 8000?"
    except requests.exceptions.Timeout:
        return False, "Request timed out."
    except Exception as exp:
        return False, f"Unexpected error: {exp}"


def api_delete(path: str) -> tuple[bool, Any]:
    try:
        resp = requests.delete(
            f"{API_URL}{path}",
            headers=auth_headers(),
            timeout=30,
        )
        if resp.ok:
            return True, resp.json() if resp.content else {"success": True}
        return False, _handle_http_error(resp, "Delete failed.")
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the backend."
    except Exception as exp:
        return False, f"Unexpected error: {exp}"


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------


def go_to(page: str) -> None:
    st.session_state.page = page


def invalidate_history() -> None:
    st.session_state.history_cache = None


# ---------------------------------------------------------------------------
# Auth callbacks
# ---------------------------------------------------------------------------


def do_login() -> None:
    username = (st.session_state.get("login_username") or "").strip()
    password = st.session_state.get("login_password") or ""

    if not username or not password:
        st.session_state.login_error = "Please enter both username and password."
        return

    ok, result = api_post_form(
        "/login",
        {"username": username, "password": password},
        auth=False,
    )
    if ok:
        st.session_state.token = result["access_token"]
        st.session_state.username = username
        st.session_state.login_error = None
        st.session_state.page = "main"
        st.session_state.selected_chat_id = None
        invalidate_history()
    else:
        st.session_state.login_error = result


def do_register() -> None:
    username = (st.session_state.get("reg_username") or "").strip()
    password = st.session_state.get("reg_password") or ""

    if len(username) < 3:
        st.session_state.register_error = "Username must be at least 3 characters."
        st.session_state.register_success = None
        return
    if len(password) < 8:
        st.session_state.register_error = "Password must be at least 8 characters."
        st.session_state.register_success = None
        return

    ok, result = api_post_json(
        "/register",
        {"username": username, "password": password},
        auth=False,
    )
    if ok:
        st.session_state.register_error = None
        st.session_state.register_success = (
            f"Account created for **{username}**. Please log in."
        )
        st.session_state.page = "login"
    else:
        st.session_state.register_error = result
        st.session_state.register_success = None


def do_logout() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    _init_state()
    st.session_state.page = "login"


# ---------------------------------------------------------------------------
# Chat API wrappers
# ---------------------------------------------------------------------------


def fetch_history() -> list[dict]:
    if st.session_state.history_cache is not None:
        return st.session_state.history_cache

    ok, result = api_get("/history")
    if ok:
        st.session_state.history_error = None
        st.session_state.history_cache = result if isinstance(result, list) else []
        return st.session_state.history_cache

    st.session_state.history_error = result
    st.session_state.history_cache = []
    return []


def fetch_chat_detail(thread_id: int) -> dict | None:
    ok, result = api_get(f"/fetch_chat/{thread_id}")
    if ok and isinstance(result, dict):
        st.session_state.detail_error = None
        return result
    st.session_state.detail_error = result if isinstance(result, str) else "Could not load chat."
    return None


def create_new_chat(question: str) -> dict | None:
    """POST /ask/new_chat — returns AnswerResponse and creates the chat server-side."""
    ok, result = api_post_json("/ask/new_chat", {"question": question})
    if ok:
        st.session_state.ask_error = None
        invalidate_history()
        return result
    st.session_state.ask_error = result
    return None


def ask_in_chat(thread_id: int, question: str) -> dict | None:
    """POST /ask/{thread_id} — follow-up question."""
    ok, result = api_post_json(f"/ask/{thread_id}", {"question": question})
    if ok:
        st.session_state.ask_error = None
        invalidate_history()
        return result
    st.session_state.ask_error = result
    return None


def delete_chat(thread_id: int) -> bool:
    ok, result = api_delete(f"/chat/{thread_id}")
    if ok:
        st.session_state.delete_error = None
        st.session_state.delete_success = "Chat deleted successfully."
        st.session_state.selected_chat_id = None
        invalidate_history()
        return True
    st.session_state.delete_error = result
    return False


# ---------------------------------------------------------------------------
# Message parsing & display
# ---------------------------------------------------------------------------


def _extract_content(msg: Any) -> tuple[str, str]:
    """
    Normalize a LangChain message dict into (role, text).
    Handles both classic messages_to_dict format and plain dicts.
    """
    if not isinstance(msg, dict):
        return "unknown", str(msg)

    # Classic: {"type": "human"|"ai"|"system", "data": {"content": "..."}}
    msg_type = (msg.get("type") or msg.get("role") or "").lower()
    data = msg.get("data") if isinstance(msg.get("data"), dict) else msg
    content = data.get("content") if isinstance(data, dict) else None

    if content is None:
        content = msg.get("content", "")

    # Flatten list content (multimodal)
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            else:
                parts.append(str(part))
        content = "\n".join(parts)

    content = str(content or "").strip()

    if msg_type in ("human", "user"):
        role = "user"
    elif msg_type in ("ai", "assistant"):
        role = "assistant"
    elif msg_type == "system":
        role = "system"
    else:
        # Fallback: try name field
        name = (data.get("name") if isinstance(data, dict) else None) or ""
        role = "user" if name.lower() == "human" else "assistant"

    return role, content


def render_messages(content: Any) -> None:
    """Render the conversation history stored in chat.content."""
    if not content:
        st.info("No messages in this chat yet.")
        return

    # content may be a list of message dicts, or a JSON string, or nested
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            st.warning("Could not parse chat content.")
            return

    if not isinstance(content, list):
        st.warning("Unexpected chat content format.")
        return

    for msg in content:
        role, text = _extract_content(msg)
        if not text:
            continue
        if role == "system":
            continue  # skip system prompts in UI

        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(text)


def render_answer_card(answer: dict) -> None:
    """Show the structured AnswerResponse (SQL + final answer) nicely."""
    can_answer = answer.get("can_answer", True)
    sql = answer.get("sql_query")
    final = answer.get("final_answer") or ""
    retries = answer.get("retry_count", 0)

    if not can_answer:
        st.warning("The agent could not answer this question with the available data.")
        if final:
            st.markdown(final)
        return

    if sql:
        with st.expander("Generated SQL", expanded=False):
            st.code(sql, language="sql")

    if final:
        st.markdown(final)

    if retries and retries > 0:
        st.caption(f"Self-corrected {retries} time(s).")


# ---------------------------------------------------------------------------
# Pages — Auth
# ---------------------------------------------------------------------------


def register_page() -> None:
    st.markdown("## Register")
    with st.container(border=True):
        st.text_input("Username", key="reg_username", placeholder="At least 3 characters")
        st.text_input(
            "Password",
            type="password",
            key="reg_password",
            placeholder="At least 8 characters",
            help="Must be at least 8 characters.",
        )
        st.button("Create account", key="reg_submit", on_click=do_register, type="primary", use_container_width=True)

        if st.session_state.register_error:
            st.error(st.session_state.register_error)

    st.markdown("Already a user?")
    st.button("Login", key="to_login", on_click=go_to, args=("login",), use_container_width=True)


def login_page() -> None:
    if st.session_state.register_success:
        st.success(st.session_state.register_success)
        st.session_state.register_success = None

    st.markdown("## Login")
    with st.container(border=True):
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        st.button("Login", key="login_submit", on_click=do_login, type="primary", use_container_width=True)

        if st.session_state.login_error:
            st.error(st.session_state.login_error)
            st.session_state.login_error = None

    st.markdown("Not a user?")
    st.button("Register", key="to_register", on_click=go_to, args=("register",), use_container_width=True)


# ---------------------------------------------------------------------------
# Pages — Main (logged in)
# ---------------------------------------------------------------------------


def _sidebar() -> None:
    with st.sidebar:
        st.markdown(f"**@{st.session_state.username}**")
        st.button("⏻ Logout", key="logout_btn", on_click=do_logout, use_container_width=True)
        st.divider()

        if st.button("＋ New Chat", key="new_chat_btn", type="primary", use_container_width=True):
            st.session_state.selected_chat_id = None
            st.session_state.ask_error = None
            st.session_state.detail_error = None
            st.rerun()

        st.markdown("**History**")

        if st.session_state.history_error:
            st.error(st.session_state.history_error)

        history = fetch_history()

        if not history:
            st.caption("No chats yet.")
        else:
            for chat in history:
                chat_id = chat.get("id")
                name = (chat.get("name") or "Untitled")[:48]
                is_selected = st.session_state.selected_chat_id == chat_id

                cols = st.columns([0.82, 0.18])
                with cols[0]:
                    label = f"{'▶ ' if is_selected else ''}{name}"
                    if st.button(
                        label,
                        key=f"hist_{chat_id}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary",
                    ):
                        st.session_state.selected_chat_id = chat_id
                        st.session_state.ask_error = None
                        st.session_state.detail_error = None
                        st.rerun()
                with cols[1]:
                    if st.button("🗑", key=f"del_{chat_id}", help="Delete chat"):
                        delete_chat(chat_id)
                        st.rerun()

        if st.session_state.delete_success:
            st.success(st.session_state.delete_success)
            st.session_state.delete_success = None
        if st.session_state.delete_error:
            st.error(st.session_state.delete_error)
            st.session_state.delete_error = None


def _welcome_pane() -> None:
    """Bottom-left wireframe: welcome + input to start a new chat."""
    st.markdown("# WELCOME TO Text-To-SQL Agent")
    st.markdown(
        "*Select a chat from the history to regain previous conversation history, "
        "or type a question below to start a new chat.*"
    )

    if st.session_state.ask_error:
        st.error(st.session_state.ask_error)

    question = st.chat_input("Ask a question about the database…", key="welcome_input")
    if question:
        question = question.strip()
        if not question:
            st.warning("Please enter a non-empty question.")
            return

        with st.spinner("Thinking… this may take a moment."):
            answer = create_new_chat(question)

        if answer is None:
            # error already stored
            st.rerun()
            return

        # Refresh history and select the newly created chat
        invalidate_history()
        history = fetch_history()
        # Newest chat is first (ordered by created_at desc)
        if history:
            st.session_state.selected_chat_id = history[0]["id"]
        st.rerun()


def _active_chat_pane(chat_id: int) -> None:
    """Bottom-right wireframe: chat name, messages, follow-up input."""
    chat = fetch_chat_detail(chat_id)

    if st.session_state.detail_error:
        st.error(st.session_state.detail_error)
        if st.button("← Back to welcome"):
            st.session_state.selected_chat_id = None
            st.rerun()
        return

    if chat is None:
        st.error("Chat not found.")
        st.session_state.selected_chat_id = None
        return

    # Header
    title = chat.get("name") or f"Chat #{chat_id}"
    col_title, col_actions = st.columns([0.85, 0.15])
    with col_title:
        st.subheader(title)
    with col_actions:
        if st.button("🗑 Delete", key="delete_active", help="Delete this chat"):
            delete_chat(chat_id)
            st.rerun()

    st.divider()

    # Messages
    render_messages(chat.get("content"))

    if st.session_state.ask_error:
        st.error(st.session_state.ask_error)

    # Follow-up input
    question = st.chat_input("Ask a follow-up question…", key=f"chat_input_{chat_id}")
    if question:
        question = question.strip()
        if not question:
            st.warning("Please enter a non-empty question.")
            return

        with st.spinner("Thinking…"):
            answer = ask_in_chat(chat_id, question)

        if answer is None:
            st.rerun()
            return

        # Show the latest structured answer immediately, then reload full history
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            render_answer_card(answer)

        # Force re-fetch so next paint has full transcript
        invalidate_history()
        st.rerun()


def main_page() -> None:
    _sidebar()
    if st.session_state.selected_chat_id is None:
        _welcome_pane()
    else:
        _active_chat_pane(st.session_state.selected_chat_id)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if st.session_state.token is None:
    # Center the auth forms a bit
    left, mid, right = st.columns([1, 1.4, 1])
    with mid:
        if st.session_state.page == "register":
            register_page()
        else:
            login_page()
else:
    main_page()
import streamlit as st
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os


def _ensure_streamlit_context():
    """Exit early with a clear hint when script is not started by streamlit."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is None:
            print("请使用 streamlit run chatbot.py 启动该应用。")
            raise SystemExit(0)
    except Exception:
        # If runtime internals change, keep app behavior unchanged.
        pass


_ensure_streamlit_context()

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="DeepSeek Chat",
    layout="centered",
)

# ── 自定义样式 ─────────────────────────────────────────────
st.markdown("""
<style>
/* 整体背景 */
.stApp { background-color: #0f1117; }

/* 聊天消息气泡 */
.stChatMessage {
    border-radius: 12px;
    margin-bottom: 8px;
}

/* 用户消息 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #1e2130;
}

/* AI 消息 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #161922;
}

/* 侧边栏 */
[data-testid="stSidebar"] { background-color: #0d0f18; }

/* 输入框 */
.stChatInputContainer textarea {
    background-color: #1e2130 !important;
    color: #e8eaf0 !important;
    border: 1px solid #2d3148 !important;
    border-radius: 12px !important;
}

/* 标题渐变色 */
.gradient-title {
    background: linear-gradient(135deg, #4f8ef7, #a259f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0;
}

.subtitle {
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: 4px;
    margin-bottom: 24px;
}

/* 统计数字 */
.stat-box {
    background: #1e2130;
    border: 1px solid #2d3148;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.stat-num { font-size: 1.5rem; font-weight: 700; color: #4f8ef7; }
.stat-label { font-size: 0.75rem; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

# ── 初始化 session state ──────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("DEEPSEEK_API_KEY", "")

# ── 侧边栏 ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 设置")

    # API Key 输入
    api_key_input = st.text_input(
        "DeepSeek API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-b691a67f20034733a5c6fa77b1b2ad95",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.divider()

    # 模型参数
    st.markdown("### 模型参数")
    model_name = st.selectbox(
        "模型",
        ["deepseek-chat", "deepseek-reasoner"],
        index=0,
    )
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1,
                            help="越高越有创意，越低越严谨")
    max_tokens = st.slider("最大输出长度", 256, 4096, 1024, 128)

    st.divider()

    # 系统提示词
    st.markdown("### 系统提示词")
    system_prompt = st.text_area(
        "设定 AI 的角色和行为",
        value="你是一个有帮助的AI助手，回答简洁、准确。",
        height=120,
    )

    st.divider()

    # 统计信息
    st.markdown("### 本次会话")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num">{len(st.session_state.messages)}</div>
            <div class="stat-label">消息数</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        turns = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num">{turns}</div>
            <div class="stat-label">对话轮次</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # 操作按钮
    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.session_state.messages:
        # 导出对话
        history_text = "\n\n".join(
            f"[{m['role'].upper()}]\n{m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            "导出对话记录",
            data=history_text,
            file_name="chat_history.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ── 主页面 ────────────────────────────────────────────────
st.markdown('<p class="gradient-title"> DeepSeek Chat</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">由 DeepSeek 大模型驱动的智能对话助手</p>', unsafe_allow_html=True)

# API Key 未设置时提示
if not st.session_state.api_key:
    st.warning("请在左侧侧边栏输入 DeepSeek API Key 以开始对话。")
    st.stop()

# ── 构建模型 ──────────────────────────────────────────────
@st.cache_resource
def get_model(api_key, model, temp):
    os.environ["DEEPSEEK_API_KEY"] = api_key
    return ChatDeepSeek(
        model=model,
        temperature=temp,
        api_key=api_key,
    )

llm = get_model(st.session_state.api_key, model_name, temperature)

# ── 显示历史消息 ──────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 欢迎语（无消息时） ────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("你好！我是 DeepSeek 智能助手, 有什么可以帮你的吗？")

    # 快捷问题建议
    st.markdown("**试试这些问题：**")
    suggestions = [
        "用 Python 写一个快速排序算法",
        "解释一下 Transformer 的注意力机制",
        "帮我写一封商务邮件",
        "今天天气好吗（测试拒绝回答）",
    ]
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(suggestion, use_container_width=True, key=f"sug_{i}"):
                st.session_state._quick_input = suggestion
                st.rerun()

# 处理快捷问题点击
if hasattr(st.session_state, "_quick_input"):
    quick = st.session_state._quick_input
    del st.session_state._quick_input
    # 注入到对话流程
    st.session_state.messages.append({"role": "user", "content": quick})
    with st.chat_message("user"):
        st.markdown(quick)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            lc_messages = [SystemMessage(content=system_prompt)]
            for m in st.session_state.messages[:-1]:
                if m["role"] == "user":
                    lc_messages.append(HumanMessage(content=m["content"]))
                else:
                    lc_messages.append(AIMessage(content=m["content"]))
            lc_messages.append(HumanMessage(content=quick))

            response = llm.invoke(lc_messages, config={"max_tokens": max_tokens})
            answer = response.content

        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# ── 用户输入 ──────────────────────────────────────────────
if user_input := st.chat_input("输入消息，按 Enter 发送..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 构建完整对话历史
    lc_messages = [SystemMessage(content=system_prompt)]
    for m in st.session_state.messages[:-1]:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))
    lc_messages.append(HumanMessage(content=user_input))

    # 流式输出
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            with st.spinner(""):
                for chunk in llm.stream(lc_messages, config={"max_tokens": max_tokens}):
                    if chunk.content:
                        full_response += chunk.content
                        placeholder.markdown(full_response)
            placeholder.markdown(full_response)
        except Exception as e:
            error_msg = f"调用失败：{str(e)}"
            placeholder.error(error_msg)
            full_response = error_msg

    st.session_state.messages.append({"role": "assistant", "content": full_response})
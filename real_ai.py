import streamlit as st
from openai import OpenAI
import time

# 1. 页面配置
st.set_page_config(page_title="欧阳毅的 AI 私人董事会", page_icon="🧠")
st.title("欧阳毅的 AI 私人董事会 🧠")
st.caption("基于 DeepSeek-V3 · 支持连续对话 & 记录保存")

# 2. 连接大脑 (使用 Secrets 安全连接)
# 只要你之前的 Secrets 配置对了，这里不用动
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

# --- 关键升级：初始化“记忆” ---
# 如果“记事本”里没有记录，就新建一个空的列表
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 3. 侧边栏设置
with st.sidebar:
    st.header("🎮 控制台")
    
    # 选择人设
    role = st.selectbox(
        "选择顾问风格：",
        ["霸道总裁", "马斯克", "苏格拉底"]
    )
    
    # 定义提示词
    system_prompt = ""
    if role == "霸道总裁":
        system_prompt = "你是商业大亨，说话简短有力，直击痛点，拒绝废话。"
    elif role == "马斯克":
        system_prompt = "你是马斯克，用第一性原理思考，极度理性，痴迷火星和未来科技。"
    elif role == "苏格拉底":
        system_prompt = "你是苏格拉底，喜欢用反问句引导用户思考，从不直接给出答案。"
        
    # --- 新功能：清除对话 ---
    if st.button("🗑️ 清空聊天记录"):
        st.session_state["messages"] = []
        st.rerun() # 刷新页面

    # --- 新功能：下载对话 ---
    # 把聊天记录变成一长串字符串
    chat_history_text = ""
    for msg in st.session_state["messages"]:
        role_name = "我" if msg["role"] == "user" else role
        chat_history_text += f"{role_name}: {msg['content']}\n\n"
    
    st.download_button(
        label="💾 下载本次对话 (TXT)",
        data=chat_history_text,
        file_name="ai_consult_history.txt",
        mime="text/plain"
    )

# 4. 展示历史聊天记录 (渲染气泡)
for msg in st.session_state["messages"]:
    # 如果是用户，显示头像 🧑‍💻，如果是AI，显示 🤖
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 5. 处理用户输入 (新的聊天框写法)
# st.chat_input 是 Streamlit 专门做的类似微信的输入框
if user_input := st.chat_input("请输入你的问题..."):
    
    # A. 先把用户的话显示出来，并记入小本本
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # B. AI 思考并回答
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty() # 占位符
        full_response = ""
        
        # 构建发给 DeepSeek 的完整消息历史 (带上 System Prompt)
        # 这样 AI 才知道上下文
        messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state["messages"]

        try:
            # 流式输出 (像打字机一样一个字一个字蹦出来，体验更好)
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_to_send,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # 加个光标效果
            
            message_placeholder.markdown(full_response) # 最后显示完整内容
            
        except Exception as e:
            st.error(f"出错了: {e}")
            full_response = "我掉线了，请重试..."

    # C. 把 AI 的话也记入小本本
    st.session_state["messages"].append({"role": "assistant", "content": full_response})
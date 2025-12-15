import streamlit as st
from openai import OpenAI

# 1. 配置页面
st.title("欧阳毅的 AI 私人董事会 🧠")
st.caption("基于 DeepSeek-V3 大模型 · 你的专属商业顾问")

# 2. 连接到 DeepSeek 大脑
# 注意：这里直接填 Key 是为了教学，以后做大项目要隐藏起来
import os
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],  # 这里的 secrets 是暗号，一会儿在网页上填
    base_url="https://api.deepseek.com"
)

# 3. 创建侧边栏（选择人设）
role = st.sidebar.selectbox(
    "请选择顾问风格：",
    ["霸道总裁 (一针见血)", "马斯克风格 (第一性原理)", "温和导师 (循循善诱)"]
)

# 定义不同的人设提示词
system_prompt = ""
if role == "霸道总裁 (一针见血)":
    system_prompt = "你是一个身价千亿的商业大亨，说话简短有力，直击痛点，喜欢用商业思维分析问题，不要说废话。"
elif role == "马斯克风格 (第一性原理)":
    system_prompt = "你是马斯克，用物理学思维和第一性原理回答问题，极度理性，甚至有点疯狂，喜欢谈论未来和科技。"
else:
    system_prompt = "你是一个智慧的人生导师，说话温暖，富有哲理，多引用书籍和名言。"

# 4. 用户输入区域
user_question = st.text_area("请告诉我你的困惑或商业构想：", height=100)

# 5. 点击按钮，开始思考
if st.button("开始咨询"):
    if not user_question:
        st.warning("老板，你还没输入问题呢！")
    else:
        # 显示加载转圈圈
        with st.spinner(f"正在连线 {role} 为你思考..."):
            try:
                # --- 关键时刻：发送请求给 DeepSeek ---
                response = client.chat.completions.create(
                    model="deepseek-chat",  # 指定模型
                    messages=[
                        {"role": "system", "content": system_prompt}, # 注入灵魂（人设）
                        {"role": "user", "content": user_question}    # 你的问题
                    ],
                    stream=False
                )
                
                # 获取答案
                answer = response.choices[0].message.content
                
                # 展示答案
                st.success("思考完成！")
                st.markdown("### 💡 顾问建议：")
                st.write(answer)
                
            except Exception as e:
                st.error(f"出错了：{e}")
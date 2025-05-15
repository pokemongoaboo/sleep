import streamlit as st
import time
import random

# 設置頁面配置
st.set_page_config(
    page_title="睡前日記",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 定義一些CSS樣式
st.markdown("""
<style>
    .main {
        background-color: #1e2a38;
        color: #f0f2f6;
        font-family: 'Arial', sans-serif;
    }
    .stButton button {
        background-color: #4e7496;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        margin: 10px 0;
        border: none;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #375980;
    }
    h1, h2, h3 {
        color: #8ab4e8;
    }
    .option-card {
        background-color: #2c3e50;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.3s;
    }
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        font-size: 12px;
        color: #8ab4e8;
    }
    .result-container {
        padding: 20px;
        background-color: #2c3e50;
        border-radius: 10px;
        margin-top: 20px;
    }
    .image-option {
        cursor: pointer;
        transition: transform 0.3s;
        margin: 10px;
        border-radius: 10px;
        overflow: hidden;
    }
    .image-option:hover {
        transform: scale(1.05);
    }
    .selected {
        border: 3px solid #8ab4e8;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state變量
if 'page' not in st.session_state:
    st.session_state.page = 1
    
if 'good_deed' not in st.session_state:
    st.session_state.good_deed = ""
    
if 'happy_moment' not in st.session_state:
    st.session_state.happy_moment = ""
    
if 'tomorrow_tasks' not in st.session_state:
    st.session_state.tomorrow_tasks = ""
    
if 'mood' not in st.session_state:
    st.session_state.mood = ""
    
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
    
if 'music_link' not in st.session_state:
    st.session_state.music_link = ""

# 定義頁面導航函數
def go_to_page(page_number):
    st.session_state.page = page_number
    
def skip_to_end():
    st.session_state.page = 6  # 結果頁面

def select_preset(field, value):
    if field == "good_deed":
        st.session_state.good_deed = value
    elif field == "happy_moment":
        st.session_state.happy_moment = value
    elif field == "tomorrow_tasks":
        st.session_state.tomorrow_tasks = value
    elif field == "mood":
        st.session_state.mood = value
        
def select_image(image_number):
    st.session_state.selected_image = image_number

# 預設選項
good_deed_options = ["幫助了同事解決問題", "整理了公共空間", "關心了家人/朋友"]
happy_moment_options = ["享受了美食", "聽了喜歡的音樂", "完成了一項任務"]
tomorrow_tasks_options = ["準備重要會議", "聯繫客戶/同事", "整理工作空間"]
mood_options = ["平靜", "疲憊", "滿足", "焦慮", "期待"]

# 模擬音樂推薦API
def get_music_recommendation(user_data):
    music_options = [
        "輕柔鋼琴曲 - 夜的詩篇",
        "自然聲音 - 雨天森林",
        "冥想音樂 - 深度放鬆",
        "環境音樂 - 海浪與微風",
        "古典樂 - 夜曲集"
    ]
    
    # 模擬API處理時間
    time.sleep(2)
    
    # 根據用戶數據選擇音樂 (實際應用中這裡會有真正的推薦算法)
    # 這裡只是簡單示範，實際可能需要更複雜的邏輯
    if "焦慮" in user_data.get('mood', ''):
        return music_options[1]  # 雨天森林
    elif "疲憊" in user_data.get('mood', ''):
        return music_options[2]  # 深度放鬆
    elif "滿足" in user_data.get('mood', ''):
        return music_options[0]  # 鋼琴曲
    else:
        return random.choice(music_options)

# 應用主體
st.title("🌙 睡前日記")

# 第一頁 - 開始界面
if st.session_state.page == 1:
    st.header("準備好進入今天的睡前儀式了嗎？")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("我準備好了，開始吧", key="start_yes"):
            go_to_page(2)
    with col2:
        if st.button("我不想寫，想直接睡覺", key="start_no"):
            skip_to_end()
            
# 第二頁 - 好事
elif st.session_state.page == 2:
    st.header("我今天做的好事")
    st.caption("請隨意書寫，沒有也沒關係")
    
    # 顯示預設選項
    st.write("你可以選擇以下預設選項或自行輸入:")
    cols = st.columns(3)
    for i, option in enumerate(good_deed_options):
        with cols[i]:
            if st.button(option, key=f"good_deed_{i}"):
                select_preset("good_deed", option)
    
    # 文本輸入
    st.session_state.good_deed = st.text_area("或者在這裡書寫", value=st.session_state.good_deed, height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("接下一題", key="good_deed_next"):
            go_to_page(3)
    with col2:
        if st.button("我不想寫，直接睡覺", key="good_deed_skip"):
            skip_to_end()

# 第三頁 - 美好事物
elif st.session_state.page == 3:
    st.header("我今天經歷的美好事物/幸福時刻")
    st.caption("請隨意書寫，沒有也沒關係")
    
    # 顯示預設選項
    st.write("你可以選擇以下預設選項或自行輸入:")
    cols = st.columns(3)
    for i, option in enumerate(happy_moment_options):
        with cols[i]:
            if st.button(option, key=f"happy_moment_{i}"):
                select_preset("happy_moment", option)
    
    # 文本輸入
    st.session_state.happy_moment = st.text_area("或者在這裡書寫", value=st.session_state.happy_moment, height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("接下一題", key="happy_moment_next"):
            go_to_page(4)
    with col2:
        if st.button("我不想寫，直接睡覺", key="happy_moment_skip"):
            skip_to_end()

# 第四頁 - 明天的事情
elif st.session_state.page == 4:
    st.header("整理寫下明天將要做的事情")
    st.caption("讓它們從腦袋卸下")
    
    # 顯示預設選項
    st.write("你可以選擇以下預設選項或自行輸入:")
    cols = st.columns(3)
    for i, option in enumerate(tomorrow_tasks_options):
        with cols[i]:
            if st.button(option, key=f"tomorrow_tasks_{i}"):
                select_preset("tomorrow_tasks", option)
    
    # 文本輸入
    st.session_state.tomorrow_tasks = st.text_area("或者在這裡書寫", value=st.session_state.tomorrow_tasks, height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("接下一題", key="tomorrow_tasks_next"):
            go_to_page(5)
    with col2:
        if st.button("我不想寫，直接睡覺", key="tomorrow_tasks_skip"):
            skip_to_end()

# 第五頁 - 心情與圖片選擇
elif st.session_state.page == 5:
    st.header("您今天的心情如何?")
    st.subheader("以下哪張圖片最適合您目前睡前的感受")
    
    # 心情選項
    st.write("選擇您的心情:")
    mood_cols = st.columns(5)
    for i, option in enumerate(mood_options):
        with mood_cols[i]:
            if st.button(option, key=f"mood_{i}"):
                select_preset("mood", option)
    
    # 文本輸入
    st.session_state.mood = st.text_input("或者描述您的心情:", value=st.session_state.mood)
    
    # 圖片選擇
    st.write("選擇一張最符合您感受的圖片:")
    
    # 顯示圖片選項 (這裡使用占位圖片，實際應用中需替換為真實圖片)
    img_cols = st.columns(3)
    
    # 使用placeholder API生成不同風格的圖片
    for i in range(3):
        with img_cols[i]:
            # 使用不同的顏色來模擬不同的圖片
            colors = ["blue", "purple", "green"]
            style_names = ["平靜的湖面", "星空下的森林", "溫暖的日落"]
            
            # 建立圖片區塊
            st.markdown(f"""
            <div class="image-option {st.session_state.selected_image == i+1 and 'selected' or ''}" 
                onclick="document.querySelector('#select_img_{i+1}').click()">
                <img src="/api/placeholder/300/200" alt="{style_names[i]}" width="100%">
                <p style="text-align:center">{style_names[i]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 隱藏按鈕，用於JavaScript觸發
            if st.button("選擇", key=f"select_img_{i+1}", help=f"選擇 {style_names[i]}", 
                         style="display:none;"):
                select_image(i+1)
    
    st.markdown("### 謝謝您對自己今天的回饋，接下來讓我來幫忙您規劃，祝您有個好夢。")
    
    if st.button("送出", key="submit_all"):
        # 準備所有使用者數據
        user_data = {
            "good_deed": st.session_state.good_deed,
            "happy_moment": st.session_state.happy_moment,
            "tomorrow_tasks": st.session_state.tomorrow_tasks,
            "mood": st.session_state.mood,
            "selected_image": st.session_state.selected_image
        }
        
        # 這裡會真正發送到後端API，但現在我們模擬處理
        st.session_state.user_data = user_data
        go_to_page(6)

# 第六頁 - 等待和結果頁面
elif st.session_state.page == 6:
    # 如果還沒有音樂推薦，顯示等待畫面
    if not st.session_state.get("music_link"):
        st.markdown("## 正在為您規劃今天的夢境旅程...")
        
        # 顯示加載動畫
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03)  # 模擬處理時間
            progress_bar.progress(i + 1)
        
        # 獲取推薦音樂
        user_data = st.session_state.get("user_data", {})
        recommended_music = get_music_recommendation(user_data)
        st.session_state.music_link = recommended_music
        
        # 重新加載頁面來顯示結果
        st.experimental_rerun()
    
    # 顯示結果和音樂播放器
    else:
        st.header("您的睡前音樂已準備好")
        
        with st.container():
            st.markdown(f"""
            <div class="result-container">
                <h3>今天為您播放的音樂是:</h3>
                <h2>{st.session_state.music_link}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # 模擬音頻播放器 (實際應用需要整合真實的音頻播放功能)
        st.markdown("### 音樂播放器")
        st.audio("/api/placeholder/audio", format="audio/mp3")
        
        # 重置按鈕
        if st.button("開始新的日記", key="restart"):
            for key in ['page', 'good_deed', 'happy_moment', 'tomorrow_tasks', 
                        'mood', 'selected_image', 'music_link', 'user_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

# 頁尾
st.markdown("""
<div class="footer">
    睡前日記 © 2025
</div>
""", unsafe_allow_html=True)

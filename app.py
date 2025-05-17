import streamlit as st
import requests
import json
import re
import time
import base64
import threading

# 設置頁面配置
st.set_page_config(
    page_title="睡眠助理小幫手",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定義CSS來改善行動裝置上的顯示效果
st.markdown("""
<style>
    body {
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .stTextArea textarea {
        font-size: 1rem;
    }
    .stButton button {
        width: 100%;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        margin-top: 0.5rem;
        background-color: #0abab5 !important;
    }
    .result-area {
        white-space: pre-wrap;
        border: 1px solid #bfe8e5;
        border-radius: 5px;
        padding: 10px;
        background-color: #f0f8f7;
        min-height: 100px;
    }
    audio {
        width: 100%;
    }
    
    /* 為Tiffany綠主題添加更多樣式 */
    .stProgress > div > div {
        background-color: #0abab5 !important;
    }
    h1, h2, h3 {
        color: #0abab5 !important;
    }
    .stAlert {
        background-color: #e6f7f6 !important;
        border-left-color: #0abab5 !important;
    }
    
    /* 行動裝置適應性設計 */
    @media (max-width: 768px) {
        .stTextArea textarea {
            font-size: 0.9rem;
        }
        h1, h2, h3 {
            font-size: 1.5rem !important;
        }
        iframe {
            height: 80px !important;
        }
    }
    
    /* 自定義按鈕樣式，特別針對行動設備 */
    .custom-button {
        display: inline-block;
        background-color: #0abab5;
        color: white !important;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 4px;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
        font-weight: bold;
        margin: 5px 0;
    }
    .download-button {
        background-color: #2c3e50;
    }
    
    /* 預設選項按鈕樣式 */
    .preset-option {
        background-color: #f0f8f7;
        border: 1px solid #0abab5;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .preset-option:hover {
        background-color: #e6f7f6;
        transform: translateY(-2px);
    }
    .preset-option h4 {
        margin: 0;
        color: #0abab5;
    }
    .preset-option p {
        margin: 5px 0 0 0;
        font-size: 0.9rem;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# 標題
st.title("睡眠助理小幫手")

# 定義預設選項
preset_options = {
    "失眠困擾": "我最近都睡不著，躺在床上輾轉反側至少一小時才能入睡，即使睡著了也容易醒來，感覺睡眠品質很差，白天精神不濟，注意力難以集中。",
    "壓力與焦慮": "工作壓力太大，晚上腦袋一直在想事情，無法放鬆，經常夢到工作相關的事情，醒來後感到疲憊，情緒也很容易緊張和焦慮。",
    "淺眠多夢": "睡覺時容易做很多夢，睡眠很淺，一點聲音就會醒來，感覺沒有真正休息好，早上起床時還是很累，這種情況已經持續好幾個月了。",
    "規律作息被打亂": "最近因為加班和生活節奏改變，作息完全不規律，有時候凌晨才睡，有時候下午才起床，感覺生理時鐘被打亂了，想恢復正常但很困難。",
    "疲勞但睡不著": "身體很疲勞，但躺下後反而精神變好，無法入睡。即使勉強睡著，睡眠時間也不足，白天感到疲憊不堪，影響了工作和生活質量。"
}

# 用戶輸入區
st.header("請輸入你的睡眠狀況：")

# 預設選項區塊
st.subheader("或選擇以下常見睡眠問題：")
selected_preset = None

# 建立兩列排版
col1, col2 = st.columns(2)

# 前三個選項在第一列
with col1:
    for i, (title, content) in enumerate(list(preset_options.items())[:3]):
        if st.button(f"{title}", key=f"preset_{i}"):
            selected_preset = content

# 後兩個選項在第二列
with col2:
    for i, (title, content) in enumerate(list(preset_options.items())[3:]):
        if st.button(f"{title}", key=f"preset_{i+3}"):
            selected_preset = content

# 文字輸入區域
user_input = st.text_area(
    label="",
    value=selected_preset if selected_preset else "",
    placeholder="例如：我最近都睡不到 5 小時...",
    height=150
)

# 提交按鈕和處理邏輯
if st.button("送出分析"):
    if not user_input.strip():
        st.error("⚠️ 請先輸入一些內容再送出！")
    else:
        # 創建一個占位符來顯示進度
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # 顯示分析中的倒數計時器
        counter = 100
        progress_bar = st.progress(0)
        
        # 發送API請求的函數
        def send_request():
            try:
                response = requests.post(
                    "https://sleep.zeabur.app/webhook/c8f29e8a-3796-43f8-940a-23b061039ff2",
                    headers={"Content-Type": "application/json"},
                    json={"user_input": user_input},
                    timeout=95
                )
                
                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        try:
                            return json.loads(response.text)
                        except:
                            return {"result": f"⚠️ 無法解析回應內容：\n\n{response.text}"}
                else:
                    return {"result": f"❌ 伺服器回應錯誤：HTTP代碼 {response.status_code}"}
            except Exception as e:
                return {"result": f"❌ 發送請求失敗，請確認網路或伺服器狀態\n{str(e)}"}
        
        # 在背景執行請求
        result = {"data": None}
        
        def background_request():
            result["data"] = send_request()
        
        thread = threading.Thread(target=background_request)
        thread.start()
        
        # 更新倒數計時器，真正的倒數
        for i in range(counter):
            if not thread.is_alive() and result["data"] is not None:
                # 請求完成，可以退出循環
                progress_placeholder.markdown(f"🧠 分析完成！")
                progress_bar.progress(1.0)
                break
                
            # 更新倒數計時器和進度條
            seconds_left = counter - i
            progress_placeholder.markdown(f"🧠 睡眠助理正在分析中，請稍候...（{seconds_left} 秒）")
            status_placeholder.info(f"正在進行第 {i+1} 步分析...")
            progress_bar.progress((i + 1) / counter)
            
            # 暫停一秒
            time.sleep(1)
        
        # 確保線程完成
        thread.join()
        
        # 清除進度顯示
        progress_placeholder.empty()
        status_placeholder.empty()
        progress_bar.empty()
        
        # 顯示結果
        st.header("分析結果：")
        
        # 檢查是否有結果
        data = result["data"] if result["data"] is not None else {"result": "❌ 無法獲取分析結果，請稍後重試"}
        
        
        # 檢查是否有結果
        if "result" in data:
            st.markdown(f"<div class='result-area'>{data['result']}</div>", unsafe_allow_html=True)
            
            # 嘗試抓出 Google Drive 連結
            result_text = data["result"]
            match = re.search(r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/', result_text)
            
            if match and match.group(1):
                file_id = match.group(1)
                
                st.header("🎧 助眠音樂：")
                
                # 為移動設備提供更好的播放體驗
                # 使用iframe嵌入Google Drive預覽，這對移動設備更友好
                embed_src = f"https://drive.google.com/file/d/{file_id}/preview"
                
                st.markdown(f"""
                <div style="width:100%; margin:10px 0;">
                    <iframe src="{embed_src}" width="100%" height="115" frameborder="0" 
                    allow="autoplay; encrypted-media" allowfullscreen style="border-radius:8px;"></iframe>
                </div>
                """, unsafe_allow_html=True)
                
                # 提供多種訪問方式，確保各類設備都能訪問
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <a href="https://drive.google.com/file/d/{file_id}/view" target="_blank" 
                    style="display:inline-block; background-color:#0abab5; color:white; 
                    padding:8px 16px; text-decoration:none; border-radius:4px; 
                    text-align:center; width:100%; box-sizing:border-box;">
                    📱 在Google Drive開啟</a>
                    """, unsafe_allow_html=True)
                
                with col2:
                    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
                    st.markdown(f"""
                    <a href="{direct_link}" target="_blank" 
                    style="display:inline-block; background-color:#2c3e50; color:white; 
                    padding:8px 16px; text-decoration:none; border-radius:4px; 
                    text-align:center; width:100%; box-sizing:border-box;">
                    💾 直接下載音樂</a>
                    """, unsafe_allow_html=True)
                
                # 給用戶一些提示
                st.info("💡 小提示：如果播放器無法正常運作，請嘗試「在Google Drive開啟」或「直接下載音樂」選項。")
                
                    
        else:
            st.error("未收到有效的分析結果。")
else:
    # 首次加載頁面時顯示的預設訊息
    st.header("分析結果：")
    st.markdown("<div class='result-area'>尚未送出分析</div>", unsafe_allow_html=True)

# 頁尾資訊
st.markdown("---")
st.markdown("© 2025 睡眠助理小幫手 | 使用 Streamlit 開發")

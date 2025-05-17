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
</style>
""", unsafe_allow_html=True)

# 標題
st.title("睡眠助理小幫手")

# 用戶輸入區
st.header("請輸入你的睡眠狀況：")
user_input = st.text_area(
    label="",
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
        import threading
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

import streamlit as st
import requests
import json
import re
import time
import base64

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
                # 使用多種可能的音訊源格式
                direct_src = f"https://drive.google.com/uc?export=download&id={file_id}"
                embed_src = f"https://drive.google.com/file/d/{file_id}/preview"
                
                st.header("🎧 點擊下方播放助眠音樂：")
                
                # 使用Streamlit內置音訊播放器
                try:
                    audio_file = requests.get(direct_src, timeout=10)
                    if audio_file.status_code == 200:
                        st.audio(audio_file.content, format="audio/mp3")
                    else:
                        # 如果直接下載失敗，使用嵌入播放器
                        st.markdown(f"""
                        <iframe src="{embed_src}" width="100%" height="100" frameborder="0" allow="autoplay"></iframe>
                        <p>如果上方播放器無法使用，請<a href="https://drive.google.com/file/d/{file_id}/view" target="_blank">點擊此處</a>在新分頁中開啟音樂。</p>
                        """, unsafe_allow_html=True)
                except:
                    # 作為備用，提供直接連結
                    st.markdown(f"""
                    <p>音樂檔案載入失敗，請<a href="https://drive.google.com/file/d/{file_id}/view" target="_blank">點擊此處</a>在新分頁中開啟播放。</p>
                    """, unsafe_allow_html=True)
                
                # 增加下載按鈕
                try:
                    st.download_button(
                        label="下載助眠音樂檔案",
                        data=requests.get(direct_src, timeout=10).content,
                        file_name="睡眠助理音樂.mp3",
                        mime="audio/mpeg"
                    )
                except:
                    st.warning("下載功能暫時無法使用，請使用Google Drive連結下載")
                    st.markdown(f'[點擊此處下載音樂](https://drive.google.com/file/d/{file_id}/view?usp=sharing)')
                    
        else:
            st.error("未收到有效的分析結果。")
else:
    # 首次加載頁面時顯示的預設訊息
    st.header("分析結果：")
    st.markdown("<div class='result-area'>尚未送出分析</div>", unsafe_allow_html=True)

# 頁尾資訊
st.markdown("---")
st.markdown("© 2025 睡眠助理小幫手 | 使用 Streamlit 開發")

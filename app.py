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
    }
    .result-area {
        white-space: pre-wrap;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        background-color: #f9f9f9;
        min-height: 100px;
    }
    audio {
        width: 100%;
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
        
        # 顯示分析中的倒數計時器
        counter = 100
        progress_bar = st.progress(0)
        
        for i in range(counter):
            # 更新倒數計時器
            progress_placeholder.markdown(f"🧠 睡眠助理正在分析中，請稍候...（{counter - i} 秒）")
            progress_bar.progress((i + 1) / counter)
            
            # 發送請求，只在第一次迭代時執行
            if i == 0:
                try:
                    response_future = requests.post(
                        "https://sleep.zeabur.app/webhook/c8f29e8a-3796-43f8-940a-23b061039ff2",
                        headers={"Content-Type": "application/json"},
                        json={"user_input": user_input},
                        timeout=95  # 設置超時時間稍短於倒計時
                    )
                    
                    # 檢查響應是否成功
                    if response_future.status_code == 200:
                        try:
                            data = response_future.json()
                            # 成功獲取數據，停止倒計時
                            break
                        except json.JSONDecodeError:
                            # 如果不是有效的JSON，嘗試解析文本
                            text_response = response_future.text
                            try:
                                data = json.loads(text_response)
                                # 成功解析，停止倒計時
                                break
                            except:
                                # 無法解析為JSON，保存原始文本
                                data = {"result": f"⚠️ 無法解析回應內容：\n\n{text_response}"}
                                # 停止倒計時
                                break
                    else:
                        data = {"result": f"❌ 伺服器回應錯誤：HTTP代碼 {response_future.status_code}"}
                        # 停止倒計時
                        break
                        
                except Exception as e:
                    data = {"result": f"❌ 發送請求失敗，請確認網路或伺服器狀態\n{str(e)}"}
                    # 發生錯誤，停止倒計時
                    break
            
            # 模擬處理時間，每次迭代暫停約1秒
            time.sleep(1)
        
        # 清除進度顯示
        progress_placeholder.empty()
        progress_bar.empty()
        
        # 顯示結果
        st.header("分析結果：")
        
        # 檢查是否有結果
        if "result" in data:
            st.markdown(f"<div class='result-area'>{data['result']}</div>", unsafe_allow_html=True)
            
            # 嘗試抓出 Google Drive 連結
            result_text = data["result"]
            match = re.search(r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/', result_text)
            
            if match and match.group(1):
                file_id = match.group(1)
                audio_src = f"https://drive.google.com/uc?export=download&id={file_id}"
                
                st.header("🎧 點擊下方播放助眠音樂：")
                
                # 使用HTML音訊播放器
                st.markdown(f"""
                <audio controls autoplay>
                    <source src="{audio_src}" type="audio/mpeg">
                    您的瀏覽器不支援播放音樂。
                </audio>
                """, unsafe_allow_html=True)
                
                # 增加下載按鈕
                st.download_button(
                    label="下載助眠音樂檔案",
                    data=requests.get(audio_src).content,
                    file_name="睡眠助理音樂.mp3",
                    mime="audio/mpeg"
                )
        else:
            st.error("未收到有效的分析結果。")
else:
    # 首次加載頁面時顯示的預設訊息
    st.header("分析結果：")
    st.markdown("<div class='result-area'>尚未送出分析</div>", unsafe_allow_html=True)

# 頁尾資訊
st.markdown("---")
st.markdown("© 2025 睡眠助理小幫手 | 使用 Streamlit 開發")

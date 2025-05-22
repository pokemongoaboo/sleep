import streamlit as st
import requests
import json
import re
import time
import base64
import threading

# Set page configuration
st.set_page_config(
    page_title="Sleep Assistant Helper",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to improve display on mobile devices
st.markdown("""
<style>
    body {
        font-family: "Arial", sans-serif;
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
    
    /* Add more styles for Tiffany green theme */
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
    
    /* Mobile responsive design */
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
    
    /* Custom button styles, especially for mobile devices */
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
    
    /* Preset option button styles */
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

# Title
st.title("Sleep Assistant Helper")

# Define preset options
preset_options = {
    "Insomnia & Irritability": "I've been having trouble sleeping lately. I toss and turn in bed for at least an hour before falling asleep, and even when I do sleep, I wake up easily. My sleep quality feels poor, I'm sluggish during the day, and it's hard to concentrate. Emotionally, I feel very irritable and get angry over small things.",
    "Stress & Anxiety": "Work stress is overwhelming. At night, my mind keeps racing with thoughts and I can't relax. I often dream about work-related things and wake up feeling exhausted. I get nervous and anxious easily. Sometimes my heart rate suddenly increases and I feel short of breath. I really need something slow and soothing.",
    "Light Sleep & Dreams with Sadness": "I have a highly sensitive personality and prefer quiet environments without any instruments. I sleep very lightly and have many dreams. I wake up at the slightest sound and never feel truly rested. I'm still tired when I wake up in the morning. This has been going on for several months now, and I'm starting to feel emotionally down and lost, losing interest in things I usually enjoy.",
    "Irregular Schedule & Mood Swings": "Recently, due to overtime and changes in my daily routine, my schedule has become completely irregular. Sometimes I sleep at 3 AM, sometimes I don't wake up until afternoon. I feel like my biological clock is completely disrupted. My emotions fluctuate greatly - sometimes happy, sometimes sad - and it's hard to control my feelings.",
    "Fatigue & Need for Peace": "My body is very tired, but when I lie down, I become mentally alert and can't fall asleep. Even when I force myself to sleep, I don't get enough sleep time and feel exhausted during the day. I desperately long to find inner peace and hope for a good night's sleep."
}

# User input section
st.header("Please describe your sleep situation:")

# Preset options section
st.subheader("Or choose from these common sleep issues:")

# Store selected preset value
if 'selected_preset' not in st.session_state:
    st.session_state.selected_preset = None

# Create two-column layout
col1, col2 = st.columns(2)

# First three options in first column
with col1:
    for i, (title, content) in enumerate(list(preset_options.items())[:3]):
        if st.button(f"{title}", key=f"preset_{i}"):
            st.session_state.selected_preset = content

# Last two options in second column
with col2:
    for i, (title, content) in enumerate(list(preset_options.items())[3:]):
        if st.button(f"{title}", key=f"preset_{i+3}"):
            st.session_state.selected_preset = content

# Text input area - use session_state to maintain value
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# If preset option is selected, update input box
if st.session_state.selected_preset:
    st.session_state.user_input = st.session_state.selected_preset
    # Clear after use to avoid repeated setting
    st.session_state.selected_preset = None

user_input = st.text_area(
    label="",
    value=st.session_state.user_input,
    placeholder="For example: I've only been sleeping 5 hours lately...",
    height=150,
    key="text_input"
)

# Submit button and processing logic
if st.button("Submit Analysis"):
    # Save current input to session_state
    st.session_state.user_input = user_input
    
    if not user_input.strip():
        st.error("⚠️ Please enter some content before submitting!")
    else:
        # Create placeholders for progress display
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # Display countdown timer during analysis
        counter = 100
        progress_bar = st.progress(0)
        
        # Function to send API request
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
                            return {"result": f"⚠️ Unable to parse response content:\n\n{response.text}"}
                else:
                    return {"result": f"❌ Server response error: HTTP code {response.status_code}"}
            except Exception as e:
                return {"result": f"❌ Failed to send request. Please check network or server status\n{str(e)}"}
        
        # Execute request in background
        result = {"data": None}
        
        def background_request():
            result["data"] = send_request()
        
        thread = threading.Thread(target=background_request)
        thread.start()
        
        # Update countdown timer with actual countdown
        for i in range(counter):
            if not thread.is_alive() and result["data"] is not None:
                # Request completed, can exit loop
                progress_placeholder.markdown(f"🧠 Analysis complete!")
                progress_bar.progress(1.0)
                break
                
            # Update countdown timer and progress bar
            seconds_left = counter - i
            progress_placeholder.markdown(f"🧠 Sleep assistant is analyzing, please wait...({seconds_left} seconds)")
            status_placeholder.info(f"Performing analysis step {i+1}...")
            progress_bar.progress((i + 1) / counter)
            
            # Pause for one second
            time.sleep(1)
        
        # Ensure thread completion
        thread.join()
        
        # Clear progress display
        progress_placeholder.empty()
        status_placeholder.empty()
        progress_bar.empty()
        
        # Display results
        st.header("Analysis Results:")
        
        # Check if there are results
        data = result["data"] if result["data"] is not None else {"result": "❌ Unable to get analysis results, please try again later"}
        
        
        # Check if there are results
        if "result" in data:
            st.markdown(f"<div class='result-area'>{data['result']}</div>", unsafe_allow_html=True)
            
            # Try to extract Google Drive link
            result_text = data["result"]
            match = re.search(r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/', result_text)
            
            if match and match.group(1):
                file_id = match.group(1)
                
                st.header("🎧 Sleep Music:")
                
                # Provide different playback options for desktop and mobile devices
                # 1. Use HTML5 Audio element (friendly for desktop and some mobile devices)
                audio_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                st.audio(audio_url, format="audio/mp3")
                
                # 2. Use iframe to embed Google Drive preview (more mobile-friendly)
                embed_src = f"https://drive.google.com/file/d/{file_id}/preview"
                
                st.markdown(f"""
                <div style="width:100%; margin:10px 0;">
                    <iframe src="{embed_src}" width="100%" height="115" frameborder="0" 
                    allow="autoplay; encrypted-media" allowfullscreen style="border-radius:8px;"></iframe>
                </div>
                """, unsafe_allow_html=True)
                
                # Provide multiple access methods to ensure all devices can access
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <a href="https://drive.google.com/file/d/{file_id}/view" target="_blank" 
                    style="display:inline-block; background-color:#0abab5; color:white; 
                    padding:8px 16px; text-decoration:none; border-radius:4px; 
                    text-align:center; width:100%; box-sizing:border-box;">
                    📱 Open in Google Drive</a>
                    """, unsafe_allow_html=True)
                
                with col2:
                    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
                    st.markdown(f"""
                    <a href="{direct_link}" target="_blank" 
                    style="display:inline-block; background-color:#2c3e50; color:white; 
                    padding:8px 16px; text-decoration:none; border-radius:4px; 
                    text-align:center; width:100%; box-sizing:border-box;">
                    💾 Download Music Directly</a>
                    """, unsafe_allow_html=True)
                
                # Give users some tips
                st.info("💡 Tip: If the player doesn't work properly, please try 'Open in Google Drive' or 'Download Music Directly' options.")
                
                    
        else:
            st.error("No valid analysis results received.")
else:
    # Default message displayed when page first loads
    st.header("Analysis Results:")
    st.markdown("<div class='result-area'>No analysis submitted yet</div>", unsafe_allow_html=True)

# Footer information
st.markdown("---")
st.markdown("© 2025 Sleep Assistant Helper | Developed with Streamlit")

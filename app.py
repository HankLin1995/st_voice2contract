import os
import tempfile
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import time
import json
import pandas as pd

# Load environment variables
load_dotenv()

CONTRACT_ITEMS = [
          {
            "item": "土方開挖",
            "unit": "立方公尺",
            "unit_price": 300,
            "quantity": 100,
            "total_price": 30000
          },
          {
            "item": "混凝土澆置",
            "unit": "立方公尺",
            "unit_price": 2500,
            "quantity": 50,
            "total_price": 125000
          },
          {
            "item": "鋼筋綁紮",
            "unit": "公斤",
            "unit_price": 25,
            "quantity": 4000,
            "total_price": 100000
          },
          {
            "item": "模板施工",
            "unit": "平方公尺",
            "unit_price": 450,
            "quantity": 200,
            "total_price": 90000
          },
          {
            "item": "排水管安裝",
            "unit": "公尺",
            "unit_price": 150,
            "quantity": 300,
            "total_price": 45000
          },
          {
            "item": "人行道鋪設",
            "unit": "平方公尺",
            "unit_price": 600,
            "quantity": 120,
            "total_price": 72000
          },
          {
            "item": "瀝青混凝土鋪築",
            "unit": "公噸",
            "unit_price": 3500,
            "quantity": 20,
            "total_price": 70000
          },
          {
            "item": "擋土牆砌築",
            "unit": "立方公尺",
            "unit_price": 1800,
            "quantity": 30,
            "total_price": 54000
          },
          {
            "item": "電纜管路埋設",
            "unit": "公尺",
            "unit_price": 200,
            "quantity": 250,
            "total_price": 50000
          },
          {
            "item": "施工圍籬設置",
            "unit": "公尺",
            "unit_price": 100,
            "quantity": 100,
            "total_price": 10000
          }
        ]
MY_COLUMN_CONFIG={
    "item": "項目名稱",
    "unit": "單位",
    "quantity": "數量",
    "unit_price": "單價",
    "total_price": "總價"
    }

# Set page configuration
st.set_page_config(
    page_title="契約項目數量錄音填寫",
    page_icon="🎤",
    layout="wide"
)

with st.sidebar:
    groq_api_key=st.text_input("Groq API Key", type="password")
    st.markdown("[GroqAPI金鑰取得教學](https://www.hanksvba.com/posts/3510612144/)")

if groq_api_key:
    client = Groq(api_key=groq_api_key)
else:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    except Exception as e:
        st.error("請輸入 Groq API Key!")
        st.stop()

def get_transcription(audio_file):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        transcription = transcribe_audio(tmp_file_path)
        return transcription
    except Exception as e:
        return None
    finally:
        os.unlink(tmp_file_path)

def transcribe_audio(audio_file):
    """Transcribe audio using Groq API"""
    try:
        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3",
                response_format="text",
                language="zh"
            )
        return transcription
    except Exception as e:
        st.error(f"Error during transcription: {str(e)}")
        return None


def process_civil_engineering_prompt(report_text):
    """Process civil engineering report using Groq API"""
    try:
        # Civil engineering contract items
        # Create the prompt for the civil engineering assistant
        prompt = f"""你是土木工程助理，任務是根據「師傅的文字回報」比對「契約項目」及數量，並回傳標準 JSON 格式的對應資料。

        規則如下：
        1. 僅選擇最符合的項目（比對工程名稱、單位、語意）
        2. 請自動計算 total_price = unit_price × quantity
        3. 比對名稱後發現沒有的項目就拒絕回答

        ---

        契約項目如下：

        {CONTRACT_ITEMS}

        師傅的文字回報：
        {report_text}
        """
        
        # Using Groq's LLM for processing
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "你是一個專業的土木工程助理，只輸出純JSON格式的回應，不包含任何額外的文字說明。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gemma2-9b-it",
            temperature=0.1,
            max_tokens=1024
        )
        
        # Get the response content
        response_content = chat_completion.choices[0].message.content
        return response_content
    except Exception as e:
        st.error(f"Error processing civil engineering prompt: {str(e)}")
        return None

# Check for API key
# if not os.getenv("GROQ_API_KEY"):
#     st.warning("⚠️ Groq API key not found. Please add your API key to the .env file.")
#     st.stop()

st.title("🤖 契約項目數量填寫")
st.markdown("---")

transcription = None
report_text = None

col1,col2=st.columns(2, gap="large")

with col1:
    # Audio input widget
    st.subheader("🎤 施工描述")
    audio_data = st.audio_input("點擊錄音", key="audio_recorder")

    if audio_data is not None:
        with st.spinner("處理中..."):
            # transcription = get_transcription(audio_data)
            # 儲存 audio_data 為臨時 WAV 檔案
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                transcription = transcribe_audio(tmp_file_path)
                # st.success("語音辨識完成")
                st.caption(transcription)
            except Exception as e:
                st.error(f"語音辨識失敗：{str(e)}")
            finally:
                os.unlink(tmp_file_path)

    if transcription:
        with st.spinner("Processing report with Groq API..."):
            max_retries = 3
            retry_delay = 1  # seconds
            success = False

            for attempt in range(max_retries):
                result = process_civil_engineering_prompt(transcription)

                if isinstance(result, str):
                    try:
                        json_data = json.loads(result)
                        success = True
                        break  # Exit retry loop if success
                    except json.JSONDecodeError:
                        st.warning(f"Attempt {attempt+1}: JSON decoding failed. Retrying...")
                        time.sleep(retry_delay)
                else:
                    break  # If result is not string, no point retrying

            if success and isinstance(json_data, list):
                st.markdown("### :star: 本日數量")
                df = pd.DataFrame(json_data)
                st.data_editor(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=MY_COLUMN_CONFIG
                )
                # st.toast("匯入日報!",icon="✅")
            else:
                st.error("Failed to parse valid JSON after multiple attempts.")
                st.write("Raw response:")
                st.write(result)

    else:
        st.toast("請先講話才能填寫報表!",icon="⚠️")
        
# Example reports
with col2:

    st.subheader(":book: 契約項目")
    st.dataframe(CONTRACT_ITEMS,
    use_container_width=True,
    hide_index=True,
    column_config=MY_COLUMN_CONFIG)

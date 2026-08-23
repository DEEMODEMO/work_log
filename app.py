from datetime import datetime
import json
import os
import time
from google import genai
import streamlit as st

# Веб хуудасны тохиргоо
st.set_page_config(
    page_title="Ажлын Тэмдэглэл", page_icon="📝", layout="centered"
)

# Загварлаг CSS (Таб товчлууруудыг утсан дээр ч заавал хэвтээ байлгах CSS-тэй)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(121, 40, 202, 0.6) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(255, 0, 128, 0.5) 0%, transparent 40%),
                    radial-gradient(circle at 50% 50%, rgba(14, 125, 248, 0.5) 0%, transparent 50%),
                    linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
        color: #f8fafc;
    }
    
    /* 3 товчлуурыг утсан дээр ч ялгаагүй заавал хэвтээ байрлуулах зохицуулалт */
    [data-testid="column"] {
        width: calc(33.333% - 1rem) !important;
        flex: 1 1 calc(33.333% - 1rem) !important;
        min-width: 90px !important;
    }
    
    div[data-testid="horizontal--block"], div.row-widget.stHorizontal {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
    }

    /* Товчны ерөнхий загвар */
    .stButton>button, div.stFormSubmitButton>button {
        color: #fff !important;
        font-size: 13px !important;
        font-weight: bold !important;
        box-shadow: 4px 4px 0px -1px #0adabe, 4px 4px 0px 1px #000 !important;
        padding: 8px 4px !important;
        border-radius: 10px !important;
        border: 2px solid #000 !important;
        background: radial-gradient(circle at top right, #2ff5ca, #0e7df8) !important;
        cursor: pointer !important;
        transition: 0.3s ease !important;
        width: 100% !important;
        white-space: nowrap !important;
    }
    
    .stButton>button:hover, div.stFormSubmitButton>button:hover {
        transform: translate(-.1em, -.1em) !important;
        box-shadow: 7px 7px 0px -1px #0e7df8, 7px 7px 0px 1px #000 !important;
    }

    /* Устгах товчны тусгай харагдах байдал (Хар дэвсгэртэй, улаан/неон хүрээтэй) */
    button[kind="secondary"] p {
        color: #fff !important;
    }

    /* Бодит цаг харуулах картын загвар */
    .live-clock-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 12px 15px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Тэмдэглэлийн карт */
    .log-card-box {
        position: relative;
        background: rgba(15, 23, 42, 0.85);
        border: 2px solid #0adabe;
        padding: 14px 16px;
        border-radius: 14px;
        margin-bottom: 8px;
        box-shadow: 4px 4px 0px #0adabe;
    }

    .summary-box {
        padding: 22px;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.9);
        border: 2px solid #ff0080;
        color: #f8fafc;
        margin-top: 10px;
        box-shadow: 6px 6px 0px #ff0080;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #f8fafc !important;
        border: 2px solid #0adabe !important;
        border-radius: 12px !important;
    }

    .neon-loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
    }
    .neon-ring {
        width: 60px;
        height: 60px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top: 3px solid #2ff5ca;
        border-radius: 50%;
        animation: neonSpin 0.9s linear infinite;
        box-shadow: 0 0 15px rgba(47, 245, 202, 0.5);
    }
    @keyframes neonSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
""",
    unsafe_allow_html=True,
)

API_KEY = "AQ.Ab8RN6LGfAzbE7ye-0PCAVc4uby4dZdGP7bjvayWkSLEyWtDHg"
client = genai.Client(api_key=API_KEY)

DATA_FILE = "work_logs.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for date_key in data:
                    for idx, item in enumerate(data[date_key].get("logs", [])):
                        if "id" not in item:
                            item["id"] = f"log_{idx}_{int(time.time())}"
                return data
        except:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if "data" not in st.session_state:
    st.session_state.data = load_data()

now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
current_time_py = now.strftime("%Y оны %m сарын %d · %H:%M:%S")

st.markdown(
    f"""
    <div class="live-clock-card">
        <span style="font-size: 12px; color: #2ff5ca; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🟢 Одоогийн цаг</span>
        <div style="font-size: 17px; font-weight: 800; color: #ffffff; margin-top: 4px;">{current_time_py}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h2 style='text-align: center; color: #2ff5ca; font-weight: 800;'>Ажлын Тэмдэглэл & Тайлан</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #cbd5e1; font-size: 14px;'>Өдрийн ажлаа бүртгээд тайлангаа хялбархан нэгтгээрэй.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Бүртгэх"

# 3 товчлуурыг хэвтээ байдлаар зэрэгцүүлэх
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("📝 Бүртгэх", use_container_width=True):
        st.session_state.nav_page = "Бүртгэх"
with col_n2:
    if st.button("📊 Нэгтгэл", use_container_width=True):
        st.session_state.nav_page = "Нэгтгэл"
with col_n3:
    if st.button("📚 Архив", use_container_width=True):
        st.session_state.nav_page = "Архив"

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.nav_page == "Бүртгэх":
    st.markdown("#### Шинэ ажил нэмэх")
    with st.form("log_form", clear_on_submit=True):
        task_input = st.text_area(
            "Ямар ажил амжуулсан бэ?",
            placeholder="Жишээ нь: Тайлан шалгаж дуусгалаа...",
            height=100,
        )
        submitted = st.form_submit_button("Бүртгэх")
        if submitted and task_input:
            time_str = datetime.now().strftime("%H:%M")
            if today_str not in st.session_state.data:
                st.session_state.data[today_str] = {"logs": [], "summary": ""}

            new_id = f"log_{int(time.time() * 1000)}"
            st.session_state.data[today_str]["logs"].append(
                {"id": new_id, "time": time_str, "text": task_input}
            )
            save_data(st.session_state.data)
            st.success("Амжилттай бүртгэгдлээ!")
            st.rerun()

    st.markdown(f"#### Өнөөдрийн тэмдэглэл ({today_str})")

    if today_str in st.session_state.data and st.session_state.data[today_str].get(
        "logs"
    ):
        logs_list = st.session_state.data[today_str]["logs"]

        for item in logs_list:
            item_id = item["id"]
            item_time = item["time"]
            item_text = item["text"]

            col_card, col_btn = st.columns([5, 1])
            with col_card:
                st.markdown(
                    f"""
                    <div class="log-card-box">
                        <span style="font-size: 11px; background: #2ff5ca; color: #000; padding: 2px 6px; border-radius: 4px; font-weight: 700;">🕒 {item_time}</span>
                        <p style="font-size: 14px; margin-top: 6px; font-weight: 600; color: #f8fafc; margin-bottom: 0px; word-break: break-word;">{item_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_btn:
                st.markdown("<div style='margin-top: 2px;'></div>", unsafe_allow_html=True)
                # Устгах товчийг илүү тод, анхаарал татахуйц неон улаан хүрээтэй болгов
                st.markdown(
                    """
                    <style>
                    div[data-testid="column"] button {
                        background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%) !important;
                        box-shadow: 3px 3px 0px #000 !important;
                        border: 2px solid #000 !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("🗑️", key=f"del_{item_id}", help="Устгах"):
                    st.session_state.data[today_str]["logs"] = [
                        x for x in logs_list if x["id"] != item_id
                    ]
                    save_data(st.session_state.data)
                    st.rerun()
    else:
        st.info("Өнөөдөр одоогоор бүртгэсэн ажил алга.")

elif st.session_state.nav_page == "Нэгтгэл":
    st.markdown("#### Ажлын нэгтгэл ба тайлан")


    def summarize_with_ai(logs_list):
        if not logs_list:
            return "Өнөөдөр бүртгэгдсэн ажил алга байна."
        prompt = (
            "Доорх цагийн дарааллаар хийсэн ажлуудыг тайлан гаргахад яг тохирохоор "
            "маш цэгцтэй, ойлгомжтой, товч тодорхой жагсаалт болгон Монгол хэлээр дүгнэж өгнө үү:\n\n"
        )
        for log in logs_list:
            prompt += f"[{log['time']}] {log['text']}\n"
        try:
            # Gemini 2.5 Flash загвар рүү амжилттай холбогдоно
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response.text
        except Exception as e:
            return f"АЛДАА ГАРЛАА: {str(e)}"


    if st.button("Тайлан гаргах"):
        if today_str in st.session_state.data and st.session_state.data[
            today_str
        ].get("logs"):
            placeholder_loading = st.empty()
            placeholder_loading.markdown(
                """
                <div class="neon-loader-container">
                    <div class="neon-ring"></div>
                    <div style="margin-top: 15px; color: #2ff5ca; font-weight: 700; font-size: 14px;">Тайланг боловсруулж байна...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            summary_result = summarize_with_ai(
                st.session_state.data[today_str]["logs"]
            )
            st.session_state.data[today_str]["summary"] = summary_result
            save_data(st.session_state.data)

            placeholder_loading.empty()
            st.success("Тайлан амжилттай үүслээ!")
            st.rerun()
        else:
            st.warning("Нэгтгэх ажил одоогоор бүртгэгдээгүй байна.")

    if (
        today_str in st.session_state.data
        and "summary" in st.session_state.data[today_str]
        and st.session_state.data[today_str]["summary"]
    ):
        st.markdown("#### Нэгтгэсэн үр дүн:")
        st.markdown(
            f"""
            <div class="summary-box">
                {st.session_state.data[today_str]["summary"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

elif st.session_state.nav_page == "Архив":
    st.markdown("#### Өмнөх өдрүүдийн архив")
    if st.session_state.data:
        selected_date = st.selectbox(
            "Өдрөө сонгоно уу",
            options=sorted(list(st.session_state.data.keys()), reverse=True),
        )

        if selected_date and selected_date in st.session_state.data:
            st.write(f"**{selected_date} өдрийн хураангуй:**")
            if st.session_state.data[selected_date].get("summary"):
                st.markdown(
                    f"""
                    <div class="summary-box">
                        {st.session_state.data[selected_date]["summary"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.info("Энэ өдөр тайлан үүсгээгүй байна.")

            with st.expander("Тухайн өдрийн дэлгэрэнгүй жагсаалт"):
                for item in st.session_state.data[selected_date].get(
                    "logs", []
                ):
                    st.markdown(f"- **{item['time']}**: {item['text']}")
    else:
        st.info("Архив хоосон байна.")

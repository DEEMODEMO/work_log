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

# Загварлаг фон болон 2 секунд удаан дарж (Hold) устгах эффектэд зориулсан CSS/JS
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
    
    /* Үндсэн товчны загвар */
    .stButton>button, div.stFormSubmitButton>button {
        color: #fff !important;
        font-size: 13px !important;
        font-weight: bold !important;
        box-shadow: 4px 4px 0px -1px #0adabe, 4px 4px 0px 1px #000 !important;
        padding: 8px 6px !important;
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

    .stButton>button:active, div.stFormSubmitButton>button:active {
        transform: translate(.3em, .3em) !important;
        box-shadow: 0px 0px 0px -1px #BEE2F9, 0px 0px 0px 0.1px #000 !important;
    }

    /* Бодит цаг харуулах загварлаг хэсэг */
    .live-clock-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 10px 15px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Ажлын тэмдэглэлийн үндсэн карт (Ямар ч илүү товчгүй, цэвэрхэн) */
    .log-card-box {
        position: relative;
        background: rgba(15, 23, 42, 0.85);
        border: 2px solid #0adabe;
        padding: 14px 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 4px 4px 0px #0adabe;
        cursor: pointer;
        user-select: none;
        transition: 0.2s;
    }
    .log-card-box:hover {
        border-color: #ef4444;
        box-shadow: 4px 4px 0px #ef4444;
    }

    /* Үр дүнгийн хайрцаг */
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

data = st.session_state.data
today_str = datetime.now().strftime("%Y-%m-%d")

st.markdown(
    """
    <div class="live-clock-card">
        <span style="font-size: 12px; color: #2ff5ca; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🟢 Бодит цаг хугацаа</span>
        <div id="live-clock" style="font-size: 17px; font-weight: 800; color: #ffffff; margin-top: 4px;">Уншиж байна...</div>
    </div>
    
    <script>
    function updateClock() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        const timeString = year + " оны " + month + " сарын " + day + " · " + hours + ":" + minutes + ":" + seconds;
        const clockElement = document.getElementById('live-clock');
        if (clockElement) {
            clockElement.innerText = timeString;
        }
    }
    if (window.clockInterval) clearInterval(window.clockInterval);
    window.clockInterval = setInterval(updateClock, 1000);
    updateClock();
    </script>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h2 style='text-align: center; color: #2ff5ca; font-weight: 800; text-shadow: 0 2px 10px rgba(47,245,202,0.3);'>Ажлын Тэмдэглэл & Тайлан</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #cbd5e1; font-size: 14px; font-weight: 500;'>Өдрийн ажлаа бүртгээд тайлангаа хялбархан нэгтгээрэй.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Бүртгэх"

col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("📝 Бүртгэх"):
        st.session_state.nav_page = "Бүртгэх"
with col_n2:
    if st.button("📊 Нэгтгэл"):
        st.session_state.nav_page = "Нэгтгэл"
with col_n3:
    if st.button("📚 Архив"):
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
            current_time = datetime.now().strftime("%H:%M")
            if today_str not in st.session_state.data:
                st.session_state.data[today_str] = {"logs": [], "summary": ""}

            new_id = f"log_{int(time.time() * 1000)}"
            st.session_state.data[today_str]["logs"].append(
                {"id": new_id, "time": current_time, "text": task_input}
            )
            save_data(st.session_state.data)
            st.success("Амжилттай бүртгэгдлээ!")
            st.rerun()

    st.markdown(f"#### Өнөөдрийн тэмдэглэл ({today_str})")
    st.markdown(
        "<p style='font-size: 12px; color: #2ff5ca; margin-top: -5px;'>💡 Карт дээр <b>2 секунд тасралтгүй дарж (Hold)</b> байхад шууд устгагдана.</p>",
        unsafe_allow_html=True,
    )

    if today_str in st.session_state.data and st.session_state.data[today_str].get(
        "logs"
    ):
        logs_list = st.session_state.data[today_str]["logs"]

        for item in logs_list:
            item_id = item["id"]
            item_time = item["time"]
            item_text = item["text"]

            # 2 секунд удаан дарвал устгах function-г ажиллуулах JavaScript код
            card_html = (
                '<div class="log-card-box" id="card_'
                + item_id
                + '" '
                + 'onmousedown="window.holdTimer_'
                + item_id
                + ' = setTimeout(() => { '
                + "window.location.href = window.location.pathname + '?delete_id="
                + item_id
                + "';"
                + "}, 2000);\" "
                + 'onmouseup="clearTimeout(window.holdTimer_'
                + item_id
                + ');" '
                + 'ontouchstart="window.holdTimer_'
                + item_id
                + ' = setTimeout(() => { '
                + "window.location.href = window.location.pathname + '?delete_id="
                + item_id
                + "';"
                + "}, 2000);\" "
                + 'ontouchend="clearTimeout(window.holdTimer_'
                + item_id
                + ');">'
                + '<div style="display: flex; justify-content: space-between; align-items: center;">'
                + '<span style="font-size: 11px; background: #2ff5ca; color: #000; padding: 3px 8px; border-radius: 6px; font-weight: 700;">🕒 '
                + item_time
                + "</span>"
                + '<span style="font-size: 10px; color: #ef4444; font-weight: 600;">⏳ 2 сек барьж устгах</span>'
                + "</div>"
                + '<p style="font-size: 14px; margin-top: 8px; font-weight: 600; color: #f8fafc; word-break: break-word; margin-bottom: 0px;">'
                + item_text
                + "</p>"
                + "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

        # Query parameter шалгаад автоматаар шууд устгах хэсэг
        query_params = st.query_params
        if "delete_id" in query_params:
            del_id = query_params["delete_id"]
            st.session_state.data[today_str]["logs"] = [
                x for x in logs_list if x["id"] != del_id
            ]
            save_data(st.session_state.data)
            st.query_params.clear()
            st.rerun()
    else:
        st.info("Өнөөдөр одоогоор бүртгэсэн ажил алга.")

elif st.session_state.nav_page == "Нэгтгэл":
    st.markdown("#### Ажлын нэгтгэл ба тайлан")


    def summarize_with_ai(logs_list):
        if not logs_list:
            return "Өнөөдөр бүртгэгдсэн ажил алга байна."

        prompt = (
            "Доорх цагийн дарааллаар хийсэн ажлуудыг цалин бодох, тайлан гаргахад "
            "яг тохирохоор маш цэгцтэй, ойлгомжтой, товч тодорхой жагсаалт болгон Монгол хэлээр дүгнэж өгнө үү:\n\n"
        )
        for log in logs_list:
            prompt += f"[{log['time']}] {log['text']}\n"

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite", contents=prompt
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
                    <div style="margin-top: 15px; color: #2ff5ca; font-weight: 700; font-size: 14px; letter-spacing: 0.5px;">Тайланг боловсруулж байна...</div>
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
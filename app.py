from datetime import datetime
import json
import os
import time
from zoneinfo import ZoneInfo
from google import genai
import streamlit as st

# Улаанбаатар хотын цагийн бүс
UB_TZ = ZoneInfo("Asia/Ulaanbaatar")


def get_ub_now():
    return datetime.now(UB_TZ)


# Веб хуудасны тохиргоо
st.set_page_config(
    page_title="Ажлын Тэмдэглэл", page_icon="📝", layout="centered"
)

# Загварлаг CSS (Товчны хэмжээг томруулж, текст бүтэн харагдах байдлаар зассан)
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
    
    /* Товчны загвар - Текст шахтахааргүй, том бөгөөд тод болгосон */
    .stButton>button, div.stFormSubmitButton>button {
        color: #fff !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        box-shadow: 4px 4px 0px -1px #0adabe, 4px 4px 0px 1px #000 !important;
        padding: 12px 18px !important;
        border-radius: 12px !important;
        border: 2px solid #000 !important;
        background: radial-gradient(circle at top right, #2ff5ca, #0e7df8) !important;
        cursor: pointer !important;
        transition: 0.3s ease !important;
        width: 100% !important;
        white-space: normal !important;
        text-align: left !important;
        line-height: 1.5 !important;
    }
    
    .stButton>button:hover, div.stFormSubmitButton>button:hover {
        transform: translate(-.1em, -.1em) !important;
        box-shadow: 7px 7px 0px -1px #0e7df8, 7px 7px 0px 1px #000 !important;
    }

    /* Улаанбаатар цаг */
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

initial_ub = get_ub_now()
initial_time_str = initial_ub.strftime("%Y оны %m сарын %d · %H:%M:%S")
today_str = initial_ub.strftime("%Y-%m-%d")

# Real-time цаг (Browser дээр ажиллах JS)
clock_html = f"""
    <div class="live-clock-card">
        <span style="font-size: 12px; color: #2ff5ca; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🟢 Улаанбаатарын цаг</span>
        <div id="live-clock" style="font-size: 17px; font-weight: 800; color: #ffffff; margin-top: 4px;">{initial_time_str}</div>
    </div>
    <script>
    function updateClock() {{
        const options = {{ timeZone: 'Asia/Ulaanbaatar', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }};
        const formatter = new Intl.DateTimeFormat([], options);
        const d = new Date();
        const parts = formatter.formatToParts(d);
        let year, month, day, hour, minute, second;
        for (let p of parts) {{
            if (p.type === 'year') year = p.value;
            if (p.type === 'month') month = p.value;
            if (p.type === 'day') day = p.value;
            if (p.type === 'hour') hour = p.value;
            if (p.type === 'minute') minute = p.value;
            if (p.type === 'second') second = p.value;
        }}
        const elem = document.getElementById('live-clock');
        if (elem) {{
            elem.innerText = year + ' оны ' + month + ' сарын ' + day + ' · ' + hour + ':' + minute + ':' + second;
        }}
    }}
    if (!window.clockInterval) {{
        window.clockInterval = setInterval(updateClock, 1000);
    }}
    </script>
"""
st.markdown(clock_html, unsafe_allow_html=True)

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
            time_str = get_ub_now().strftime("%H:%M")
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
    st.markdown("<p style='font-size: 13px; color: #94a3b8;'>💡 Засах эсвэл устгахын тулд тухайн ажил дээр дарна уу.</p>", unsafe_allow_html=True)

    if today_str in st.session_state.data and st.session_state.data[today_str].get("logs"):
        logs_list = st.session_state.data[today_str]["logs"]

        if "editing_id" not in st.session_state:
            st.session_state.editing_id = None

        for item in logs_list:
            item_id = item["id"]
            item_time = item["time"]
            item_text = item["text"]

            if st.session_state.editing_id == item_id:
                st.markdown(f"**🕒 {item_time} - Засварлах хэсэг:**")
                with st.form(key=f"edit_form_{item_id}"):
                    updated_text = st.text_area(
                        "Засах утга:", value=item_text, height=80, label_visibility="collapsed"
                    )
                    c_save, c_del, c_cancel = st.columns(3)
                    with c_save:
                        save_btn = st.form_submit_button("💾 Хадгалах")
                    with c_del:
                        delete_btn = st.form_submit_button("🗑️ Устгах")
                    with c_cancel:
                        cancel_btn = st.form_submit_button("❌ Болих")

                    if save_btn:
                        item["text"] = updated_text
                        save_data(st.session_state.data)
                        st.session_state.editing_id = None
                        st.rerun()
                    if delete_btn:
                        st.session_state.data[today_str]["logs"] = [
                            x for x in logs_list if x["id"] != item_id
                        ]
                        save_data(st.session_state.data)
                        st.session_state.editing_id = None
                        st.rerun()
                    if cancel_btn:
                        st.session_state.editing_id = None
                        st.rerun()
            else:
                btn_label = f"🕒 {item_time}\n\n{item_text}"
                if st.button(btn_label, key=f"btn_edit_{item_id}", use_container_width=True):
                    st.session_state.editing_id = item_id
                    st.rerun()
    else:
        st.info("Өнөөдөр одоогоор бүртгэсэн ажил алга.")

elif st.session_state.nav_page == "Нэгтгэл":
    st.markdown("#### Ажлын тайлан нэгтгэх")


    def generate_options_with_ai(logs_list):
        if not logs_list:
            return []
        
        logs_text = ""
        for log in logs_list:
            logs_text += f"[{log['time']}] {log['text']}\n"

        prompt = f"""
Доорх ажил боловсруулсан тэмдэглэлүүд дээр үндэслэн ямар нэгэн илүү дутуу оршил, тайлбар үггүйгээр шууд цэвэр тайлангийн агуулга бүхий **3 өөр загварын хувилбар** бэлтгэж өгнө үү.
Хувилбар тус бүрийг '---HUVIILBAR---' гэсэн үгээр хооронд нь зааглаж ялгаж бичнэ үү.

Тэмдэглэлүүд:
{logs_text}

Хувилбарууд:
1. Цэгцтэй гол санааг гаргасан товч жагсаалт хэлбэрээр.
2. Албан ёсны ажил хэргийн тайлан байдлаар.
3. Нэгтгэсэн цулгуй өгүүлбэр хэлбэртэйгээр.
"""
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash", contents=prompt
            )
            parts = response.text.split("---HUVIILBAR---")
            cleaned_parts = [p.strip() for p in parts if p.strip()]
            return cleaned_parts if cleaned_parts else [response.text]
        except Exception as e:
            return [f"АЛДАА ГАРЛАА: {str(e)}"]


    if st.button("✨ Тайлангийн хувилбарууд үүсгэх"):
        if today_str in st.session_state.data and st.session_state.data[today_str].get("logs"):
            with st.spinner("Боловсруулж байна..."):
                options = generate_options_with_ai(st.session_state.data[today_str]["logs"])
                st.session_state["ai_options"] = options
        else:
            st.warning("Нэгтгэх ажил одоогоор бүртгэгдээгүй байна.")

    if "ai_options" in st.session_state and st.session_state["ai_options"]:
        st.markdown("---")
        st.markdown("<p style='color: #2ff5ca; font-weight: 700; margin-bottom: 10px;'>📌 Таалагдсан хувилбараа сонгоно уу:</p>", unsafe_allow_html=True)
        
        selected_option = st.radio(
            "Хувилбар сонгох:",
            options=range(len(st.session_state["ai_options"])),
            format_func=lambda x: f"Хувилбар #{x + 1}",
            label_visibility="collapsed"
        )

        st.markdown(
            f"""
            <div class="summary-box">
                {st.session_state["ai_options"][selected_option]}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Сонгосон хувилбарыг Архив руу хадгалах"):
            st.session_state.data[today_str]["summary"] = st.session_state["ai_options"][selected_option]
            save_data(st.session_state.data)
            st.success("Амжилттай Архив руу хадгалагдлаа!")

    elif today_str in st.session_state.data and st.session_state.data[today_str].get("summary"):
        st.markdown("#### Өнөөдрийн хадгалсан тайлан:")
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
                st.info("Энэ өдөр тайлан хадгалаагүй байна.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.write("**Тухайн өдрийн дэлгэрэнгүй жагсаалт (Засах эсвэл устгах):**")

            if "archive_editing_id" not in st.session_state:
                st.session_state.archive_editing_id = None

            archive_logs = st.session_state.data[selected_date].get("logs", [])
            for item in archive_logs:
                item_id = item["id"]
                item_time = item["time"]
                item_text = item["text"]

                if st.session_state.archive_editing_id == item_id:
                    with st.form(key=f"archive_edit_form_{item_id}"):
                        up_text = st.text_area("Засах:", value=item_text, height=80, label_visibility="collapsed")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            s_btn = st.form_submit_button("💾 Хадгалах")
                        with c2:
                            d_btn = st.form_submit_button("🗑️ Устгах")
                        with c3:
                            c_btn = st.form_submit_button("❌ Болих")

                        if s_btn:
                            item["text"] = up_text
                            save_data(st.session_state.data)
                            st.session_state.archive_editing_id = None
                            st.rerun()
                        if d_btn:
                            st.session_state.data[selected_date]["logs"] = [
                                x for x in archive_logs if x["id"] != item_id
                            ]
                            save_data(st.session_state.data)
                            st.session_state.archive_editing_id = None
                            st.rerun()
                        if c_btn:
                            st.session_state.archive_editing_id = None
                            st.rerun()
                else:
                    if st.button(f"🕒 {item_time}\n\n{item_text}", key=f"arch_btn_{item_id}", use_container_width=True):
                        st.session_state.archive_editing_id = item_id
                        st.rerun()
    else:
        st.info("Архив хоосон байна.")

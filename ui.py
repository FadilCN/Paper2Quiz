import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Lato:wght@400;700&display=swap');

        * { box-sizing: border-box; }

        header[data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
        }

        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }

        .left-content {
            background-color: #e1f5fe;
            padding: 60px 50px 60px 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-end;
            height: 100vh;
            text-align: right;
        }

        .right-content {
            margin-top: 250px;
        }

        .q-label {
            font-family: 'Nunito', sans-serif;
            font-size: 0.85rem;
            font-weight: 900;
            color: #0288d1;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 4px;
        }

        .q-title {
            font-family: 'Nunito', sans-serif;
            font-size: 2rem;
            font-weight: 900;
            color: #01579b;
            line-height: 1.3;
            margin: 0;
        }

        .q-subtitle {
            font-family: 'Lato', sans-serif;
            font-size: 0.95rem;
            color: #0288d1;
            margin-top: 18px;
            font-weight: 400;
        }

        button[kind="secondary"] {
            display: block !important;
            width: 80% !important;
            max-width: 520px !important;
            margin: 8px auto !important;
            padding: 16px 30px !important;
            font-family: 'Nunito', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            background-color: #f5f5f5 !important;
            color: #333 !important;
            border: none !important;
            border-radius: 14px !important;
            text-align: left !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
        }

        button[kind="secondary"]:hover {
            background-color: #ececec !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }

        button[kind="primary"] {
            display: block !important;
            width: auto !important;
            margin: 24px auto 0 auto !important;
            padding: 12px 32px !important;
            font-family: 'Nunito', sans-serif !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            background-color: #43a047 !important;
            color: #fff !important;
            border: none !important;
            border-radius: 50px !important;
            box-shadow: 0 4px 14px rgba(67,160,71,0.35) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"]:hover {
            background-color: #2e7d32 !important;
            transform: translateY(-2px) !important;
        }

        div[data-testid="stAlert"] {
            width: 80%;
            max-width: 520px;
            margin: 6px auto !important;
            border-radius: 10px !important;
            font-family: 'Lato', sans-serif !important;
        }

        [data-testid="column"]:nth-child(2) > div:first-child {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            min-height: 100vh !important;
        }
    </style>
""", unsafe_allow_html=True)

from llm import get_chunks, use_llm

# ── Load question only once (or when Next is clicked) ──
if "data" not in st.session_state:
    chunks = get_chunks()
    st.session_state.data = use_llm(chunks)
    st.session_state.chunks = chunks
    st.session_state.selected = None
    st.session_state.question_num = 1

data = st.session_state.data

col1, col2 = st.columns([1, 2])

# ── Left panel ──
question = data["question"]

with col1:
    st.markdown(f"""
        <div class="left-content">
            <div class="q-label">Question {str(st.session_state.question_num).zfill(2)}</div>
            <h1 class="q-title">{question}</h1>
            <p class="q-subtitle">Select the best answer and tap Next to continue.</p>
        </div>
    """, unsafe_allow_html=True)

# ── Right panel ──
try:
    o1 = data["options"][0]
except Exception as e:
    o1 = "Option 1"

try:
    o2 = data["options"][1]
except Exception as e:
    o2 = "Option 2"

try:
    o3 = data["options"][2]
except Exception as e:
    o3 = "Option 3"

try:
    o4 = data["options"][3]
except Exception as e:
    o4 = "Option 4"

try:
    ans = data["answer"]    
except Exception as e:
    ans = "no_answer"

try:
    source = data["source"]
except Exception as e:      
    source = "no_source"

def feedback(option):
    if option == ans:
        st.success(f"✅ Correct! '{option}' is the right answer.")
        st.info(source)
    else:
        st.warning(f"❌ Not quite! '{option}' is incorrect.")

with col2:
    st.markdown('<div class="right-content"></div>', unsafe_allow_html=True)

    if st.button(f"1️⃣ {o1}"):
        st.session_state.selected = o1

    if st.button(f"2️⃣ {o2}"):
        st.session_state.selected = o2

    if st.button(f"3️⃣ {o3}"):
        st.session_state.selected = o3

    if st.button(f"4️⃣ {o4}"):
        st.session_state.selected = o4

    # Show feedback if an answer was selected
    if st.session_state.selected:
        feedback(st.session_state.selected)

    # Next button — reload question
    if st.button("Next Question →", type="primary"):
        chunks = st.session_state.chunks
        st.session_state.data = use_llm(chunks)
        st.session_state.selected = None
        st.session_state.question_num += 1
        st.rerun()
"""
FlightLens Streamlit Application
Improved v2 – Optimized for MPNet + Updated RAG Chain
"""

import sys
from pathlib import Path
import streamlit as st

# ---------------------------------------------------------
# Project Path Setup
# ---------------------------------------------------------
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.chain import answer_question, answer_question_with_sources
from src.utils.context_simconnect import MSFSContext
from src.integrations.aviation_weather import get_metar, decode_metar

# Voice support
try:
    import whisper
    import sounddevice as sd
    import wavio
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


# ---------------------------------------------------------
# Load Custom CSS
# ---------------------------------------------------------
def load_css():
    css_file = Path(__file__).parent / "styles" / "app_styles.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8", errors="ignore") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error("⚠️ Custom CSS file not found.")

# ---------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="FlightLens – Cockpit AI Assistant",
    page_icon="🛫",
    layout="wide"
)

load_css()


# ---------------------------------------------------------
# Initialize SimConnect (cached)
# ---------------------------------------------------------
@st.cache_resource
def init_simconnect():
    try:
        return MSFSContext()
    except Exception as e:
        st.error(f"SimConnect Error: {e}")
        return None

sim = init_simconnect()


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------
if "query_history" not in st.session_state:
    st.session_state.query_history = []


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("🛫 FlightLens – Advanced Cockpit AI Assistant")
st.markdown("### Real-time aviation knowledge with source-grounded answers")
st.divider()


# ---------------------------------------------------------
# SIDEBAR — WEATHER + TELEMETRY
# ---------------------------------------------------------
with st.sidebar:
    st.header("🌦️ Weather Assistant")
    icao = st.text_input("ICAO Code", "KDFW")

    if st.button("Get METAR", use_container_width=True):
        raw = get_metar(icao)
        st.text_area("Raw METAR", raw, height=80)

        if not raw.startswith("Error") and "No METAR" not in raw:
            decoded = decode_metar(raw)
            st.info(f"**Decoded METAR:**\n\n{decoded}")
        else:
            st.error(raw)

    st.divider()
    st.header("✈️ Live Telemetry")

    if st.button("Refresh Telemetry", use_container_width=True):
        if sim:
            status = sim.get_status()
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Altitude", f"{status['altitude']:.0f} ft")
                st.metric("Airspeed", f"{status['airspeed']:.0f} kts")
                st.metric("Heading", f"{status['heading']:.0f}°")

            with col2:
                st.metric("Vertical Speed", f"{status['vertical_speed']:.0f} fpm")
                st.metric("Fuel", f"{status['fuel_quantity']:.1f} gal")
                st.metric("Engine RPM", f"{status['engine_rpm']:.0f}")

            st.caption(f"Mode: {sim.mode}")
        else:
            st.error("SimConnect not initialized.")
    else:
        st.info("Click to refresh telemetry")


# ---------------------------------------------------------
# MAIN TABS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["💬 Text Query", "🎤 Voice Query", "📚 Source Grounding"])


# ---------------------------------------------------------
# TAB 1 — TEXT QUERY
# ---------------------------------------------------------
with tab1:
    st.header("Ask a Question")

    col1, col2 = st.columns([3, 1])
    query = col1.text_input("Question", placeholder="E.g., What are VFR minimums?")
    show_src = col2.checkbox("Show sources", value=True)

    if st.button("Submit Query", type="primary", use_container_width=True):
        if not query:
            st.warning("Please enter a valid question.")
        else:
            st.session_state.query_history.append(query)

            with st.spinner("Processing your query..."):
                if show_src:
                    result = answer_question_with_sources(query)
                    st.success("Answer")
                    st.markdown(
                        f'<div class="answer-block">{result["answer"]}</div>',
                        unsafe_allow_html=True,
                    )

                    with st.expander(f"Sources ({result['num_sources']})"):
                        st.markdown('<div class="sources-block">', unsafe_allow_html=True)
                        for s in result["sources"]:
                            st.text(s["content"])
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.success("Answer")
                    st.write(answer_question(query))

    # Recent history
    if len(st.session_state.query_history):
        with st.expander("Recent Queries"):
            for q in reversed(st.session_state.query_history[-5:]):
                st.write("• " + q)


# ---------------------------------------------------------
# TAB 2 — VOICE QUERY
# ---------------------------------------------------------
with tab2:
    st.header("Voice Query")

    if not VOICE_AVAILABLE:
        st.error("Voice mode unavailable. Install: openai-whisper, sounddevice, wavio")
    else:
        duration = st.slider("Recording Duration (seconds)", 3, 10, 5)

        if st.button("🎙 Record", type="primary"):
            st.write("Recording...")
            fs = 16000
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
            sd.wait()

            wavio.write("query.wav", audio, fs, sampwidth=2)

            st.success("Recording saved. Transcribing...")

            model = whisper.load_model("base")
            transcription = model.transcribe("query.wav")["text"]

            st.info("Transcribed Text:")
            st.write(transcription)

            st.success("Answer:")
            st.write(answer_question(transcription))


# ---------------------------------------------------------
# TAB 3 — SOURCE GROUNDING
# ---------------------------------------------------------
with tab3:
    st.header("Source Grounding Demo")

    examples = [
        "What is the minimum safe altitude?",
        "Interpret METAR visibility",
        "VFR weather minimums in Class E",
        "Engine fire procedure in flight",
    ]

    q = st.selectbox("Choose a question:", examples)

    if st.button("Run Source Grounding", type="primary"):
        result = answer_question_with_sources(q)

        st.success("Answer")
        st.markdown(
            f'<div class="answer-block">{result["answer"]}</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Sources"):
            st.markdown('<div class="sources-block">', unsafe_allow_html=True)
            for s in result["sources"]:
                st.text(s["content"])
            st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
col1, col2, col3 = st.columns(3)
col1.caption("FlightLens v2.0 — RAG + MPNet Engine")
col2.caption(f"Telemetry Mode: {sim.mode if sim else 'N/A'}")
col3.caption("UNT Research Project – DTSC 5082")

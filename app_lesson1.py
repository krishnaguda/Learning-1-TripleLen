import streamlit as st
import time
import concurrent.futures
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TripleLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Root Variables ── */
  :root {
    --gemini:   #4285F4;
    --llama33:  #F97316;
    --llama4:   #22D3EE;
    --purple:   #8B5CF6;
    --bg-base:  #0A0A0F;
    --bg-card:  #111118;
    --bg-glass: rgba(255,255,255,0.04);
    --border:   rgba(255,255,255,0.08);
    --text-1:   #F1F0FF;
    --text-2:   #A09EC0;
    --text-3:   #6B69A0;
    --radius:   14px;
    --glow-blur: 60px;
  }

  /* ── Base Reset ── */
  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-1);
  }

  .stApp {
    background: var(--bg-base) !important;
    background-image:
      radial-gradient(ellipse 80% 50% at 20% -10%, rgba(139,92,246,0.12) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 110%, rgba(34,211,238,0.08) 0%, transparent 55%),
      radial-gradient(ellipse 50% 60% at 50% 50%, rgba(66,133,244,0.04) 0%, transparent 70%);
    background-attachment: fixed;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0D0D14 !important;
    border-right: 1px solid var(--border) !important;
  }
  [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

  /* ── Sidebar Logo ── */
  .sidebar-logo {
    text-align: center;
    padding: 0 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
  }
  .sidebar-logo .logo-mark {
    font-size: 2rem;
    line-height: 1;
    margin-bottom: 0.25rem;
  }
  .sidebar-logo h2 {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: var(--text-1) !important;
    letter-spacing: -0.02em;
    margin: 0 !important;
  }
  .sidebar-logo p {
    font-size: 0.7rem !important;
    color: var(--text-3) !important;
    margin: 0 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  /* Sidebar section label */
  .sidebar-section {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-3);
    padding: 0 0 0.5rem 0;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }

  /* ── Main Title Area ── */
  .hero-header {
    text-align: center;
    padding: 2.5rem 0 2rem;
    position: relative;
  }
  .hero-header h1 {
    font-size: clamp(2.5rem, 5vw, 3.8rem) !important;
    font-weight: 700 !important;
    letter-spacing: -0.04em !important;
    line-height: 1 !important;
    margin: 0 0 0.75rem !important;
    background: linear-gradient(135deg, #F1F0FF 0%, #8B5CF6 50%, #22D3EE 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
  }
  .hero-header p {
    color: var(--text-2);
    font-size: 1rem;
    font-weight: 400;
    margin: 0;
    letter-spacing: 0.01em;
  }
  .hero-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, var(--purple), var(--llama4));
    margin: 1.25rem auto 0;
    border-radius: 99px;
  }

  /* ── Model Badge Headers ── */
  .model-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.75rem 1rem;
    border-radius: var(--radius) var(--radius) 0 0;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
  }
  .model-header::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.08;
  }
  .model-header .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
  }
  .header-gemini   { background: rgba(66,133,244,0.12);  color: #93BBFD; border: 1px solid rgba(66,133,244,0.25);  }
  .header-gemini .dot   { background: #4285F4; color: #4285F4; }
  .header-llama33  { background: rgba(249,115,22,0.12); color: #FDBA74; border: 1px solid rgba(249,115,22,0.25);  }
  .header-llama33 .dot  { background: #F97316; color: #F97316; }
  .header-llama4   { background: rgba(34,211,238,0.12);  color: #67E8F9; border: 1px solid rgba(34,211,238,0.25); }
  .header-llama4 .dot   { background: #22D3EE; color: #22D3EE; }

  /* ── Response Cards ── */
  .response-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 var(--radius) var(--radius);
    padding: 1.1rem 1.1rem 0.6rem;
    min-height: 220px;
    position: relative;
  }
  .response-text {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text-1);
    white-space: pre-wrap;
    word-break: break-word;
    font-family: 'Space Grotesk', sans-serif;
  }
  .response-placeholder {
    color: var(--text-3);
    font-size: 0.8rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 180px;
    gap: 0.5rem;
    text-align: center;
  }
  .response-placeholder .lock-icon { font-size: 1.5rem; opacity: 0.4; }
  .response-error {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #FCA5A5;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ── Stats Caption ── */
  .stats-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    padding: 0.6rem 0 0.2rem;
    border-top: 1px solid var(--border);
    margin-top: 0.8rem;
  }
  .stat-chip {
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 0.2rem 0.6rem;
    font-size: 0.68rem;
    color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
  }
  .stat-chip span { color: var(--text-1); font-weight: 500; }

  /* ── Metrics Section ── */
  .metrics-header {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-3);
    text-align: center;
    padding: 1.5rem 0 0.75rem;
  }

  /* ── Prompt Templates ── */
  .template-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0.5rem 0;
  }

  /* ── History ── */
  .history-item {
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
  }
  .history-item .h-prompt {
    color: var(--text-1);
    font-weight: 500;
    margin-bottom: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .history-item .h-meta {
    color: var(--text-3);
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ── Compare Button ── */
  .stButton > button {
    background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(139,92,246,0.3) !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(139,92,246,0.45) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* Template buttons */
  div[data-testid="column"] .stButton > button {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.75rem !important;
    padding: 0.35rem 0.75rem !important;
    box-shadow: none !important;
    color: var(--text-2) !important;
    font-weight: 500 !important;
  }
  div[data-testid="column"] .stButton > button:hover {
    border-color: rgba(139,92,246,0.4) !important;
    color: var(--text-1) !important;
    transform: none !important;
  }

  /* Inputs */
  .stTextArea textarea, .stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-1) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.875rem !important;
  }
  .stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
  }
  .stTextInput input[type="password"] {
    font-family: 'JetBrains Mono', monospace !important;
  }

  /* Sliders */
  .stSlider [data-baseweb="slider"] > div:first-child {
    background: var(--border) !important;
  }
  .stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--purple) !important;
    border-color: var(--purple) !important;
  }

  /* Expanders */
  .streamlit-expanderHeader {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-2) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
  }
  .streamlit-expanderContent {
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    background: var(--bg-card) !important;
  }

  /* Metric cards */
  [data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
  }
  [data-testid="stMetricLabel"] { color: var(--text-3) !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
  [data-testid="stMetricValue"] { color: var(--text-1) !important; font-family: 'JetBrains Mono', monospace !important; }
  [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }

  /* Labels */
  label, .stSelectbox label, .stSlider label {
    color: var(--text-2) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

  /* Spinner */
  .stSpinner > div { border-top-color: var(--purple) !important; }

  /* Hide default streamlit elements */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 0 !important; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)

# ─── API Call Functions ────────────────────────────────────────────────────────

def call_gemini(prompt: str, system_prompt: str, api_key: str, temperature: float, max_tokens: int) -> dict:
    from google import genai
    from google.genai import types

    start = time.time()
    try:
        client = genai.Client(api_key=api_key)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt.strip() else prompt
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        elapsed = time.time() - start
        return {
            "text": response.text,
            "tokens_in": response.usage_metadata.prompt_token_count,
            "tokens_out": response.usage_metadata.candidates_token_count,
            "time": elapsed,
            "error": None,
        }
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": time.time() - start, "error": str(e)}


def call_groq(model_id: str, prompt: str, system_prompt: str, api_key: str, temperature: float, max_tokens: int) -> dict:
    from groq import Groq

    start = time.time()
    try:
        client = Groq(api_key=api_key)
        messages = []
        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
        elapsed = time.time() - start
        return {
            "text": response.choices[0].message.content,
            "tokens_in": response.usage.prompt_tokens,
            "tokens_out": response.usage.completion_tokens,
            "time": elapsed,
            "error": None,
        }
    except Exception as e:
        return {"text": None, "tokens_in": 0, "tokens_out": 0, "time": time.time() - start, "error": str(e)}


def run_all(prompt: str, system_prompt: str, gemini_key: str, groq_key: str, temperature: float, max_tokens: int):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {}
        if gemini_key:
            futures["gemini"] = ex.submit(call_gemini, prompt, system_prompt, gemini_key, temperature, max_tokens)
        if groq_key:
            futures["llama33"] = ex.submit(call_groq, "llama-3.3-70b-versatile", prompt, system_prompt, groq_key, temperature, max_tokens)
            futures["llama4"] = ex.submit(call_groq, "meta-llama/llama-4-scout-17b-16e-instruct", prompt, system_prompt, groq_key, temperature, max_tokens)
        for k, f in futures.items():
            results[k] = f.result()
    return results

# ─── Session State Init ────────────────────────────────────────────────────────

if "history" not in st.session_state:
    st.session_state.history = []
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="logo-mark">🔍</div>
      <h2>TripleLens</h2>
      <p>Multi-Model Comparator</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">API Keys</div>', unsafe_allow_html=True)
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", help="Google AI Studio key for Gemini")
    groq_key   = st.text_input("Groq API Key",   type="password", placeholder="gsk_...",  help="Covers both Llama 3.3 and Llama 4")

    st.markdown("---")
    st.markdown('<div class="sidebar-section">Generation Settings</div>', unsafe_allow_html=True)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, help="Higher = more creative")
    max_tokens  = st.slider("Max Tokens",  100, 4000, 1024, 50, help="Max output length")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.68rem; color:var(--text-3); line-height:1.6;">
      <b style="color:var(--text-2);">Models</b><br>
      <span style="color:#93BBFD;">●</span> Gemini 2.0 Flash (Google)<br>
      <span style="color:#FDBA74;">●</span> Llama 3.3 70B (Groq)<br>
      <span style="color:#67E8F9;">●</span> Llama 4 Scout 17B (Groq)<br><br>
      All models run simultaneously via parallel API calls.
    </div>
    """, unsafe_allow_html=True)

# ─── Main Area ────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
  <h1>🔍 TripleLens</h1>
  <p>Compare three AI models side-by-side — same prompt, same moment, real differences.</p>
  <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Prompt Templates ──
TEMPLATES = {
    "⚡ Code Explanation": "Explain the concept of recursion with a simple Python example. Walk me through how the call stack works step by step.",
    "✍️ Writing Help":    "Write a compelling opening paragraph for a short story set in a city that exists only at night, with characters who have no memory of the day.",
    "🔍 Analysis":        "Analyze the tradeoffs between microservices and monolithic architecture. When should a team choose one over the other?",
    "💡 Brainstorm":      "Brainstorm 10 creative product ideas for a startup targeting remote workers who feel isolated. Include one-line descriptions.",
    "📚 Research":        "Summarize the key arguments for and against universal basic income, citing the most compelling evidence on each side.",
}

with st.expander("📋 Prompt Templates", expanded=False):
    cols = st.columns(len(TEMPLATES))
    for i, (label, text) in enumerate(TEMPLATES.items()):
        if cols[i].button(label, key=f"tmpl_{i}"):
            st.session_state.prompt_text = text
            st.rerun()

# ── System Prompt ──
with st.expander("⚙️ System Prompt (optional)", expanded=False):
    system_prompt = st.text_area(
        "System Prompt",
        height=80,
        placeholder="e.g. You are a concise technical expert. Answer in bullet points.",
        label_visibility="collapsed",
    )

# ── Main Prompt Input ──
prompt = st.text_area(
    "Your Prompt",
    value=st.session_state.prompt_text,
    height=120,
    placeholder="Ask anything — the same question will be sent to all three models simultaneously...",
    label_visibility="collapsed",
)
if prompt != st.session_state.prompt_text:
    st.session_state.prompt_text = prompt

col_btn, col_info = st.columns([1, 4])
with col_btn:
    compare_clicked = st.button("⚡ Compare", use_container_width=True)
with col_info:
    active = (1 if gemini_key else 0) + (2 if groq_key else 0)
    model_count = (1 if gemini_key else 0) + (2 if groq_key else 0)
    st.markdown(f"""
    <div style="display:flex;align-items:center;height:100%;gap:0.5rem;padding-top:0.25rem;">
      <span style="font-size:0.75rem;color:var(--text-3);">
        {'✅' if gemini_key else '🔒'} Gemini &nbsp;
        {'✅' if groq_key else '🔒'} Llama 3.3 &nbsp;
        {'✅' if groq_key else '🔒'} Llama 4 Scout
        &nbsp;·&nbsp; <span style="color:var(--text-2);font-weight:600;">{model_count} model{'s' if model_count != 1 else ''} active</span>
      </span>
    </div>
    """, unsafe_allow_html=True)

# ─── Run Comparison ───────────────────────────────────────────────────────────

if compare_clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    elif not gemini_key and not groq_key:
        st.error("Add at least one API key in the sidebar to get started.")
    else:
        with st.spinner("Sending to models in parallel..."):
            sys_p = system_prompt if "system_prompt" in dir() else ""
            results = run_all(prompt, sys_p, gemini_key or "", groq_key or "", temperature, max_tokens)
        st.session_state["last_results"] = results
        st.session_state["last_prompt"] = prompt

        # Save to history
        st.session_state.history.insert(0, {
            "prompt": prompt,
            "timestamp": datetime.now().strftime("%H:%M · %b %d"),
            "models": list(results.keys()),
        })
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[:20]

# ─── Display Results ──────────────────────────────────────────────────────────

MODELS = [
    {
        "key": "gemini",
        "label": "Gemini 2.0 Flash",
        "provider": "Google",
        "badge_class": "header-gemini",
        "icon": "✦",
        "fallback_key": "gemini_key",
        "missing_msg": "Add Gemini API key to enable",
    },
    {
        "key": "llama33",
        "label": "Llama 3.3 · 70B",
        "provider": "Meta via Groq",
        "badge_class": "header-llama33",
        "icon": "◈",
        "fallback_key": "groq_key",
        "missing_msg": "Add Groq API key to enable",
    },
    {
        "key": "llama4",
        "label": "Llama 4 Scout · 17B",
        "provider": "Meta via Groq",
        "badge_class": "header-llama4",
        "icon": "◆",
        "fallback_key": "groq_key",
        "missing_msg": "Add Groq API key to enable",
    },
]

col1, col2, col3 = st.columns(3, gap="medium")
columns = [col1, col2, col3]

if "last_results" in st.session_state:
    results = st.session_state["last_results"]

    for col, model in zip(columns, MODELS):
        with col:
            # Header
            st.markdown(f"""
            <div class="model-header {model['badge_class']}">
              <span class="dot"></span>
              <div>
                <div>{model['label']}</div>
                <div style="font-size:0.6rem;opacity:0.6;font-weight:400;letter-spacing:0.02em;">{model['provider']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if model["key"] in results:
                r = results[model["key"]]
                if r["error"]:
                    st.markdown(f"""
                    <div class="response-card">
                      <div class="response-error">⚠ {r['error']}</div>
                      <div class="stats-row">
                        <span class="stat-chip">⏱ <span>{r['time']:.2f}s</span></span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    words = len(r["text"].split()) if r["text"] else 0
                    st.markdown(f"""
                    <div class="response-card">
                      <div class="response-text">{r['text']}</div>
                      <div class="stats-row">
                        <span class="stat-chip">⏱ <span>{r['time']:.2f}s</span></span>
                        <span class="stat-chip">↑ <span>{r['tokens_in']:,}</span> in</span>
                        <span class="stat-chip">↓ <span>{r['tokens_out']:,}</span> out</span>
                        <span class="stat-chip">📝 <span>{words}</span> words</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                key_present = gemini_key if model["key"] == "gemini" else groq_key
                if not key_present:
                    st.markdown(f"""
                    <div class="response-card">
                      <div class="response-placeholder">
                        <span class="lock-icon">🔒</span>
                        <span>{model['missing_msg']}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Comparison Metrics ──
    valid = {k: v for k, v in results.items() if not v["error"] and v["text"]}
    if valid:
        st.markdown('<div class="metrics-header">Comparison Metrics</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3, gap="medium")
        metric_cols = [m1, m2, m3]
        names = {"gemini": "Gemini 2.0 Flash", "llama33": "Llama 3.3 70B", "llama4": "Llama 4 Scout"}

        for col, model in zip(metric_cols, MODELS):
            with col:
                k = model["key"]
                if k in valid:
                    r = valid[k]
                    words = len(r["text"].split())
                    tps = r["tokens_out"] / r["time"] if r["time"] > 0 else 0
                    st.metric(
                        label=model["label"],
                        value=f"{r['time']:.2f}s",
                        delta=f"{int(tps)} tok/s · {words} words",
                    )
                else:
                    st.metric(label=model["label"], value="—", delta="Not available")

else:
    # Empty state — show placeholders
    for col, model in zip(columns, MODELS):
        with col:
            key_present = gemini_key if model["key"] == "gemini" else groq_key
            st.markdown(f"""
            <div class="model-header {model['badge_class']}">
              <span class="dot"></span>
              <div>
                <div>{model['label']}</div>
                <div style="font-size:0.6rem;opacity:0.6;font-weight:400;">{model['provider']}</div>
              </div>
            </div>
            <div class="response-card">
              <div class="response-placeholder">
                {'<span class="lock-icon">🔒</span><span>' + model["missing_msg"] + '</span>' if not key_present else '<span style="font-size:1.5rem;opacity:0.2;">◈</span><span>Response will appear here</span>'}
              </div>
            </div>
            """, unsafe_allow_html=True)

# ─── History ─────────────────────────────────────────────────────────────────

if st.session_state.history:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"🕘 Session History ({len(st.session_state.history)} queries)", expanded=False):
        for item in st.session_state.history:
            model_badges = " · ".join(item["models"])
            st.markdown(f"""
            <div class="history-item">
              <div class="h-prompt">{item['prompt'][:120]}{'...' if len(item['prompt']) > 120 else ''}</div>
              <div class="h-meta">{item['timestamp']} · {model_badges}</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Clear History", key="clear_hist"):
            st.session_state.history = []
            st.rerun()

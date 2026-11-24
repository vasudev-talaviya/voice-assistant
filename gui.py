import streamlit as st
import asyncio
import main

st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🤖",
    layout="centered"
)

# ---------------------------------------------------------------
# Siri-style orb CSS
# ---------------------------------------------------------------
ORB_CSS = """<style>
.siri-wrap{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:18px 0 6px 0;}
.siri-stage{position:relative;width:170px;height:170px;display:flex;align-items:center;justify-content:center;}
.siri-glow{position:absolute;inset:0;border-radius:50%;
background:conic-gradient(from 0deg,var(--g1),var(--g2),var(--g3),var(--g4),var(--g1));
filter:blur(26px);opacity:.55;animation:siri-spin 6s linear infinite;}
.siri-orb{position:relative;width:120px;height:120px;border-radius:50%;
background:radial-gradient(circle at 30% 30%,#ffffff 0%,var(--o1) 28%,var(--o2) 58%,var(--o3) 82%,#0a0f2c 100%);
box-shadow:0 0 34px rgba(var(--sh),.65),inset 0 0 25px rgba(255,255,255,.35);
animation:siri-breathe 4s ease-in-out infinite;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.siri-bars{display:none;align-items:center;gap:5px;height:60px;}
.siri-bars span{display:block;width:6px;height:14px;border-radius:4px;background:rgba(255,255,255,.95);}
.siri-label{margin-top:14px;font-size:15px;letter-spacing:.5px;opacity:.85;text-align:center;}
.siri-sub{font-size:12px;opacity:.55;margin-top:2px;text-align:center;}

/* Colour themes per state */
.idle{--g1:#00e5ff;--g2:#7c4dff;--g3:#ff4081;--g4:#ffab40;--o1:#b388ff;--o2:#448aff;--o3:#00e5ff;--sh:124,77,255;}
.listening{--g1:#00e5ff;--g2:#2979ff;--g3:#00bfa5;--g4:#18ffff;--o1:#b3e5fc;--o2:#40c4ff;--o3:#2979ff;--sh:41,121,255;}
.thinking{--g1:#7c4dff;--g2:#e040fb;--g3:#536dfe;--g4:#ff4081;--o1:#e1bee7;--o2:#ba68c8;--o3:#7c4dff;--sh:186,104,200;}
.speaking{--g1:#ff4081;--g2:#ffab40;--g3:#ffd740;--g4:#ff6e40;--o1:#ffe0b2;--o2:#ff80ab;--o3:#ff6e40;--sh:255,110,64;}
.speaking .siri-stage{animation:siri-hue 4s linear infinite;}
.speaking .siri-label{background:linear-gradient(90deg,#ff4081,#ffab40,#7c4dff,#00e5ff,#ff4081);background-size:300% 100%;
-webkit-background-clip:text;background-clip:text;color:transparent;opacity:1;animation:siri-text 3s linear infinite;}

.listening .siri-glow{animation:siri-spin 2.2s linear infinite;opacity:.85;}
.listening .siri-orb{animation:siri-pulse 1.1s ease-in-out infinite;}
.listening .siri-bars{display:flex;}
.listening .siri-bars span{animation:siri-wave 0.9s ease-in-out infinite;}
.listening .siri-bars span:nth-child(1){animation-delay:0s}
.listening .siri-bars span:nth-child(2){animation-delay:.1s}
.listening .siri-bars span:nth-child(3){animation-delay:.2s}
.listening .siri-bars span:nth-child(4){animation-delay:.3s}
.listening .siri-bars span:nth-child(5){animation-delay:.2s}
.listening .siri-bars span:nth-child(6){animation-delay:.1s}
.listening .siri-bars span:nth-child(7){animation-delay:0s}

.thinking .siri-glow{animation:siri-spin 1s linear infinite;opacity:.95;}
.thinking .siri-orb{animation:siri-think 1.2s ease-in-out infinite;}

.speaking .siri-glow{animation:siri-spin 3s linear infinite;opacity:.8;}
.speaking .siri-orb{animation:siri-pulse 1.6s ease-in-out infinite;}
.speaking .siri-bars{display:flex;}
.speaking .siri-bars span{animation:siri-wave 0.7s ease-in-out infinite;}
.speaking .siri-bars span:nth-child(1){animation-delay:.05s}
.speaking .siri-bars span:nth-child(2){animation-delay:.25s}
.speaking .siri-bars span:nth-child(3){animation-delay:.1s}
.speaking .siri-bars span:nth-child(4){animation-delay:.35s}
.speaking .siri-bars span:nth-child(5){animation-delay:.15s}
.speaking .siri-bars span:nth-child(6){animation-delay:.3s}
.speaking .siri-bars span:nth-child(7){animation-delay:.2s}

@keyframes siri-hue{from{filter:hue-rotate(0deg)}to{filter:hue-rotate(360deg)}}
@keyframes siri-text{from{background-position:0% 0}to{background-position:300% 0}}
@keyframes siri-spin{to{transform:rotate(360deg)}}
@keyframes siri-breathe{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
@keyframes siri-pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.18)}}
@keyframes siri-think{0%,100%{transform:scale(.88)}50%{transform:scale(1.08)}}
@keyframes siri-wave{0%,100%{height:12px}50%{height:56px}}
</style>"""

st.markdown(ORB_CSS, unsafe_allow_html=True)

STATES = {
    "idle":      ("Tap Speak to start talking", "I'm here"),
    "listening": ("Listening…", "Go ahead, I'm all ears"),
    "thinking":  ("Thinking…", "One moment"),
    "speaking":  ("Speaking…", "Playing response"),
}

# Words that end the voice conversation
EXIT_WORDS = {"exit", "stop", "quit", "goodbye", "bye", "stop listening"}

# Stop automatically after this many empty / failed listens in a row
MAX_SILENT_TURNS = 3


def render_orb(slot, state="idle"):
    label, sub = STATES[state]
    html = (
        f'<div class="siri-wrap {state}">'
        '<div class="siri-stage">'
        '<div class="siri-glow"></div>'
        '<div class="siri-orb"><div class="siri-bars">'
        '<span></span><span></span><span></span><span></span>'
        '<span></span><span></span><span></span>'
        '</div></div></div>'
        f'<div class="siri-label">{label}</div>'
        f'<div class="siri-sub">{sub}</div>'
        '</div>'
    )
    slot.markdown(html, unsafe_allow_html=True)


st.title("🤖 AI Voice Assistant")
st.caption("Your personal AI voice companion")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "voice_active" not in st.session_state:
    st.session_state.voice_active = False

# Chat area: all messages (old and new) are drawn inside this container
chat_container = st.container()

with chat_container:
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

# Orb sits right AFTER the chat, so it follows the conversation
# instead of staying at the top. It updates in place as state changes.
orb_slot = st.empty()
render_orb(orb_slot, "idle")


def process_message(user_text):
    """Send text to the AI, show + speak the reply.
    Returns False if the user asked to exit, otherwise True."""

    if not user_text.strip():
        return True

    if user_text.strip().lower() in EXIT_WORDS:
        with chat_container:
            st.write("Thanks")
        return False

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_text
    })

    with chat_container:
        with st.chat_message("user"):
            st.write(user_text)

    try:
        render_orb(orb_slot, "thinking")

        response = main.get_ai_response(user_text)

        print("[Response] :- ", response)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        with chat_container:
            with st.chat_message("assistant"):
                st.write(response)

        render_orb(orb_slot, "speaking")
        asyncio.run(main.speak(response))

    except Exception as e:
        st.error(f"Error: {e}")

    return True


# Text input (works as before, no auto-listening)
user_input = st.chat_input("Type your message...")

if user_input:
    process_message(user_input)
    render_orb(orb_slot, "idle")


# Voice controls
st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Speak", use_container_width=True,
                 disabled=st.session_state.voice_active):
        # Button is clicked only ONCE to start the conversation loop
        st.session_state.voice_active = True
        st.rerun()

with col2:
    if st.button("⏹️ Stop", use_container_width=True,
                 disabled=not st.session_state.voice_active):
        st.session_state.voice_active = False
        st.rerun()


# Clear conversation
if st.button("🗑️ Clear Chat"):

    st.session_state.chat_history = []
    st.session_state.voice_active = False

    main.messages = [
        {
            "role": "system",
            "content": "You're my good friend. Talk naturally and keep responses conversational."
        }
    ]

    st.rerun()


# ---------------------------------------------------------------
# Continuous voice loop:
# listen -> AI reply -> speak -> listen again ... (no more clicks)
# Ends on: exit word, Stop button, or several silent turns in a row.
# ---------------------------------------------------------------
if st.session_state.voice_active:

    silent_turns = 0

    while st.session_state.voice_active:

        try:
            render_orb(orb_slot, "listening")

            user_text = main.listen()

            if not user_text or not user_text.strip():
                raise ValueError("No speech detected")

            silent_turns = 0

        except Exception as e:
            silent_turns += 1
            print("[Listen]", e)

            if silent_turns >= MAX_SILENT_TURNS:
                st.info("I didn't hear anything, so I stopped listening. "
                        "Press 🎤 Speak to start again.")
                st.session_state.voice_active = False
                break

            continue

        keep_going = process_message(user_text)

        if not keep_going:
            st.session_state.voice_active = False
            break

    render_orb(orb_slot, "idle")
    st.rerun()
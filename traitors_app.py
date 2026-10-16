import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# PAGE CONFIG & GOTHIC CASTLE STYLING
# ==========================================
st.set_page_config(
    page_title="The Traitors: The Castle",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global App Background - Dark Stone & Crisp White Text */
    .stApp {
        background-color: #111015;
        color: #ffffff !important;
    }
    
    /* Ensure all general markdown and text is bright and readable */
    .stMarkdown, p, span, label, div {
        color: #f0ede6;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #16151c;
        border-right: 2px solid #3a3324;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Gothic Typography & Headers */
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        color: #f3e5ab !important;
        letter-spacing: 1px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
    }

    /* Player Cards - Stone Plaques with High Contrast Text */
    .player-card {
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 14px;
        text-align: center;
        border: 2px solid #c5a059;
        background: linear-gradient(145deg, #1f1d26 0%, #151319 100%);
        color: #ffffff !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.05);
    }
    .player-card div {
        color: #ffffff !important;
    }
    .player-dead {
        border: 2px solid #423d33;
        background: linear-gradient(145deg, #121115 0%, #0a090c 100%);
        color: #b3aca1 !important;
        opacity: 0.75;
    }
    .player-dead div {
        color: #b3aca1 !important;
    }
    
    /* Grand Finale Banners */
    .finale-banner-traitor {
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        background: linear-gradient(135deg, #380808 0%, #140303 100%);
        border: 3px solid #8b0000;
        color: #ffffff;
        margin-bottom: 24px;
    }
    .finale-banner-faithful {
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        background: linear-gradient(135deg, #0b2b18 0%, #041008 100%);
        border: 3px solid #c5a059;
        color: #ffffff;
        margin-bottom: 24px;
    }
    
    /* Award Plaques */
    .award-card {
        border-radius: 6px;
        padding: 20px;
        background: linear-gradient(145deg, #1a1820 0%, #121015 100%);
        border: 2px solid #c5a059;
        text-align: center;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .award-card div {
        color: #ffffff !important;
    }

    /* Role Highlights */
    .role-traitor {
        color: #ff6b6b !important;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .role-faithful {
        color: #5bc0be !important;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .role-hidden {
        color: #f39c12 !important;
        font-weight: bold;
    }

    /* Streamlit Form & Input Styling Overrides */
    .stTextInput input, .stSelectbox select {
        background-color: #1c1a24 !important;
        color: #ffffff !important;
        border: 1px solid #c5a059 !important;
    }
    .stButton button {
        background: linear-gradient(180deg, #c5a059 0%, #9e7b34 100%) !important;
        color: #111015 !important;
        font-weight: bold;
        border: 1px solid #e6cb8a !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
    .stButton button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #b38f42 100%) !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA PERSISTENCE & HOST CONFIG
# ==========================================
DATA_FILE = "castle_state.json"
HOST_PIN = "1411"  # Host Neilio's PIN

PHASES = [
    "Breakfast",
    "Mission & Discussion",
    "Round Table Voting",
    "The Fire Pit (Endgame)",
    "Overnight (Turret)",
    "🏆 The Grand Reveal (Finale)"
]

def get_default_state():
    default_players = {}
    for i in range(1, 38):  # Configured for up to 37 Players!
        name = f"Player {i:02d}"
        default_players[name] = {
            "pin": f"{1000 + i}",  # Default PINs: 1001 to 1037
            "role": "Traitor" if i in [3, 11, 18, 25, 32] else "Faithful", # 5 Traitors
            "status": "Alive",
            "eliminated_day": "",
            "shield": False,
            "public_shield": False,
            "hide_role": False
        }
    return {
        "current_day": 1,
        "fire_pit_round": 1,
        "phase": "Mission & Discussion",
        "prize_pot": 100,
        "traitor_pot": 0,
        "headline": "Welcome to the Castle, subjects of Neilio! Check your secret role in the Player Portal and complete Mission 1.",
        "mission_text": "🏆 **MISSION 1: TWO TRUTHS & AN ALIBI**\nPost two true facts and one lie in the WhatsApp chat before 13:30!",
        "players": default_players,
        "votes": {},
        "fire_pit_votes": {},
        "turret_targets": {}
    }

def load_state():
    if not os.path.exists(DATA_FILE):
        state = get_default_state()
        save_state(state)
        return state
    with open(DATA_FILE, "r") as f:
        state = json.load(f)
    state.setdefault("fire_pit_round", 1)
    state.setdefault("fire_pit_votes", {})
    for p in state.get("players", {}).values():
        p.setdefault("hide_role", False)
        p.setdefault("public_shield", False)
    return state

def save_state(state):
    with open(DATA_FILE, "w") as f:
        json.dump(state, f, indent=4)

state = load_state()
day_key = f"Day {state['current_day']}"
fp_key = f"Round {state['fire_pit_round']}"
is_finale_unlocked = (state["phase"] == "🏆 The Grand Reveal (Finale)")

def get_public_identity(pdata, force_reveal=False):
    status = pdata["status"]
    if not force_reveal:
        if status == "Alive":
            return "❓ Unknown", ""
        if pdata.get("hide_role", False):
            return "🔒 Hidden (Finale)", "role-hidden"
        if status == "Murdered":
            return "🕯️ Faithful", "role-faithful"
    if "Traitor" in pdata["role"]:
        return f"🗡️ {pdata['role'].upper()}", "role-traitor"
    return "🕯️ Faithful", "role-faithful"

def compute_superlatives(state):
    all_traitors = {n for n, d in state["players"].items() if "Traitor" in d["role"]}
    detective_scores = {n: 0 for n, d in state["players"].items() if "Traitor" not in d["role"]}
    votes_against = {n: 0 for n in state["players"]}

    for d_votes in state["votes"].values():
        for voter, vdata in d_votes.items():
            target = vdata["target"]
            if target in votes_against:
                votes_against[target] += 1
            if voter in detective_scores and target in all_traitors:
                detective_scores[voter] += 1

    best_detective = max(detective_scores.items(), key=lambda x: x[1]) if detective_scores else ("None", 0)
    scapegoat = max(votes_against.items(), key=lambda x: x[1]) if votes_against else ("None", 0)
    stealth_traitor = min(
        ((n, votes_against[n]) for n in all_traitors),
        key=lambda x: x[1],
        default=("None", 0)
    )
    return best_detective, scapegoat, stealth_traitor

# ==========================================
# SIDEBAR NAVIGATION & METRICS
# ==========================================
st.sidebar.title("🕯️ THE CASTLE")
st.sidebar.markdown(f"**High Host:** Neilio 👑")
st.sidebar.markdown(f"**Current Day:** Day {state['current_day']} of 10")
st.sidebar.markdown(f"**Current Phase:** `{state['phase']}`")

alive_count = sum(1 for p in state["players"].values() if p["status"] == "Alive")
st.sidebar.metric("🟢 Survivors in Castle", f"{alive_count} / {len(state['players'])}")
st.sidebar.metric("🏆 Faithful Prize Pot", f"{state['prize_pot']} pts")

st.sidebar.divider()
nav_options = [
    "🏰 Castle Hall (Public)",
    "🗳️ Player Portal (Vote & Role)",
    "📊 The Voting Matrix",
    "🏆 The Grand Reveal (4PM Finale)",
    "👑 Host Control (Neilio)"
]
nav = st.sidebar.radio("Navigate", nav_options)

# ==========================================
# TAB 1: CASTLE HALL
# ==========================================
if nav == "🏰 Castle Hall (Public)":
    st.title("🏰 The Great Hall of Shadows")
    st.info(f"📢 **DECREE FROM HOST NEILIO:** {state['headline']}")

    if is_finale_unlocked:
        st.success("🏆 **THE GRAND FINALE IS LIVE!** Click **'🏆 The Grand Reveal (4PM Finale)'** in the sidebar to see who won and unmask every player!")
    elif state["phase"] == "The Fire Pit (Endgame)":
        st.error(f"🔥 **THE FIRE PIT IS LIT (Round {state['fire_pit_round']})!** Head to the Player Portal to cast your final pouch.")

    with st.expander("📜 Today's Daily Mission / Castle Decrees", expanded=True):
        st.markdown(state["mission_text"])

    st.subheader("🖼️ Portraits on the Great Hall Wall")
    players_list = list(state["players"].items())
    cols = st.columns(5)

    for idx, (name, pdata) in enumerate(players_list):
        col = cols[idx % 5]
        status = pdata["status"]
        
        if status == "Alive":
            shield_badge = " 🛡️" if pdata.get("public_shield") else ""
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card">
                <div style="font-size: 28px;">🛡️{shield_badge}</div>
                <div style="font-weight: bold; font-size: 16px; margin-top: 4px; color: #ffffff;">{name}</div>
                <div style="color: #5bc0be; font-size: 13px;">🟢 In the Castle</div>
                <div class="{role_class}" style="font-size: 12px; margin-top: 4px;">Identity: {revealed_role}</div>
            </div>
            """
        else:
            icon = "💀" if status == "Murdered" else "🔴"
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card player-dead">
                <div style="font-size: 28px;">{icon}</div>
                <div style="font-weight: bold; font-size: 16px; margin-top: 4px; text-decoration: line-through; color: #d1cbd5;">{name}</div>
                <div style="font-size: 13px; color: #b3aca1;">{status} ({pdata['eliminated_day']})</div>
                <div class="{role_class}" style="font-size: 12px; margin-top: 4px;">{revealed_role}</div>
            </div>
            """
        col.markdown(card_html, unsafe_allow_html=True)

# ==========================================
# TAB 2: PLAYER PORTAL
# ==========================================
elif nav == "🗳️ Player Portal (Vote & Role)":
    st.title("🗝️ The Secret Chamber Portal")
    st.caption("Select your name and enter your personal 4-digit PIN to consult the shadows, inspect for Shields, or cast your ballot.")

    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Select Your Name", list(state["players"].keys()))
    entered_pin = col2.text_input("Enter Your 4-Digit PIN", type="password")

    if entered_pin:
        p_info = state["players"][selected_player]
        if entered_pin != p_info["pin"]:
            st.error("❌ Incorrect PIN. Speak in whispers with Host Neilio if you forgot your credentials.")
        else:
            st.success(f"Welcome back to the shadows, **{selected_player}**.")
            
            r_col1, r_col2, r_col3 = st.columns(3)
            r_col1.metric("Your Secret Role", f"🗡️ {p_info['role']}" if "Traitor" in p_info["role"] else "🕯️ Faithful")
            r_col2.metric("Current Status", p_info["status"])
            r_col3.metric("Protected by Shield Tonight?", "🛡️ YES" if p_info["shield"] else "No")

            st.divider()

            if state["phase"] == "The Fire Pit (Endgame)":
                st.subheader(f"🔥 The Fire Pit of Truth — {fp_key}")
                if p_info["status"] != "Alive":
                    st.warning("👻 Only surviving finalists stand before the Fire Pit flames!")
                else:
                    st.markdown(
                        "Throw **🟢 END GAME** if you believe only Faithfuls remain (or if you are a Traitor ready to steal the pot!). "
                        "If **even one player** throws **🔴 BANISH AGAIN**, the group must immediately face another Banishment vote."
                    )
                    existing_fp = state["fire_pit_votes"].get(fp_key, {}).get(selected_player, {})
                    
                    with st.form("fire_pit_form"):
                        fp_choice = st.radio(
                            "Choose your pouch to cast into the fire:",
                            ["🟢 END GAME", "🔴 BANISH AGAIN"],
                            index=0 if existing_fp.get("choice", "🟢 END GAME") == "🟢 END GAME" else 1
                        )
                        fp_reason = st.text_input(
                            "1-Sentence Final Statement (read aloud as the flames shift):",
                            value=existing_fp.get("reason", "")
                        )
                        fp_submit = st.form_submit_button("Throw Pouch into the Flames 🔥")
                        if fp_submit:
                            if not fp_reason.strip():
                                st.error("Please add a 1-sentence reason for your pouch choice!")
                            else:
                                state["fire_pit_votes"].setdefault(fp_key, {})[selected_player] = {
                                    "choice": fp_choice,
                                    "reason": fp_reason.strip(),
                                    "timestamp": datetime.now().strftime("%H:%M")
                                }
                                save_state(state)
                                st.success(f"✅ Your **{fp_choice}** pouch is locked in for {fp_key}!")
            else:
                st.subheader(f"🗳️ Round Table Ballot ({day_key})")
                if p_info["status"] != "Alive":
                    st.warning("👻 Ghosts cannot cast votes at the Round Table!")
                elif state["phase"] != "Round Table Voting":
                    st.info(f"The Round Table ballot box is currently sealed (Current Phase: **

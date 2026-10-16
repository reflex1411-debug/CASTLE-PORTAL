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
        for

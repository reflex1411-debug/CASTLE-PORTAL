import streamlit as st
import pandas as pd
import json
import os
import base64
import random
from datetime import datetime

# ==========================================
# PAGE CONFIG & PARCHMENT CASTLE STYLING
# ==========================================
st.set_page_config(
    page_title="The Traitors: The Castle",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global App Background - Warm Parchment & Dark Readable Text */
    .stApp {
        background-color: #f6f1e7 !important;
        color: #2c2a29 !important;
    }
    
    /* Ensure all general markdown and text is dark and readable */
    .stMarkdown, p, span, label, div {
        color: #2c2a29 !important;
    }
    
    /* Sidebar Styling - Aged Scroll */
    [data-testid="stSidebar"] {
        background-color: #ebdccb !important;
        border-right: 2px solid #c5a059;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #2c2a29 !important;
    }

    /* Gothic Typography & Headers - Rich Burgundy */
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        color: #5c1d1d !important;
        letter-spacing: 1px;
    }

    /* Player Cards - Crisp White Parchment Plaques */
    .player-card {
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 14px;
        text-align: center;
        border: 2px solid #c5a059;
        background: #ffffff;
        color: #2c2a29 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        position: relative;
    }
    .player-card div {
        color: #2c2a29 !important;
    }
    
    /* Murdered / Dead Player Card Overlays with Blood-Red Cross */
    .player-card-dead {
        position: relative;
        border: 2px solid #5c1d1d;
        background: #d4cfc5;
        opacity: 0.85;
        filter: grayscale(70%);
    }
    .blood-cross {
        position: absolute;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 58px;
        color: #b30000;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
        pointer-events: none;
        z-index: 5;
    }
    
    /* Grand Finale Banners */
    .finale-banner-traitor {
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        background: #5c1d1d;
        border: 3px solid #380808;
        color: #ffffff;
        margin-bottom: 24px;
    }
    .finale-banner-traitor h1, .finale-banner-traitor p {
        color: #ffffff !important;
    }
    .finale-banner-faithful {
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        background: #1b4d3e;
        border: 3px solid #c5a059;
        color: #ffffff;
        margin-bottom: 24px;
    }
    .finale-banner-faithful h1, .finale-banner-faithful p {
        color: #ffffff !important;
    }
    
    /* Award Plaques */
    .award-card {
        border-radius: 6px;
        padding: 20px;
        background: #ffffff;
        border: 2px solid #c5a059;
        text-align: center;
        color: #2c2a29 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .award-card div {
        color: #2c2a29 !important;
    }

    /* Role Highlights */
    .role-traitor {
        color: #b30000 !important;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .role-faithful {
        color: #006666 !important;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .role-hidden {
        color: #b36b00 !important;
        font-weight: bold;
    }

    /* Streamlit Form & Input Styling Overrides */
    .stTextInput input, .stSelectbox select {
        background-color: #ffffff !important;
        color: #2c2a29 !important;
        border: 1px solid #c5a059 !important;
    }
    .stButton button {
        background: linear-gradient(180deg, #c5a059 0%, #9e7b34 100%) !important;
        color: #ffffff !important;
        font-weight: bold;
        border: 1px solid #7d6126 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    .stButton button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #b38f42 100%) !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA PERSISTENCE & HOST CONFIG
# ==========================================
DATA_FILE = "castle_state.json"
BACKUP_FILE = "castle_state_backup.json"
HOST_PIN = "1411"  # Host Neilio's PIN

PHASES = [
    "Breakfast & Launch",
    "24-Hour Asynchronous Window",
    "Round Table Voting",
    "The Fire Pit (Endgame)",
    "Overnight (Turret)",
    "🏆 The Grand Reveal (Finale)"
]

def get_default_state():
    default_players = {}
    for i in range(1, 21):  # Configured for exactly 20 Players!
        name = f"Player {i:02d}"
        random_pin = str(random.randint(1000, 9999))  # Random secure 4-digit PIN generator
        default_players[name] = {
            "pin": random_pin,
            "role": "Faithful",  # Everyone starts as Faithful by default! Neilio assigns Traitors later.
            "status": "Alive",
            "eliminated_day": "",
            "shield": False,
            "public_shield": False,
            "hide_role": False,
            "photo": ""
        }
    return {
        "current_day": 1,
        "fire_pit_round": 1,
        "phase": "24-Hour Asynchronous Window",
        "prize_pot": 100,
        "traitor_pot": 0,
        "headline": "Welcome to Neilio's Castle! The 24-hour asynchronous window is open. Check your role and vote whenever you have a break.",
        "mission_text": "🏆 **MISSION 1: TWO TRUTHS & AN ALIBI**\nPost two true facts and one lie in the WhatsApp chat over the next 24 hours!",
        "players": default_players,
        "votes": {},
        "fire_pit_votes": {},
        "turret_nominations": {},
        "unanimous_murder": {},
        "vault_winners": {},
        "vault_attempts": {},
        "vault_riddle_solved": {},
        "vault_riddles": {
            "Day 1": {
                "question": "I have multiple faces, but I hide my breath. One holds salvation, the rest hold emptiness. To touch the iron doors and test your fate, you must first name the symbol of my estate. What word am I, spoken when the dandelions blow?",
                "answer": "wish"
            }
        }
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
    state.setdefault("turret_nominations", {})
    state.setdefault("unanimous_murder", {})
    state.setdefault("vault_winners", {})
    state.setdefault("vault_attempts", {})
    state.setdefault("vault_riddle_solved", {})
    state.setdefault("vault_riddles", {
        "Day 1": {
            "question": "I have multiple faces, but I hide my breath. One holds salvation, the rest hold emptiness. To touch the iron doors and test your fate, you must first name the symbol of my estate. What word am I, spoken when the dandelions blow?",
            "answer": "wish"
        }
    })
    for p in state.get("players", {}).values():
        p.setdefault("hide_role", False)
        p.setdefault("public_shield", False)
        p.setdefault("photo", "")
        p.setdefault("role", "Faithful")
    return state

def save_state(state):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            current_data = f.read()
        with open(BACKUP_FILE, "w") as f:
            f.write(current_data)
            
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

def render_player_portal_view(selected_player):
    """Renders the complete player portal interface (Faithful/Traitor/Turret/Vault view) for any selected user."""
    p_info = state["players"][selected_player]
    st.success(f"Viewing portal as: **{selected_player}**")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Secret Role", f"🗡️ {p_info['role']}" if "Traitor" in p_info["role"] else "🕯️ Faithful")
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
            
            with st.form(f"fire_pit_form_{selected_player}"):
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
    elif state["phase"] == "Round Table Voting":
        st.subheader(f"🗳️ Round Table Ballot ({day_key})")
        if p_info["status"] != "Alive":
            st.warning("👻 Ghosts cannot cast votes at the Round Table!")
        else:
            alive_targets = [
                name for name, d in state["players"].items() 
                if d["status"] == "Alive" and name != selected_player
            ]
            existing_vote = state["votes"].get(day_key, {}).get(selected_player, {})
            
            if existing_vote:
                st.info("ℹ️ You have already cast a vote today. Submitting again will update your ballot.")

            with st.form(f"vote_form_{selected_player}"):
                target = st.selectbox(
                    "Who are you voting to BANISH from the Castle?", 
                    alive_targets,
                    index=alive_targets.index(existing_vote["target"]) if existing_vote.get("target") in alive_targets else 0
                )
                reason = st.text_input(
                    "1-Sentence Accusation (read aloud at Breakfast):",
                    value=existing_vote.get("reason", "")
                )
                submitted = st.form_submit_button("Seal My Fate & Lock In Vote 🕯️")
                if submitted:
                    if not reason.strip():
                        st.error("Please provide a short 1-sentence reason for your vote!")
                    else:
                        state["votes"].setdefault(day_key, {})[selected_player] = {
                            "target": target,
                            "reason": reason.strip(),
                            "timestamp": datetime.now().strftime("%H:%M")
                        }
                        save_state(state)
                        st.success(f"✅ Your vote to banish **{target}** has been recorded in the shadows.")
    else:
        st.subheader("🗳️ Round Table Ballot")
        st.info("🔒 **The Round Table is currently sealed.** High Host Neilio has not yet decreed that voting is open. Stand by in the Great Hall!")

    # --- VAULT OF SAFETY DEPOSIT BOXES CHALLENGE ---
    st.divider()
    st.subheader("🏦 The Vault of Safety Deposit Boxes")
    alive_count = sum(1 for d in state["players"].values() if d["status"] == "Alive")
    total_boxes = alive_count * 3
    
    if day_key not in state["vault_winners"]:
        state["vault_winners"][day_key] = random.randint(1, total_boxes)
        save_state(state)
    
    winning_box = state["vault_winners"][day_key]
    riddle_solved_dict = state["vault_riddle_solved"].setdefault(day_key, {})
    attempts_dict = state["vault_attempts"].setdefault(day_key, {})
    
    has_solved_riddle = riddle_solved_dict.get(selected_player, False)
    has_attempted_today = attempts_dict.get(selected_player, False)

    # Fetch daily riddle set by Host
    daily_riddle_data = state["vault_riddles"].get(day_key, {
        "question": "Solve the riddle to gain access to the Safety Deposit Boxes.",
        "answer": "wish"
    })

    if p_info["status"] != "Alive":
        st.warning("👻 Ghosts cannot tamper with the Safety Deposit Vault!")
    else:
        st.markdown(f"**Total Deposit Boxes Active Today:** `{total_boxes}` (3x surviving players)")
        
        if p_info["shield"]:
            st.success("🛡️ You already hold a Shield in your possession! The vault doors remain closed to you today.")
        elif has_attempted_today:
            st.info("ℹ️ You have already tested your luck at the Safety Deposit Vault today. Return tomorrow!")
        else:
            if not has_solved_riddle:
                st.markdown("### 🧩 Step 1: Solve the Gatekeeper Riddle")
                st.markdown(f"> *\"{daily_riddle_data['question']}\"*")
                with st.form(f"riddle_form_{selected_player}"):
                    riddle_answer = st.text_input("Enter the secret password / word:")
                    riddle_submit = st.form_submit_button("Submit Riddle Answer 🗝️")
                    if riddle_submit:
                        clean_ans = riddle_answer.strip().lower()
                        correct_ans = daily_riddle_data["answer"].strip().lower()
                        if clean_ans == correct_ans or clean_ans in [a.strip() for a in correct_ans.split(",")]:
                            state["vault_riddle_solved"].setdefault(day_key, {})[selected_player] = True
                            save_state(state)
                            st.success("🔓 Correct! The gatekeeper unlocks access to the Safety Deposit Boxes.")
                            st.rerun()
                        else:
                            st.error("❌ Incorrect answer. The vault remains sealed. Consult the whispers in the Castle and try again.")
            else:
                st.success("🔓 Gatekeeper Riddle Solved! You have 1 Key to open one Safety Deposit Box.")
                st.markdown("### 🏦 Step 2: Choose Your Box (1 to {})".format(total_boxes))
                
                with st.form(f"vault_box_form_{selected_player}"):
                    chosen_box = st.number_input("Select Box Number:", min_value=1, max_value=total_boxes, value=1, step=1)
                    box_submit = st.form_submit_button("Open Box 📦")
                    if box_submit:
                        state["vault_attempts"].setdefault(day_key, {})[selected_player] = True
                        if chosen_box == winning_box:
                            state["players"][selected_player]["shield"] = True
                            save_state(state)
                            st.balloons()
                            st.success(f"🎉 INCREDIBLE! Box #{chosen_box} contained the **Shield**! You are protected tonight.")
                        else:
                            save_state(state)
                            st.error(f"💀 Box #{chosen_box} swings open... but it is completely empty. Better luck next time, Faithful.")
                        st.rerun()

    # --- TRAITOR TURRET ACCESS SECTION ---
    if "Traitor" in p_info["role"] and p_info["status"] == "Alive":
        st.divider()
        st.subheader("🗡️ The Traitors' Turret (Secret Access)")
        fellow_traitors = [
            n for n, d in state["players"].items() 
            if "Traitor" in d["role"] and d["status"] == "Alive"
        ]
        st.markdown(f"**Surviving Traitors in the Turret:** {', '.join(fellow_traitors)} | **Traitor Pot:** `{state['traitor_pot']} pts`")
        
        faithful_targets = [
            n for n, d in state["players"].items()
            if "Traitor" not in d["role"] and d["status"] == "Alive" and not d.get("public_shield")
        ]
        
        turret_noms = state["turret_nominations"].get(day_key, {})
        if turret_noms:
            st.markdown("---")
            st.write("📜 **Traitor Discussion Board (All Nominees):**")
            for t_name, choices in turret_noms.items():
                st.write(f"• 🗡️ **{t_name}**'s 3 choices: **1st:** {choices.get('1st', '—')} | **2nd:** {choices.get('2nd', '—')} | **3rd:** {choices.get('3rd', '—')}")

        existing_user_noms = turret_noms.get(selected_player, {})
        with st.form(f"turret_noms_form_{selected_player}"):
            st.markdown("### 🎯 Submit Your Top 3 Murder Preferences")
            st.caption("Select up to 3 possible Faithful victims in order of priority for tonight's discussion.")
            
            def_1st = existing_user_noms.get("1st", faithful_targets[0] if faithful_targets else "")
            def_2nd = existing_user_noms.get("2nd", faithful_targets[1] if len(faithful_targets) > 1 else (faithful_targets[0] if faithful_targets else ""))
            def_3rd = existing_user_noms.get("3rd", faithful_targets[2] if len(faithful_targets) > 2 else (faithful_targets[0] if faithful_targets else ""))

            opt_1st = st.selectbox("1st Choice (Top Target):", faithful_targets, index=faithful_targets.index(def_1st) if def_1st in faithful_targets else 0)
            opt_2nd = st.selectbox("2nd Choice (Backup Target):", faithful_targets, index=faithful_targets.index(def_2nd) if def_2nd in faithful_targets else 0)
            opt_3rd = st.selectbox("3rd Choice (Third Option):", faithful_targets, index=faithful_targets.index(def_3rd) if def_3rd in faithful_targets else 0)
            
            submit_noms = st.form_submit_button("Lock In My Top 3 Choices 🩸")
            if submit_noms:
                state["turret_nominations"].setdefault(day_key, {})[selected_player] = {
                    "1st": opt_1st,
                    "2nd": opt_2nd,
                    "3rd": opt_3rd
                }
                save_state(state)
                st.success("✅ Your 3 target preferences have been shared with your fellow Traitors in the Turret.")
                st.rerun()

        st.markdown("---")
        st.subheader("⚖️ Unanimous Murder Decree")
        current_murder = state["unanimous_murder"].get(day_key, "")
        if current_murder:
            st.error(f"🩸 **UNANIMOUS MURDER LOCKED IN:** **{current_murder}** will not see the light of breakfast tomorrow!")
        
        if faithful_targets:
            unanimous_choice = st.selectbox("Select Unanimous Murder Victim (Agreed upon by Traitors):", faithful_targets, key=f"unanimous_sel_{selected_player}")
            col_lock, col_reset = st.columns(2)
            if col_lock.button("🔒 Lock In Unanimous Murder Victim 💀", key=f"lock_murder_{selected_player}"):
                state["unanimous_murder"][day_key] = unanimous_choice
                save_state(state)
                st.success(f"🩸 Murder decree sealed! **{unanimous_choice}** has been marked for death.")
                st.rerun()
            if col_reset.button("🔄 Emergency Reset Turret", key=f"reset_turret_{selected_player}"):
                if day_key in state["turret_nominations"]:
                    del state["turret_nominations"][day_key]
                if day_key in state["unanimous_murder"]:
                    del state["unanimous_murder"][day_key]
                save_state(state)
                st.warning("⚠️ Turret nominations and unanimous murder choice have been reset for tonight.")
                st.rerun()

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

    with st.expander("📜 Today's Daily Mission / Asynchronous Rules", expanded=True):
        st.markdown(state["mission_text"])

    st.subheader("🖼️ Portraits on the Great Hall Wall")
    players_list = list(state["players"].items())
    cols = st.columns(5)

    for idx, (name, pdata) in enumerate(players_list):
        col = cols[idx % 5]
        status = pdata["status"]
        photo_url = pdata.get("photo", "")
        
        if photo_url:
            avatar_display = f'<img src="{photo_url}" style="width: 55px; height: 55px; border-radius: 50%; object-fit: cover; border: 2px solid #c5a059; margin-bottom: 4px;" />'
        else:
            avatar_display = '<div style="font-size: 26px;">🛡️</div>'

        if status == "Alive":
            shield_badge = " 🛡️" if pdata.get("public_shield") else ""
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card">
                {avatar_display}
                <div style="font-weight: bold; font-size: 15px; margin-top: 2px; color: #2c2a29;">{name}{shield_badge}</div>
                <div style="color: #006666; font-size: 12px;">🟢 In the Castle</div>
                <div class="{role_class}" style="font-size: 11px; margin-top: 2px;">Identity: {revealed_role}</div>
            </div>
            """
        else:
            icon = "💀" if status == "Murdered" else "🔴"
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card player-card-dead">
                <div class="blood-cross">❌</div>
                {avatar_display}
                <div style="font-weight: bold; font-size: 15px; margin-top: 2px; text-decoration: line-through; color: #5c1d1d;">{name}</div>
                <div style="font-size: 12px; color: #5c1d1d; font-weight: bold;">{status} ({pdata['eliminated_day']})</div>
                <div class="{role_class}" style="font-size: 11px; margin-top: 2px;">{revealed_role}</div>
            </div>
            """
        col.markdown(card_html, unsafe_allow_html=True)

# ==========================================
# TAB 2: PLAYER PORTAL
# ==========================================
elif nav == "🗳️ Player Portal (Vote & Role)":
    st.title("🗝️ The Secret Chamber Portal")
    st.caption("Select your name and enter your personal 4-digit PIN to consult the shadows, inspect for Shields, or cast your ballot within the 24-hour window.")

    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Select Your Name", list(state["players"].keys()))
    entered_pin = col2.text_input("Enter Your 4-Digit PIN", type="password")

    if entered_pin:
        p_info = state["players"][selected_player]
        if entered_pin != p_info["pin"]:
            st.error("❌ Incorrect PIN. Speak in whispers with Host Neilio if you forgot your credentials.")
        else:
            st.success(f"Welcome back to the shadows, **{selected_player}**.")
            
            # --- UPLOAD PROFILE PHOTO SECTION ---
            with st.expander("📸 Upload or Update Your Profile Photo", expanded=False):
                uploaded_file = st.file_uploader("Choose a photo of yourself (JPEG/PNG)", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    bytes_data = uploaded_file.getvalue()
                    base64_encoded = base64.b64encode(bytes_data).decode("utf-8")
                    p_info["photo"] = f"data:image/jpeg;base64,{base64_encoded}"
                    save_state(state)
                    st.success("✨ Your portrait has been hung in the Great Hall!")
                    st.rerun()
                if p_info.get("photo"):
                    st.image(p_info["photo"], width=100, caption="Current Portrait")

            render_player_portal_view(selected_player)

# ==========================================
# TAB 3: VOTING MATRIX
# ==========================================
elif nav == "📊 The Voting Matrix":
    st.title("📊 The Castle Archives: Voting Matrix")
    st.caption("Every asynchronous ballot cast since day one. Votes against exposed Traitors are marked with 🎯.")

    known_traitors = {
        name for name, d in state["players"].items()
        if "Traitor" in d["role"] and (is_finale_unlocked or (d["status"] == "Banished" and not d.get("hide_role", False)))
    }

    all_days = sorted(state["votes"].keys(), key=lambda x: int(x.split(" ")[1]))
    rows = []
    for name, pdata in state["players"].items():
        status = pdata["status"]
        identity, _ = get_public_identity(pdata, force_reveal=is_finale_unlocked)

        row = {
            "Player": name,
            "Status": f"🟢 Alive" if status == "Alive" else f"{'💀' if status=='Murdered' else '🔴'} {status} ({pdata['eliminated_day']})",
            "Revealed Identity": identity
        }
        
        total_votes_received = 0
        for d in all_days:
            day_votes = state["votes"].get(d, {})
            total_votes_received += sum(1 for v in day_votes.values() if v["target"] == name)
            
            if name in day_votes:
                voted_for = day_votes[name]["target"]
                row[d] = f"🎯 {voted_for}" if voted_for in known_traitors else voted_for
            else:
                row[d] = "—"
        
        row["Total Votes Against"] = total_votes_received
        rows.append(row)

    df_matrix = pd.DataFrame(rows)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)

# ==========================================
# TAB 4: THE GRAND REVEAL (FINALE)
# ==========================================
elif nav == "🏆 The Grand Reveal (4PM Finale)":
    st.title("🏆 The Grand Finale & Ultimate Reveal")

    if not is_finale_unlocked:
        st.warning("🔒 **THE GRAND REVEAL CHAMBER IS SEALED!**")
        st.markdown(
            "Gather close to the Fire Pit. Host Neilio will shatter the seal at **16:00 on Finale Friday** "
            "once the final pouches have been thrown."
        )
    else:
        survivors = {n: d for n, d in state["players"].items() if d["status"] == "Alive"}
        surviving_traitors = [n for n, d in survivors.items() if "Traitor" in d["role"]]
        surviving_faithfuls = [n for n, d in survivors.items() if "Traitor" not in d["role"]]

        if surviving_traitors:
            st.snow()
            winner_names = ", ".join(surviving_traitors)
            st.markdown(f"""
            <div class="finale-banner-traitor">
                <h1 style="margin:0; font-size: 38px;">🗡️ THE TRAITORS HAVE CONQUERED! 🗡️</h1>
                <p style="font-size: 20px; margin-top: 10px;">
                    Deception triumphs in the shadows! <b>{winner_names}</b> survived the Fire Pit undetected and stole the entire <b>{state['prize_pot']} pt</b> Prize Pot!
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.balloons()
            winner_names = ", ".join(surviving_faithfuls)
            st.markdown(f"""
            <div class="finale-banner-faithful">
                <h1 style="margin:0; font-size: 38px;">🕯️ TRIUMPH OF THE FAITHFULS! 🕯️</h1>
                <p style="font-size: 20px; margin-top: 10px;">
                    Every single Traitor was purged from the Castle! <b>{winner_names}</b> stand victorious and share the <b>{state['prize_pot']} pt</b> Prize Pot!
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("🔥 The Fire Pit Finalists — Unmasked")
        f_cols = st.columns(max(len(survivors), 1))
        for idx, (name, d) in enumerate(survivors.items()):
            is_t = "Traitor" in d["role"]
            badge = "🗡️ TRAITOR" if is_t else "🕯️ FAITHFUL"
            role_cls = "role-traitor" if is_t else "role-faithful"
            f_cols[idx].markdown(f"""
            <div class="player-card">
                <div style="font-size: 34px;">{'😈' if is_t else '😇'}</div>
                <div style="font-weight: bold; font-size: 18px; margin-top: 6px; color: #2c2a29;">{name}</div>
                <div class="{role_cls}" style="font-size: 16px; margin-top: 6px;">{badge}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.subheader("🗡️ Complete Roll Call of the Traitors")
        all_traitors = [(n, d) for n, d in state["players"].items() if "Traitor" in d["role"]]
        t_cols = st.columns(max(len(all_traitors), 1))
        for idx, (t_name, t_data) in enumerate(all_traitors):
            fate = "🏆 SURVIVED TO THE END" if t_data["status"] == "Alive" else f"🔴 Banished ({t_data['eliminated_day']})"
            t_cols[idx].markdown(f"""
            <div class="award-card">
                <div style="font-size: 24px; color: #2c2a29;">🗡️ <b>{t_name}</b></div>
                <div style="color: #b30000; font-size: 14px; margin-top: 4px;">{t_data['role']}</div>
                <div style="color: #7a756b; font-size: 13px; margin-top: 6px;">{fate}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.subheader("🏅 Official Castle Honours & Superlatives")
        best_detective, scapegoat, stealth_traitor = compute_superlatives(state)
        a_col1, a_col2, a_col3 = st.columns(3)

        a_col1.markdown(f"""
        <div class="award-card">
            <div style="font-size: 28px;">🕵️‍♂️</div>
            <div style="font-weight: bold; color: #7a5914;">Chief Castle Detective</div>
            <div style="font-size: 20px; margin: 6px 0; color: #2c2a29;"><b>{best_detective[0]}</b></div>
            <div style="font-size: 13px; color: #7a756b;">Cast <b>{best_detective[1]}</b> ballot(s) directly against Traitors!</div>
        </div>
        """, unsafe_allow_html=True)

        a_col2.markdown(f"""
        <div class="award-card">
            <div style="font-size: 28px;">🐐</div>
            <div style="font-weight: bold; color: #7a5914;">The Ultimate Scapegoat</div>
            <div style="font-size: 20px; margin: 6px 0; color: #2c2a29;"><b>{scapegoat[0]}</b></div>
            <div style="font-size: 13px; color: #7a756b;">Endured <b>{scapegoat[1]}</b> Round Table votes across the game!</div>
        </div>
        """, unsafe_allow_html=True)

        a_col3.markdown(f"""
        <div class="award-card">
            <div style="font-size: 28px;">🎭</div>
            <div style="font-weight: bold; color: #7a5914;">Master of the Shadows</div>
            <div style="font-size: 20px; margin: 6px 0; color: #2c2a29;"><b>{stealth_traitor[0]}</b></div>
            <div style="font-size: 13px; color: #7a756b;">Traitor with only <b>{stealth_traitor[1]}</b> vote(s) against them!</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 5: HOST CONTROL CENTRE
# ==========================================
elif nav == "👑 Host Control (Neilio)":
    st.title("👑 Neilio's High Host Sanctuary")
    admin_pin = st.text_input("Enter Host Master PIN", type="password")
    
    if admin_pin == HOST_PIN:
        st.success("Sanctuary unlocked. Welcome back, High Host Neilio.")
        
        # --- HOST GOD-MODE VIEW (FAITHFUL, TRAITOR & TURRET ACCESS) ---
        st.markdown("---")
        st.subheader("👁️ Host All-Seeing Eye: Faithful, Traitor & Turret Access")
        st.caption("Select any player below to preview their exact portal view (Faithful or Traitor) and access the Turret with the exact same view and controls as the Traitors.")
        
        god_mode_player = st.selectbox("Select Player Perspective to Preview:", list(state["players"].keys()), key="god_mode_select")
        with st.expander(f"🔮 Active Viewport Preview: {god_mode_player}", expanded=True):
            render_player_portal_view(god_mode_player)
        st.markdown("---")
        
        # --- THE MASTER TREACHERY SWITCH ---
        st.subheader("⚔️ Master Game Launch Control")
        col_launch1, col_launch2 = st.columns([2, 1])
        with col_launch1:
            st.markdown("Ready to unleash the Traitors? Click this button to officially open Day 1 and broadcast the asynchronous decree to the entire Castle.")
        with col_launch2:
            if st.button("🔥 Let the Treachery Begin!", type="primary"):
                state["current_day"] = 1
                state["phase"] = "24-Hour Asynchronous Window"
                state["headline"] = "The Castle gates are officially open... Let the treachery begin!"
                save_state(state)
                st.balloons()
                st.success("🔥 The game is LIVE! The asynchronous window is open.")
                st.rerun()
        st.markdown("---")

        st.subheader("1. Game Day, Phase & Castle Decrees")
        c1, c2, c3, c4 = st.columns(4)
        new_day = c1.number_input("Current Day (1-12)", min_value=1, max_value=12, value=state["current_day"])
        new_phase = c2.selectbox(
            "Current Phase", 
            PHASES,
            index=PHASES.index(state["phase"]) if state["phase"] in PHASES else 0
        )
        new_fp_round = c3.number_input("Fire Pit Round", min_value=1, max_value=5, value=state.get("fire_pit_round", 1))
        new_pot = c4.number_input("Faithful Prize Pot", value=state["prize_pot"], step=50)
        
        new_headline = st.text_input("Great Hall Banner Headline", value=state["headline"])
        new_mission = st.text_area("Daily Mission / Decree Instructions", value=state["mission_text"])
        
        if st.button("💾 Save Castle State & Decrees"):
            state["current_day"] = new_day
            state["phase"] = new_phase
            state["fire_pit_round"] = new_fp_round
            state["prize_pot"] = new_pot
            state["headline"] = new_headline
            state["mission_text"] = new_mission
            save_state(state)
            st.success("Successful state update!")
            st.rerun()

        st.divider()

        # --- HOST RIDDLE EDITOR FOR SAFETY DEPOSIT VAULT ---
        st.subheader("5. 🧩 Daily Safety Deposit Vault & Riddle Settings")
        st.caption("Set the gatekeeper riddle and correct password for each day's safety deposit box challenge.")
        
        riddle_day_select = st.selectbox("Select Day to Configure Riddle:", [f"Day {i}" for i in range(1, 13)], index=state["current_day"] - 1)
        existing_riddle = state["vault_riddles"].get(riddle_day_select, {"question": "", "answer": ""})
        
        with st.form("host_riddle_form"):
            host_riddle_q = st.text_area("Gatekeeper Riddle Question (Markdown supported):", value=existing_riddle["question"])
            host_riddle_a = st.text_input("Correct Answer / Password (comma separated for multiple):", value=existing_riddle["answer"])
            save_riddle_btn = st.form_submit_button("💾 Save Riddle for " + riddle_day_select)
            if save_riddle_btn:
                state["vault_riddles"].setdefault(riddle_day_select, {})["question"] = host_riddle_q.strip()
                state["vault_riddles"].setdefault(riddle_day_select, {})["answer"] = host_riddle_a.strip().lower()
                save_state(state)
                st.success(f"✅ Riddle successfully updated for {riddle_day_select}!")
                st.rerun()

        st.divider()

        col_rt, col_fp = st.columns(2)
        alive_players = [n for n, d in state["players"].items() if d["status"] == "Alive"]

        with col_rt:
            st.subheader(f"2A. Asynchronous Ballot Tally ({day_key})")
            day_votes = state["votes"].get(day_key, {})
            voted_players = list(day_votes.keys())
            missing_voters = [n for n in alive_players if n not in voted_players]

            st.write(f"**Ballots Cast:** {len(voted_players)} / {len(alive_players)}")
            if missing_voters:
                st.warning(f"⏳ **Still awaiting whispers from:** {', '.join(missing_voters)}")
            
            # --- EMERGENCY VOTE RESET TOOL ---
            with st.expander("🛠️ Emergency Vote Correction"):
                voted_names = list(day_votes.keys())
                if voted_names:
                    player_to_reset = st.selectbox("Select player to clear vote for:", voted_names, key="reset_vote_select")
                    if st.button("🗑️ Clear This Player's Vote"):
                        if player_to_reset in state["votes"].get(day_key, {}):
                            del state["votes"][day_key][player_to_reset]
                            save_state(state)
                            st.success(f"Successfully cleared vote for {player_to_reset}. They can now vote again.")
                            st.rerun()
                else:
                    st.write("No votes cast yet today.")

            if day_votes:
                tally = {}
                whatsapp_lines = [f"🕯️ *ASYNCHRONOUS BALLOTS TALLIED ({day_key.upper()})* — *High Host: Neilio* 🕯️\n"]
                for voter, vdata in day_votes.items():
                    target = vdata["target"]
                    tally[target] = tally.get(target, 0) + 1
                    whatsapp_lines.append(f"• *{voter}* accused *{target}*: _\"{vdata['reason']}\"_")
                
                sorted_tally = sorted(tally.items(), key=lambda x: x[1], reverse=True)
                whatsapp_lines.append("\n📜 *BALLOT TALLY:*")
                for cand, count in sorted_tally:
                    whatsapp_lines.append(f"• *{cand}* : {count} vote(s)")
                
                top_candidate = sorted_tally[0][0]
                if state["current_day"] >= 10:
                    whatsapp_lines.append(f"\n🔴 With the heaviest burden of votes, *{top_candidate}* is banished by High Host Neilio. In the Endgame, true identities remain locked away...")
                else:
                    whatsapp_lines.append(f"\n🔴 With the heaviest burden of votes, *{top_candidate}* is banished by High Host Neilio. Step forward into the light and reveal your true identity...")

                st.code("\n".join(whatsapp_lines), language="markdown")

        with col_fp:
            st.subheader(f"2B. 🔥 Fire Pit & Finale Scripts")
            fp_votes = state["fire_pit_votes"].get(fp_key, {})
            if fp_votes:
                red_count = sum(1 for v in fp_votes.values() if "RED" in v["choice"] or "BANISH" in v["choice"])
                fp_lines = [f"🔥 *THE FIRE PIT OF TRUTH ({fp_key.upper()})* — *High Host: Neilio* 🔥\n"]
                for voter, vdata in fp_votes.items():
                    fp_lines.append(f"• *{voter}* cast *{vdata['choice']}*: _\"{vdata['reason']}\"_")
                
                if red_count > 0:
                    fp_lines.append(f"\n🔴 *THE FLAMES BURN CRIMSON RED!* ({red_count} vote(s) to Banish Again).")
                    fp_lines.append("The end is not yet written! High Host Neilio demands an immediate return to the Round Table.")
                else:
                    fp_lines.append("\n🟢 *THE FLAMES BURN UNANIMOUSLY GOLDEN GREEN!*")
                    fp_lines.append("The reckoning has arrived. High Host Neilio has shattered the seals on the 4PM Grand Reveal screen!")
                st.code("\n".join(fp_lines), language="markdown")

            surviving_traitors = [n for n in alive_players if "Traitor" in state["players"][n]["role"]]
            best_detective, scapegoat, stealth_traitor = compute_superlatives(state)
            finale_lines = ["🏆 *THE GRAND FINALE REVEAL* — *High Host: Neilio* 🏆\n"]
            finale_lines.append("The Fire Pit has spoken under Neilio's vigilant eye. Behold the unmasked survivors:")
            for n in alive_players:
                r = state["players"][n]["role"]
                finale_lines.append(f"• *{n}*: {'🗡️ TRAITOR' if 'Traitor' in r else '🕯️ FAITHFUL'}")
            if surviving_traitors:
                finale_lines.append(f"\n😈 *THE TRAITORS TRIUMPH!* *{', '.join(surviving_traitors)}* deceived the Castle and seized the entire *{state['prize_pot']} pt* Prize Pot!")
            else:
                finale_lines.append(f"\n🕯️ *THE FAITHFULS PREVAIL!* All Traitors were purged, and *{', '.join(alive_players)}* share the *{state['prize_pot']} pt* Prize Pot!")
            finale_lines.append(f"\n🏅 *CASTLE HONOURS:*\n• 🕵️ Chief Detective: *{best_detective[0]}* ({best_detective[1]} Traitor targets)\n• 🐐 Ultimate Scapegoat: *{scapegoat[0]}* ({scapegoat[1]} votes endured)\n• 🎭 Master of the Shadows: *{stealth_traitor[0]}* ({stealth_traitor[1]} votes against)")
            st.caption("👇 Copy this final WhatsApp scroll:")
            st.code("\n".join(finale_lines), language="markdown")

        st.divider()

        st.subheader("3. Manage Players, Roles, Shields & Finale Banishments")
        st.caption("Tip: Use the quick Traitor Crown selector below to instantly assign your secret Traitors, or edit the table directly.")

        # --- QUICK TRAITOR CROWN SELECTOR ---
        all_player_names = list(state["players"].keys())
        current_traitors = [name for name, d in state["players"].items() if "Traitor" in d["role"]]
        
        selected_traitors = st.multiselect(
            "👑 Quick Crown Traitors (Select who will be a Traitor):",
            options=all_player_names,
            default=current_traitors
        )
        
        if st.button("👑 Crown Selected Traitors"):
            for name in all_player_names:
                if name in selected_traitors:
                    state["players"][name]["role"] = "Traitor"
                else:
                    state["players"][name]["role"] = "Faithful"
            save_state(state)
            st.success(f"👑 Traitors successfully crowned: {', '.join(selected_traitors) if selected_traitors else 'None'}")
            st.rerun()

        st.markdown("---")
        st.caption("Detailed Roster Editor:")
        
        roster_rows = []
        for name, d in state["players"].items():
            roster_rows.append({
                "Player Name": name,
                "PIN": d["pin"],
                "Role": d["role"],
                "Status": d["status"],
                "Eliminated On": d["eliminated_day"],
                "Secret Shield": d["shield"],
                "Public Shield": d.get("public_shield", False),
                "Hide Identity (Finale)": d.get("hide_role", False)
            })
        
        edited_df = st.data_editor(
            pd.DataFrame(roster_rows),
            column_config={
                "Role": st.column_config.SelectboxColumn("Role", options=["Faithful", "Traitor", "Recruited Traitor"]),
                "Status": st.column_config.SelectboxColumn("Status", options=["Alive", "Banished", "Murdered"]),
            },
            use_container_width=True,
            hide_index=True
        )

        if st.button("💾 Save Castle Roster"):
            updated_players = {}
            for _, row in edited_df.iterrows():
                player_name = row["Player Name"]
                existing_pdata = state["players"].get(player_name, {})
                
                updated_players[player_name] = {
                    "pin": str(row["PIN"]),
                    "role": row["Role"],
                    "status": row["Status"],
                    "eliminated_day": row["Eliminated On"],
                    "shield": bool(row["Secret Shield"]),
                    "public_shield": bool(row["Public Shield"]),
                    "hide_role": bool(row["Hide Identity (Finale)"]),
                    "photo": existing_pdata.get("photo", "")
                }
            state["players"] = updated_players
            save_state(state)
            st.success("Castle roster updated successfully!")
            st.rerun()

        st.divider()

        st.subheader("4. ☁️ Castle Vault Backup & Restore")
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        
        with b_col1:
            json_bytes = json.dumps(state, indent=4).encode("utf-8")
            st.download_button(
                label=f"⬇️ Download Backup",
                data=json_bytes,
                file_name=f"castle_state_day_{state['current_day']}.json",
                mime="application/json"
            )
            
        with b_col2:
            if st.button("🔄 Restore Last Save"):
                if os.path.exists(BACKUP_FILE):
                    with open(BACKUP_FILE, "r") as f:
                        backup_state = json.load(f)
                    with open(DATA_FILE, "w") as f:
                        json.dump(backup_state, f, indent=4)
                    st.success("✅ Castle restored to last checkpoint!")
                    st.rerun()
                else:
                    st.warning("No backup checkpoint found.")

        with b_col3:
            if st.button("⚠️ Day 1 Defaults"):
                reset_state = get_default_state()
                save_state(reset_state)
                st.warning("Castle reset to Day 1 defaults.")
                st.rerun()

        with b_col4:
            uploaded_file = st.file_uploader("⬆️ Upload JSON", type=["json"], label_visibility="collapsed")
            if uploaded_file is not None:
                if st.button("🔄 Confirm Upload"):
                    restored_state = json.load(uploaded_file)
                    save_state(restored_state)
                    st.success("✅ Vault restored from file!")
                    st.rerun()

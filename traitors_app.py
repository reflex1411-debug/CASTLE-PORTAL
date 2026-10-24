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

    /* Undead / Ghost Card Styling */
    .player-card-undead {
        position: relative;
        border: 2px solid #4a154b;
        background: #e2d9f3;
        opacity: 0.9;
    }
    .undead-ghost {
        position: absolute;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 52px;
        pointer-events: none;
        z-index: 5;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.4));
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
    for i in range(1, 21):
        name = f"Player {i:02d}"
        random_pin = str(random.randint(1000, 9999))
        default_players[name] = {
            "pin": random_pin,
            "role": "Faithful",
            "status": "Alive",
            "eliminated_day": "",
            "shield": False,
            "public_shield": False,
            "hide_role": False,
            "photo": "",
            "points": 0,
            "claimed_items": []
        }

    default_curses = {}
    default_riddles = {}
    for d_num in range(1, 13):
        default_curses[f"Day {d_num}"] = {
            "boxes": ["3", "7", "12", "15", "19"],
            "items": [
                {"name": "Moth-Eaten Spores", "toxicity": "Less Toxic", "target": "All", "desc": "📜 Minor irritation: Lose 25 points from group pot."},
                {"name": "Whispering Chokeweed", "toxicity": "Moderately Toxic", "target": "All", "desc": "🌿 Coughing fit: Lose 50 points from group pot & forced truth at Round Table."},
                {"name": "Turret Venom", "toxicity": "Highly Toxic", "target": "All", "desc": "☠️ Heavy poison: Lose 100 points from group pot & automatically nominated for murder."},
                {"name": "Traitors' Bane", "toxicity": "Traitor-Lethal", "target": "Traitor", "desc": "🗡️ TRAP FOR TRAITORS! If opened by a Traitor, they are instantly eliminated from the Castle!"},
                {"name": "Gorgon's Gaze", "toxicity": "Instant Death", "target": "All", "desc": "⚡ INSTANT DEATH! Whoever opens this cursed box is immediately struck down and murdered!"}
            ]
        }
        default_riddles[f"Day {d_num}"] = {
            "question": f"Day {d_num}: I have multiple faces, but I hide my breath. One holds salvation, the rest hold emptiness. To touch the iron doors and test your fate, you must first name the symbol of my estate. What word am I, spoken when the dandelions blow?",
            "answer": "wish"
        }

    return {
        "current_day": 1,
        "fire_pit_round": 1,
        "phase": "Round Table Voting",
        "prize_pot": 100,
        "traitor_pot": 0,
        "vault_room_open": True,
        "voting_matrix_unlocked": False,
        "traitor_vote_locked": False,
        "chamber_of_relics_locked": True,
        "headline": "Welcome to Neilio's Castle! The Round Table is now in session.",
        "mission_text": "🏆 **MISSION: ROUND TABLE ACCUSATIONS**\nDebate theories and cast your vote before the timer expires!",
        "players": default_players,
        "votes": {},
        "fire_pit_votes": {},
        "turret_nominations": {},
        "unanimous_murder": {},
        "vault_contents": {},
        "vault_attempts": {},
        "vault_riddle_solved": {},
        "vault_recent_open": {},  
        "custom_curses": default_curses,
        "vault_riddles": default_riddles,
        "vault_config": {
            "shields_count": 2,
            "prize_points_value": 25,
            "relics_list": "Rusted Iron Key, Moth-Eaten Tapestry Fragment, Dusty Tome of Spells, Broken Dagger, Empty Urn, Tarnished Silver Chalice, Heavy Iron Shackles"
        },
        "relics_vault_contents": {},
        "relics_config": {},
        # --- ROUND TABLE STATE ---
        "round_table_seating": {},
        "round_table_chat": {},
        "round_table_timers": {},
        "round_table_tie_breaker": {}
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
    state.setdefault("vault_contents", {})
    state.setdefault("vault_attempts", {})
    state.setdefault("vault_riddle_solved", {})
    state.setdefault("vault_recent_open", {})
    state.setdefault("vault_room_open", True)
    state.setdefault("voting_matrix_unlocked", False)
    state.setdefault("traitor_vote_locked", False)
    state.setdefault("chamber_of_relics_locked", True)
    state.setdefault("relics_vault_contents", {})
    state.setdefault("round_table_seating", {})
    state.setdefault("round_table_chat", {})
    state.setdefault("round_table_timers", {})
    state.setdefault("round_table_tie_breaker", {})
    
    default_state = get_default_state()
    state.setdefault("custom_curses", default_state["custom_curses"])
    state.setdefault("vault_riddles", default_state["vault_riddles"])
    state.setdefault("vault_config", default_state["vault_config"])
    state.setdefault("relics_config", default_state["relics_config"])

    for p in state.get("players", {}).values():
        p["role"] = str(p.get("role", "Faithful"))
        p["status"] = str(p.get("status", "Alive"))
        p.setdefault("hide_role", False)
        p.setdefault("public_shield", False)
        p.setdefault("photo", "")
        p.setdefault("points", 0)
        p.setdefault("claimed_items", [])
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
    status = str(pdata.get("status", "Alive"))
    role = str(pdata.get("role", "Faithful"))
    if not force_reveal:
        if status == "Alive":
            return "❓ Unknown", ""
        if pdata.get("hide_role", False):
            return "🔒 Hidden (Finale)", "role-hidden"
        if status in ["Undead", "Murdered", "Banished", "Executed (No Vote Penalty)"]:
            return "🕯️ Faithful", "role-faithful"
    if "Traitor" in role:
        return f"🗡️ {role.upper()}", "role-traitor"
    return "🕯️ Faithful", "role-faithful"

def compute_superlatives(state):
    all_traitors = {n for n, d in state["players"].items() if "Traitor" in str(d.get("role", ""))}
    detective_scores = {n: 0 for n, d in state["players"].items() if "Traitor" not in str(d.get("role", ""))}
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

def initialize_vault_boxes(day_k, total_boxes, config):
    boxes = {}
    box_numbers = list(range(1, total_boxes + 1))
    random.shuffle(box_numbers)
    
    shields_to_assign = min(config.get("shields_count", 2), total_boxes)
    
    day_curse_data = state.get("custom_curses", {}).get(day_k, {"boxes": [], "items": []})
    host_cursed_box_nums = [str(b) for b in day_curse_data.get("boxes", [])]
    host_curse_items = day_curse_data.get("items", [])
    
    relics_pool = [r.strip() for r in config.get("relics_list", "").split(",") if r.strip()]
    if not relics_pool:
        relics_pool = ["Rusted Iron Key", "Dusty Tome of Spells", "Broken Dagger"]

    curse_item_idx = 0
    for i in range(total_boxes):
        b_num = str(box_numbers[i])
        if i < shields_to_assign:
            boxes[b_num] = {"type": "Shield", "desc": "🛡️ A Royal Castle Shield!", "opened": False, "opened_by": ""}
        elif b_num in host_cursed_box_nums and host_curse_items:
            c_item = host_curse_items[curse_item_idx % len(host_curse_items)]
            curse_item_idx += 1
            boxes[b_num] = {
                "type": "Curse", 
                "toxicity": c_item.get("toxicity", "Moderately Toxic"),
                "target_role": c_item.get("target", "All"),
                "desc": f"💀 **{c_item.get('name', 'Cursed Trap')}** ({c_item.get('toxicity', 'Toxic')}): {c_item.get('desc', 'A dark curse strikes!')}", 
                "opened": False, 
                "opened_by": ""
            }
        else:
            if i % 2 == 0:
                pts = config.get("prize_points_value", 25)
                boxes[b_num] = {"type": "Points", "value": pts, "desc": f"✨ {pts} Group Prize Points added!", "opened": False, "opened_by": ""}
            else:
                relic = random.choice(relics_pool)
                boxes[b_num] = {"type": "Relic", "desc": f"📜 A Castle Relic: {relic} (No effect)", "opened": False, "opened_by": ""}
            
    return boxes

def initialize_relics_boxes():
    boxes = {}
    riddles_dict = state["relics_config"].get("riddles", {})
    box_keys = list(riddles_dict.keys())
    for b_key in box_keys:
        r_info = riddles_dict[b_key]
        boxes[b_key] = {
            "name": r_info["name"],
            "clue": r_info["clue"],
            "opened": False,
            "opened_by": ""
        }
    return boxes

def assign_round_table_seats():
    alive_players = [n for n, d in state["players"].items() if str(d.get("status", "Alive")) in ["Alive", "Undead"]]
    random.shuffle(alive_players)
    seating = {}
    for idx, player in enumerate(alive_players, start=1):
        seating[f"Seat {idx}"] = player
    state["round_table_seating"][day_key] = seating
    save_state(state)

def render_player_portal_view(selected_player):
    p_info = state["players"][selected_player]
    role = str(p_info.get("role", "Faithful"))
    status = str(p_info.get("status", "Alive"))
    st.success(f"Viewing portal as: **{selected_player}**")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Secret Role", f"🗡️ {role}" if "Traitor" in role else "🕯️ Faithful")
    r_col2.metric("Current Status", status)
    r_col3.metric("Personal Points", f"{p_info.get('points', 0)} pts")

    st.divider()

    with st.expander("📦 My Claimed Vault Items & Winnings History", expanded=True):
        claimed_list = p_info.get("claimed_items", [])
        if claimed_list:
            st.write("Here is the official record of everything your character has unlocked and won:")
            for item in claimed_list:
                st.write(f"• **{item['time']}** ({item['day']}) — {item['box']}: {item['desc']}")
        else:
            st.info("You haven't opened any Safety Deposit Boxes or Relic Chambers yet today.")

    st.divider()

    if state["phase"] == "The Fire Pit (Endgame)":
        st.subheader(f"🔥 The Fire Pit of Truth — {fp_key}")
        if status != "Alive" and status != "Undead":
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
        if status != "Alive" and status != "Undead":
            st.warning("👻 Ghosts cannot cast votes at the Round Table!")
        else:
            tie_data = state["round_table_tie_breaker"].get(day_key, {})
            is_tie_breaker = tie_data.get("active", False)
            tied_players = tie_data.get("tied_players", [])

            if is_tie_breaker and selected_player in tied_players:
                st.error("⚖️ **SUDDEN DEATH RE-VOTE:** You were tied in the initial ballot and are **barred** from voting in this tie-breaker. Watch from the shadows!")
            else:
                alive_targets = [
                    name for name, d in state["players"].items() 
                    if str(d.get("status", "Alive")) in ["Alive", "Undead"] and name != selected_player
                ]
                
                vote_storage_key = f"{day_key}_tie" if is_tie_breaker else day_key
                existing_vote = state["votes"].get(vote_storage_key, {}).get(selected_player, {})
                
                if existing_vote:
                    st.info("ℹ️ You have already cast your ballot. Submitting again will update your choice.")

                with st.form(f"vote_form_{selected_player}_{vote_storage_key}"):
                    ballot_title = "⚖️ SUDDEN DEATH: Who are you voting to BANISH?" if is_tie_breaker else "Who are you voting to BANISH from the Castle?"
                    target = st.selectbox(ballot_title, alive_targets, index=alive_targets.index(existing_vote["target"]) if existing_vote.get("target") in alive_targets else 0)
                    reason = st.text_input("1-Sentence Accusation / Defense:", value=existing_vote.get("reason", ""))
                    submitted = st.form_submit_button("Seal My Fate & Lock In Vote 🕯️")
                    if submitted:
                        if not reason.strip():
                            st.error("Please provide a short 1-sentence reason!")
                        else:
                            state["votes"].setdefault(vote_storage_key, {})[selected_player] = {
                                "target": target,
                                "reason": reason.strip(),
                                "timestamp": datetime.now().strftime("%H:%M")
                            }
                            save_state(state)
                            st.success(f"✅ Your vote against **{target}** has been recorded.")
    else:
        st.subheader("🗳️ Round Table Ballot")
        st.info("🔒 **The Round Table is currently sealed.** High Host Neilio has not yet decreed that voting is open.")

    # --- VAULT OF SAFETY DEPOSIT BOXES CHALLENGE ---
    st.divider()
    st.subheader("🏦 The Wall of Safety Deposit Boxes")
    
    if not state.get("vault_room_open", True):
        st.warning("🔒 **THE SAFETY DEPOSIT VAULT ROOM IS CURRENTLY LOCKED BY HOST NEILIO.**")
        st.info("Await further instructions or decrees from the Host before attempting to open any boxes.")
        return

    alive_count = sum(1 for d in state["players"].values() if str(d.get("status", "Alive")) in ["Alive", "Undead"])
    total_boxes = alive_count * 3
    
    vault_contents = state["vault_contents"].setdefault(day_key, {})
    if not vault_contents:
        state["vault_contents"][day_key] = initialize_vault_boxes(day_key, total_boxes, state["vault_config"])
        save_state(state)
        vault_contents = state["vault_contents"][day_key]

    riddle_solved_dict = state["vault_riddle_solved"].setdefault(day_key, {})
    attempts_dict = state["vault_attempts"].setdefault(day_key, {})
    
    has_solved_riddle = riddle_solved_dict.get(selected_player, False)
    player_attempts = attempts_dict.get(selected_player, 0)

    daily_riddle_data = state["vault_riddles"].get(day_key, {
        "question": "Solve the riddle to gain access to the Safety Deposit Boxes.",
        "answer": "wish"
    })

    if status != "Alive" and status != "Undead":
        st.warning("👻 Ghosts cannot tamper with the Safety Deposit Vault!")
    else:
        st.markdown(f"**Active Wall:** `{len(vault_contents)}` Deposit Boxes | **Your Attempts Today:** `{player_attempts} / 3 used`")
        
        recent_open = state.get("vault_recent_open", {}).get(selected_player)
        if recent_open and recent_open.get("day") == day_key:
            if recent_open["type"] in ["Shield", "Points"]:
                st.success(f"🎉 **Box #{recent_open['box']} Opened!** {recent_open['desc']}")
            elif recent_open["type"] == "Curse":
                st.error(f"💀 **Box #{recent_open['box']} Opened!** {recent_open['desc']}")
            else:
                st.info(f"📜 **Box #{recent_open['box']} Opened!** {recent_open['desc']}")

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
                        st.success("🔓 Correct! The gatekeeper unlocks the Wall of Safety Deposit Boxes.")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect answer. The vault remains sealed.")
        else:
            st.success("🔓 Gatekeeper Riddle Solved! Select up to 3 closed boxes on the wall.")
            if player_attempts >= 3:
                st.warning("⏳ You have used all 3 of your box selections for today.")
            else:
                cols_per_row = 5
                box_keys = sorted(vault_contents.keys(), key=int)
                for i in range(0, len(box_keys), cols_per_row):
                    row_keys = box_keys[i:i + cols_per_row]
                    cols = st.columns(cols_per_row)
                    for idx, b_key in enumerate(row_keys):
                        b_data = vault_contents[b_key]
                        with cols[idx]:
                            unique_box_btn_key = f"btn_box_{day_key}_{selected_player}_{b_key}"
                            if b_data["opened"]:
                                st.button(f"🔒 #{b_key}\n(Opened)", disabled=True, key=unique_box_btn_key)
                            else:
                                if st.button(f"📦 Box #{b_key}", key=unique_box_btn_key):
                                    if not vault_contents[b_key]["opened"]:
                                        vault_contents[b_key]["opened"] = True
                                        vault_contents[b_key]["opened_by"] = selected_player
                                        state["vault_attempts"].setdefault(day_key, {})[selected_player] = player_attempts + 1
                                        
                                        claim_record = {
                                            "day": day_key,
                                            "box": f"Box #{b_key}",
                                            "desc": b_data["desc"],
                                            "time": datetime.now().strftime("%H:%M")
                                        }
                                        state["players"][selected_player].setdefault("claimed_items", []).append(claim_record)
                                        
                                        state.setdefault("vault_recent_open", {})[selected_player] = {
                                            "day": day_key,
                                            "box": b_key,
                                            "type": b_data["type"],
                                            "desc": b_data["desc"]
                                        }
                                        
                                        if b_data["type"] == "Shield":
                                            state["players"][selected_player]["shield"] = True
                                        elif b_data["type"] == "Points":
                                            pts = b_data["value"]
                                            state["prize_pot"] += pts 
                                        elif b_data["type"] == "Curse":
                                            toxicity = b_data.get("toxicity", "Moderately Toxic")
                                            target_role = b_data.get("target_role", "All")
                                            is_traitor = "Traitor" in str(state["players"][selected_player].get("role", ""))
                                            
                                            if target_role == "Traitor" and not is_traitor:
                                                b_data["desc"] = "🛡️ Safe! This cursed trap was meant for Traitors, and you are a Faithful!"
                                            else:
                                                if toxicity == "Instant Death" or (target_role == "Traitor" and is_traitor):
                                                    state["players"][selected_player]["status"] = "Murdered"
                                                    state["players"][selected_player]["eliminated_day"] = day_key
                                                elif toxicity == "Highly Toxic":
                                                    state["prize_pot"] = max(0, state["prize_pot"] - 100)
                                                elif toxicity == "Moderately Toxic":
                                                    state["prize_pot"] = max(0, state["prize_pot"] - 50)
                                                else: 
                                                    state["prize_pot"] = max(0, state["prize_pot"] - 25)

                                        save_state(state)
                                        st.rerun()

    # --- TRAITOR TURRET ACCESS SECTION ---
    if "Traitor" in role and status in ["Alive", "Undead"]:
        st.divider()
        st.subheader("🗡️ The Traitors' Turret (Secret Access)")
        fellow_traitors = [
            n for n, d in state["players"].items() 
            if "Traitor" in str(d.get("role", "")) and str(d.get("status", "")) in ["Alive", "Undead"]
        ]
        st.markdown(f"**Surviving Traitors in the Turret:** {', '.join(fellow_traitors)} | **Traitor Pot:** `{state['traitor_pot']} pts`")
        
        if state.get("traitor_vote_locked", False):
            st.error("🔒 **THE TURRET DOORS ARE BARRED!** High Host Neilio has locked Traitor voting for the night.")
        else:
            faithful_targets = [
                n for n, d in state["players"].items()
                if "Traitor" not in str(d.get("role", "")) and str(d.get("status", "")) in ["Alive", "Undead"] and not d.get("public_shield")
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
                    st.success("✅ Your 3 target preferences have been shared with your fellow Traitors.")
                    st.rerun()

# ==========================================
# SIDEBAR NAVIGATION & METRICS
# ==========================================
st.sidebar.title("🕯️ THE CASTLE")
st.sidebar.markdown(f"**High Host:** Neilio 👑")
st.sidebar.markdown(f"**Current Day:** Day {state['current_day']} of 10")
st.sidebar.markdown(f"**Current Phase:** `{state['phase']}`")

alive_count = sum(1 for p in state["players"].values() if str(p.get("status", "Alive")) in ["Alive", "Undead"])
st.sidebar.metric("🟢 Survivors in Castle", f"{alive_count} / {len(state['players'])}")
st.sidebar.metric("🏆 Faithful Prize Pot", f"{state['prize_pot']} pts")

st.sidebar.divider()
nav_options = [
    "🏰 Castle Hall (Public)",
    "🪑 The Round Table Room",
    "🗳️ Player Portal (Vote & Role)",
    "💍 Chamber of Relics",
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
        st.success("🏆 **THE GRAND FINALE IS LIVE!** Click **'🏆 The Grand Reveal (4PM Finale)'** in the sidebar.")
    elif state["phase"] == "The Fire Pit (Endgame)":
        st.error(f"🔥 **THE FIRE PIT IS LIT (Round {state['fire_pit_round']})!** Head to the Player Portal.")

    with st.expander("📜 Today's Daily Mission / Asynchronous Rules", expanded=True):
        st.markdown(state["mission_text"])

    st.subheader("🖼️ Portraits on the Great Hall Wall")
    players_list = list(state["players"].items())
    cols = st.columns(5)

    for idx, (name, pdata) in enumerate(players_list):
        col = cols[idx % 5]
        status = str(pdata.get("status", "Alive"))
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
        elif status == "Undead":
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card player-card-undead">
                <div class="undead-ghost">👻</div>
                {avatar_display}
                <div style="font-weight: bold; font-size: 15px; margin-top: 2px; color: #4a154b;">{name}</div>
                <div style="font-size: 12px; color: #4a154b; font-weight: bold;">👻 Undead</div>
                <div class="{role_class}" style="font-size: 11px; margin-top: 2px;">{revealed_role}</div>
            </div>
            """
        else:
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card player-card-dead">
                <div class="blood-cross">❌</div>
                {avatar_display}
                <div style="font-weight: bold; font-size: 15px; margin-top: 2px; text-decoration: line-through; color: #5c1d1d;">{name}</div>
                <div style="font-size: 12px; color: #5c1d1d; font-weight: bold;">{status} ({pdata.get('eliminated_day', '')})</div>
                <div class="{role_class}" style="font-size: 11px; margin-top: 2px;">{revealed_role}</div>
            </div>
            """
        col.markdown(card_html, unsafe_allow_html=True)

# ==========================================
# TAB: THE ROUND TABLE ROOM (CONCEPT A)
# ==========================================
elif nav == "🪑 The Round Table Room":
    st.title("🪑 The Great Round Table Chamber")
    st.markdown(
        "> *\"We gather in the flickering candlelight around the circular oak. Eyes meet eyes, accusations are hurled, "
        "and secrets hang in the balance. Take your assigned seat, state your truth, and prepare for the ballot.\"*"
    )

    # 1. Timers & Countdowns Section
    st.subheader("⏳ Round Table Countdowns")
    timers = state["round_table_timers"].setdefault(day_key, {
        "voting_opens": "2026-10-24 18:00",
        "voting_closes": "2026-10-24 21:00"
    })
    t_col1, t_col2 = st.columns(2)
    t_col1.markdown(f"""
    <div class="award-card">
        <div style="font-size: 22px;">🟢 Voting Opens At</div>
        <div style="font-size: 18px; color: #5c1d1d; margin-top: 6px;"><b>{timers['voting_opens']}</b></div>
    </div>
    """, unsafe_allow_html=True)
    t_col2.markdown(f"""
    <div class="award-card">
        <div style="font-size: 22px;">🔴 Voting Closes At</div>
        <div style="font-size: 18px; color: #5c1d1d; margin-top: 6px;"><b>{timers['voting_closes']}</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 2. Circular Seating Chart Display
    st.subheader("🪑 The Circular Seating Arrangement")
    seating = state["round_table_seating"].get(day_key, {})
    if not seating:
        st.info("The seating chart has not yet been shuffled for today. Host Neilio can assign seats in the Host Control tab!")
    else:
        seat_cols = st.columns(4)
        for idx, (seat_name, occupant) in enumerate(seating.items()):
            col = seat_cols[idx % 4]
            pdata = state["players"].get(occupant, {})
            photo_url = pdata.get("photo", "")
            avatar = f'<img src="{photo_url}" style="width: 45px; height: 45px; border-radius: 50%; object-fit: cover; border: 2px solid #c5a059;" />' if photo_url else '🛡️'
            col.markdown(f"""
            <div class="player-card" style="padding: 10px;">
                <div style="font-size: 12px; color: #c5a059; font-weight: bold;">{seat_name}</div>
                <div style="margin: 4px 0;">{avatar}</div>
                <div style="font-weight: bold; font-size: 14px;">{occupant}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 3. Discussion Chamber (Live Accusation Chat)
    st.subheader("💬 Round Table Accusation & Theory Stream")
    chat_messages = state["round_table_chat"].setdefault(day_key, [])

    with st.form("rt_chat_form", clear_on_submit=True):
        ch_col1, ch_col2 = st.columns([1, 3])
        chat_author = ch_col1.selectbox("Posting As:", list(state["players"].keys()), key="rt_chat_author")
        chat_text = ch_col2.text_input("State your accusation or defense theory:")
        chat_submit = st.form_submit_button("Publish to Round Table 📜")
        if chat_submit:
            if chat_text.strip():
                chat_messages.append({
                    "author": chat_author,
                    "text": chat_text.strip(),
                    "time": datetime.now().strftime("%H:%M")
                })
                save_state(state)
                st.rerun()

    st.markdown("---")
    if chat_messages:
        for msg in reversed(chat_messages[-15:]):
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #c5a059; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                <b>{msg['author']}</b> <span style="font-size: 11px; color: #7a756b;">({msg['time']})</span>: {msg['text']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("The chamber is silent. Be the first to cast suspicion across the table...")

# ==========================================
# TAB: PLAYER PORTAL
# ==========================================
elif nav == "🗳️ Player Portal (Vote & Role)":
    st.title("🗝️ The Secret Chamber Portal")
    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Select Your Name", list(state["players"].keys()))
    entered_pin = col2.text_input("Enter Your 4-Digit PIN", type="password")

    if entered_pin:
        p_info = state["players"][selected_player]
        if entered_pin != str(p_info.get("pin", "")):
            st.error("❌ Incorrect PIN.")
        else:
            st.success(f"Welcome back, **{selected_player}**.")
            render_player_portal_view(selected_player)

# ==========================================
# TAB: CHAMBER OF RELICS
# ==========================================
elif nav == "💍 Chamber of Relics":
    st.title("💍 The Alchemist's Chamber of Relics")
    if state.get("chamber_of_relics_locked", True):
        st.warning("🔒 **THE CHAMBER OF RELICS IS SEALED!**")
    else:
        st.markdown("Test your wits against the riddles within...")
        col_p_sel, col_p_pin = st.columns(2)
        r_player = col_p_sel.selectbox("Select Your Name for Relic Claim", list(state["players"].keys()), key="relic_player_sel")
        r_pin = col_p_pin.text_input("Enter Your 4-Digit PIN", type="password", key="relic_pin_sel")
        
        if r_pin:
            p_dat = state["players"][r_player]
            if r_pin != str(p_dat.get("pin", "")):
                st.error("❌ Incorrect PIN.")
            else:
                relics_contents = state["relics_vault_contents"]
                if not relics_contents:
                    state["relics_vault_contents"] = initialize_relics_boxes()
                    save_state(state)
                    relics_contents = state["relics_vault_contents"]
                
                solved_dict = state.setdefault("relics_riddle_solved", {}).setdefault(r_player, {})
                box_keys = sorted(relics_contents.keys(), key=lambda x: int(x.replace("Box ", "")))
                for b_key in box_keys:
                    b_info = relics_contents[b_key]
                    if not b_info["opened"]:
                        with st.container(border=True):
                            st.markdown(f"**{b_key}: {b_info['name']}**")
                            st.markdown(f"> *\"{b_info['clue']}\"*")
                            if st.button(f"Claim {b_info['name']} 🎁", key=f"claim_{r_player}_{b_key}"):
                                b_info["opened"] = True
                                b_info["opened_by"] = r_player
                                p_dat.setdefault("claimed_items", []).append({
                                    "day": "Chamber of Relics", "box": b_key, "desc": b_info['name'], "time": datetime.now().strftime("%H:%M")
                                })
                                save_state(state)
                                st.success(f"🎉 Claimed **{b_info['name']}**!")
                                st.rerun()

# ==========================================
# TAB: VOTING MATRIX
# ==========================================
elif nav == "📊 The Voting Matrix":
    st.title("📊 The Castle Archives: Voting Matrix")
    if not state.get("voting_matrix_unlocked", False):
        st.warning("🔒 **THE CASTLE ARCHIVES ARE SEALED!**")
    else:
        rows = []
        for name, pdata in state["players"].items():
            rows.append({"Player": name, "Status": pdata.get("status"), "Points": pdata.get("points")})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ==========================================
# TAB: THE GRAND REVEAL (FINALE)
# ==========================================
elif nav == "🏆 The Grand Reveal (4PM Finale)":
    st.title("🏆 The Grand Finale & Ultimate Reveal")
    if not is_finale_unlocked:
        st.warning("🔒 **THE GRAND REVEAL CHAMBER IS SEALED!**")
    else:
        st.balloons()
        st.success("The finale has been revealed!")

# ==========================================
# TAB: HOST CONTROL CENTRE
# ==========================================
elif nav == "👑 Host Control (Neilio)":
    st.title("👑 Neilio's High Host Sanctuary")
    admin_pin = st.text_input("Enter Host Master PIN", type="password")
    
    if admin_pin == HOST_PIN:
        st.success("Sanctuary unlocked.")
        
        st.markdown("---")
        st.subheader("🪑 Round Table Seating & Vote Tally Host Controls")
        
        c_seat1, c_seat2 = st.columns(2)
        if c_seat1.button("🪑 Randomly Allocate Round Table Seats"):
            assign_round_table_seats()
            st.success("✅ Players have been randomly assigned seats around the Round Table!")
            st.rerun()

        if c_seat2.button("⚖️ Tally Votes & Check for Ties"):
            tie_data = state["round_table_tie_breaker"].setdefault(day_key, {})
            is_tie_br = tie_data.get("active", False)
            v_key = f"{day_key}_tie" if is_tie_br else day_key
            day_votes = state["votes"].get(v_key, {})
            
            tally = {}
            for vdata in day_votes.values():
                tgt = vdata["target"]
                tally[tgt] = tally.get(tgt, 0) + 1
            
            if tally:
                max_votes = max(tally.values())
                top_targets = [t for t, count in tally.items() if count == max_votes]
                
                if len(top_targets) > 1 and not is_tie_br:
                    tie_data["active"] = True
                    tie_data["tied_players"] = top_targets
                    save_state(state)
                    st.error(f"⚖️ **TIE DETECTED!** Tied between: {', '.join(top_targets)}. Automatic Sudden Death Re-vote initiated! Tied players are now barred from voting.")
                else:
                    banished_target = top_targets[0]
                    st.success(f"🏆 **BANISHMENT DECIDED:** **{banished_target}** has received the most votes ({max_votes}) and is banished from the Castle!")
                    if banished_target in state["players"]:
                        state["players"][banished_target]["status"] = "Banished"
                        state["players"][banished_target]["eliminated_day"] = day_key
                    save_state(state)
            else:
                st.warning("No votes recorded for this ballot yet.")

        st.markdown("---")
        st.subheader("1. Game Day, Phase & Castle Decrees")
        c1, c2, c3, c4 = st.columns(4)
        new_day = c1.number_input("Current Day (1-12)", min_value=1, max_value=12, value=state["current_day"])
        new_phase = c2.selectbox("Current Phase", PHASES, index=PHASES.index(state["phase"]) if state["phase"] in PHASES else 0)
        new_fp_round = c3.number_input("Fire Pit Round", min_value=1, max_value=5, value=state.get("fire_pit_round", 1))
        new_pot = c4.number_input("Group Prize Pot", value=state["prize_pot"], step=50)
        
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
        st.subheader("3. Manage Players & Roster")
        roster_rows = []
        for name, d in state["players"].items():
            roster_rows.append({
                "Player Name": name, "PIN": str(d.get("pin", "1000")), "Role": str(d.get("role", "Faithful")),
                "Status": str(d.get("status", "Alive")), "Eliminated On": str(d.get("eliminated_day", ""))
            })
        
        edited_df = st.data_editor(pd.DataFrame(roster_rows), use_container_width=True, hide_index=True)
        if st.button("💾 Save Castle Roster"):
            updated_players = {}
            for _, row in edited_df.iterrows():
                player_name = row["Player Name"]
                if not player_name or not str(player_name).strip():
                    continue
                updated_players[player_name] = {
                    "pin": str(row["PIN"]), "role": str(row["Role"]), "status": str(row["Status"]),
                    "eliminated_day": str(row["Eliminated On"]), "shield": False, "public_shield": False,
                    "hide_role": False, "photo": state["players"].get(player_name, {}).get("photo", ""), "points": 0
                }
            state["players"] = updated_players
            save_state(state)
            st.success("Roster updated!")
            st.rerun()

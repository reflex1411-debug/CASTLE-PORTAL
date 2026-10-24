import streamlit as st
import pandas as pd
import json
import os
import base64
import random
import math
from datetime import datetime
import smtplib
from email.message import EmailMessage

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

    /* Expanded & Spacious Circular Round Table CSS Layout */
    .rt-container {
        position: relative;
        width: 100%;
        max-width: 580px;
        height: 580px;
        margin: 30px auto;
        border-radius: 50%;
        border: 4px dashed #c5a059;
        background: radial-gradient(circle, #2c2a29 0%, #1a1817 100%);
        box-shadow: 0 15px 40px rgba(0,0,0,0.5);
    }
    .rt-table-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: #3b2219;
        border: 3px solid #c5a059;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #ebdccb;
        font-family: 'Georgia', serif;
        font-weight: bold;
        font-size: 14px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
        z-index: 2;
    }
    .rt-seat {
        position: absolute;
        width: 95px;
        height: 95px;
        transform: translate(-50%, -50%);
        background: #ffffff;
        border: 2px solid #c5a059;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 6px 14px rgba(0,0,0,0.35);
        z-index: 3;
    }
    .rt-seat div {
        color: #2c2a29 !important;
        font-size: 11px;
        font-weight: bold;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 85px;
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
# DATA PERSISTENCE & EMAIL AUTO-BACKUP CONFIG
# ==========================================
DATA_FILE = "castle_state.json"
BACKUP_FILE = "castle_state_backup.json"
HOST_PIN = "1411"  # Host Neilio's PIN

AOL_SENDER_EMAIL = "hoeyneil@aol.com"
AOL_PASSWORD = "YOUR_AOL_APP_PASSWORD_HERE"  # Replace with your generated AOL App Password

def send_email_backup(state_data):
    """Automatically emails the castle state backup JSON file to hoeyneil@aol.com."""
    try:
        msg = EmailMessage()
        msg['Subject'] = f"🏰 Castle Auto-Backup: Day {state_data.get('current_day', 1)}"
        msg['From'] = AOL_SENDER_EMAIL
        msg['To'] = "hoeyneil@aol.com"
        msg.set_content(f"Attached is the automated state backup for Neilio's Castle as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")

        json_bytes = json.dumps(state_data, indent=4).encode("utf-8")
        msg.add_attachment(json_bytes, maintype='application', subtype='json', filename=f"castle_state_day_{state_data.get('current_day', 1)}.json")

        with smtplib.SMTP_SSL('smtp.aol.com', 465) as smtp:
            smtp.login(AOL_SENDER_EMAIL, AOL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email Backup Error: {e}")

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
        "mission_text": "🏆 **MISSION: ROUND TABLE ACCUSATIONS**\nDebate theories in the chamber and cast your vote before the timer expires!",
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
        "relics_config": {
            "riddles": {
                "Box 1": {"name": "💍 Ring of Truth", "clue": "It has no beginning, it has no end, yet it forces a foe to speak like a friend. Look where the mirror reflects not your face, but the pure unvarnished truth of the place.", "answer": "truth, mirror"},
                "Box 2": {"name": "📜 Amulet of Echoes", "clue": "Wear me close and bare your chest, for yesterday's secrets will not take a rest. What whispers were spoken in corners of old, through silver and glass shall soon be retold.", "answer": "echo, echo echoes"},
                "Box 3": {"name": "👑 Crown of Thorns", "clue": "Sharp to the touch and heavy to bear, I ward off the blade and chase off the snare. Sleep soundly tonight when the shadows creep near, for the fangs of the turret will find nothing here.", "answer": "thorn, thorns, crown"},
                "Box 4": {"name": "⏳ Hourglass Pendant", "clue": "I measure no sand, yet I alter the clock; I turn back the key in a time-frozen lock. When the votes are all cast and the whispers are done, I grant you a second chance under the sun.", "answer": "hourglass, sand, time"},
                "Box 5": {"name": "📌 Cloakpin of Silence", "clue": "I hold back the cloth, but I muzzle the tongue; I quiet the songs that the ravens have sung. Fasten me tightly and look to the floor—one voice in this room shall be heard nevermore.", "answer": "silence, pin, cloakpin"},
                "Box 6": {"name": "🍷 Poisoned Chalice Ring", "clue": "Drink deep of my fortune or swallow my pain—I double your glory or double your bane. A gamble of silver, a wager of gold, the sweetest of lies or the bitterest cold.", "answer": "chalice, poison, cup"},
                "Box 7": {"name": "🔮 Whispering Locket", "clue": "Open my casing and press to your ear, I carry the echoes of what they held dear. Secrets and shadows are locked in my brass—peek through the keyhole and watch the truth pass.", "answer": "locket, whisper, brass"},
                "Box 8": {"name": "⛓️ Iron Shackles Bracelet", "clue": "Two wrists bound together by iron and rust, a shared fate of peril, a compact of trust. If your partner falls victim to blade or to stone, you carry the heavy affliction alone.", "answer": "shackles, iron, handcuffs"},
                "Box 9": {"name": "🪶 Phoenix Feather Brooch", "clue": "Burned to a cinder and cast in the ash, I rise from the ruin in one sudden flash. Death may knock loudly and rattle the gate, but I am the stitch that rewrites your dark fate.", "answer": "phoenix, feather, ash"},
                "Box 10": {"name": "🃏 Jester’s Gold Tooth", "clue": "I grin from the dark with a flash and a gleam, turning reality into a scheme. Touch me and swap what you hold in your hand—the richest of rulers, the poorest of land.", "answer": "jester, tooth, gold"},
                "Box 11": {"name": "🪞 Mirror of Vanity", "clue": "I reflect not your face, but the fog in the hall; I blank out your name on the great castle wall. A ghost in the numbers, a blur in the light—who hides in the shadows of vanity's night?", "answer": "mirror, vanity, reflection"},
                "Box 12": {"name": "🪙 Fool’s Copper Band", "clue": "Glittering brightly under the light, I promise great power, I promise great might. But open me up and read my decree: you’ve been wonderfully fooled by a bit of debris!", "answer": "fool, copper, brass"}
            }
        },
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
    
    for key in ["fire_pit_round", "fire_pit_votes", "turret_nominations", "unanimous_murder",
                "vault_contents", "vault_attempts", "vault_riddle_solved", "vault_recent_open",
                "vault_room_open", "voting_matrix_unlocked", "traitor_vote_locked",
                "chamber_of_relics_locked", "relics_vault_contents", "round_table_seating",
                "round_table_chat", "round_table_timers", "round_table_tie_breaker"]:
        state.setdefault(key, {} if "votes" in key or "nominations" in key or "contents" in key or "chat" in key or "timers" in key or "seating" in key or "breaker" in key or "unanimous" in key or "solved" in key or "attempts" in key else (True if key=="vault_room_open" else {}))
    
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
        
    send_email_backup(state)

state = load_state()
day_key = f"Day {state['current_day']}"
fp_key = f"Round {state['fire_pit_round']}"
is_finale_unlocked = (state["phase"] == "🏆 The Grand Reveal (Finale)")

def get_public_identity(pdata, force_reveal=False):
    status = str(pdata.get("status", "Alive"))
    role = str(pdata.get("role", "Faithful"))
    if not force_reveal:
        if status == "Alive": return "❓ Unknown", ""
        if pdata.get("hide_role", False): return "🔒 Hidden (Finale)", "role-hidden"
        if status in ["Undead", "Murdered", "Banished", "Executed (No Vote Penalty)"]: return "🕯️ Faithful", "role-faithful"
    if "Traitor" in role: return f"🗡️ {role.upper()}", "role-traitor"
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
    if not relics_pool: relics_pool = ["Rusted Iron Key", "Dusty Tome of Spells", "Broken Dagger"]

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
                "opened": False, "opened_by": ""
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
    for b_key, r_info in riddles_dict.items():
        boxes[b_key] = {"name": r_info["name"], "clue": r_info["clue"], "opened": False, "opened_by": ""}
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
            for item in claimed_list:
                st.write(f"• **{item['time']}** ({item['day']}) — {item['box']}: {item['desc']}")
        else:
            st.info("You haven't opened any Safety Deposit Boxes or Relic Chambers yet today.")

    st.divider()

    if state["phase"] == "The Fire Pit (Endgame)":
        st.subheader(f"🔥 The Fire Pit of Truth — {fp_key}")
        if status not in ["Alive", "Undead"]:
            st.warning("👻 Only surviving finalists stand before the Fire Pit flames!")
        else:
            existing_fp = state["fire_pit_votes"].get(fp_key, {}).get(selected_player, {})
            with st.form(f"fire_pit_form_{selected_player}"):
                fp_choice = st.radio("Choose your pouch:", ["🟢 END GAME", "🔴 BANISH AGAIN"], index=0 if existing_fp.get("choice", "🟢 END GAME") == "🟢 END GAME" else 1)
                fp_reason = st.text_input("1-Sentence Final Statement:", value=existing_fp.get("reason", ""))
                if st.form_submit_button("Throw Pouch into Flames 🔥"):
                    if not fp_reason.strip(): st.error("Please add a 1-sentence reason!")
                    else:
                        state["fire_pit_votes"].setdefault(fp_key, {})[selected_player] = {"choice": fp_choice, "reason": fp_reason.strip(), "timestamp": datetime.now().strftime("%H:%M")}
                        save_state(state)
                        st.success(f"✅ Your **{fp_choice}** pouch is locked in!")
    elif state["phase"] == "Round Table Voting":
        st.subheader(f"🗳️ Round Table Ballot ({day_key})")
        if status not in ["Alive", "Undead"]:
            st.warning("👻 Ghosts cannot cast votes!")
        else:
            tie_data = state["round_table_tie_breaker"].get(day_key, {})
            is_tie_breaker = tie_data.get("active", False)
            tied_players = tie_data.get("tied_players", [])

            if is_tie_breaker and selected_player in tied_players:
                st.error("⚖️ **SUDDEN DEATH RE-VOTE:** You were tied and are barred from voting.")
            else:
                alive_targets = [n for n, d in state["players"].items() if str(d.get("status", "Alive")) in ["Alive", "Undead"] and n != selected_player]
                vote_key = f"{day_key}_tie" if is_tie_breaker else day_key
                existing_vote = state["votes"].get(vote_key, {}).get(selected_player, {})
                
                with st.form(f"vote_form_{selected_player}_{vote_key}"):
                    target = st.selectbox("Who are you voting to BANISH?", alive_targets, index=alive_targets.index(existing_vote["target"]) if existing_vote.get("target") in alive_targets else 0)
                    reason = st.text_input("1-Sentence Accusation:", value=existing_vote.get("reason", ""))
                    if st.form_submit_button("Lock In Vote 🕯️"):
                        if not reason.strip(): st.error("Please provide a short reason!")
                        else:
                            state["votes"].setdefault(vote_key, {})[selected_player] = {"target": target, "reason": reason.strip(), "timestamp": datetime.now().strftime("%H:%M")}
                            save_state(state)
                            st.success(f"✅ Vote against **{target}** recorded.")
    else:
        st.subheader("🗳️ Round Table Ballot")
        st.info("🔒 **The Round Table is currently sealed.**")

    # --- VAULT OF SAFETY DEPOSIT BOXES ---
    st.divider()
    st.subheader("🏦 The Wall of Safety Deposit Boxes")
    if state.get("vault_room_open", True):
        alive_count = sum(1 for d in state["players"].values() if str(d.get("status", "Alive")) in ["Alive", "Undead"])
        total_boxes = alive_count * 3
        vault_contents = state["vault_contents"].setdefault(day_key, {})
        if not vault_contents:
            state["vault_contents"][day_key] = initialize_vault_boxes(day_key, total_boxes, state["vault_config"])
            save_state(state)
            vault_contents = state["vault_contents"][day_key]

        riddle_solved = state["vault_riddle_solved"].setdefault(day_key, {}).get(selected_player, False)
        attempts = state["vault_attempts"].setdefault(day_key, {}).get(selected_player, 0)
        daily_riddle = state["vault_riddles"].get(day_key, {"question": "Solve the riddle.", "answer": "wish"})

        if status not in ["Alive", "Undead"]:
            st.warning("👻 Ghosts cannot tamper with the Vault!")
        else:
            st.markdown(f"**Attempts Today:** `{attempts} / 3 used`")
            if not riddle_solved:
                st.markdown(f"### 🧩 Gatekeeper Riddle\n> *\"{daily_riddle['question']}\"*")
                with st.form(f"riddle_form_{selected_player}"):
                    ans = st.text_input("Enter password:")
                    if st.form_submit_button("Submit Riddle 🗝️"):
                        if ans.strip().lower() in [a.strip() for a in daily_riddle["answer"].lower().split(",")]:
                            state["vault_riddle_solved"].setdefault(day_key, {})[selected_player] = True
                            save_state(state)
                            st.success("🔓 Correct!")
                            st.rerun()
                        else: st.error("❌ Incorrect.")
            else:
                st.success("🔓 Riddle Solved! Select up to 3 boxes.")
                if attempts < 3:
                    box_keys = sorted(vault_contents.keys(), key=int)
                    for i in range(0, len(box_keys), 5):
                        cols = st.columns(5)
                        for idx, b_key in enumerate(box_keys[i:i+5]):
                            b_data = vault_contents[b_key]
                            with cols[idx]:
                                btn_key = f"btn_box_{day_key}_{selected_player}_{b_key}"
                                if b_data["opened"]:
                                    st.button(f"🔒 #{b_key}\n(Opened)", disabled=True, key=btn_key)
                                else:
                                    if st.button(f"📦 Box #{b_key}", key=btn_key):
                                        if not vault_contents[b_key]["opened"]:
                                            vault_contents[b_key]["opened"] = True
                                            vault_contents[b_key]["opened_by"] = selected_player
                                            state["vault_attempts"].setdefault(day_key, {})[selected_player] = attempts + 1
                                            state["players"][selected_player].setdefault("claimed_items", []).append({
                                                "day": day_key, "box": f"Box #{b_key}", "desc": b_data["desc"], "time": datetime.now().strftime("%H:%M")
                                            })
                                            if b_data["type"] == "Shield": state["players"][selected_player]["shield"] = True
                                            elif b_data["type"] == "Points": state["prize_pot"] += b_data["value"]
                                            elif b_data["type"] == "Curse":
                                                if b_data.get("toxicity") == "Instant Death" or ("Traitor" in str(role) and b_data.get("target_role") == "Traitor"):
                                                    state["players"][selected_player]["status"] = "Murdered"
                                            save_state(state)
                                            st.rerun()

    # --- TRAITOR TURRET ---
    if "Traitor" in role and status in ["Alive", "Undead"]:
        st.divider()
        st.subheader("🗡️ The Traitors' Turret (Secret Access)")
        if not state.get("traitor_vote_locked", False):
            faithfuls = [n for n, d in state["players"].items() if "Traitor" not in str(d.get("role", "")) and str(d.get("status", "")) in ["Alive", "Undead"] and not d.get("public_shield")]
            turret_noms = state["turret_nominations"].setdefault(day_key, {})
            existing_noms = turret_noms.get(selected_player, {})
            with st.form(f"turret_form_{selected_player}"):
                opt_1 = st.selectbox("1st Choice:", faithfuls, index=faithfuls.index(existing_noms.get("1st", faithfuls[0])) if faithfuls and existing_noms.get("1st") in faithfuls else 0)
                opt_2 = st.selectbox("2nd Choice:", faithfuls, index=faithfuls.index(existing_noms.get("2nd", faithfuls[0])) if faithfuls and existing_noms.get("2nd") in faithfuls else 0)
                opt_3 = st.selectbox("3rd Choice:", faithfuls, index=faithfuls.index(existing_noms.get("3rd", faithfuls[0])) if faithfuls and existing_noms.get("3rd") in faithfuls else 0)
                if st.form_submit_button("Lock In Top 3 🩸"):
                    turret_noms[selected_player] = {"1st": opt_1, "2nd": opt_2, "3rd": opt_3}
                    save_state(state)
                    st.success("✅ Preferences saved.")
                    st.rerun()

# ==========================================
# SIDEBAR NAVIGATION & METRICS
# ==========================================
st.sidebar.title("🕯️ THE CASTLE")
st.sidebar.markdown(f"**High Host:** Neilio 👑")
st.sidebar.markdown(f"**Current Day:** Day {state['current_day']} of 10")
st.sidebar.markdown(f"**Current Phase:** `{state['phase']}`")

alive_count = sum(1 for p in state["players"].values() if str(p.get("status", "Alive")) in ["Alive", "Undead"])
st.sidebar.metric("🟢 Survivors", f"{alive_count} / {len(state['players'])}")
st.sidebar.metric("🏆 Prize Pot", f"{state['prize_pot']} pts")

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
        st.success("🏆 **THE GRAND FINALE IS LIVE!** Click **'🏆 The Grand Reveal'** in the sidebar.")
    elif state["phase"] == "The Fire Pit (Endgame)":
        st.error(f"🔥 **THE FIRE PIT IS LIT!** Head to your Player Portal.")

    with st.expander("📜 Today's Daily Mission / Rules", expanded=True):
        st.markdown(state["mission_text"])

    st.subheader("🖼️ Portraits on the Great Hall Wall")
    cols = st.columns(5)
    for idx, (name, pdata) in enumerate(state["players"].items()):
        col = cols[idx % 5]
        status = str(pdata.get("status", "Alive"))
        photo_url = pdata.get("photo", "")
        avatar = f'<img src="{photo_url}" style="width: 55px; height: 55px; border-radius: 50%; object-fit: cover; border: 2px solid #c5a059;" />' if photo_url else '🛡️'
        
        if status == "Alive":
            badge = " 🛡️" if pdata.get("public_shield") else ""
            rev_role, r_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card = f'<div class="player-card">{avatar}<div style="font-weight:bold; font-size:15px;">{name}{badge}</div><div style="color:#006666; font-size:12px;">🟢 Alive</div><div class="{r_class}" style="font-size:11px;">{rev_role}</div></div>'
        elif status == "Undead":
            rev_role, r_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card = f'<div class="player-card player-card-undead"><div class="undead-ghost">👻</div>{avatar}<div style="font-weight:bold; font-size:15px; color:#4a154b;">{name}</div><div style="font-size:12px; color:#4a154b; font-weight:bold;">👻 Undead</div><div class="{r_class}" style="font-size:11px;">{rev_role}</div></div>'
        else:
            rev_role, r_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card = f'<div class="player-card player-card-dead"><div class="blood-cross">❌</div>{avatar}<div style="font-weight:bold; font-size:15px; text-decoration:line-through; color:#5c1d1d;">{name}</div><div style="font-size:12px; color:#5c1d1d; font-weight:bold;">{status}</div><div class="{r_class}" style="font-size:11px;">{rev_role}</div></div>'
        col.markdown(card, unsafe_allow_html=True)

# ==========================================
# TAB 2: THE ROUND TABLE ROOM (INTERACTIVE CHAT & CIRCLE)
# ==========================================
elif nav == "🪑 The Round Table Room":
    st.title("🪑 The Great Round Table Chamber")
    st.markdown("> *\"Debate theories in the main chamber. Select your identity once below, then type freely like an internet chatroom!\"*")

    timers = state["round_table_timers"].setdefault(day_key, {"voting_opens": "18:00", "voting_closes": "21:00"})
    t1, t2 = st.columns(2)
    t1.markdown(f"<div class='award-card'><b>🟢 Voting Opens:</b> {timers['voting_opens']}</div>", unsafe_allow_html=True)
    t2.markdown(f"<div class='award-card'><b>🔴 Voting Closes:</b> {timers['voting_closes']}</div>", unsafe_allow_html=True)
    st.divider()

    left_panel, main_panel = st.columns([1, 2])

    with left_panel:
        st.subheader("👥 Chamber Roster")
        seating = state["round_table_seating"].get(day_key, {})
        if not seating:
            st.info("Seats not yet allocated by Host.")
        else:
            for seat, name in seating.items():
                pdata = state["players"].get(name, {})
                status_icon = "🟢" if pdata.get("status") == "Alive" else "👻"
                st.markdown(f"**{seat}:** {status_icon} {name}")

        st.divider()
        st.markdown("### 🪑 Circular Table View")
        if seating:
            total_seats = len(seating)
            circle_html = '<div class="rt-container"><div class="rt-table-center">THE ROUND<br>TABLE</div>'
            for idx, (seat, name) in enumerate(seating.items()):
                angle = (idx / total_seats) * 2 * math.pi - math.pi / 2
                x = 50 + 38 * math.cos(angle)
                y = 50 + 38 * math.sin(angle)
                pdata = state["players"].get(name, {})
                photo_url = pdata.get("photo", "")
                avatar = f'<img src="{photo_url}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />' if photo_url else '🛡️'
                circle_html += f'<div class="rt-seat" style="top: {y}%; left: {x}%;"><div>{avatar}</div><div>{name}</div></div>'
            circle_html += '</div>'
            st.markdown(circle_html, unsafe_allow_html=True)

    with main_panel:
        st.subheader("💬 Live Discussion Chamber")
        
        # Persistent identity selector for the chat room (so users don't have to pick from a dropdown per message)
        chat_identity = st.selectbox("Select Your Identity for Chat:", list(state["players"].keys()), key="rt_chat_identity_persistent")
        
        chat_messages = state["round_table_chat"].setdefault(day_key, [])

        with st.form("rt_chat_form", clear_on_submit=True):
            chat_text = st.text_input("Type your theory, defense, or accusation here...")
            if st.form_submit_button("Send Message 💬") and chat_text.strip():
                chat_messages.append({
                    "author": chat_identity, 
                    "text": chat_text.strip(), 
                    "time": datetime.now().strftime("%H:%M")
                })
                save_state(state)
                st.rerun()

        st.markdown("---")
        chat_container = st.container(height=450)
        with chat_container:
            if chat_messages:
                for msg in chat_messages:
                    st.markdown(f'<div style="background: #ffffff; border: 1px solid #c5a059; border-radius: 6px; padding: 10px; margin-bottom: 8px;"><b>{msg["author"]}</b> <span style="font-size: 11px; color: #7a756b;">({msg["time"]})</span><br>{msg["text"]}</div>', unsafe_allow_html=True)
            else:
                st.info("The chamber is silent. Be the first to speak...")

# ==========================================
# TAB 3: PLAYER PORTAL
# ==========================================
elif nav == "🗳️ Player Portal (Vote & Role)":
    st.title("🗝️ The Secret Chamber Portal")
    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Select Your Name", list(state["players"].keys()))
    entered_pin = col2.text_input("Enter PIN", type="password")
    if entered_pin:
        p_info = state["players"][selected_player]
        if entered_pin != str(p_info.get("pin", "")):
            st.error("❌ Incorrect PIN.")
        else:
            st.success(f"Welcome back, **{selected_player}**.")
            with st.expander("📸 Upload or Update Your Profile Photo", expanded=False):
                uploaded_file = st.file_uploader("Choose a photo (JPEG/PNG)", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    p_info["photo"] = f"data:image/jpeg;base64,{base64.b64encode(uploaded_file.getvalue()).decode('utf-8')}"
                    save_state(state)
                    st.success("✨ Portrait updated!")
                    st.rerun()
                if p_info.get("photo"): st.image(p_info["photo"], width=100)
            render_player_portal_view(selected_player)

# ==========================================
# TAB 4: CHAMBER OF RELICS
# ==========================================
elif nav == "💍 Chamber of Relics":
    st.title("💍 The Alchemist's Chamber of Relics")
    if state.get("chamber_of_relics_locked", True):
        st.warning("🔒 **THE CHAMBER OF RELICS IS SEALED!**")
    else:
        col_p_sel, col_p_pin = st.columns(2)
        r_player = col_p_sel.selectbox("Select Your Name", list(state["players"].keys()), key="relic_player_sel")
        r_pin = col_p_pin.text_input("Enter PIN", type="password", key="relic_pin_sel")
        if r_pin and r_pin == str(state["players"][r_player].get("pin")):
            relics_contents = state["relics_vault_contents"]
            if not relics_contents:
                state["relics_vault_contents"] = initialize_relics_boxes()
                save_state(state)
                relics_contents = state["relics_vault_contents"]
            solved_dict = state.setdefault("relics_riddle_solved", {}).setdefault(r_player, {})
            for b_key, b_info in relics_contents.items():
                if b_info["opened"]:
                    st.markdown(f'<div class="player-card" style="opacity: 0.7;"><b>{b_key} (Claimed)</b>: {b_info["name"]} by {b_info["opened_by"]}</div>', unsafe_allow_html=True)
                else:
                    with st.container(border=True):
                        st.markdown(f"**{b_key}**\n> *\"{b_info['clue']}\"*")
                        if not solved_dict.get(b_key, False):
                            with st.form(f"solve_{r_player}_{b_key}"):
                                ans = st.text_input("Name Keyword:")
                                if st.form_submit_button("Test Lock 🗝️"):
                                    if any(c in ans.strip().lower() for c in state["relics_config"]["riddles"][b_key]["answer"].split(",")):
                                        solved_dict[b_key] = True
                                        save_state(state)
                                        st.success("🔓 Unlocked!")
                                        st.rerun()
                                    else: st.error("❌ Incorrect.")
                        else:
                            if st.button(f"Claim {b_info['name']} 🎁", key=f"claim_{r_player}_{b_key}"):
                                b_info["opened"] = True
                                b_info["opened_by"] = r_player
                                state["players"][r_player].setdefault("claimed_items", []).append({"day": "Relics", "box": b_key, "desc": b_info['name'], "time": datetime.now().strftime("%H:%M")})
                                save_state(state)
                                st.balloons()
                                st.success("🎉 Claimed!")
                                st.rerun()

# ==========================================
# TAB 5: VOTING MATRIX
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
# TAB 6: THE GRAND REVEAL (FINALE)
# ==========================================
elif nav == "🏆 The Grand Reveal (4PM Finale)":
    st.title("🏆 The Grand Finale & Ultimate Reveal")
    if not is_finale_unlocked:
        st.warning("🔒 **THE GRAND REVEAL CHAMBER IS SEALED!**")
    else:
        survivors = {n: d for n, d in state["players"].items() if str(d.get("status", "")) in ["Alive", "Undead"]}
        if any("Traitor" in str(d.get("role", "")) for d in survivors.values()):
            st.snow()
            st.markdown('<div class="finale-banner-traitor"><h1>🗡️ TRAITORS WIN! 🗡️</h1></div>', unsafe_allow_html=True)
        else:
            st.balloons()
            st.markdown('<div class="finale-banner-faithful"><h1>🕯️ FAITHFULS WIN! 🕯️</h1></div>', unsafe_allow_html=True)

# ==========================================
# TAB 7: HOST CONTROL CENTRE
# ==========================================
elif nav == "👑 Host Control (Neilio)":
    st.title("👑 Neilio's High Host Sanctuary")
    if st.text_input("Enter Host Master PIN", type="password") == HOST_PIN:
        st.success("Sanctuary unlocked.")
        
        st.markdown("---")
        st.subheader("🪑 Round Table Seating & Vote Tally Controls")
        c_sc1, c_sc2 = st.columns(2)
        if c_sc1.button("🪑 Randomly Allocate Round Table Seats"):
            assign_round_table_seats()
            st.success("✅ Seats allocated!")
            st.rerun()

        if c_sc2.button("⚖️ Tally Votes & Check for Ties"):
            tie_data = state["round_table_tie_breaker"].setdefault(day_key, {})
            v_key = f"{day_key}_tie" if tie_data.get("active", False) else day_key
            tally = {}
            for vdata in state["votes"].get(v_key, {}).values():
                tgt = vdata["target"]
                tally[tgt] = tally.get(tgt, 0) + 1
            if tally:
                max_v = max(tally.values())
                top_t = [t for t, c in tally.items() if c == max_v]
                if len(top_t) > 1 and not tie_data.get("active", False):
                    tie_data["active"] = True
                    tie_data["tied_players"] = top_t
                    save_state(state)
                    st.error(f"⚖️ **TIE DETECTED!** Between: {', '.join(top_t)}. Sudden Death Re-vote initiated!")
                else:
                    banished = top_t[0]
                    state["players"][banished]["status"] = "Banished"
                    state["players"][banished]["eliminated_day"] = day_key
                    save_state(state)
                    st.success(f"🏆 **{banished}** banished with {max_v} votes!")
            else: st.warning("No votes recorded yet.")

        st.markdown("---")
        st.subheader("💍 Chamber & Vault Locks")
        c_l1, c_l2 = st.columns(2)
        new_r_lock = c_l1.toggle("🔒 Seal Chamber of Relics", value=state.get("chamber_of_relics_locked", True))
        if new_r_lock != state.get("chamber_of_relics_locked"):
            state["chamber_of_relics_locked"] = new_r_lock
            save_state(state)
            st.rerun()

        new_v_lock = c_l2.toggle("🔓 Vault Room Open", value=state.get("vault_room_open", True))
        if new_v_lock != state.get("vault_room_open"):
            state["vault_room_open"] = new_v_lock
            save_state(state)
            st.rerun()

        st.markdown("---")
        st.subheader("1. Game Day, Phase & Decrees")
        c1, c2, c3, c4 = st.columns(4)
        new_day = c1.number_input("Day", 1, 12, state["current_day"])
        new_phase = c2.selectbox("Phase", PHASES, index=PHASES.index(state["phase"]) if state["phase"] in PHASES else 0)
        new_fp = c3.number_input("Fire Pit Round", 1, 5, state.get("fire_pit_round", 1))
        new_pot = c4.number_input("Prize Pot", value=state["prize_pot"], step=50)
        new_head = st.text_input("Headline", state["headline"])
        new_miss = st.text_area("Mission Text", state["mission_text"])
        if st.button("💾 Save State & Decrees"):
            state.update({"current_day": new_day, "phase": new_phase, "fire_pit_round": new_fp, "prize_pot": new_pot, "headline": new_head, "mission_text": new_miss})
            save_state(state)
            st.success("Updated!")
            st.rerun()

        st.markdown("---")
        st.subheader("3. Manage Roster & Roles")
        roster_rows = [{"Player Name": n, "PIN": d.get("pin"), "Role": d.get("role"), "Status": d.get("status"), "Eliminated On": d.get("eliminated_day")} for n, d in state["players"].items()]
        edited_df = st.data_editor(pd.DataFrame(roster_rows), use_container_width=True, hide_index=True)
        if st.button("💾 Save Roster"):
            new_players = {}
            for _, row in edited_df.iterrows():
                name = row["Player Name"]
                if name.strip():
                    new_players[name] = {
                        "pin": str(row["PIN"]), "role": str(row["Role"]), "status": str(row["Status"]),
                        "eliminated_day": str(row["Eliminated On"]), "shield": False, "public_shield": False,
                        "hide_role": False, "photo": state["players"].get(name, {}).get("photo", ""), "points": 0
                    }
            state["players"] = new_players
            save_state(state)
            st.success("Roster saved!")
            st.rerun()

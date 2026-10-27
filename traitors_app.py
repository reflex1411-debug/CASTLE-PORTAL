import streamlit as st
import pandas as pd
import json
import os
import base64
import random
from datetime import datetime, timedelta
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

    /* Castle Chat UI */
    .castle-chat-container {
        background-color: #2c2a29;
        border-radius: 8px;
        border: 2px solid #c5a059;
        padding: 16px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
    }
    .castle-chat-header {
        background-color: #5c1d1d;
        color: #ebdccb !important;
        padding: 12px 16px;
        border-radius: 6px 6px 0 0;
        font-family: 'Georgia', serif;
        font-weight: bold;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #c5a059;
    }
    .castle-chat-header span {
        color: #ebdccb !important;
    }
    .castle-message-bubble {
        background-color: #f6f1e7;
        border: 1px solid #c5a059;
        border-radius: 7.5px;
        padding: 10px 14px;
        margin-bottom: 10px;
        max-width: 85%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .castle-message-bubble b {
        color: #5c1d1d !important;
    }
    .castle-message-time {
        font-size: 10px;
        color: #7a756b !important;
        text-align: right;
        margin-top: 4px;
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
AOL_PASSWORD = "bypwmpqzaqgfklgx"  # Configured AOL App Password

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

def send_login_alert(player_name):
    """Sends an instant email alert to Host Neilio when a player logs into their portal."""
    try:
        msg = EmailMessage()
        msg['Subject'] = f"🗝️ Castle Login Alert: {player_name} has entered!"
        msg['From'] = AOL_SENDER_EMAIL
        msg['To'] = "hoeyneil@aol.com"
        msg.set_content(f"High Host Neilio,\n\nPlayer {player_name} successfully unlocked and logged into their Castle Portal at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")

        with smtplib.SMTP_SSL('smtp.aol.com', 465) as smtp:
            smtp.login(AOL_SENDER_EMAIL, AOL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Login Alert Email Error: {e}")

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
            "enabled": True,
            "traitors_bane_enabled": True,
            "boxes": ["3", "7", "12", "15", "19"]
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
        "voting_active": True,
        "chat_locked": False,
        "castle_gates_open": True,
        "headline": "Welcome to Neilio's Castle! The Round Table voting is now live.",
        "mission_text": "🏆 **MISSION: ROUND TABLE ACCUSATIONS**\nCast your vote before voting is closed by the Host!",
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
                "Box 2": {"name": "📜 Amulet of Cleansing Fire", "clue": "I burn with no ember, I smoke with no ash, yet I shatter the venom in one sudden flash. Where the shadows of curses cling thick to the door, I cleanse every trap that was laid on the floor. Name what devours the darkness and frees up the stone, and the power of purification is yours alone.", "answer": "fire, flame, cleansing fire, purge, burn, light"},
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
        "round_table_chat": {},
        "round_table_timers": {},
        "round_table_tie_breaker": {},
        "non_voters": {},
        "public_execution": {},
        "login_history": [],
        "host_item_audit": [],
        "custom_songs": {"traitors_theme.mp3": "traitors_theme.mp3"}
    }

# ==========================================
# RELIC AUTOMATION & BOX INITIALIZATION
# ==========================================
def initialize_vault_boxes(day_k, total_boxes, config, current_state=None):
    boxes = {}
    box_numbers = list(range(1, total_boxes + 1))
    
    custom_curses = current_state.get("custom_curses", {}) if current_state else (state.get("custom_curses", {}) if 'state' in globals() else {})
    day_curse_data = st.session_state.get("temp_curses", {}).get(day_k, custom_curses.get(day_k, {"enabled": True, "boxes": ["3", "7", "12", "15", "19"]}))
    
    random.shuffle(box_numbers)
    
    shields_to_assign = min(config.get("shields_count", 2), total_boxes)
    
    curses_enabled = day_curse_data.get("enabled", True)
    host_cursed_box_nums = [str(b) for b in day_curse_data.get("boxes", [])] if curses_enabled else []
    traitors_bane_enabled = day_curse_data.get("traitors_bane_enabled", True)
    
    relics_pool = [r.strip() for r in config.get("relics_list", "").split(",") if r.strip()]
    if not relics_pool: relics_pool = ["Rusted Iron Key", "Dusty Tome of Spells", "Broken Dagger"]

    bane_placed = False

    for i in range(total_boxes):
        b_num = str(box_numbers[i])
        if i < shields_to_assign:
            boxes[b_num] = {"type": "Shield", "desc": "🛡️ A Royal Castle Shield!", "opened": False, "opened_by": ""}
        elif curses_enabled and b_num in host_cursed_box_nums:
            if traitors_bane_enabled and not bane_placed:
                boxes[b_num] = {
                    "type": "Curse", 
                    "toxicity": "Traitor-Lethal",
                    "target_role": "Traitor",
                    "desc": "🗡️ **Traitors' Bane**: TRAP FOR TRAITORS! If opened by a Traitor, they are instantly eliminated from the Castle!", 
                    "opened": False, "opened_by": ""
                }
                bane_placed = True
            else:
                if i % 2 == 0:
                    pts = config.get("prize_points_value", 25)
                    boxes[b_num] = {"type": "Points", "value": pts, "desc": f"✨ {pts} Group Prize Points added!", "opened": False, "opened_by": ""}
                else:
                    relic = random.choice(relics_pool)
                    boxes[b_num] = {"type": "Relic", "desc": f"📜 A Castle Relic: {relic} (No effect)", "opened": False, "opened_by": ""}
        else:
            if i % 2 == 0:
                pts = config.get("prize_points_value", 25)
                boxes[b_num] = {"type": "Points", "value": pts, "desc": f"✨ {pts} Group Prize Points added!", "opened": False, "opened_by": ""}
            else:
                relic = random.choice(relics_pool)
                boxes[b_num] = {"type": "Relic", "desc": f"📜 A Castle Relic: {relic} (No effect)", "opened": False, "opened_by": ""}
            
    if curses_enabled and traitors_bane_enabled and not bane_placed and boxes:
        first_box = list(boxes.keys())[0]
        boxes[first_box] = {
            "type": "Curse", 
            "toxicity": "Traitor-Lethal",
            "target_role": "Traitor",
            "desc": "🗡️ **Traitors' Bane**: TRAP FOR TRAITORS! If opened by a Traitor, they are instantly eliminated from the Castle!", 
            "opened": False, "opened_by": ""
        }

    return boxes

def initialize_relics_boxes():
    boxes = {}
    riddles_dict = state["relics_config"].get("riddles", {})
    for b_key, r_info in riddles_dict.items():
        existing = state.get("relics_vault_contents", {}).get(b_key, {})
        boxes[b_key] = {
            "name": r_info["name"],
            "clue": r_info["clue"],
            "opened": existing.get("opened", False),
            "opened_by": existing.get("opened_by", "")
        }
    return boxes

def load_state():
    if not os.path.exists(DATA_FILE):
        state_dict = get_default_state()
        save_state(state_dict)
        return state_dict
    with open(DATA_FILE, "r") as f:
        state_dict = json.load(f)
    
    for key in ["fire_pit_round", "fire_pit_votes", "turret_nominations", "unanimous_murder",
                "vault_contents", "vault_attempts", "vault_riddle_solved", "vault_recent_open",
                "vault_room_open", "voting_matrix_unlocked", "traitor_vote_locked",
                "chamber_of_relics_locked", "relics_vault_contents",
                "round_table_chat", "round_table_timers", "round_table_tie_breaker", "non_voters", "public_execution", "login_history", "host_item_audit", "custom_songs"]:
        state_dict.setdefault(key, [] if key in ["login_history", "host_item_audit"] else ({} if key == "custom_songs" else ({} if "votes" in key or "nominations" in key or "contents" in key or "chat" in key or "timers" in key or "breaker" in key or "execution" in key or "non_voters" in key or "unanimous" in key or "solved" in key or "attempts" in key else (True if key in ["vault_room_open", "voting_active", "castle_gates_open", "chat_locked"] else {}))))
    
    default_state = get_default_state()
    state_dict.setdefault("custom_curses", default_state["custom_curses"])
    state_dict.setdefault("vault_riddles", default_state["vault_riddles"])
    state_dict.setdefault("vault_config", default_state["vault_config"])
    state_dict.setdefault("relics_config", default_state["relics_config"])

    for p in state_dict.get("players", {}).values():
        p["role"] = str(p.get("role", "Faithful"))
        p["status"] = str(p.get("status", "Alive"))
        p.setdefault("hide_role", False)
        p.setdefault("public_shield", False)
        p.setdefault("photo", "")
        p.setdefault("points", 0)
        p.setdefault("claimed_items", [])
        
    synth_v_key = f"Day {state_dict.get('current_day', 1)}"
    if synth_v_key not in state_dict.setdefault("vault_contents", {}):
        alive_c = sum(1 for d in state_dict["players"].values() if str(d.get("status", "")) in ["Alive", "Undead"])
        state_dict["vault_contents"][synth_v_key] = initialize_vault_boxes(synth_v_key, max(alive_c * 3, 15), state_dict["vault_config"], current_state=state_dict)

    return state_dict

def save_state(state_data):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            current_data = f.read()
        with open(BACKUP_FILE, "w") as f:
            f.write(current_data)
            
    with open(DATA_FILE, "w") as f:
        json.dump(state_data, f, indent=4)
        
    send_email_backup(state_data)

state = load_state()
day_key = f"Day {state['current_day']}"
fp_key = f"Round {state['fire_pit_round']}"
is_finale_unlocked = (state["phase"] == "🏆 The Grand Reveal (Finale)")

# ==========================================
# RELIC AUTOMATION HELPER FUNCTIONS
# ==========================================
def player_has_relic(player_name, relic_keyword):
    """Checks if a player holds an item containing a specific keyword in their inventory."""
    p_data = state["players"].get(player_name, {})
    claimed = p_data.get("claimed_items", [])
    for item in claimed:
        if relic_keyword.lower() in item.get("desc", "").lower():
            return True
    return False

def consume_relic(player_name, relic_keyword):
    """Removes a single-use relic from a player's inventory once triggered."""
    p_data = state["players"].get(player_name, {})
    claimed = p_data.get("claimed_items", [])
    for idx, item in enumerate(claimed):
        if relic_keyword.lower() in item.get("desc", "").lower():
            removed = claimed.pop(idx)
            save_state(state)
            return removed
    return None

def get_public_identity(pdata, force_reveal=False):
    status = str(pdata.get("status", "Alive"))
    role = str(pdata.get("role", "Faithful"))
    if not force_reveal:
        if status == "Alive": return "❓ Unknown", ""
        if pdata.get("hide_role", False): return "🔒 Hidden (Finale)", "role-hidden"
        if status in ["Undead", "Murdered", "Banished", "Executed (No Vote Penalty)"]: return "🕯️ Faithful", "role-faithful"
    if "Traitor" in role: return f"🗡️ {role.upper()}", "role-traitor"
    return "🕯️ Faithful", "role-faithful"

def compute_superlatives(state_data):
    all_traitors = {n for n, d in state_data["players"].items() if "Traitor" in str(d.get("role", ""))}
    detective_scores = {n: 0 for n, d in state_data["players"].items() if "Traitor" not in str(d.get("role", ""))}
    votes_against = {n: 0 for n in state_data["players"]}

    for d_votes in state_data["votes"].values():
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
    p_info = state["players"][selected_player]
    role = str(p_info.get("role", "Faithful"))
    status = str(p_info.get("status", "Alive"))
    st.success(f"Viewing portal as: **{selected_player}**")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Secret Role", f"🗡️ {role}" if "Traitor" in role else "🕯️ Faithful")
    r_col2.metric("Current Status", status)
    r_col3.metric("Personal Points", f"{p_info.get('points', 0)} pts")

    st.divider()

    has_secret_shield = p_info.get("shield", False)
    has_public_shield = p_info.get("public_shield", False)
    if has_secret_shield or has_public_shield:
        s_type = "🛡️ Public Shield (Displayed on Great Hall Wall)" if has_public_shield else "🔒 Secret Shield (Hidden in Portal)"
        st.info(f"Active Armor: **{s_type}**")
        with st.form(f"shield_visibility_{selected_player}"):
            new_pub_toggle = st.toggle("Make Shield Public (Display on Portrait Wall)", value=has_public_shield)
            if st.form_submit_button("Update Shield Visibility"):
                p_info["public_shield"] = new_pub_toggle
                save_state(state)
                st.success("✅ Shield visibility updated!")
                st.rerun()

    st.divider()

    with st.expander("📦 My Claimed Vault Items & Winnings History", expanded=True):
        claimed_list = p_info.get("claimed_items", [])
        if claimed_list:
            for item in claimed_list:
                st.write(f"• **{item['time']}** ({item['day']}) — {item['box']}: {item['desc']}")
        else:
            st.info("You haven't opened any Safety Deposit Boxes or Relic Chambers yet today.")

    # --- AUTOMATED JESTER'S GOLD TOOTH FEATURE ---
    if player_has_relic(selected_player, "Jester’s Gold Tooth"):
        st.divider()
        with st.expander("🃏 Unleash Jester's Gold Tooth (Point Swap)"):
            other_players = [p for p in state["players"] if p != selected_player]
            target_swap = st.selectbox("Choose player to swap point totals with:", other_players, key=f"jester_target_{selected_player}")
            if st.button("🃏 Swap Points Now", key=f"jester_btn_{selected_player}"):
                consume_relic(selected_player, "Jester’s Gold Tooth")
                my_pts = state["players"][selected_player]["points"]
                target_pts = state["players"][target_swap]["points"]
                
                state["players"][selected_player]["points"] = target_pts
                state["players"][target_swap]["points"] = my_pts
                save_state(state)
                st.success(f"🃏 Chaos reigns! You successfully swapped point totals with {target_swap}!")
                st.rerun()

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
        elif not state.get("voting_active", True):
            st.warning("🔒 **Voting is currently closed. Reviewing final votes below:**")
            
            # --- SECRET VOTE REVEAL PANEL ---
            vote_key = day_key
            cast_votes = state["votes"].get(vote_key, {})
            if cast_votes:
                for voter, vdata in cast_votes.items():
                    clean_voter = voter.replace("🔒 [ANONYMOUS SHADOW — ", "").replace("]", "")
                    st.markdown(f"• **{clean_voter}** voted to banish **{vdata['target']}** — *\"{vdata['reason']}\"*")
            else:
                st.info("No votes were cast for this Round Table.")
        else:
            tie_data = state["round_table_tie_breaker"].get(day_key, {})
            is_tie_breaker = tie_data.get("active", False)
            tied_players = tie_data.get("tied_players", [])

            if is_tie_breaker and selected_player in tied_players:
                st.error("⚖️ **SUDDEN DEATH RE-VOTE:** You were tied and are barred from voting.")
            else:
                alive_targets = [n for n, d in state["players"].items() if str(d.get("status", "Alive")) in ["Alive", "Undead"] and n != selected_player]
                vote_key = f"{day_key}_tie" if is_tie_breaker else day_key
                
                # Check if player already voted (permanent lock)
                existing_vote = None
                for v_key, v_data in state["votes"].get(vote_key, {}).items():
                    if selected_player in v_key:
                        existing_vote = v_data
                        break

                if existing_vote and "target" in existing_vote:
                    st.success(f"🔒 **Your vote has been cast and sealed!** You voted to banish **{existing_vote['target']}**.")
                    st.markdown(f"> *\"{existing_vote['reason']}\"*")
                    st.info("Your vote is permanently locked in and cannot be changed.")
                else:
                    with st.form(f"vote_form_{selected_player}_{vote_key}"):
                        target = st.selectbox("Who are you voting to BANISH?", alive_targets, key=f"vote_target_{selected_player}_{day_key}")
                        reason = st.text_input("1-Sentence Accusation:", key=f"vote_reason_{selected_player}_{day_key}")
                        if st.form_submit_button("Lock In Vote & Seal Forever 🕯️"):
                            if not reason.strip(): 
                                st.error("Please provide a short reason!")
                            else:
                                voter_key = selected_player
                                if player_has_relic(selected_player, "Mirror of Vanity"):
                                    voter_key = f"🔒 [ANONYMOUS SHADOW — {selected_player}]"

                                state["votes"].setdefault(vote_key, {})[voter_key] = {
                                    "target": target, 
                                    "reason": reason.strip(), 
                                    "timestamp": datetime.now().strftime("%H:%M")
                                }
                                save_state(state)
                                st.success(f"✅ Your secret vote against **{target}** is permanently locked in!")
                                st.rerun()
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
            state["vault_contents"][day_key] = initialize_vault_boxes(day_key, total_boxes, state["vault_config"], current_state=state)
            save_state(state)
            vault_contents = state["vault_contents"][day_key]

        riddle_solved = state["vault_riddle_solved"].setdefault(day_key, {}).get(selected_player, False)
        attempts = state["vault_attempts"].setdefault(day_key, {}).get(selected_player, 0)
        daily_riddle = state["vault_riddles"].get(day_key, {"question": "Solve the riddle.", "answer": "wish"})

        if status not in ["Alive", "Undead"]:
            st.warning("👻 Ghosts cannot tamper with the Vault!")
        else:
            st.markdown(f"**Attempts Today:** `{attempts} / 3 used`")
            
            # --- AUTOMATED HOURGLASS PENDANT CHECK FOR ATTEMPTS ---
            if attempts >= 3 and player_has_relic(selected_player, "Hourglass Pendant"):
                st.warning("⏳ You have used all 3 attempts, but your **Hourglass Pendant** can rewind time!")
                if st.button("Use Hourglass Pendant for +1 Bonus Attempt ⏳"):
                    consume_relic(selected_player, "Hourglass Pendant")
                    state["vault_attempts"][day_key][selected_player] = 2  # Reset back to 2 so they get 1 more try
                    save_state(state)
                    st.success("⏳ Time rewinds! Your Hourglass Pendant shatters, granting you 1 additional vault box attempt.")
                    st.rerun()

            if not riddle_solved:
                st.markdown(f"### 🧩 Gatekeeper Riddle\n> *\"{daily_riddle['question']}\"*")
                with st.form(f"riddle_form_{selected_player}"):
                    ans = st.text_input("Enter password:", key=f"riddle_input_{selected_player}_{day_key}")
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
                                            b_item_type = vault_contents[b_key].get("type")
                                            is_traitor = "Traitor" in str(role)

                                            # --- TRAITORS' BANE FAITHFUL STEALTH RESET ---
                                            if b_item_type == "Curse" and vault_contents[b_key].get("toxicity") == "Traitor-Lethal" and not is_traitor:
                                                vault_contents[b_key] = {
                                                    "type": "Points", 
                                                    "value": 25, 
                                                    "desc": "✨ 25 Group Prize Points added!", 
                                                    "opened": False, 
                                                    "opened_by": ""
                                                }
                                                state["vault_attempts"].setdefault(day_key, {})[selected_player] = attempts + 1
                                                save_state(state)
                                                st.warning("⚠️ The box felt bitterly cold to your touch, but the latch snapped shut before you could see inside! (Attempt counted).")
                                                st.rerun()

                                            vault_contents[b_key]["opened"] = True
                                            vault_contents[b_key]["opened_by"] = selected_player
                                            state["vault_attempts"].setdefault(day_key, {})[selected_player] = attempts + 1
                                            
                                            item_log_desc = b_data["desc"]
                                            state["players"][selected_player].setdefault("claimed_items", []).append({
                                                "day": day_key, "box": f"Box #{b_key}", "desc": item_log_desc, "time": datetime.now().strftime("%H:%M")
                                            })
                                            state.setdefault("host_item_audit", []).append({
                                                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                "player": selected_player,
                                                "source": f"{day_key} Box #{b_key}",
                                                "item": item_log_desc
                                            })

                                            if b_data["type"] == "Shield":
                                                state["players"][selected_player]["shield"] = True
                                            elif b_data["type"] == "Points":
                                                state["prize_pot"] += b_data["value"]
                                                state["players"][selected_player]["points"] += b_data["value"]
                                            elif b_data["type"] == "Curse":
                                                if b_data.get("toxicity") == "Instant Death" or ("Traitor" in str(role) and b_data.get("target_role") == "Traitor"):
                                                    
                                                    # --- AUTOMATED PHOENIX FEATHER BROOCH CHECK ---
                                                    if player_has_relic(selected_player, "Phoenix Feather Brooch"):
                                                        consumed = consume_relic(selected_player, "Phoenix Feather Brooch")
                                                        st.balloons()
                                                        st.success(f"🔥 **PHOENIX REBIRTH TRIGGERED!** Your *{consumed['desc']}* turns to ash, saving you from instant death!")
                                                    else:
                                                        state["players"][selected_player]["status"] = "Murdered"
                                                        state["players"][selected_player]["eliminated_day"] = day_key
                                                        st.session_state["instant_death_player"] = selected_player

                                            save_state(state)
                                            st.rerun()

    if st.session_state.get("instant_death_player") == selected_player:
        st.error("⚡ **INSTANT DEATH TRIGGERED!** You opened a lethal box. Send your final message to the group:")
        with st.form(f"last_will_form_{selected_player}"):
            last_msg = st.text_input("Your Last Words / Testament:", key=f"last_msg_{selected_player}")
            if st.form_submit_button("Publish Final Words to Group 📜"):
                if last_msg.strip():
                    state.setdefault("round_table_chat", {}).setdefault(day_key, []).append({
                        "author": f"👻 {selected_player} (Last Will)",
                        "text": f"⚠️ *My dying words from the grave:* \"{last_msg.strip()}\"",
                        "time": datetime.now().strftime("%H:%M")
                    })
                    save_state(state)
                del st.session_state["instant_death_player"]
                st.success("Your final message has echoed through the castle.")
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
                opt_1 = st.selectbox("1st Choice:", faithfuls, index=faithfuls.index(existing_noms.get("1st", faithfuls[0])) if faithfuls and existing_noms.get("1st") in faithfuls else 0, key=f"turret_1_{selected_player}")
                opt_2 = st.selectbox("2nd Choice:", faithfuls, index=faithfuls.index(existing_noms.get("2nd", faithfuls[0])) if faithfuls and existing_noms.get("2nd") in faithfuls else 0, key=f"turret_2_{selected_player}")
                opt_3 = st.selectbox("3rd Choice:", faithfuls, index=faithfuls.index(existing_noms.get("3rd", faithfuls[0])) if faithfuls and existing_noms.get("3rd") in faithfuls else 0, key=f"turret_3_{selected_player}")
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

if "logged_in_player" in st.session_state:
    st.sidebar.success(f"🔑 Logged in as: **{st.session_state['logged_in_player']}**")
    if st.sidebar.button("🔓 Logout"):
        del st.session_state["logged_in_player"]
        st.rerun()

st.sidebar.divider()
alive_count = sum(1 for p in state["players"].values() if str(p.get("status", "Alive")) in ["Alive", "Undead"])
st.sidebar.metric("🟢 Survivors", f"{alive_count} / {len(state['players'])}")
st.sidebar.metric("🏆 Prize Pot", f"{state['prize_pot']} pts")

st.sidebar.divider()
nav_options = [
    "🏰 Castle Hall (Public)",
    "💬 Round Table Live Chat",
    "💀 Public Execution Room",
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
        
        public_shield_badge = " 🛡️" if pdata.get("public_shield", False) else ""

        if status == "Alive":
            rev_role, r_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card = f'<div class="player-card">{avatar}<div style="font-weight:bold; font-size:15px;">{name}{public_shield_badge}</div><div style="color:#006666; font-size:12px;">🟢 Alive</div><div class="{r_class}" style="font-size:11px;">{rev_role}</div></div>'
        elif status == "Undead":
            rev_role, r_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card = f'<div class="player-card player-card-undead"><div class="undead-ghost">👻</div>{avatar}<div style="font-weight:bold; font-size:15px; color:#4a154b;">{name}{public_shield_badge}</div><div style="font-size:12px; color:#4a154b; font-weight:bold;">👻 Undead</div><div class="{r_class}" style="font-size:11px;">{rev_role}</div></div>'
        else:
            rev_role, r_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card = f'<div class="player-card player-card-dead"><div class="blood-cross">❌</div>{avatar}<div style="font-weight:bold; font-size:15px; text-decoration:line-through; color:#5c1d1d;">{name}</div><div style="font-size:12px; color:#5c1d1d; font-weight:bold;">{status}</div><div class="{r_class}" style="font-size:11px;">{rev_role}</div></div>'
        col.markdown(card, unsafe_allow_html=True)

# ==========================================
# TAB 2: ROUND TABLE LIVE CHAT
# ==========================================
elif nav == "💬 Round Table Live Chat":
    st.title("💬 Round Table Live Chat")
    
    # --- SECURE CHAT IDENTITY (NO SPOOFING) ---
    if "logged_in_player" in st.session_state and st.session_state["logged_in_player"] in state["players"]:
        chat_author = st.session_state["logged_in_player"]
        st.success(f"💬 Chatting as: **{chat_author}**")
    else:
        chat_author = "👑 High Host Neilio"
        st.info("👑 Chatting as **High Host Neilio** (The Host). *Note: Players must log into their Player Portal to chat as themselves.*")

    timers = state["round_table_timers"].setdefault(day_key, {"voting_opens": "18:00", "voting_closes": "21:00"})
    t1, t2 = st.columns(2)
    t1.markdown(f"<div class='award-card'><b>🟢 Voting Opens:</b> {timers['voting_opens']}</div>", unsafe_allow_html=True)
    t2.markdown(f"<div class='award-card'><b>🔴 Voting Closes:</b> {timers['voting_closes']}</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="castle-chat-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="castle-chat-header"><span>💬 The Round Table ({day_key})</span><span>🔒 Encrypted Whispers</span></div>', unsafe_allow_html=True)

    chat_messages = state["round_table_chat"].setdefault(day_key, [])

    chat_container = st.container(height=420)
    with chat_container:
        if chat_messages:
            for msg in chat_messages:
                st.markdown(f"""
                <div class="castle-message-bubble">
                    <b>{msg['author']}</b><br>
                    {msg['text']}
                    <div class="castle-message-time">{msg['time']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No messages in the chat yet. Start the discussion below...")

    # --- CHECK IF CHAT IS LOCKED BY HOST ---
    if state.get("chat_locked", False):
        st.warning("🔒 **The Round Table Chat has been temporarily locked by Host Neilio.**")
    else:
        with st.form("castle_chat_form", clear_on_submit=True):
            c_input, c_btn = st.columns([4, 1])
            chat_text = c_input.text_input("Type a message...", placeholder="Type your accusation or defense...", label_visibility="collapsed")
            chat_submit = c_btn.form_submit_button("Send ➔")
            if chat_submit and chat_text.strip():
                chat_messages.append({
                    "author": chat_author,
                    "text": chat_text.strip(),
                    "time": datetime.now().strftime("%H:%M")
                })
                save_state(state)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: PUBLIC EXECUTION ROOM
# ==========================================
elif nav == "💀 Public Execution Room":
    st.title("💀 The Public Execution Chamber")
    st.markdown(
        "> *\"Those who fail to cast their ballot before the Castle gates seal are branded as cowards and traitors to the realm. "
        "The living must now vote to send a silent soul straight to the Ghost's gallows...\"*"
    )

    timers = state["round_table_timers"].get(day_key, {"voting_closes": "21:00"})
    st.markdown(f"### ⏳ Voting Closure Countdown: **{timers['voting_closes']}**")
    st.divider()

    manual_non_voters = state["non_voters"].setdefault(day_key, [])

    if not manual_non_voters:
        st.success("✨ All surviving players successfully cast their votes! The execution chamber is empty.")
    else:
        st.warning(f"⚠️ **{len(manual_non_voters)} player(s) failed to vote and face Public Execution:**")
        for nv in manual_non_voters:
            st.markdown(f"• 🩸 <b>{nv}</b>", unsafe_allow_html=True)

        st.divider()
        st.subheader("⚖️ Cast Your Execution Vote")
        
        alive_players = [n for n, d in state["players"].items() if str(d.get("status", "Alive")) in ["Alive", "Undead"]]
        default_voter_idx = 0
        if "logged_in_player" in st.session_state and st.session_state["logged_in_player"] in alive_players:
            default_voter_idx = alive_players.index(st.session_state["logged_in_player"])

        exec_voter = st.selectbox("Select Your Name (Voter):", alive_players, index=default_voter_idx, key="exec_voter_select")
        st.info(f"Voting as: **{exec_voter}**")

        pub_exec_votes = state["public_execution"].setdefault(day_key, {})

        with st.form("public_execution_form"):
            exec_target = st.selectbox("Select guilty non-voter to execute:", manual_non_voters)
            exec_submit = st.form_submit_button("Throw them to the Ghost 👻")
            if exec_submit:
                pub_exec_votes[exec_voter] = exec_target
                save_state(state)
                st.success(f"✅ Your vote ({exec_voter}) to throw **{exec_target}** to the ghost has been recorded!")

        st.markdown("---")
        st.subheader("📊 Live Execution Tally Board")
        tally = {}
        for v in pub_exec_votes.values():
            tally[v] = tally.get(v, 0) + 1

        if tally:
            for target, count in tally.items():
                st.markdown(f"• 👻 **{target}**: `{count} vote(s)`")
        else:
            st.info("No execution votes cast yet.")

# ==========================================
# TAB 4: PLAYER PORTAL
# ==========================================
elif nav == "🗳️ Player Portal (Vote & Role)":
    st.title("🗝️ The Secret Chamber Portal")
    
    if not state.get("castle_gates_open", True):
        st.error("🏰 **THE CASTLE GATES ARE CURRENTLY CLOSED!**")
        st.warning("High Host Neilio has barred entry to the player portals. Stand by in the Great Hall until the gates are reopened.")
    else:
        if "logged_in_player" in st.session_state and st.session_state["logged_in_player"] in state["players"]:
            selected_player = st.session_state["logged_in_player"]
            st.success(f"🔓 Authenticated in the shadows as **{selected_player}**.")
            
            if st.button("🔒 Lock Portal & Switch User"):
                del st.session_state["logged_in_player"]
                st.rerun()

            with st.expander("📸 Upload or Update Your Profile Photo", expanded=False):
                uploaded_file = st.file_uploader("Choose a photo (JPEG/PNG)", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    state["players"][selected_player]["photo"] = f"data:image/jpeg;base64,{base64.b64encode(uploaded_file.getvalue()).decode('utf-8')}"
                    save_state(state)
                    st.success("✨ Portrait updated!")
                    st.rerun()
                if state["players"][selected_player].get("photo"): 
                    st.image(state["players"][selected_player]["photo"], width=100)

            render_player_portal_view(selected_player)
        else:
            st.caption("Select your name and enter your personal 4-digit PIN to unlock your portal session.")
            col1, col2 = st.columns(2)
            login_player = col1.selectbox("Select Your Name", list(state["players"].keys()), key="login_player_select")
            entered_pin = col2.text_input("Enter PIN", type="password", key="login_pin_input")

            if st.button("Unlock Portal 🗝️", key="unlock_portal_btn"):
                p_info = state["players"][login_player]
                if entered_pin and entered_pin == str(p_info.get("pin", "")):
                    st.session_state["logged_in_player"] = login_player
                    login_entry = {"player": login_player, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "day": day_key}
                    state.setdefault("login_history", []).append(login_entry)
                    save_state(state)
                    send_login_alert(login_player)
                    st.success(f"Welcome back, {login_player}!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect PIN.")

# ==========================================
# TAB 5: CHAMBER OF RELICS
# ==========================================
elif nav == "💍 Chamber of Relics":
    st.title("💍 The Alchemist's Chamber of Relics")
    if state.get("chamber_of_relics_locked", True):
        st.warning("🔒 **THE CHAMBER OF RELICS IS SEALED!**")
    elif "logged_in_player" not in st.session_state or st.session_state["logged_in_player"] not in state["players"]:
        st.error("🔒 **PORTAL LOCKED:** You must log into your Player Portal using your 4-digit PIN before you can enter the Chamber of Relics!")
    else:
        r_player = st.session_state["logged_in_player"]
        st.success(f"🔑 Authenticated in the Chamber as: **{r_player}**")

        p_dat = state["players"][r_player]
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
                            ans = st.text_input("Name Keyword:", key=f"relic_ans_{r_player}_{b_key}")
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
                            item_found_desc = b_info['name']
                            state["players"][r_player].setdefault("claimed_items", []).append({
                                "day": "Chamber of Relics", "box": b_key, "desc": item_found_desc, "time": datetime.now().strftime("%H:%M")
                            })
                            state.setdefault("host_item_audit", []).append({
                                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "player": r_player,
                                "source": f"Chamber of Relics ({b_key})",
                                "item": item_found_desc
                            })
                            save_state(state)
                            st.balloons()
                            st.success("🎉 Claimed!")
                            st.rerun()

# ==========================================
# TAB 6: VOTING MATRIX
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
# TAB 7: THE GRAND REVEAL (FINALE)
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
# TAB 8: HOST CONTROL CENTRE
# ==========================================
elif nav == "👑 Host Control (Neilio)":
    st.title("👑 Neilio's High Host Sanctuary")
    host_pin_input = st.text_input("Enter Host Master PIN", type="password", key="host_pin_secure_input")
    if host_pin_input == HOST_PIN:
        st.success("Sanctuary unlocked.")
        
        # --- HOST ITEM TRANSFER / REALLOCATION DESK ---
        st.markdown("---")
        st.subheader("🔄 Host Item & Relic Transfer Desk")
        st.markdown("Transfer an item or relic from one player's inventory to another player.")
        
        with st.form("host_item_transfer_form"):
            col_t1, col_t2, col_t3 = st.columns(3)
            from_player = col_t1.selectbox("From Player:", list(state["players"].keys()), key="transfer_from_sel")
            
            source_claimed = state["players"][from_player].get("claimed_items", [])
            source_item_descs = [item["desc"] for item in source_claimed] if source_claimed else ["No items in inventory"]
            
            item_to_transfer = col_t2.selectbox("Select Item to Transfer:", source_item_descs, key="transfer_item_sel")
            to_player = col_t3.selectbox("To Player:", list(state["players"].keys()), key="transfer_to_sel")
            
            if st.form_submit_button("🔄 Transfer Item Between Players"):
                if not source_claimed or item_to_transfer == "No items in inventory":
                    st.error("Source player has no items to transfer!")
                elif from_player == to_player:
                    st.error("Cannot transfer an item to the same player!")
                else:
                    transferred_item = None
                    for idx, item in enumerate(source_claimed):
                        if item["desc"] == item_to_transfer:
                            transferred_item = source_claimed.pop(idx)
                            break
                    
                    if transferred_item:
                        state["players"][to_player].setdefault("claimed_items", []).append(transferred_item)
                        
                        if "Shield" in transferred_item["desc"]:
                            if "Secret" in transferred_item["desc"] or "Armor" in transferred_item["desc"]:
                                state["players"][from_player]["shield"] = False
                                state["players"][to_player]["shield"] = True
                            elif "Public" in transferred_item["desc"]:
                                state["players"][from_player]["public_shield"] = False
                                state["players"][to_player]["public_shield"] = True
                        
                        state.setdefault("host_item_audit", []).append({
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "player": f"{from_player} ➔ {to_player}",
                            "source": "Host Transfer Desk",
                            "item": transferred_item["desc"]
                        })
                        save_state(state)
                        st.success(f"✅ Successfully transferred **{item_to_transfer}** from **{from_player}** to **{to_player}**!")
                        st.rerun()
                    else:
                        st.error("Item could not be located in source inventory.")

        # --- HOST RELIC & SPECIAL ITEM ALLOCATOR ---
        st.markdown("---")
        st.subheader("🛡️ Host Relic & Special Item Allocator")
        st.markdown("Manually assign shields, brooches, or game-changing relics directly to any player's inventory or active armor status.")
        
        with st.form("host_relic_allocator_form"):
            target_player = st.selectbox("Select Player:", list(state["players"].keys()), key="alloc_player_sel")
            item_categories = ["Secret Shield (Hidden Armour)", "Public Shield (Portrait Wall Armour)", "🪶 Phoenix Feather Brooch (Revival Relic)", "⏳ Hourglass Pendant", "💍 Ring of Truth", "📜 Amulet of Cleansing Fire", "👑 Crown of Thorns", "Custom Relic / Item"]
            selected_item_type = st.selectbox("Select Item to Allocate:", item_categories, key="alloc_item_sel")
            custom_item_name = st.text_input("Custom Item Name (if Custom selected):", value="", key="alloc_custom_name")
            
            if st.form_submit_button("🎁 Grant Item to Player"):
                p_dict = state["players"][target_player]
                assigned_desc = ""
                
                if "Secret Shield" in selected_item_type:
                    p_dict["shield"] = True
                    assigned_desc = "🔒 Secret Shield (Armor)"
                elif "Public Shield" in selected_item_type:
                    p_dict["public_shield"] = True
                    assigned_desc = "🛡️ Public Shield (Armor)"
                elif "Custom" in selected_item_type and custom_item_name.strip():
                    assigned_desc = custom_item_name.strip()
                else:
                    assigned_desc = selected_item_type
                
                p_dict.setdefault("claimed_items", []).append({
                    "day": day_key, "box": "Host Grant", "desc": f"✨ Granted by Host: {assigned_desc}", "time": datetime.now().strftime("%H:%M")
                })
                state.setdefault("host_item_audit", []).append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "player": target_player,
                    "source": "Host Manual Grant",
                    "item": assigned_desc
                })
                save_state(state)
                st.success(f"✅ Successfully granted **{assigned_desc}** to **{target_player}**!")
                st.rerun()

        # --- HOST AUDIO SOUNDBOARD ---
        st.markdown("---")
        st.subheader("🎶 Host Dramatic Soundboard & Audio Library")
        song_uploader = st.file_uploader("Upload New MP3 Song", type=["mp3"], key="host_audio_uploader")
        if song_uploader is not None:
            song_name = song_uploader.name
            with open(song_name, "wb") as f:
                f.write(song_uploader.getbuffer())
            state.setdefault("custom_songs", {})[song_name] = song_name
            save_state(state)
            st.success(f"✅ Successfully uploaded and added **{song_name}**!")
            st.rerun()

        custom_songs = state.setdefault("custom_songs", {"traitors_theme.mp3": "traitors_theme.mp3"})
        existing_songs = [s for s in custom_songs.keys() if os.path.exists(s)]
        if existing_songs:
            selected_song = st.selectbox("Select Audio Track:", existing_songs, key="host_audio_track_sel")
            col_play, col_stop = st.columns(2)
            if col_play.button("🎵 Play Track 🎶", key="host_play_audio_btn"):
                st.audio(selected_song, format="audio/mp3", autoplay=True)
                st.success(f"🎶 Playing **{selected_song}**!")
            if col_stop.button("⏹️ Stop / Silence Music", key="host_stop_audio_btn"):
                st.audio("", format="audio/mp3")
                st.info("⏹️ Music stopped.")

        st.markdown("---")
        st.subheader("📦 Host Global Item & Discovery Audit Log")
        item_audit_log = state.setdefault("host_item_audit", [])
        if item_audit_log:
            st.dataframe(pd.DataFrame(item_audit_log), use_container_width=True, hide_index=True)
        else:
            st.info("No items have been found or received yet.")

        synth_vault_key = f"Day {state['current_day']}"
        st.markdown("---")
        st.subheader(f"🏦 Host Armoury Box Grid & Control ({synth_vault_key})")
        current_vault_data = state["vault_contents"].setdefault(synth_vault_key, {})
        if not current_vault_data:
            alive_c = sum(1 for d in state["players"].values() if str(d.get("status", "")) in ["Alive", "Undead"])
            state["vault_contents"][synth_vault_key] = initialize_vault_boxes(synth_vault_key, max(alive_c * 3, 15), state["vault_config"], current_state=state)
            save_state(state)
            current_vault_data = state["vault_contents"][synth_vault_key]

        if current_vault_data:
            vault_rows = []
            for b_num, b_dat in sorted(current_vault_data.items(), key=lambda x: int(x[0])):
                vault_rows.append({
                    "Box #": int(b_num),
                    "Type": b_dat.get("type"),
                    "Description": b_dat.get("desc"),
                    "Opened Status": "Opened 🔒" if b_dat.get("opened") else "Closed 📦",
                    "Opened By": b_dat.get("opened_by", "—")
                })
            st.dataframe(pd.DataFrame(vault_rows).sort_values("Box #"), use_container_width=True, hide_index=True)
            
            if st.button("🎲 Randomise Armoury Boxes Now", key="host_randomise_boxes_btn"):
                alive_c = sum(1 for d in state["players"].values() if str(d.get("status", "")) in ["Alive", "Undead"])
                state["vault_contents"][synth_vault_key] = initialize_vault_boxes(synth_vault_key, max(alive_c * 3, 15), state["vault_config"], current_state=state)
                save_state(state)
                st.success("🎲 Armoury boxes successfully randomised!")
                st.rerun()

        # --- HOST ARMOURY RIDDLE EDITOR ---
        st.markdown("---")
        st.subheader("🧩 Host Armoury Daily Riddle Editor")
        riddle_day_sel = st.selectbox("Select Day to Edit Armoury Riddle:", [f"Day {i}" for i in range(1, 13)], index=state["current_day"] - 1, key="host_riddle_day_sel")
        current_day_riddle = state.setdefault("vault_riddles", {}).setdefault(riddle_day_sel, {"question": "Enter riddle.", "answer": "wish"})

        with st.form("host_edit_riddle_form"):
            new_riddle_q = st.text_area("Armoury Riddle Question:", value=current_day_riddle.get("question", ""), key="host_riddle_q_input")
            new_riddle_a = st.text_input("Correct Answer Keyword(s) (comma-separated):", value=current_day_riddle.get("answer", ""), key="host_riddle_a_input")
            if st.form_submit_button(f"💾 Save Riddle for {riddle_day_sel}"):
                state["vault_riddles"][riddle_day_sel] = {
                    "question": new_riddle_q.strip(),
                    "answer": new_riddle_a.strip().lower()
                }
                save_state(state)
                st.success(f"✅ Successfully updated Armoury Gatekeeper Riddle for **{riddle_day_sel}**!")
                st.rerun()

        st.markdown("---")
        st.subheader("💍 Host Relic Chamber & Riddle Editor")
        relics_config_dict = state["relics_config"].setdefault("riddles", {})
        selected_relic_box = st.selectbox("Select Relic Box to Edit:", list(relics_config_dict.keys()), key="host_relic_box_sel")
        r_info = relics_config_dict[selected_relic_box]
        
        with st.form("edit_relic_form"):
            new_r_name = st.text_input("Relic Name / Item:", value=r_info["name"], key="host_relic_name_input")
            new_r_clue = st.text_area("Riddle / Clue:", value=r_info["clue"], key="host_relic_clue_input")
            new_r_ans = st.text_input("Correct Keywords (comma separated):", value=r_info["answer"], key="host_relic_ans_input")
            if st.form_submit_button("💾 Save & Sync Relic Box Changes"):
                relics_config_dict[selected_relic_box] = {
                    "name": new_r_name.strip(),
                    "clue": new_r_clue.strip(),
                    "answer": new_r_ans.strip().lower()
                }
                if selected_relic_box in state["relics_vault_contents"]:
                    state["relics_vault_contents"][selected_relic_box]["name"] = new_r_name.strip()
                    state["relics_vault_contents"][selected_relic_box]["clue"] = new_r_clue.strip()
                save_state(state)
                st.success(f"✅ Successfully updated and synced **{selected_relic_box}**!")
                st.rerun()

        st.markdown("---")
        st.subheader("👁️ Castle Login Audit Log (Active & Past 24 Hours)")
        login_history = state.setdefault("login_history", [])
        recent_logins = [e for e in login_history if datetime.strptime(e["time"], "%Y-%m-%d %H:%M:%S") >= datetime.now() - timedelta(hours=24)]
        if recent_logins:
            st.dataframe(pd.DataFrame(recent_logins), use_container_width=True, hide_index=True)
        else:
            st.caption("No player logins recorded in the last 24 hours.")

        st.markdown("---")
        c_g1, c_g2, c_g3 = st.columns(3)
        state["castle_gates_open"] = c_g1.toggle("🔓 Castle Gates Open", value=state.get("castle_gates_open", True), key="host_toggle_gates")
        state["chamber_of_relics_locked"] = c_g2.toggle("🔒 Seal Chamber of Relics", value=state.get("chamber_of_relics_locked", True), key="host_toggle_relics")
        state["vault_room_open"] = c_g3.toggle("🏦 Vault Room Open", value=state.get("vault_room_open", True), key="host_toggle_vault")
        save_state(state)

        st.markdown("---")
        st.subheader("💀 Host Traitors' Bane Box Configuration")
        st.caption("Configure or toggle the Traitors' Bane box numbers for the currently selected day.")
        
        curse_day_sel = st.selectbox("Select Day for Bane Configuration:", [f"Day {i}" for i in range(1, 13)], index=state["current_day"] - 1, key="host_curse_day_sel")
        day_curse_config = state.setdefault("custom_curses", {}).setdefault(curse_day_sel, {
            "enabled": True,
            "traitors_bane_enabled": True,
            "boxes": ["3", "7", "12", "15", "19"]
        })

        with st.form("host_curse_config_form"):
            c_en, c_tb = st.columns(2)
            enable_curses = c_en.toggle("💀 Enable Cursed Boxes for this Day", value=day_curse_config.get("enabled", True), key="host_curse_en_toggle")
            traitors_bane_on = c_tb.toggle("🗡️ Enable 'Traitors' Bane' Trap (Lethal to Traitors)", value=day_curse_config.get("traitors_bane_enabled", True), key="host_tb_toggle")
            
            st.markdown("### 📦 Elect Traitors' Bane Box Numbers")
            current_boxes_str = ", ".join([str(b) for b in day_curse_config.get("boxes", ["3", "7", "12", "15", "19"])])
            boxes_input = st.text_input("Enter box numbers separated by commas:", value=current_boxes_str, key="host_cursed_boxes_input")

            save_curses_btn = st.form_submit_button("💾 Save Traitors' Bane Settings for " + curse_day_sel)
            if save_curses_btn:
                parsed_boxes = [b.strip() for b in boxes_input.split(",") if b.strip().isdigit()]
                day_curse_config["enabled"] = enable_curses
                day_curse_config["traitors_bane_enabled"] = traitors_bane_on
                day_curse_config["boxes"] = parsed_boxes
                save_state(state)
                st.success(f"✅ Successfully updated Traitors' Bane settings for {curse_day_sel}!")
                st.rerun()

        st.markdown("---")
        st.subheader("🕹️ Host Voting Phase & Non-Voter Controls")
        alive_names = [n for n, d in state["players"].items() if str(d.get("status", "")) in ["Alive", "Undead"]]
        current_non_voters = state["non_voters"].setdefault(day_key, [])
        
        valid_default_non_voters = [n for n in current_non_voters if n in alive_names]

        selected_non_voters = st.multiselect(
            f"Select players who did NOT vote for {day_key}:",
            options=alive_names,
            default=valid_default_non_voters,
            key="host_non_voters_multiselect"
        )
        if st.button("💾 Save Non-Voters List", key="host_save_non_voters_btn"):
            state["non_voters"][day_key] = selected_non_voters
            save_state(state)
            st.success("✅ Non-voters updated and sent to the Public Execution Room!")
            st.rerun()

        st.divider()
        c_v1, c_v2, c_v3 = st.columns(3)
        if c_v1.button("🟢 Start Voting Live", key="host_start_voting_btn"):
            state["voting_active"] = True
            save_state(state)
            st.success("Voting is now live for all players!")
            st.rerun()
        if c_v2.button("⏸️ Pause Voting", key="host_pause_voting_btn"):
            state["voting_active"] = False
            save_state(state)
            st.warning("Voting has been paused.")
            st.rerun()
        if c_v3.button("🔴 End Voting", key="host_end_voting_btn"):
            state["voting_active"] = False
            save_state(state)
            st.info("Voting ended.")
            st.rerun()

        # --- LIVE HOST VOTING TALLY BOARD (NEW) ---
        st.markdown("---")
        st.subheader(f"📊 Live Host Voting Tally ({day_key})")
        host_votes = state["votes"].get(day_key, {})
        if host_votes:
            host_tally = {}
            for voter_raw, vdata in host_votes.items():
                clean_voter = voter_raw.replace("🔒 [ANONYMOUS SHADOW — ", "").replace("]", "")
                target = vdata["target"]
                host_tally[target] = host_tally.get(target, 0) + 1
                st.markdown(f"• 🕯️ **{clean_voter}** voted for **{target}** (*\"{vdata['reason']}\"*)")
            
            st.markdown("---")
            st.markdown("**Current Vote Counts:**")
            for t_name, t_count in sorted(host_tally.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"• **{t_name}**: `{t_count} vote(s)`")
        else:
            st.info("No votes have been locked in by players yet for today.")

        # --- HOST CHAT LOCK TOGGLE ---
        st.markdown("---")
        st.subheader("💬 Round Table Chat Control")
        state["chat_locked"] = st.toggle("🔒 Lock Round Table Chat Room (Suspend Messages)", value=state.get("chat_locked", False), key="host_chat_lock_toggle")
        save_state(state)

        st.markdown("---")
        st.subheader("👻 Execute Non-Voter (Ghost Strike)")
        if st.button("🪓 Tally Execution Votes & Execute Most Voted", key="host_exec_voter_btn"):
            pub_exec_votes = state["public_execution"].get(day_key, {})
            tally = {}
            for v in pub_exec_votes.values():
                tally[v] = tally.get(v, 0) + 1
            if tally:
                max_v = max(tally.values())
                top_t = [t for t, c in tally.items() if c == max_v]
                if len(top_t) > 1:
                    st.error(f"⚖️ **TIE DETECTED IN EXECUTION:** Between: {', '.join(top_t)}. Automatic re-vote required!")
                else:
                    victim = top_t[0]
                    state["players"][victim]["status"] = "Executed (No Vote Penalty)"
                    state["players"][victim]["eliminated_day"] = day_key
                    save_state(state)
                    st.error(f"👻 **GHOST STRIKE!** {victim} received {max_v} execution votes and has been instantly struck down by the Ghost!")
            else:
                st.warning("No execution votes recorded.")

        st.markdown("---")
        st.subheader("1. Game Day, Phase & Decrees")
        c1, c2, c3, c4 = st.columns(4)
        new_day = c1.number_input("Day", 1, 12, state["current_day"], key="host_new_day_input")
        new_phase = c2.selectbox("Phase", PHASES, index=PHASES.index(state["phase"]) if state["phase"] in PHASES else 0, key="host_new_phase_sel")
        new_fp = c3.number_input("Fire Pit Round", 1, 5, state.get("fire_pit_round", 1), key="host_new_fp_input")
        new_pot = c4.number_input("Prize Pot", value=state["prize_pot"], step=50, key="host_new_pot_input")
        new_head = st.text_input("Headline", state["headline"], key="host_new_headline_input")
        new_miss = st.text_area("Mission Text", state["mission_text"], key="host_new_mission_input")
        if st.button("💾 Save State & Decrees", key="host_save_decrees_btn"):
            state.update({"current_day": new_day, "phase": new_phase, "fire_pit_round": new_fp, "prize_pot": new_pot, "headline": new_head, "mission_text": new_miss})
            save_state(state)
            st.success("Updated!")
            st.rerun()

        st.markdown("---")
        st.subheader("3. Manage Roster & Roles")
        roster_rows = [{"Player Name": n, "PIN": d.get("pin"), "Role": d.get("role"), "Status": d.get("status"), "Eliminated On": d.get("eliminated_day")} for n, d in state["players"].items()]
        edited_df = st.data_editor(pd.DataFrame(roster_rows), use_container_width=True, hide_index=True, key="host_roster_editor")
        if st.button("💾 Save Roster", key="host_save_roster_btn"):
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

        st.markdown("---")
        st.subheader("4. ☁️ Castle Vault Backup & Restore Sanctuary")
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        
        with b_col1:
            json_bytes = json.dumps(state, indent=4).encode("utf-8")
            st.download_button(
                label="⬇️ Download Backup",
                data=json_bytes,
                file_name=f"castle_state_day_{state['current_day']}.json",
                mime="application/json",
                key="host_download_backup_btn"
            )
            
        with b_col2:
            if st.button("🔄 Restore Last Checkpoint", key="host_restore_checkpoint_btn"):
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
            if st.button("⚠️ Reset to Day 1 Defaults", key="host_reset_day1_btn"):
                reset_state = get_default_state()
                save_state(reset_state)
                st.warning("Castle reset to Day 1 defaults.")
                st.rerun()

        with b_col4:
            uploaded_file = st.file_uploader("⬆️ Upload JSON", type=["json"], label_visibility="collapsed", key="host_upload_json_file")
            if uploaded_file is not None:
                if st.button("🔄 Confirm File Upload", key="host_confirm_upload_btn"):
                    restored_state = json.load(uploaded_file)
                    save_state(restored_state)
                    st.success("✅ Vault successfully restored from uploaded file!")
                    st.rerun()

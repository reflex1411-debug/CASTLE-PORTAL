import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# PAGE CONFIG & CASTLE STYLING
# ==========================================
st.set_page_config(
    page_title="The Traitors: Castle Portal",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .player-card {
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 14px;
        text-align: center;
        border: 2px solid #d4af37;
        background-color: #1a1c23;
        color: #f0f0f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }
    .player-dead {
        border: 2px solid #555555;
        background-color: #111217;
        color: #777777;
        opacity: 0.7;
    }
    .finale-banner-traitor {
        border-radius: 14px;
        padding: 28px;
        text-align: center;
        background: linear-gradient(135deg, #4a0000 0%, #1a0000 100%);
        border: 3px solid #ff4b4b;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 8px 20px rgba(255, 75, 75, 0.35);
    }
    .finale-banner-faithful {
        border-radius: 14px;
        padding: 28px;
        text-align: center;
        background: linear-gradient(135deg, #0b3d20 0%, #071f10 100%);
        border: 3px solid #d4af37;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.35);
    }
    .award-card {
        border-radius: 10px;
        padding: 18px;
        background-color: #1e2129;
        border: 1px solid #d4af37;
        text-align: center;
        color: #f0f0f0;
    }
    .role-traitor {
        color: #ff4b4b;
        font-weight: bold;
    }
    .role-faithful {
        color: #4da6ff;
        font-weight: bold;
    }
    .role-hidden {
        color: #ffb703;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA PERSISTENCE & HOST CONFIG
# ==========================================
DATA_FILE = "castle_state.json"
HOST_PIN = "1411"  # <--- Set to Neilio's Host PIN!

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
        "headline": "Welcome to the Castle, Neilio's subjects! Check your secret role in the Player Portal and complete Mission 1.",
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
st.sidebar.title("🕯️ THE CASTLE PORTAL")
st.sidebar.markdown(f"**Host:** Neilio 👑")
st.sidebar.markdown(f"**Current Day:** Day {state['current_day']} of 10")
st.sidebar.markdown(f"**Current Phase:** `{state['phase']}`")

alive_count = sum(1 for p in state["players"].values() if p["status"] == "Alive")
st.sidebar.metric("🟢 Survivors in the Castle", f"{alive_count} / {len(state['players'])}")
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
    st.title("🏰 The Traitors: Castle Hall")
    st.info(f"📢 **LATEST CASTLE DECREE (Neilio):** {state['headline']}")

    if is_finale_unlocked:
        st.success("🏆 **THE GRAND FINALE IS LIVE!** Click **'🏆 The Grand Reveal (4PM Finale)'** in the sidebar to see who won and unmask every player!")
    elif state["phase"] == "The Fire Pit (Endgame)":
        st.error(f"🔥 **THE FIRE PIT IS LIT (Round {state['fire_pit_round']})!** Head to the Player Portal to throw your Green or Red pouch into the flames.")

    with st.expander("📜 Today's Daily Mission / Endgame Rules", expanded=True):
        st.markdown(state["mission_text"])

    st.subheader("🖼️ Portraits on the Wall")
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
                <div style="font-size: 28px;">🧑{shield_badge}</div>
                <div style="font-weight: bold; font-size: 16px; margin-top: 4px;">{name}</div>
                <div style="color: #4CAF50; font-size: 13px;">🟢 Finalist / Alive</div>
                <div class="{role_class}" style="font-size: 12px; margin-top: 4px;">{revealed_role}</div>
            </div>
            """
        else:
            icon = "💀" if status == "Murdered" else "🔴"
            revealed_role, role_class = get_public_identity(pdata, force_reveal=is_finale_unlocked)
            card_html = f"""
            <div class="player-card player-dead">
                <div style="font-size: 28px;">{icon}</div>
                <div style="font-weight: bold; font-size: 16px; margin-top: 4px; text-decoration: line-through;">{name}</div>
                <div style="font-size: 13px;">{status} ({pdata['eliminated_day']})</div>
                <div class="{role_class}" style="font-size: 12px; margin-top: 4px;">{revealed_role}</div>
            </div>
            """
        col.markdown(card_html, unsafe_allow_html=True)

# ==========================================
# TAB 2: PLAYER PORTAL
# ==========================================
elif nav == "🗳️ Player Portal (Vote & Role)":
    st.title("🗝️ Secret Player Portal")
    st.caption("Select your name and enter your personal 4-digit PIN to view your role, check for Shields, or cast your vote.")

    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Select Your Name", list(state["players"].keys()))
    entered_pin = col2.text_input("Enter Your 4-Digit PIN", type="password")

    if entered_pin:
        p_info = state["players"][selected_player]
        if entered_pin != p_info["pin"]:
            st.error("❌ Incorrect PIN. Check with Host Neilio if you forgot your PIN.")
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
                    st.warning("👻 Only surviving finalists stand at the Fire Pit!")
                else:
                    st.markdown(
                        "Throw **🟢 END GAME** if you believe only Faithfuls remain (or if you are a Traitor ready to steal the pot!). "
                        "If **even one player** throws **🔴 BANISH AGAIN**, the group must immediately banish another player."
                    )
                    existing_fp = state["fire_pit_votes"].get(fp_key, {}).get(selected_player, {})
                    
                    with st.form("fire_pit_form"):
                        fp_choice = st.radio(
                            "Choose your pouch to throw into the fire:",
                            ["🟢 END GAME", "🔴 BANISH AGAIN"],
                            index=0 if existing_fp.get("choice", "🟢 END GAME") == "🟢 END GAME" else 1
                        )
                        fp_reason = st.text_input(
                            "1-Sentence Final Statement (read aloud when flames change colour):",
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
                    st.warning("👻 Ghosts cannot vote at the Round Table!")
                elif state["phase"] != "Round Table Voting":
                    st.info(f"The Round Table ballot box is currently closed (Current Phase: **{state['phase']}**).")
                else:
                    alive_targets = [
                        name for name, d in state["players"].items() 
                        if d["status"] == "Alive" and name != selected_player
                    ]
                    existing_vote = state["votes"].get(day_key, {}).get(selected_player, {})
                    
                    with st.form("vote_form"):
                        target = st.selectbox(
                            "Who are you voting to BANISH from the Castle?", 
                            alive_targets,
                            index=alive_targets.index(existing_vote["target"]) if existing_vote.get("target") in alive_targets else 0
                        )
                        reason = st.text_input(
                            "1-Sentence Reason (will be read aloud in WhatsApp):",
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
                                st.success(f"✅ Your vote to banish **{target}** has been locked in!")

            if "Traitor" in p_info["role"] and p_info["status"] == "Alive":
                st.divider()
                st.subheader("🗡️ The Traitors' Turret (Secret Access)")
                fellow_traitors = [
                    n for n, d in state["players"].items() 
                    if "Traitor" in d["role"] and d["status"] == "Alive"
                ]
                st.markdown(f"**Surviving Traitors:** {', '.join(fellow_traitors)} | **Traitor Bonus Pot:** `{state['traitor_pot']} pts`")
                
                faithful_targets = [
                    n for n, d in state["players"].items()
                    if "Traitor" not in d["role"] and d["status"] == "Alive" and not d.get("public_shield")
                ]
                
                current_turret = state["turret_targets"].get(day_key, {})
                if current_turret:
                    st.write("**Current Overnight Murder Nominations:**")
                    for t_name, victim in current_turret.items():
                        st.write(f"• 🗡️ **{t_name}** wants to murder: **{victim}**")

                if faithful_targets:
                    murder_choice = st.selectbox("Nominate Tonight's Murder Victim:", faithful_targets)
                    if st.button("Lock In Murder Nomination 🩸"):
                        state["turret_targets"].setdefault(day_key, {})[selected_player] = murder_choice
                        save_state(state)
                        st.rerun()

# ==========================================
# TAB 3: VOTING MATRIX
# ==========================================
elif nav == "📊 The Voting Matrix":
    st.title("📊 Official Castle Voting Matrix")
    st.caption("Every Round Table vote cast so far. Votes against confirmed Traitors are marked with 🎯.")

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
    st.title("🏆 The Traitors: Grand Finale & Role Reveal")

    if not is_finale_unlocked:
        st.warning("🔒 **THE GRAND REVEAL IS CURRENTLY LOCKED!**")
        st.markdown(
            "Gather round the Fire Pit! Host Neilio will unlock this screen at **16:00 on Finale Friday** "
            "once the final pouches have been thrown into the flames."
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
                <h1 style="margin:0; font-size: 38px;">🗡️ THE TRAITORS PREVAIL! 🗡️</h1>
                <p style="font-size: 20px; margin-top: 10px;">
                    Deception triumphs! <b>{winner_names}</b> survived the Fire Pit undetected and stole the entire <b>{state['prize_pot']} pt</b> Prize Pot!
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.balloons()
            winner_names = ", ".join(surviving_faithfuls)
            st.markdown(f"""
            <div class="finale-banner-faithful">
                <h1 style="margin:0; font-size: 38px;">🕯️ THE FAITHFULS PREVAIL! 🕯️</h1>
                <p style="font-size: 20px; margin-top: 10px;">
                    Every single Traitor was banished! <b>{winner_names}</b> share the <b>{state['prize_pot']} pt</b> Prize Pot in glorious victory!
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
                <div style="font-weight: bold; font-size: 18px; margin-top: 6px;">{name}</div>
                <div class="{role_cls}" style="font-size: 16px; margin-top: 6px;">{badge}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.subheader("🗡️ Complete Roll Call of the Traitors")
        all_traitors = [(n, d) for n, d in state["players"].items() if "Traitor" in d["role"]]
        t_cols = st.columns(max(len(all_traitors), 1))
        for idx, (t_name, t_data) in enumerate(all_traitors):
            fate = "🏆 WON AT THE FIRE PIT" if t_data["status"] == "Alive" else f"🔴 Banished ({t_data['eliminated_day']})"
            t_cols[idx].markdown(f"""
            <div class="award-card">
                <div style="font-size: 24px;">🗡️ <b>{t_name}</b></div>
                <div style="color: #ff4b4b; font-size: 14px; margin-top: 4px;">{t_data['role']}</div>
                <div style="color: #ccc; font-size: 13px; margin-top: 6px;">{fate}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.subheader("🏅 Official Castle Honours & Superlatives")
        best_detective, scapegoat, stealth_traitor = compute_superlatives(state)
        a_col1, a_col2, a_col3 = st.columns(3)

        a_col1.markdown(f"""
        <div class="award-card">
            <div style="font-size: 28px;">🕵️‍♂️</div>
            <div style="font-weight: bold; color: #d4af37;">Chief Castle Detective</div>
            <div style="font-size: 20px; margin: 6px 0;"><b>{best_detective[0]}</b></div>
            <div style="font-size: 13px; color: #aaa;">Cast <b>{best_detective[1]}</b> vote(s) directly against Traitors!</div>
        </div>
        """, unsafe_allow_html=True)

        a_col2.markdown(f"""
        <div class="award-card">
            <div style="font-size: 28px;">🐐</div>
            <div style="font-weight: bold; color: #d4af37;">The Ultimate Scapegoat</div>
            <div style="font-size: 20px; margin: 6px 0;"><b>{scapegoat[0]}</b></div>
            <div style="font-size: 13px; color: #aaa;">Received <b>{scapegoat[1]}</b> Round Table votes across the game!</div>
        </div>
        """, unsafe_allow_html=True)

        a_col3.markdown(f"""
        <div class="award-card">
            <div style="font-size: 28px;">🎭</div>
            <div style="font-weight: bold; color: #d4af37;">Master of the Shadows</div>
            <div style="font-size: 20px; margin: 6px 0;"><b>{stealth_traitor[0]}</b></div>
            <div style="font-size: 13px; color: #aaa;">Traitor with only <b>{stealth_traitor[1]}</b> total vote(s) cast against them!</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 5: HOST CONTROL CENTRE
# ==========================================
elif nav == "👑 Host Control (Neilio)":
    st.title("👑 Neilio's Host Control Centre")
    admin_pin = st.text_input("Enter Host Master PIN", type="password")
    
    if admin_pin == HOST_PIN:
        st.success("Host Controls Unlocked, Neilio.")
        
        st.subheader("1. Game Day, Phase & Announcements")
        c1, c2, c3, c4 = st.columns(4)
        new_day = c1.number_input("Current Day (1-12)", min_value=1, max_value=12, value=state["current_day"])
        new_phase = c2.selectbox(
            "Current Phase", 
            PHASES,
            index=PHASES.index(state["phase"]) if state["phase"] in PHASES else 0
        )
        new_fp_round = c3.number_input("Fire Pit Round", min_value=1, max_value=5, value=state.get("fire_pit_round", 1))
        new_pot = c4.number_input("Faithful Prize Pot", value=state["prize_pot"], step=50)
        
        new_headline = st.text_input("Castle Hall Banner Headline", value=state["headline"])
        new_mission = st.text_area("Daily Mission / Endgame Instructions", value=state["mission_text"])
        
        if st.button("💾 Save Game Phase & Announcements"):
            state["current_day"] = new_day
            state["phase"] = new_phase
            state["fire_pit_round"] = new_fp_round
            state["prize_pot"] = new_pot
            state["headline"] = new_headline
            state["mission_text"] = new_mission
            save_state(state)
            st.success("Updated!")
            st.rerun()

        st.divider()

        col_rt, col_fp = st.columns(2)
        alive_players = [n for n, d in state["players"].items() if d["status"] == "Alive"]

        with col_rt:
            st.subheader(f"2A. Round Table Tally ({day_key})")
            day_votes = state["votes"].get(day_key, {})
            voted_players = list(day_votes.keys())
            missing_voters = [n for n in alive_players if n not in voted_players]

            st.write(f"**Votes Cast:** {len(voted_players)} / {len(alive_players)}")
            if missing_voters:
                st.warning(f"⏳ **Waiting on:** {', '.join(missing_voters)}")
            
            if day_votes:
                tally = {}
                whatsapp_lines = [f"🕯️ *THE ROUND TABLE VOTES ARE IN ({day_key.upper()})* — *Host: Neilio* 🕯️\n"]
                for voter, vdata in day_votes.items():
                    target = vdata["target"]
                    tally[target] = tally.get(target, 0) + 1
                    whatsapp_lines.append(f"• *{voter}* voted for *{target}*: _\"{vdata['reason']}\"_")
                
                sorted_tally = sorted(tally.items(), key=lambda x: x[1], reverse=True)
                whatsapp_lines.append("\n📜 *FINAL VOTE COUNT:*")
                for cand, count in sorted_tally:
                    whatsapp_lines.append(f"• *{cand}*: {count} vote(s)")
                
                top_candidate = sorted_tally[0][0]
                if state["current_day"] >= 10:
                    whatsapp_lines.append(f"\n🔴 With the most votes, *{top_candidate}* has been BANISHED by Neilio's decree. Because we are in the Endgame, you will *NOT* reveal your identity...")
                else:
                    whatsapp_lines.append(f"\n🔴 With the most votes, *{top_candidate}* has been BANISHED by Neilio's decree. Step forward and reveal your true identity...")

                st.code("\n".join(whatsapp_lines), language="markdown")

        with col_fp:
            st.subheader(f"2B. 🔥 Fire Pit & 4PM Finale Scripts")
            fp_votes = state["fire_pit_votes"].get(fp_key, {})
            if fp_votes:
                red_count = sum(1 for v in fp_votes.values() if "RED" in v["choice"] or "BANISH" in v["choice"])
                fp_lines = [f"🔥 *THE FIRE PIT OF TRUTH ({fp_key.upper()})* — *Host: Neilio* 🔥\n"]
                for voter, vdata in fp_votes.items():
                    fp_lines.append(f"• *{voter}* threw *{vdata['choice']}*: _\"{vdata['reason']}\"_")
                
                if red_count > 0:
                    fp_lines.append(f"\n🔴 *THE FLAMES BURN RED!* ({red_count} vote(s) to Banish Again).")
                    fp_lines.append("The game is NOT over! Head back to the Player Portal—Neilio demands an immediate Banishment vote!")
                else:
                    fp_lines.append("\n🟢 *THE FLAMES BURN UNANIMOUSLY GREEN!*")
                    fp_lines.append("The game is officially OVER! Open the Castle Portal now—Neilio has unlocked the 4PM Grand Reveal screen!")
                st.code("\n".join(fp_lines), language="markdown")

            surviving_traitors = [n for n in alive_players if "Traitor" in state["players"][n]["role"]]
            best_detective, scapegoat, stealth_traitor = compute_superlatives(state)
            finale_lines = ["🏆 *THE TRAITORS: GRAND FINALE REVEAL* — *Host: Neilio* 🏆\n"]
            finale_lines.append("The Fire Pit has spoken under Neilio's watch. Here are your surviving finalists unmasked:")
            for n in alive_players:
                r = state["players"][n]["role"]
                finale_lines.append(f"• *{n}*: {'🗡️ TRAITOR' if 'Traitor' in r else '🕯️ FAITHFUL'}")
            if surviving_traitors:
                finale_lines.append(f"\n😈 *THE TRAITORS WIN!* *{', '.join(surviving_traitors)}* deceived the Castle and stole the entire *{state['prize_pot']} pt* Prize Pot!")
            else:
                finale_lines.append(f"\n🕯️ *THE FAITHFULS WIN!* Every Traitor was banished, and *{', '.join(alive_players)}* share the *{state['prize_pot']} pt* Prize Pot!")
            finale_lines.append(f"\n🏅 *CASTLE HONOURS:*\n• 🕵️ Chief Detective: *{best_detective[0]}* ({best_detective[1]} Traitor votes)\n• 🐐 Ultimate Scapegoat: *{scapegoat[0]}* ({scapegoat[1]} votes received)\n• 🎭 Master of the Shadows: *{stealth_traitor[0]}* ({stealth_traitor[1]} votes against)")
            st.caption("👇 Copy this 4PM Grand Reveal script for WhatsApp:")
            st.code("\n".join(finale_lines), language="markdown")

        st.divider()

        st.subheader("3. Manage Players, Roles, Shields & Finale Eliminations")
        st.caption("Tip: If fewer than 37 people sign up, simply delete the extra unused rows or mark them as 'Banished' on Day 0 so they don't appear active!")
        
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

        if st.button("💾 Save Player Roster Changes"):
            updated_players = {}
            for _, row in edited_df.iterrows():
                updated_players[row["Player Name"]] = {
                    "pin": str(row["PIN"]),
                    "role": row["Role"],
                    "status": row["Status"],
                    "eliminated_day": row["Eliminated On"],
                    "shield": bool(row["Secret Shield"]),
                    "public_shield": bool(row["Public Shield"]),
                    "hide_role": bool(row["Hide Identity (Finale)"])
                }
            state["players"] = updated_players
            save_state(state)
            st.success("Player roster updated!")
            st.rerun()

        st.divider()

        st.subheader("4. ☁️ Cloud Backup & Restore")
        b_col1, b_col2, b_col3 = st.columns(3)
        
        with b_col1:
            json_bytes = json.dumps(state, indent=4).encode("utf-8")
            st.download_button(
                label=f"⬇️ Download Backup (Day {state['current_day']})",
                data=json_bytes,
                file_name=f"castle_state_day_{state['current_day']}.json",
                mime="application/json"
            )
            
        with b_col2:
            uploaded_file = st.file_uploader("⬆️ Restore from JSON Backup", type=["json"], label_visibility="collapsed")
            if uploaded_file is not None:
                if st.button("🔄 Confirm & Restore Backup"):
                    restored_state = json.load(uploaded_file)
                    save_state(restored_state)
                    st.success("✅ Backup restored successfully!")
                    st.rerun()

        with b_col3:
            if st.button("⚠️ Reset Entire Castle to Default (Day 1)"):
                reset_state = get_default_state()
                save_state(reset_state)
                st.warning("Game reset to Day 1 defaults.")
                st.rerun()

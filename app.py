import os
import math
import io
import json
import requests
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
import main_engine as engine

# Initialize widescreen desktop-free cloud layout environment configurations
st.set_page_config(page_title="Sisonke Football Analytics and Prediction", page_icon="⚽", layout="wide")

# Secure layout styling layer with native performance enhancements
CUSTOM_DASHBOARD_STYLING = """
<style>
.stApp { background-color: #0b0f19; color: #f1f5f9; }
h1 { color: #facc15; font-weight: 900 !important; font-size: 42px !important; margin: 0; padding-bottom: 5px; }
h3 { color: #facc15; font-weight: 700 !important; margin-top: 25px !important; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }
.metric-card { background-color: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: center; }
.metric-title { font-size: 13px; font-weight: 600; text-transform: uppercase; color:#94a3b8; }
.metric-value { font-size: 28px; font-weight: 800; line-height: 1; margin-top: 5px; }
.market-header { color: #38bdf8; font-weight: 700; font-size: 15px; text-transform: uppercase; border-bottom: 2px solid #0284c7; margin-bottom: 12px; }
.insight-box { background-color: #1e293b; border-left: 5px solid #eab308; padding: 15px; border-radius: 4px; margin-top: 15px; }
</style>
"""
st.markdown(CUSTOM_DASHBOARD_STYLING, unsafe_allow_html=True)
st.write("<h1>Sis⚽nke Football Analytics and Prediction</h1>", unsafe_allow_html=True)

# --- LIVE API-FOOTBALL QUOTA AND LIMIT MONITORING TOP ROW PANEL ---
if "api_quota_left" in st.session_state:
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        st.metric("API-Football Daily Limit Ceiling", f"{st.session_state.get('api_quota_max', '100')} Requests")
    with q_col2:
        st.metric("Remaining Available Calls (Safe Balance)", f"{st.session_state.get('api_quota_left', 'N/A')} Left")
    with q_col3:
        st.metric("Account Subscription Tier", f"{st.session_state.get('api_account_tier', 'Free / RapidAPI')}")
    st.markdown("---")

API_LEAGUE_ID_MAP = {
    "uefa champions league": 2, "south africa": 288, "england": 39, "scotland": 179, "spain": 140,
    "germany": 78, "italy": 135, "brazil": 71, "egypt": 233, "usa": 253,
    "argentina": 128, "austria": 218, "belgium": 144, "china": 169, 
    "croatia": 210, "denmark": 119, "finland": 244, "iceland": 230, 
    "netherlands": 88, "norway": 103, "poland": 106, "portugal": 94, "switzerland": 207
}

REQUIRED_COLUMNS = [
    "league_country", "match_timestamp", "home_team", "away_team", "home_goals", "away_goals",
    "home_sot", "away_sot", "home_big_chances", "away_big_chances", "home_box_touches", "away_box_touches",
    "home_through_passes", "away_through_passes", "home_final_third_entries", "away_final_third_entries",
    "home_interceptions", "away_interceptions", "home_recoveries", "away_recoveries", "home_saves", "away_saves",
    "home_ground_duels_won_pct", "away_ground_duels_won_pct", "home_aerial_duels_won_pct", "away_aerial_duels_won_pct",
    "home_dribbles_won_pct", "away_dribbles_won_pct", "home_tackles_won_pct", "away_tackles_won_pct",
    "home_passes_final_third_pct", "away_passes_final_third_pct", "home_rest_days", "away_rest_days"
]

with st.sidebar:
    st.markdown("### 📂 Data Control Room")
    uploaded_file = st.file_uploader("Upload Master Match CSV", type=["csv"])
    st.markdown("---")
    st.markdown("### 🔑 Free API Automation Sync")
    api_token_input = st.text_input("Enter Free API-Football Token Key:", type="password")
    target_sync_country = st.selectbox("Select Target Sync Country:", list(API_LEAGUE_ID_MAP.keys()))
    sync_mode = st.radio("Select Sync Target Scope:", ["Settled Historical Data", "Upcoming 14-Day Fixtures"])
    api_sync_triggered = st.button("🔄 Run Live League Sync")
    st.markdown("---")
    st.markdown("### 🚨 Live Notification Routes")
    ui_email_recipient = st.text_input("Primary Email:", value="vvuyo007@gmail.com")
    ui_sms_recipient = st.text_input("Mobile SMS:", value="0750739223@sms.telkom.co.za")
    ui_google_app_password = st.text_input("Password Key:", type="password", value="your_free_google_app_password")

is_valid_data, uploaded_leagues = False, []
if api_sync_triggered:
    if not api_token_input:
        st.error("⚠️ Token Missing!")
    else:
        with st.spinner("Connecting to servers... Executing Volumetric Background Extraction..."):
            try:
                league_id = API_LEAGUE_ID_MAP[target_sync_country.lower().strip()]
                current_year = datetime.datetime.now().year
                api_url = "https://api-sports.io"
                api_headers = {"x-rapidapi-key": api_token_input, "x-rapidapi-host": "v3.football.api-sports.io"}
                
                if "Upcoming" in sync_mode:
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    future_end = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
                    api_params = {"league": str(league_id), "season": str(current_year), "from": today, "to": future_end}
                else:
                    api_params = {"league": str(league_id), "season": str(current_year), "last": "20", "status": "FT"}
                    
                api_response = requests.get(api_url, headers=api_headers, params=api_params, timeout=15)
                api_data = api_response.json()
                
                # Capture metadata headers sent back by API-Football to feed top metrics
                res_headers = api_response.headers
                st.session_state["api_quota_max"] = res_headers.get("x-ratelimit-requests-limit", "100")
                st.session_state["api_quota_left"] = res_headers.get("x-ratelimit-requests-remaining", "N/A")
                st.session_state["api_account_tier"] = "Active Subscription" if int(res_headers.get("x-ratelimit-requests-limit", 0)) > 100 else "Free Plan Tier"
                
                compiled_api_rows = []
                if "response" in api_data and api_data["response"]:
                    for item in api_data["response"]:
                        f_meta, teams, goals = item["fixture"], item["teams"], item["goals"]
                        stats_list = item.get("statistics", [])
                        s_dict = {}
                        for s_entry in stats_list:
                            if "statistics" in s_entry and s_entry["team"]:
                                s_dict[s_entry["team"]["name"]] = {st_item["type"]: st_item["value"] for st_item in s_entry["statistics"]}
                        h_name, a_name = teams["home"]["name"], teams["away"]["name"]
                        h_s, a_s = s_dict.get(h_name, {}), s_dict.get(a_name, {})
                        
                        def get_pct(w, t):
                            if w is None or t is None: return 0.50
                            try:
                                return round(float(str(w).replace("%","")) / max(1.0, float(str(t).replace("%",""))), 2)
                            except: return 0.50
                        
                        row_dict = {
                            "league_country": target_sync_country, "match_timestamp": f_meta["date"],
                            "home_team": h_name, "away_team": a_name,
                            "home_goals": goals["home"] if goals["home"] is not None else np.nan,
                            "away_goals": goals["away"] if goals["away"] is not None else np.nan,
                            "home_sot": float(h_s.get("Shots on Goal", 0)) if "Upcoming" not in sync_mode else np.nan,
                            "away_sot": float(a_s.get("Shots on Goal", 0)) if "Upcoming" not in sync_mode else np.nan,
                            "home_big_chances": float(h_s.get("Big Chances Created", 0)) if "Upcoming" not in sync_mode else np.nan,
                            "away_big_chances": float(a_s.get("Big Chances Created", 0)) if "Upcoming" not in sync_mode else np.nan,
                            "home_box_touches": float(h_s.get("Touches in Opposition Box", 15)) if "Upcoming" not in sync_mode else np.nan,
                            "away_box_touches": float(a_s.get("Touches in Opposition Box", 15)) if "Upcoming" not in sync_mode else np.nan,
                            "home_through_passes": float(h_s.get("Through Passes", 2)) if "Upcoming" not in sync_mode else np.nan,
                            "away_through_passes": float(a_s.get("Through Passes", 2)) if "Upcoming" not in sync_mode else np.nan,
                            "home_final_third_entries": float(h_s.get("Final Third Entries", 35)) if "Upcoming" not in sync_mode else np.nan,
                            "away_final_third_entries": float(a_s.get("Final Third Entries", 35)) if "Upcoming" not in sync_mode else np.nan,
                            "home_interceptions": float(h_s.get("Interceptions", 12)) if "Upcoming" not in sync_mode else np.nan,
                            "away_interceptions": float(a_s.get("Interceptions", 12)) if "Upcoming" not in sync_mode else np.nan,
                            "home_recoveries": float(h_s.get("Ball Recoveries", 45)) if "Upcoming" not in sync_mode else np.nan,
                            "away_recoveries": float(a_s.get("Ball Recoveries", 45)) if "Upcoming" not in sync_mode else np.nan,
                            "home_saves": float(h_s.get("Goalkeeper Saves", 2)) if "Upcoming" not in sync_mode else np.nan,
                            "away_saves": float(a_s.get("Goalkeeper Saves", 2)) if "Upcoming" not in sync_mode else np.nan,
                            "home_ground_duels_won_pct": get_pct(h_s.get("Ground Duels Won"), h_s.get("Ground Duels Total")),
                            "away_ground_duels_won_pct": get_pct(a_s.get("Ground Duels Won"), a_s.get("Ground Duels Total")),
                            "home_aerial_duels_won_pct": get_pct(h_s.get("Aerial Duels Won"), h_s.get("Aerial Duels Total")),
                            "away_aerial_duels_won_pct": get_pct(a_s.get("Aerial Duels Won"), a_s.get("Aerial Duels Total")),
                            "home_dribbles_won_pct": get_pct(h_s.get("Successful Dribbles"), h_s.get("Total Dribbles")),
                            "away_dribbles_won_pct": get_pct(a_s.get("Successful Dribbles"), a_s.get("Total Dribbles")),
                            "home_tackles_won_pct": get_pct(h_s.get("Tackles Won"), h_s.get("Total Tackles")),
                            "away_tackles_won_pct": get_pct(a_s.get("Tackles Won"), a_s.get("Total Tackles")),
                            "home_passes_final_third_pct": get_pct(h_s.get("Passes Accurate"), h_s.get("Total Passes")),
                            "away_passes_final_third_pct": get_pct(a_s.get("Passes Accurate"), a_s.get("Total Passes")),
                            "home_rest_days": 5, "away_rest_days": 5
                        }
                        compiled_api_rows.append(row_dict)
                        
                if compiled_api_rows:
                    new_api_df = pd.DataFrame(compiled_api_rows)
                    st.session_state["api_downloaded_data"] = new_api_df
                    
                    storage_path = "master_sisonke_database.csv"
                    if os.path.exists(storage_path):
                        try:
                            existing_disk_df = pd.read_csv(storage_path)
                            combined_disk_df = pd.concat([existing_disk_df, new_api_df], ignore_index=True)
                            combined_disk_df.drop_duplicates(subset=["league_country", "match_timestamp", "home_team", "away_team"], keep="last", inplace=True)
                            combined_disk_df.to_csv(storage_path, index=False)
                            st.sidebar.success("💾 Server disk copy successfully updated in background layout.")
                        except Exception as disk_err:
                            st.sidebar.error(f"Write failure: {disk_err}")
                    else:
                        new_api_df.to_csv(storage_path, index=False)
                        st.sidebar.success("📁 Local database created on hard drive partition.")
                    st.success("⚡ SUCCESS! Network pull fully completed and saved to disk.")
                    st.rerun()
                else:
                    st.warning("⚠️ No data columns received.")
            except Exception as api_err:
                st.error(f"Handshake Timeout: {api_err}")
                # --- DATA CONTROL ROOM INPUT CONVERGENCE LAYER ---
full_validation_df = pd.DataFrame()
storage_path = "master_sisonke_database.csv"

if os.path.exists(storage_path):
    try:
        full_validation_df = pd.read_csv(storage_path)
        is_valid_data = True
    except:
        pass

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)
        raw_lines = [line.decode("utf-8").strip() for line in uploaded_file.readlines() if line.strip()]
        headers = raw_lines[0].split(",")
        target_column_count = len(headers)
        cleaned_rows = []
        for line in raw_lines:
            parts = line.split(",")
            cleaned_rows.append(",".join(parts[:target_column_count]))
        corrected_csv_data = io.StringIO("\n".join(cleaned_rows))
        manual_upload_df = pd.read_csv(corrected_csv_data)
        
        full_validation_df = pd.concat([full_validation_df, manual_upload_df], ignore_index=True)
        is_valid_data = True
    except Exception as e:
        st.error(f"Manual Ingestion Shield Error: {e}")

if "api_downloaded_data" in st.session_state:
    full_validation_df = pd.concat([full_validation_df, st.session_state["api_downloaded_data"]], ignore_index=True)
    is_valid_data = True

if is_valid_data and not full_validation_df.empty:
    full_validation_df.drop_duplicates(subset=["league_country", "match_timestamp", "home_team", "away_team"], keep="last", inplace=True)
    full_validation_df["league_country"] = full_validation_df["league_country"].astype(str).str.strip()
    uploaded_leagues = sorted(list(full_validation_df["league_country"].dropna().unique()))
else:
    st.info("📂 Data Control Room: Drop your master match CSV file into the uploader or click 'Run Live League Sync' to start pulling data.")
    st.stop()

selected_league_filter = st.selectbox("Select Target League:", uploaded_leagues)
half_life_days = st.slider("Time-Decay Half Life (Days)", 15, 90, 45, 1)

if "freeze_matrix" not in st.session_state: st.session_state.freeze_matrix = {}
for idx, league in enumerate(uploaded_leagues):
    l_cl = league.strip().lower()
    st.session_state.freeze_matrix[l_cl] = st.checkbox(f"Freeze Decay: {league.upper()}", value=False, key=f"f_sw_{l_cl}_{idx}")

max_score_cap = st.slider("Max Score Ceiling", 4, 10, 6, 1)
vol_dampener = st.slider("Volatility Dampener", 0.5, 1.5, 1.0, 0.05)
backtest_window = st.slider("Backtest Window Size (Days)", 90, 365, 180, 5)
accuracy_threshold_floor = st.slider("Strict Accuracy Floor (%)", 35, 75, 50, 5) / 100.0

raw_master_df = full_validation_df.copy()
raw_master_df["match_timestamp"] = pd.to_datetime(raw_master_df["match_timestamp"])
filtered_df = raw_master_df[raw_master_df["league_country"].str.lower().str.strip() == selected_league_filter.lower().strip()].reset_index(drop=True)

# Build unified visual navigation interface panels
tab_pred, tab_tables, tab_history, tab_past = st.tabs(["📅 PROJECTIONS", "🌍 STANDINGS", "📜 BACKTESTER", "📜 PAST GAMES"])
with tab_tables:
    st.markdown(f"### Dynamic Standings Matrix: {selected_league_filter.upper()}")
    base_table = engine.generate_dynamic_league_table(filtered_df)
    if not base_table.empty:
        st.dataframe(base_table, use_container_width=True)

with tab_history:
    st.markdown("### Backtest Calibration Analysis")
    league_key = selected_league_filter.lower().strip()
    baseline_goals = engine.COMPETITION_MATRIX.get(league_key, {"baseline_goals": 2.65}).get("baseline_goals", 2.65)
    
    b_df = engine.run_rolling_window_backtest(filtered_df, baseline_goals, backtest_window, 7, vol_dampener)
    if not b_df.empty:
        b_df["is_correct"] = b_df["model_probability"] >= accuracy_threshold_floor
        st.metric("Backtest Prediction Accuracy", f"{(b_df['is_correct'].sum()/len(b_df))*100:.1f}%")
        st.dataframe(b_df, use_container_width=True)

with tab_past:
    st.markdown("### 📜 Settled Historical Results Ledger")
    past_historical = filtered_df.dropna(subset=["home_goals", "away_goals"]).copy()
    if not past_historical.empty:
        past_historical = past_historical.sort_values(by="match_timestamp", ascending=False).reset_index(drop=True)
        display_past = past_historical[["match_timestamp", "home_team", "away_team", "home_goals", "away_goals"]]
        st.dataframe(display_past, use_container_width=True)
    else:
        st.info("No historical matches found for this filter combination.")
        with tab_pred:
            options = {f"[{r['league_country'].upper()}] {r['home_team']} vs {r['away_team']} ({pd.to_datetime(r['match_timestamp']).strftime('%Y-%m-%d')})": r for idx, r in filtered_df.iterrows()}
            if options:
               sel_match = st.selectbox("Select Profile Target fixture:", list(options.keys()))
        if sel_match:
            target = options[sel_match]
            target_ts = pd.to_datetime(target["match_timestamp"])
            
            o_col1, o_col2, o_col3, o_col4 = st.columns(4)
            with o_col1:
                odds_1 = st.number_input("Home Odds (1):", min_value=1.01, value=2.10, step=0.05, key="o_1")
                odds_1X = st.number_input("Double Chance Odds (1X):", min_value=1.01, value=1.35, step=0.05, key="o_1x")
                odds_btts_y = st.number_input("BTTS Yes Odds:", min_value=1.01, value=1.80, step=0.05, key="o_by")
            with o_col2:
                odds_X = st.number_input("Draw Odds (X):", min_value=1.01, value=3.20, step=0.05, key="o_x")
                odds_X2 = st.number_input("Double Chance Odds (X2):", min_value=1.01, value=1.65, step=0.05, key="o_x2")
                odds_btts_n = st.number_input("BTTS No Odds:", min_value=1.01, value=1.95, step=0.05, key="o_bn")
            with o_col3:
                odds_2 = st.number_input("Away Odds (2):", min_value=1.01, value=3.40, step=0.05, key="o_2")
                odds_12 = st.number_input("Double Chance Odds (12):", min_value=1.01, value=1.30, step=0.05, key="o_12")
                odds_dnb1 = st.number_input("Draw No Bet Home (DNB1):", min_value=1.01, value=1.50, step=0.05, key="o_d1")
            with o_col4:
                odds_over = st.number_input("Over 2.5 Goals Odds:", min_value=1.01, value=1.95, step=0.05, key="o_ov")
                odds_under = st.number_input("Under 2.5 Goals Odds:", min_value=1.01, value=1.85, step=0.05, key="o_un")
                odds_dnb2 = st.number_input("Draw No Bet Away (DNB2):", min_value=1.01, value=2.40, step=0.05, key="o_d2")

            h_status = st.selectbox("Home Status:", ["stable", "promoted", "relegated"], key="h_stat")
            a_status = st.selectbox("Away Status:", ["stable", "promoted", "relegated"], key="a_stat")
            
            league_key = selected_league_filter.lower().strip()
            baseline_goals = engine.COMPETITION_MATRIX.get(league_key, {"baseline_goals": 2.65}).get("baseline_goals", 2.65)
            is_fr = st.session_state.freeze_matrix.get(league_key, False)
            
            res = engine.predict_match_probabilities(filtered_df, target["home_team"], target["away_team"], target_ts, baseline_goals, 5, 5, h_status, a_status, max_score_cap, vol_dampener, is_fr)
            h_s = engine.parse_live_team_averages(filtered_df, target["home_team"], target_ts, half_life_days, h_status, is_fr)
            a_s = engine.parse_live_team_averages(filtered_df, target["away_team"], target_ts, half_life_days, a_status, is_fr)
            
            prob_home = res["market_probabilities"]["1 (Home Win)"]
            prob_draw = res["market_probabilities"]["X (Draw)"]
            prob_away = res["market_probabilities"]["2 (Away Win)"]
            prob_matrix = res["raw_matrix"]
            
            over_25_p, btts_yes_p, home_cs_p, away_cs_p = 0.0, 0.0, 0.0, 0.0
            
            for r_idx in range(prob_matrix.shape[0]):
                for a_idx in range(prob_matrix.shape[1]):
                    cell_p = prob_matrix[r_idx, a_idx]
                    if r_idx + a_idx > 2.5: over_25_p += cell_p
                    if r_idx > 0 and a_idx > 0: btts_yes_p += cell_p
                    if a_idx == 0: home_cs_p += cell_p
                    if r_idx == 0: away_cs_p += cell_p
                    
            under_25_p, btts_no_p = 1.0 - over_25_p, 1.0 - btts_yes_p
            dc_1X_p, dc_X2_p, dc_12_p = prob_home + prob_draw, prob_draw + prob_away, prob_home + prob_away
            dnb_denom = 1.0 - prob_draw if prob_draw < 1.0 else 1.0
            dnb_1_p, dnb_2_p = prob_home / dnb_denom, prob_away / dnb_denom
            
            markets_master_manifest = [
                ("HOME WIN (1)", odds_1, prob_home), ("DRAW MATCH (X)", odds_X, prob_draw), ("AWAY WIN (2)", odds_2, prob_away),
                ("DOUBLE CHANCE 1X", odds_1X, dc_1X_p), ("DOUBLE CHANCE X2", odds_X2, dc_X2_p), ("DOUBLE CHANCE 12", odds_12, dc_12_p),
                ("OVER 2.5 GOALS", odds_over, over_25_p), ("UNDER 2.5 GOALS", odds_under, under_25_p),
                ("BOTH TEAMS TO SCORE (YES)", odds_btts_y, btts_yes_p), ("BOTH TEAMS TO SCORE (NO)", odds_btts_n, btts_no_p),
                ("DRAW NO BET HOME (DNB1)", odds_dnb1, dnb_1_p), ("DRAW NO BET AWAY (DNB2)", odds_dnb2, dnb_2_p)
            ]
            
            qualified_projections = []
            for label, b_odds, m_prob in markets_master_manifest:
                calculated_ev = (m_prob * b_odds) - 1.0
                if calculated_ev > 0.0 and m_prob >= 0.35: 
                    qualified_projections.append((label, calculated_ev, m_prob, b_odds))
            
            if qualified_projections:
                qualified_projections.sort(key=lambda x: x[1], reverse=True)
                best_pick, best_ev, best_prob, best_odds = qualified_projections[0]
                raw_kelly = ((best_prob * best_odds) - 1.0) / (best_odds - 1.0) if best_odds > 1.0 else 0.0
                fractional_scale_stake = max(0.5, min(5.0, round(raw_kelly * 0.25 * 100, 2)))
                optimal_bet = best_pick
            else: 
                optimal_bet, best_ev, fractional_scale_stake, best_prob = "NO COMPREHENSIVE SELECTION MET FLOORS", 0.0, 0.0, 0.0
                
            sd = min(h_s.get("games_played", 0), a_s.get("games_played", 0))
            confidence = min(100, int((sd / 12.0) * 100)) if sd > 0 else 15
            bet_rec = "🔥 HIGH BET (KELLY MAXIMUM)" if best_ev >= 0.071 else "❌ NO BET"
            
            if "HIGH" in bet_rec:
                try:
                    email_body = (
                        f"========================================\n"
                        f"        SISONKE PREMIUM VALUE DETECTED  \n"
                        f"========================================\n"
                        f"MATCH PROFILE : {target['home_team']} vs {target['away_team']}\n"
                        f"RECOMMENDED POSITION : {optimal_bet}\n"
                        f"EXPECTED VALUE (EV)  : +{best_ev*100:.1f}%\n"
                        f"FRACTIONAL STAKE SELECTION : {fractional_scale_stake}% OF BANKROLL\n"
                        f"========================================"
                    )
                    sms_body = (
                        f"⚽ SISONKE VALUE ALERT!\n"
                        f"Match: {target['home_team']} vs {target['away_team']}\n"
                        f"Pick: {optimal_bet}\n"
                        f"Edge: +{best_ev*100:.1f}% EV\n"
                        f"Stake: {fractional_scale_stake}%"
                    )
                    
                    destination_mailing_list = [ui_email_recipient.strip(), ui_sms_recipient.strip()]
                    server = smtplib.SMTP('://gmail.com', 587)
                    server.starttls()
                    server.login("sisonke.predictions@gmail.com", ui_google_app_password.strip())
                    
                    for recipient in destination_mailing_list:
                        is_sms = "@" in recipient and ("sms" in recipient or "telkom" in recipient or "voda" in recipient)
                        msg = MIMEText(sms_body if is_sms else email_body)
                        msg['Subject'] = f"🚨 SISONKE ALERT: 🔥 HIGH BET"
                        msg['From'] = "sisonke.predictions@gmail.com"
                        msg['To'] = recipient
                        server.sendmail(msg['From'], [recipient], msg.as_string())
                    server.quit()
                    st.toast("📬 Coupon successfully broadcasted via SMS and Email!")
                except:
                    pass
            
            c_l, c_r = st.columns(2)
            with c_l:
                st.markdown("### 📊 Live Analytics Monitor")
                st.metric("Match Confidence Value", f"{confidence}%")
                
                st.markdown("### 🧠 Model Tactical Rationale Breakdown")
                insight_lines = []
                h_att = h_s.get("att_strength_goals", 1.0)
                a_att = a_s.get("att_strength_goals", 1.0)
                h_box = h_s.get("box_threat", 12.0)
                
                if h_att > a_att * 1.25:
                    insight_lines.append(f"• **Dominant Threat Area**: {target['home_team']}'s attacking index ({h_att:.2f}) heavily outclasses the visitors due to superior Final Third entries and an average Box Threat metric of {h_box:.1f}.")
                elif a_att > h_att * 1.25:
                    insight_lines.append(f"• **Dominant Threat Area**: {target['away_team']}'s offensive efficiency ({a_att:.2f}) proves superior. Their final-third progression metrics outscale the hosts' backline layout.")
                else: 
                    insight_lines.append("• **Balanced Attacking Structure**: Both teams display closely matched offensive process metrics, indicating an even midfield matchup.")
                    
                st.markdown(f'<div class="insight-box">{"<br><br>".join(insight_lines)}</div>', unsafe_allow_html=True)
                
                with c_r:
                    st.markdown("### 🎫 Calibrated Ticket Slip")
                ticket = f"MATCH: {target['home_team']} vs {target['away_team']}\nPOSITION: {optimal_bet}\nSTAKE: {fractional_scale_stake}%"
                st.text_area("Ticket Log Slip", value=ticket, height=200)
                else:
                    st.info("No fixtures found.")
        

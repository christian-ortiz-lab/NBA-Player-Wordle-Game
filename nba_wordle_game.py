import streamlit as st
import random
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
import pandas as pd
import time

st.set_page_config(page_title="NBA Player Wordle", layout="centered")

@st.cache_data
def get_active_players():
    return [p for p in players.get_active_players() if p['is_active']]

@st.cache_data
def get_player_info(player_id):
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    data = info.get_data_frames()[0]

    # Safely handle age extraction
    age_val = data.get('AGE', pd.Series([None])).values[0]
    try:
        age = int(age_val) if age_val is not None and not pd.isna(age_val) else None
    except (TypeError, ValueError):
        age = None

    return {
        'id': player_id,
        'name': data['DISPLAY_FIRST_LAST'].values[0],
        'team': data['TEAM_NAME'].values[0],
        'position': data['POSITION'].values[0],
        'height': data['HEIGHT'].values[0],
        'age': age
    }

def height_to_inches(height_str):
    try:
        ft, inch = height_str.split('-')
        return int(ft) * 12 + int(inch)
    except:
        return 0

def feedback(guess, answer):
    fb = {}
    fb['name'] = guess['name']
    fb['team'] = '🟩' if guess['team'] == answer['team'] else '🟨' if guess['team'].split()[-1] == answer['team'].split()[-1] else '⬜'
    fb['position'] = '🟩' if guess['position'] == answer['position'] else '⬜'
    
    g_height = height_to_inches(guess['height'])
    a_height = height_to_inches(answer['height'])
    fb['height'] = '🟩' if g_height == a_height else '🟨' if abs(g_height - a_height) <= 2 else '⬜'

    if guess['age'] is not None and answer['age'] is not None:
        fb['age'] = '🟩' if guess['age'] == answer['age'] else '🟨' if abs(guess['age'] - answer['age']) <= 2 else '⬜'
    else:
        fb['age'] = '⬜'

    return fb

# Load player data
st.title("🏀 NBA Player Wordle Game")
st.caption("Guess the mystery NBA player! Feedback: 🟩 correct, 🟨 close, ⬜ wrong.")

active_players = get_active_players()
player_dict = {p['full_name']: p['id'] for p in active_players}
all_names = sorted(player_dict.keys())

# Session state
if "answer_info" not in st.session_state:
    mystery_name = random.choice(all_names)
    st.session_state.answer_name = mystery_name
    st.session_state.answer_info = get_player_info(player_dict[mystery_name])
    st.session_state.guesses = []

# Input guess
guess = st.selectbox("Pick your player guess:", all_names)
if st.button("Submit Guess"):
    guess_info = get_player_info(player_dict[guess])
    fb = feedback(guess_info, st.session_state.answer_info)
    st.session_state.guesses.append(fb)

# Show guesses
if st.session_state.guesses:
    st.subheader("Your Guesses:")
    df = pd.DataFrame(st.session_state.guesses)
    st.dataframe(df)

# Win condition
if st.session_state.guesses:
    if st.session_state.guesses[-1]['name'] == st.session_state.answer_info['name']:
        st.success("🎉 You guessed it!")
        if st.button("Play Again"):
            st.session_state.clear()
            st.experimental_rerun()

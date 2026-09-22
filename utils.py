# utils.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

@st.cache_resource
def connect_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(st.secrets["spreadsheet"]["url"])
    return sh


@st.cache_data(ttl=3600)
def load_kampo_master():
    sh = connect_sheet()
    ws = sh.worksheet("漢方薬マスタ")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_shoyaku_master():
    sh = connect_sheet()
    ws = sh.worksheet("生薬マスタ")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_kousei():
    sh = connect_sheet()
    ws = sh.worksheet("漢方薬_生薬構成")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_monshin():
    sh = connect_sheet()
    ws = sh.worksheet("問診シート")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_yojo():
    sh = connect_sheet()
    ws = sh.worksheet("養生提案")
    return pd.DataFrame(ws.get_all_records())

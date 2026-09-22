import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="漢方問診アプリ", page_icon="🌿")

st.title("🌿 漢方おすすめ問診アプリ（開発中）")
st.write("店舗での問診補助を目的としたアプリです。")

# --- スプレッドシート接続テスト ---
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

try:
    sh = connect_sheet()
    worksheet = sh.worksheet("漢方薬マスタ")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    st.success("✅ スプレッドシートへの接続に成功しました")
    st.dataframe(df)
except Exception as e:
    st.error(f"❌ 接続エラー: {e}")
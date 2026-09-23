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


# ===== 以下、utils.py に追記 =====

@st.cache_data(ttl=3600)
def load_redflag_master():
    """レッドフラグ問診一覧を読み込む"""
    sh = connect_sheet()
    ws = sh.worksheet("レッドフラグ問診一覧")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_category_master():
    """症状カテゴリマスタを読み込む"""
    sh = connect_sheet()
    ws = sh.worksheet("カテゴリマスタ")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_category_flag_mapping():
    """カテゴリ_フラグ対応表を読み込む"""
    sh = connect_sheet()
    ws = sh.worksheet("カテゴリ_フラグ対応表")
    return pd.DataFrame(ws.get_all_records())


@st.cache_data(ttl=3600)
def load_escalation():
    """エスカレーション条件を読み込む"""
    sh = connect_sheet()
    ws = sh.worksheet("エスカレーション条件")
    return pd.DataFrame(ws.get_all_records())


def get_redflags_for_category(category_id, df_redflag=None, df_mapping=None):
    """
    指定カテゴリID に紐づくレッドフラグ質問一覧を返す。
    df_redflag, df_mapping を渡さない場合は自動で読み込む。
    """
    if df_redflag is None:
        df_redflag = load_redflag_master()
    if df_mapping is None:
        df_mapping = load_category_flag_mapping()

    target_flag_ids = df_mapping[df_mapping["category_id"] == category_id]["flag_id"].tolist()
    return df_redflag[df_redflag["フラグID"].isin(target_flag_ids)]


def get_common_redflags(df_redflag=None, df_mapping=None):
    """共通必須フラグ（CAT15）一覧を返す"""
    return get_redflags_for_category("CAT15", df_redflag, df_mapping)


def get_escalation_for_flag(flag_id, df_escalation=None):
    """
    指定フラグIDに対するエスカレーション条件があれば返す（無ければ空のDataFrame）
    """
    if df_escalation is None:
        df_escalation = load_escalation()
    return df_escalation[df_escalation["base_flag_id"] == flag_id]
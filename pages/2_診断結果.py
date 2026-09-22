import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="診断結果", page_icon="🌿")
st.title("🌿 おすすめ漢方の診断結果")

# --- 前のページのデータがあるか確認 ---
if "top_sho" not in st.session_state:
    st.warning("先に「問診入力」ページでチェックを入れて、診断結果を確認してください。")
    st.stop()

scores = st.session_state["scores"]
top_sho = st.session_state["top_sho"]
gi_flag = st.session_state.get("gi_flag", False)

st.write(f"最有力証：**{top_sho}**")
if gi_flag:
    st.info("ℹ️ 胃腸が弱いという回答があったため、地黄を含む処方は優先度を下げて表示します。")

# --- スプレッドシート接続 ---
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

sh = connect_sheet()
kampo_ws = sh.worksheet("漢方薬マスタ")
df_kampo = pd.DataFrame(kampo_ws.get_all_records())

# 数値であるべき列を数値型に変換(スプレッドシートは全部文字列で来ることがあるため)
numeric_cols = ["血虚", "気虚", "瘀血", "気滞", "陰虚", "水滞"]
for col in numeric_cols:
    if col in df_kampo.columns:
        df_kampo[col] = pd.to_numeric(df_kampo[col], errors="coerce").fillna(0)

# --- マッチングロジック ---
if top_sho in numeric_cols:
    # 数値列でそのままソート
    df_result = df_kampo.sort_values(top_sho, ascending=False)
elif top_sho in ["寒", "熱"]:
    # 寒熱テキスト列で絞り込み
    keyword = "寒" if top_sho == "寒" else "熱"
    df_result = df_kampo[df_kampo["寒熱"].str.contains(keyword, na=False)]
    if df_result.empty:
        st.warning(f"「{keyword}」に対応する処方が見つかりませんでした。全処方を表示します。")
        df_result = df_kampo.copy()
    df_result = df_result.sort_values(numeric_cols, ascending=False)
elif top_sho == "実証傾向":
    df_result = df_kampo[df_kampo["虚実"].str.contains("実", na=False)]
    if df_result.empty:
        st.warning("実証に対応する処方が見つかりませんでした。全処方を表示します。")
        df_result = df_kampo.copy()
else:
    df_result = df_kampo.copy()

# --- 胃腸フラグによる地黄含有薬の除外(降順) ---
if gi_flag and "地黄含有" in df_result.columns:
    df_result["地黄ペナルティ"] = df_result["地黄含有"].apply(lambda x: 1 if x == "有" else 0)
    df_result = df_result.sort_values("地黄ペナルティ")  # 地黄含有=有(1)を後ろに

# --- 結果表示 ---
st.subheader("📋 おすすめ処方（上位3件）")
display_cols = ["漢方ID", "薬名", "虚実", "寒熱", "地黄含有"] + numeric_cols
display_cols = [c for c in display_cols if c in df_result.columns]

top3 = df_result.head(3)
for idx, row in top3.iterrows():
    with st.container(border=True):
        st.markdown(f"### {row['薬名']}（{row['漢方ID']}）")
        st.write(f"虚実：{row.get('虚実','-')}　寒熱：{row.get('寒熱','-')}　地黄含有：{row.get('地黄含有','-')}")
        score_text = "　".join([f"{c}:{row[c]}" for c in numeric_cols if c in row])
        st.caption(score_text)

with st.expander("全処方リストを見る"):
    st.dataframe(df_result[display_cols], hide_index=True)
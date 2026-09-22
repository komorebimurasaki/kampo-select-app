import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="養生提案", page_icon="🍵")
st.title("🍵 養生・食養生のおすすめ")

# --- 前のページのデータがあるか確認 ---
if "top_sho" not in st.session_state:
    st.warning("先に「問診入力」ページでチェックを入れて、診断結果を確認してください。")
    st.stop()

top_sho = st.session_state["top_sho"]
st.write(f"最有力証：**{top_sho}** に基づくおすすめ養生法です。")

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
yojo_ws = sh.worksheet("養生提案")
df_yojo = pd.DataFrame(yojo_ws.get_all_records())

# --- ターゲット証でフィルタリング(カンマ区切り対応) ---
def match_target(target_str, sho):
    if not target_str:
        return False
    targets = [t.strip() for t in str(target_str).split(",")]
    return sho in targets

df_yojo["マッチ"] = df_yojo["ターゲット証"].apply(lambda x: match_target(x, top_sho))
df_match = df_yojo[df_yojo["マッチ"]]

if df_match.empty:
    st.info("該当する養生提案がまだ登録されていません。")
else:
    # カテゴリごとにグループ表示
    categories = ["食材", "料理", "和漢茶", "ハーブ"]
    icons = {"食材": "🥬", "料理": "🍲", "和漢茶": "🍵", "ハーブ": "🌿"}

    for cat in categories:
        df_cat = df_match[df_match["カテゴリ"] == cat]
        if df_cat.empty:
            continue
        st.subheader(f"{icons.get(cat, '•')} {cat}")
        for idx, row in df_cat.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['アイテム名']}**　（性：{row.get('性(寒熱)', row.get('性（寒熱）',''))}　味：{row['味']}）")
                st.caption(f"帰経：{row['帰経']}　旬：{row.get('旬','-')}")
                st.write(row["ワンポイント"])

with st.expander("養生提案データ 全件を見る"):
    st.dataframe(df_yojo.drop(columns=["マッチ"], errors="ignore"), hide_index=True)
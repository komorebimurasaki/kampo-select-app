import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="問診入力", page_icon="📝")
st.title("📝 問診入力")

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

# --- 問診シートのデータを取得 ---
mondai_ws = sh.worksheet("問診シート")
mondai_data = mondai_ws.get_all_records()
df_mondai = pd.DataFrame(mondai_data)

# 証のカテゴリ列を自動判定（質問ID・質問文・チェック以外の列を証の列とみなす）
score_columns = [col for col in df_mondai.columns if col not in ["質問ID", "質問文", "チェック"]]

st.write("気になる症状・体質にチェックを入れてください。")

# --- チェックボックスを表示し、回答を記録 ---
answers = {}
for idx, row in df_mondai.iterrows():
    checked = st.checkbox(row["質問文"], key=row["質問ID"])
    answers[row["質問ID"]] = 1 if checked else 0

st.divider()

# --- スコア集計 ---
if st.button("診断結果を見る"):
    scores = {col: 0 for col in score_columns}
    for idx, row in df_mondai.iterrows():
        qid = row["質問ID"]
        if answers[qid] == 1:
            for col in score_columns:
                scores[col] += row[col]

    st.subheader("📊 診断結果（証ごとのスコア）")
    df_scores = pd.DataFrame(
        list(scores.items()), columns=["証", "点数"]
    ).sort_values("点数", ascending=False)
    st.dataframe(df_scores, hide_index=True)

    top_sho = df_scores.iloc[0]["証"]
    st.success(f"✅ 最有力証：**{top_sho}**")

    # 次のステップで使うため、session_stateに保存
    st.session_state["scores"] = scores
    st.session_state["top_sho"] = top_sho
    st.session_state["gi_flag"] = (answers.get("Q21", 0) == 1)  # 胃腸が弱いフラグ
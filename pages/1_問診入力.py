import streamlit as st
import pandas as pd
from utils import load_monshin

st.set_page_config(page_title="問診入力", page_icon="📝")
st.title("📝 問診入力")

df_mondai = load_monshin()

score_columns = [col for col in df_mondai.columns if col not in ["質問ID", "質問文", "チェック"]]

st.write("気になる症状・体質にチェックを入れてください。")

answers = {}
for idx, row in df_mondai.iterrows():
    checked = st.checkbox(row["質問文"], key=row["質問ID"])
    answers[row["質問ID"]] = 1 if checked else 0

st.divider()

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

    st.session_state["scores"] = scores
    st.session_state["top_sho"] = top_sho
    st.session_state["gi_flag"] = (answers.get("Q21", 0) == 1)

    st.divider()
    st.write("次のページで詳しい結果を確認できます👇")

    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/2_診断結果.py", label="🌿 おすすめ漢方を見る", icon="➡️")
    with col2:
        st.page_link("pages/3_養生提案.py", label="🍵 養生提案を見る", icon="➡️")

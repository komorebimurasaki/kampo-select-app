import streamlit as st
import pandas as pd
from utils import load_yojo

st.set_page_config(page_title="養生提案", page_icon="🍵")
st.title("🍵 養生・食養生のおすすめ")

# --- 前のページのデータがあるか確認 ---
if "top_sho" not in st.session_state:
    st.warning("先に「問診入力」ページでチェックを入れて、診断結果を確認してください。")
    st.stop()

top_sho = st.session_state["top_sho"]
st.write(f"最有力証：**{top_sho}** に基づくおすすめ養生法です。")

# --- データ取得（キャッシュ済み） ---
df_yojo = load_yojo()

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

st.divider()
st.page_link("pages/2_診断結果.py", label="🌿 おすすめ漢方を見る", icon="➡️")

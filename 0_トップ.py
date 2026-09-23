import streamlit as st
from utils import load_kampo_master

st.set_page_config(page_title="漢方問診アプリ", page_icon="🌿")

st.title("🌿 漢方おすすめ問診アプリ（開発中）")
st.write("店舗での問診補助を目的としたアプリです。")

try:
    df = load_kampo_master()
    st.success("✅ スプレッドシートへの接続に成功しました")
    st.dataframe(df)
except Exception as e:
    st.error(f"❌ 接続エラー: {e}")

# --- 一時テストコード（確認後削除） ---
from utils import get_redflags_for_category, get_escalation_for_flag

st.divider()
st.subheader("🔧 テスト：循環カテゴリのレッドフラグ")
st.dataframe(get_redflags_for_category("CAT06"))

st.subheader("🔧 テスト：RF12のエスカレーション条件")
st.dataframe(get_escalation_for_flag("RF12"))

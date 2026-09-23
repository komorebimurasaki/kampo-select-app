import streamlit as st
from utils import load_category_master, get_redflags_for_category, get_escalation_for_flag, get_common_redflags

st.set_page_config(page_title="問診トリアージ", page_icon="🩺")
st.title("🩺 問診トリアージ（新フロー・開発中）")

# --- ステップ1：本人か子どもか ---
st.write("まず、どなたのご相談か教えてください。")

col1, col2 = st.columns(2)
with col1:
    if st.button("👤 ご本人の相談", use_container_width=True):
        st.session_state["patient_type"] = "本人"
with col2:
    if st.button("🧒 お子さんの相談", use_container_width=True):
        st.session_state["patient_type"] = "子ども"

# --- ステップ2：本人の場合、急性期/慢性期を選ぶ ---
if st.session_state.get("patient_type") == "本人":
    st.divider()
    st.write("次に、症状の経過について教えてください。")

    col3, col4 = st.columns(2)
    with col3:
        if st.button("🌡️ 急性期（最近始まった症状）", use_container_width=True):
            st.session_state["stage_type"] = "急性期"
    with col4:
        if st.button("📅 慢性期（以前から続く体質）", use_container_width=True):
            st.session_state["stage_type"] = "慢性期"

elif st.session_state.get("patient_type") == "子ども":
    st.divider()
    st.info("🧒 小児フローは現在準備中です。今後実装予定です。")

# --- ステップ3：急性期の場合、症状カテゴリを選ぶ ---
if st.session_state.get("stage_type") == "急性期":
    st.divider()
    st.write("気になる症状のカテゴリを選んでください。")

    df_category = load_category_master()
    # 「通常」カテゴリのみ抽出し、表示順で並べる
    df_normal = df_category[df_category["axis_type"] == "通常"].sort_values("display_order")

    # 3列でボタンを並べる
    cols = st.columns(3)
    for i, (idx, row) in enumerate(df_normal.iterrows()):
        with cols[i % 3]:
            if st.button(row["category_name"], key=row["category_id"], use_container_width=True):
                st.session_state["selected_category_id"] = row["category_id"]
                st.session_state["selected_category_name"] = row["category_name"]

elif st.session_state.get("stage_type") == "慢性期":
    st.divider()
    st.info("📅 慢性期フロー（全体問診）は今後実装予定です。")

# --- ステップ4：選んだカテゴリのレッドフラグ質問を表示 ---
if "selected_category_id" in st.session_state:
    st.divider()
    st.write(
        f"選択中：**{st.session_state['patient_type']}** / "
        f"**{st.session_state['stage_type']}** / "
        f"**{st.session_state['selected_category_name']}**"
    )
    st.divider()

    st.subheader("⚠️ 該当する症状がないか確認してください")

    df_redflags = get_redflags_for_category(st.session_state["selected_category_id"])

    if df_redflags.empty:
        st.info("このカテゴリには危険な症状のチェック項目がありません。")
    else:
        triggered_flags = []

        for idx, row in df_redflags.iterrows():
            checked = st.checkbox(row["判定質問文（問診テキスト）"], key=row["フラグID"])

            escalated_row = None

            if checked:
                df_escalation = get_escalation_for_flag(row["フラグID"])

                if not df_escalation.empty:
                    esc = df_escalation.iloc[0]
                    st.write("　↳ 以下も併せて確認してください：")

                    additional_questions = [
                        esc.get("additional_question_1", ""),
                        esc.get("additional_question_2", ""),
                        esc.get("additional_question_3", ""),
                        esc.get("additional_question_4", ""),
                        esc.get("additional_question_5", ""),
                    ]

                    esc_triggered = False
                    for i, q in enumerate(additional_questions):
                        if q:
                            esc_checked = st.checkbox(
                                f"　　・{q}",
                                key=f"{esc['escalation_id']}_{i}"
                            )
                            if esc_checked:
                                esc_triggered = True

                    if esc_triggered:
                        escalated_row = row.copy()
                        escalated_row["警告レベル"] = esc["escalated_severity"]
                        escalated_row["対応アクション"] = esc["escalated_action"]
                        escalated_row["根拠・ソース資料"] = row["根拠・ソース資料"] + "（随伴症状により格上げ）"

                triggered_flags.append(escalated_row if escalated_row is not None else row)

        st.divider()

        if triggered_flags:
            st.error("🚨 該当する症状がありました。以下をご確認ください。")
            for row in triggered_flags:
                with st.container(border=True):
                    st.markdown(f"**警告レベル：{row['警告レベル']}**")
                    st.write(f"対応：{row['対応アクション']}")
                    st.caption(f"根拠：{row['根拠・ソース資料']}")
            none_checked = False
        else:
            none_checked = st.checkbox("✔️ 上記のいずれにも該当する症状はありません", key="none_category")
            if none_checked:
                st.success("✅ 確認しました。")

    # --- 共通必須フラグ（カテゴリに関係なく必ず確認） ---
    st.divider()
    st.subheader("⚠️ 以下の症状もあわせて確認してください（共通確認事項）")

    df_common = get_common_redflags()
    common_triggered = []

    for idx, row in df_common.iterrows():
        checked = st.checkbox(row["判定質問文（問診テキスト）"], key=f"common_{row['フラグID']}")
        if checked:
            common_triggered.append(row)

    st.divider()

    if common_triggered:
        st.error("🚨 共通確認事項で該当する症状がありました。")
        for row in common_triggered:
            with st.container(border=True):
                st.markdown(f"**警告レベル：{row['警告レベル']}**")
                st.write(f"対応：{row['対応アクション']}")
                st.caption(f"根拠：{row['根拠・ソース資料']}")
        none_checked_common = False
    else:
        none_checked_common = st.checkbox("✔️ 上記のいずれにも該当する症状はありません", key="none_common")
        if none_checked_common:
            st.success("✅ 確認しました。")


    # --- 全て問題なければ、体質問診への導線を表示 ---
    category_ok = (not triggered_flags) and none_checked
    common_ok = (not common_triggered) and none_checked_common

    if category_ok and common_ok:
        st.divider()
        st.write("危険な症状が確認されなかったため、詳しい体質問診に進めます。")
        st.page_link("pages/1_問診入力.py", label="📝 体質問診に進む", icon="➡️")
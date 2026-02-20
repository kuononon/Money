import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("CSV費目編集・自動集計ツール")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

if uploaded_file:

    # 初回だけ読み込み
    if "df" not in st.session_state:
        df = pd.read_csv(uploaded_file, encoding="cp932")
        if '費目' not in df.columns:
            df['費目'] = '未分類'
        st.session_state.df = df
    else:
        df = st.session_state.df

    # =============================
    # 🔹 現金支出追加フォーム
    # =============================
st.subheader("0. 現金支出の追加")

with st.form("cash_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("支払日")
    with col2:
        description = st.text_input("内容")
    with col3:
        amount = st.number_input("金額（円）", min_value=0)

    category = st.selectbox(
        "費目",
        ['食費', '交通費', '通信費', '消耗品費', '未分類']
    )

    submitted = st.form_submit_button("追加")

    if submitted:

        # 列名を取得
        columns = st.session_state.df.columns.tolist()

        # 3列目と4列目を取得（インデックス2と3）
        content_col = columns[2]
        date_col = columns[3]

        # 空の1行を作る
        new_row = {col: "" for col in columns}

        # 指定列に代入
        new_row[content_col] = description
        new_row[date_col] = pd.to_datetime(date)
        new_row["ご利用金額（円）"] = amount
        new_row["費目"] = category

        st.session_state.df = pd.concat(
            [st.session_state.df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.success("現金支出を追加しました！")

    # =============================
    # 🔹 日付順に並び替え
    # =============================
    if "日付" in st.session_state.df.columns:
        st.session_state.df["日付"] = pd.to_datetime(st.session_state.df["日付"])
        st.session_state.df = st.session_state.df.sort_values("日付")

    # =============================
    # 🔹 編集
    # =============================
    st.subheader("1. データ編集")

    categories = ['食費', '交通費', '通信費', '消耗品費', '未分類']

    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "費目": st.column_config.SelectboxColumn(
                "費目",
                options=categories,
                required=True,
            )
        },
        hide_index=True,
        use_container_width=True
    )

    st.session_state.df = edited_df

    # =============================
    # 🔹 集計
    # =============================
    st.subheader("2. 費目別集計結果")

    if 'ご利用金額（円）' in edited_df.columns:
        summary = edited_df.groupby('費目')['ご利用金額（円）'].sum().reset_index()

        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(summary, hide_index=True)
        with col2:
            st.bar_chart(summary.set_index('費目'))

    # =============================
    # 🔹 CSV保存（追加分含む）
    # =============================
    st.subheader("3. 編集済みデータのダウンロード")

    csv = edited_df.to_csv(index=False).encode('utf_8_sig')

    st.download_button(
        label="CSVとしてダウンロード",
        data=csv,
        file_name='edited_data_sorted.csv',
        mime='text/csv',
    )
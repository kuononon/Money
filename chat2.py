import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("CSV費目編集・自動集計ツール")

# 初期化
if "df" not in st.session_state:
    st.session_state.df = None

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

# アップロード処理
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="cp932")

    # =============================
    # 🔹 データ整形関数
    # =============================
    def normalized_df(df):

        # JALパターン
        if "ご利用店名（海外ご利用店名／海外都市名）" in df.columns:
            df = df.rename(columns={
                "ご利用店名（海外ご利用店名／海外都市名）": "ご利用店",
                "ご利用金額（円）": "ご利用金額",
            })

        # EPOSパターン
        elif "ご利用年月日" in df.columns:
            df = df.rename(columns={
                "ご利用場所": "ご利用店",
                "ご利用金額（キャッシングでは元金になります）": "ご利用金額",
                "ご利用年月日": "ご利用日"
            })

        df["ご利用日"] = pd.to_datetime(
    df["ご利用日"],
    format="%Y年%m月%d日",
    errors="coerce"
)
     

        if "費目" not in df.columns:
            df["費目"] = "未分類"

        df = df[["ご利用日","ご利用店","ご利用金額","費目"]]
        return df

    df = normalized_df(df)   # ← ここで整形

    categories = ['食費', '交通費', '通信費', '消耗品費', '未分類']

    st.session_state.df = df


# =============================
# 🔹 dfが存在する場合のみ実行
# =============================
if st.session_state.df is not None:

    # =============================
    # 🔹 現金支出追加
    # =============================
    st.subheader("0. 現金支出の追加")

    with st.form("cash_form"):

        col1, col2, col3 = st.columns(3)

        with col1:
            date = st.date_input("ご利用日")
        with col2:
            description = st.text_input("ご利用内容")
        with col3:
            amount = st.number_input("ご利用金額", min_value=0)

        category = st.selectbox(
            "費目",
            ['食費', '交通費', '通信費', '消耗品費', '未分類']
        )

        submitted = st.form_submit_button("追加")

        if submitted:

            columns = st.session_state.df.columns.tolist()

            new_row = {col: "" for col in columns}
            new_row["ご利用日"] = pd.to_datetime(date)
            new_row["ご利用金額"] = amount
            new_row["費目"] = category

            if "ご利用店" in columns:
                new_row["ご利用店"] = description

            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            st.success("現金支出を追加しました！")

    
    # =============================
    # 🔹 データ編集
    # =============================
    st.subheader("1. データ編集")

    st.session_state.df = st.session_state.df.sort_values("ご利用日")

    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "ご利用日": st.column_config.DateColumn(
                "支払日",
                format="YYYY年M月D日"
            ),
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

    if "ご利用金額" in edited_df.columns:
        summary = edited_df.groupby("費目")["ご利用金額"].sum().reset_index()

        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(summary, hide_index=True)
        with col2:
            st.bar_chart(summary.set_index("費目"))

    # =============================
    # 🔹 ダウンロード
    # =============================
    st.subheader("3. 編集済みデータのダウンロード")

    csv = edited_df.to_csv(index=False).encode("utf_8_sig")

    st.download_button(
        label="CSVとしてダウンロード",
        data=csv,
        file_name="edited_data_sorted.csv",
        mime="text/csv",
    )
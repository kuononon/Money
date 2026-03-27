import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(layout="wide")
st.title("生活費管理ツール")

# =============================
# 初期化
# =============================
if "df" not in st.session_state:
    st.session_state.df = None

if "income_df" not in st.session_state:
    st.session_state.income_df = pd.DataFrame(
        columns=["日付", "内容", "金額"]
    )

categories = ['食費', '教養教育', 'ほの', '交通費', '通信費', '消耗品費', '健康医療', '未分類']
types = ['生活費', '自費']

# =============================
# 🔹 EPOS整形
# =============================
def normalize_epos(df):
    df = df.rename(columns={
        "ご利用場所": "ご利用店",
        "ご利用金額（キャッシングでは元金になります）": "ご利用金額",
        "ご利用年月日": "ご利用日"
    })
    df["ご利用日"] = pd.to_datetime(df["ご利用日"], format="%Y年%m月%d日", errors="coerce")
    df["ご利用金額"] = pd.to_numeric(df["ご利用金額"].astype(str).str.replace(",", ""), errors="coerce")
    df["費目"] = "未分類"
    df["区分"] = "生活費"
    df["カード"] = "EPOS"
    df = df.dropna(subset=["ご利用日"])
    return df[["ご利用日", "ご利用店", "ご利用金額", "費目", "区分", "カード"]]

# =============================
# 🔹 JAL整形
# =============================
def normalize_jal(df):
    df = df.rename(columns={
        "ご利用店名（海外ご利用店名／海外都市名）": "ご利用店",
        "ご利用金額（円）": "ご利用金額",
    })
    df["ご利用日"] = pd.to_datetime(df["ご利用日"], format="%Y年%m月%d日", errors="coerce")
    df["ご利用金額"] = pd.to_numeric(df["ご利用金額"].astype(str).str.replace(",", ""), errors="coerce")
    df["費目"] = "未分類"
    df["区分"] = "生活費"
    df["カード"] = "JAL"
    df = df.dropna(subset=["ご利用日"])
    return df[["ご利用日", "ご利用店", "ご利用金額", "費目", "区分", "カード"]]



# =============================
# 🔹 アップロード
# =============================
col1, col2 = st.columns(2)
with col1:
    epos_files = st.file_uploader("EPOS CSV", type=["csv"], accept_multiple_files=True)
with col2:
    jal_files = st.file_uploader("JAL CSV", type=["csv"], accept_multiple_files=True)

all_df = []
if epos_files:
    for file in epos_files:
        df = pd.read_csv(file, encoding="cp932", header=1)
        all_df.append(normalize_epos(df))
if jal_files:
    for file in jal_files:
        df = pd.read_csv(file, encoding="cp932", header=0)
        all_df.append(normalize_jal(df))
if all_df :
    merged_df = pd.concat(all_df, ignore_index=True)
    merged_df = merged_df.sort_values("ご利用日")
    st.session_state.df = merged_df

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
            ['食費', '教養教育', 'ほの', '交通費', '通信費', '消耗品費', '健康医療', '未分類']
        )
        payment_type = st.selectbox(
            "区分",
            ['生活費', '自費']
        )


        submitted = st.form_submit_button("追加")

        if submitted:

            columns = st.session_state.df.columns.tolist()

            new_row = {col: "" for col in columns}
            new_row["ご利用日"] = pd.to_datetime(date)
            new_row["ご利用金額"] = amount
            new_row["費目"] = category
            new_row["区分"] = payment_type
            new_row["カード"] = "現金"

            if "ご利用店" in columns:
                new_row["ご利用店"] = description

            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            st.session_state.df = st.session_state.df.sort_values("ご利用日").reset_index(drop=True)

            st.success("現金支出を追加しました！")

# =============================
# 🔹 データ処理
# =============================
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    df["年月"] = df["ご利用日"].dt.to_period("M").astype(str)

    edited_df = st.data_editor(
        df,
        key="editor",
        column_config={
            "費目": st.column_config.SelectboxColumn("費目", options=categories),
            "区分": st.column_config.SelectboxColumn("区分", options=types),
            "ご利用日": st.column_config.DateColumn("ご利用日", format="YYYY年M月D日")
        },
        use_container_width=True,
        hide_index=True
    )
    st.session_state.df = edited_df

    st.subheader("集計結果")

    # =============================
    # 各種集計
    # =============================
    monthly_total = edited_df.groupby("年月")["ご利用金額"].sum().reset_index()
    monthly_category = edited_df.groupby(["年月", "費目"])["ご利用金額"].sum().reset_index()
    monthly_type = edited_df.groupby(["年月", "区分"])["ご利用金額"].sum().reset_index()
    type_category = edited_df.groupby(["区分", "費目"])["ご利用金額"].sum().reset_index()
    card_total = edited_df.groupby("カード")["ご利用金額"].sum().reset_index()
    card_month = edited_df.groupby(["カード", "年月"])["ご利用金額"].sum().reset_index()
    card_category = edited_df.groupby(["カード", "費目"])["ご利用金額"].sum().reset_index()

    st.write("### 月別合計")
    st.dataframe(monthly_total)

    st.write("### 月別×費目")
    st.dataframe(monthly_category)

    st.write("### 月別×区分")
    st.dataframe(monthly_type)

    st.write("### 区分×費目")
    st.dataframe(type_category)

    st.write("### カード別合計")
    st.dataframe(card_total)

    st.write("### カード別（自費のみ）")

    self_expense = edited_df[
    edited_df["区分"].fillna("").str.strip() == "自費"
    ]

    card_self_total = (
    self_expense
    .groupby("カード")["ご利用金額"]
    .sum()
    .reset_index()
    )

    st.dataframe(card_self_total)

    # =============================
    # 🔹 保存形式選択
    # =============================
    st.subheader("集計データ保存")
    file_type = st.radio("保存形式", ["CSV（ZIP）", "Excel"])

    if file_type == "CSV（ZIP）":
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("card_all.csv", edited_df.to_csv(index=False))
        st.download_button(
            "CSVまとめてダウンロード",
            data=zip_buffer.getvalue(),
            file_name="summary_csv.zip",
            mime="application/zip"
        )
    else:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # =============================
            # 日付順支出（1枚目シート）
            # =============================
            worksheet_name = "日付順支出"
            start_row = 0
            worksheet = writer.book.add_worksheet(worksheet_name)
            writer.sheets[worksheet_name] = worksheet

            # ---- 全体日付順 ----
            df_all_sorted = edited_df.copy()
            df_all_sorted["ご利用日"] = pd.to_datetime(df_all_sorted["ご利用日"], errors="coerce").dt.strftime("%Y/%m/%d")
            df_all_sorted = df_all_sorted.sort_values(["ご利用日", "カード"])
            df_all_sorted.to_excel(writer, sheet_name=worksheet_name, startrow=start_row+1, index=False)
            worksheet.write(start_row, 0, "=== 全体日付順 ===")
            start_row += len(df_all_sorted) + 3

            # ---- カード別日付順 ----
            for card in edited_df["カード"].unique():
                card_df = edited_df[edited_df["カード"] == card].copy()
                card_df["ご利用日"] = pd.to_datetime(card_df["ご利用日"], errors="coerce").dt.strftime("%Y/%m/%d")
                card_df = card_df.sort_values("ご利用日")
                card_df.to_excel(writer, sheet_name=worksheet_name, startrow=start_row+1, index=False)
                worksheet.write(start_row, 0, f"=== カード: {card} 日付順 ===")
                start_row += len(card_df) + 3

            # =============================
            # 集計結果シート（2枚目）
            # =============================
            sheet_name = "集計結果"
            start_row = 0
            df_list = [
                ("月別合計", monthly_total),
                ("月別×費目", monthly_category),
                ("月別×区分", monthly_type),
                ("区分×費目", type_category),
                ("カード別合計", card_total),
                ("カード月別", card_month),
                ("カード費目別", card_category)
            ]
            for title, table in df_list:
                table.to_excel(writer, sheet_name=sheet_name, startrow=start_row+1, index=False)
                worksheet2 = writer.sheets[sheet_name]
                worksheet2.write(start_row, 0, title)
                start_row += len(table) + 3

        from datetime import datetime

        today_str = datetime.today().strftime("%Y-%m-%d")
        file_name = f"{today_str}_生活費.xlsx"

        st.download_button(
            "Excelダウンロード",
            data=output.getvalue(),
            file_name=file_name
        )

# =============================
# 🔹 収入管理
# =============================

st.subheader("収入入力")

with st.form("income_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("収入日")
    with col2:
        description = st.text_input("収入内容")
    with col3:
        amount = st.number_input("収入金額", min_value=0)

    submitted = st.form_submit_button("追加")

    if submitted:
        new_row = {
            "日付": pd.to_datetime(date),
            "内容": description,
            "金額": amount
        }

        st.session_state.income_df = pd.concat(
            [st.session_state.income_df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.session_state.income_df = (
            st.session_state.income_df
            .sort_values("日付")
            .reset_index(drop=True)
        )

        st.success("収入を追加しました！")


# =============================
# 🔹 収入一覧
# =============================

st.subheader("収入一覧")

income_df = st.session_state.income_df.copy()

if not income_df.empty:

    income_df["年月"] = income_df["日付"].dt.to_period("M").astype(str)

    edited_income_df = st.data_editor(
        income_df,
        column_config={
            "日付": st.column_config.DateColumn("日付", format="YYYY年M月D日")
        },
        use_container_width=True,
        hide_index=True,
        key="income_editor"
    )

    st.session_state.income_df = edited_income_df

jal_self_df = edited_df[
(edited_df["カード"] == "JAL") &
(edited_df["区分"].fillna("").str.strip() == "自費")
].copy()
    # =============================
# JAL自費合計
# =============================
jal_total = jal_self_df["ご利用金額"].sum()

# =============================
# 今月
# =============================
today = pd.Timestamp.today()
this_month = today.to_period("M")

# =============================
# 10日までの収入
# =============================
start = pd.Timestamp(f"{this_month}-01")
end = pd.Timestamp(f"{this_month}-10")

income_total = income_df[
    (income_df["日付"] >= start) &
    (income_df["日付"] <= end)
]["金額"].sum()

# =============================
# 差（借金）
# =============================
debt = jal_total - income_total

# =============================
# 表示
# =============================
st.metric("借金", f"{debt:,.0f} 円")
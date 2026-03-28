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
# 🔹 正規化
# =============================
def normalize_epos(df, file_name):
    df = df.rename(columns={
        "ご利用場所": "ご利用店",
        "ご利用金額（キャッシングでは元金になります）": "ご利用金額",
        "ご利用年月日": "ご利用日"
    })
    df["ファイル"] = file_name
    df["ご利用日"] = pd.to_datetime(df["ご利用日"], format="%Y年%m月%d日", errors="coerce")
    df["ご利用金額"] = pd.to_numeric(df["ご利用金額"].astype(str).str.replace(",", ""), errors="coerce")
    df["費目"] = "未分類"
    df["区分"] = "生活費"
    df["カード"] = "EPOS"
    df = df.dropna(subset=["ご利用日"])
    return df[["ご利用日","ご利用店","ご利用金額","費目","区分","カード","ファイル"]]

def normalize_jal(df, file_name):
    df = df.rename(columns={
        "ご利用店名（海外ご利用店名／海外都市名）": "ご利用店",
        "ご利用金額（円）": "ご利用金額",
    })
    df["ファイル"] = file_name
    df["ご利用日"] = pd.to_datetime(df["ご利用日"], format="%Y年%m月%d日", errors="coerce")
    df["ご利用金額"] = pd.to_numeric(df["ご利用金額"].astype(str).str.replace(",", ""), errors="coerce")
    df["費目"] = "未分類"
    df["区分"] = "生活費"
    df["カード"] = "JAL"
    df = df.dropna(subset=["ご利用日"])
    return df[["ご利用日","ご利用店","ご利用金額","費目","区分","カード","ファイル"]]

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
        all_df.append(normalize_epos(df, file.name))

if jal_files:
    for file in jal_files:
        df = pd.read_csv(file, encoding="cp932", header=0)
        all_df.append(normalize_jal(df, file.name))

if all_df:
    merged_df = pd.concat(all_df, ignore_index=True)
    merged_df = merged_df.sort_values("ご利用日")
    st.session_state.df = merged_df

# =============================
# 🔹 現金支出追加
# =============================
if st.session_state.df is not None:

    st.subheader("現金支出追加")

    with st.form("cash_form"):

        col1, col2, col3 = st.columns(3)

        date = col1.date_input("ご利用日")
        description = col2.text_input("ご利用内容")
        amount = col3.number_input("ご利用金額", min_value=0)

        category = st.selectbox("費目", categories)
        payment_type = st.selectbox("区分", types)

        submitted = st.form_submit_button("追加")

        if submitted:

            new_row = {
                "ご利用日": pd.to_datetime(date),
                "ご利用店": description,
                "ご利用金額": amount,
                "費目": category,
                "区分": payment_type,
                "カード": "現金",
                "ファイル": pd.to_datetime(date).strftime("%Y%m")
            }

            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            st.session_state.df = st.session_state.df.sort_values("ご利用日").reset_index(drop=True)

            st.success("現金支出を追加しました！")

# =============================
# 🔹 データ編集
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
    # 集計
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
        self_expense.groupby("カード")["ご利用金額"].sum().reset_index()
    )

    st.dataframe(card_self_total)

    # =============================
    # 保存
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

            worksheet_name = "日付順支出"
            start_row = 0

            df_all_sorted = edited_df.copy()
            df_all_sorted["ご利用日"] = pd.to_datetime(df_all_sorted["ご利用日"]).dt.strftime("%Y/%m/%d")
            df_all_sorted = df_all_sorted.sort_values(["ご利用日", "カード"])

            df_all_sorted.to_excel(writer, sheet_name=worksheet_name, startrow=start_row+1, index=False)

        st.download_button(
            "Excelダウンロード",
            data=output.getvalue(),
            file_name="生活費.xlsx"
        )

# =============================
# 🔹 収入
# =============================
st.subheader("収入入力")

with st.form("income_form"):
    date = st.date_input("収入日")
    desc = st.text_input("内容")
    amount = st.number_input("金額", min_value=0)

    if st.form_submit_button("追加"):
        new_row = {"日付": pd.to_datetime(date), "内容": desc, "金額": amount}
        st.session_state.income_df = pd.concat(
            [st.session_state.income_df, pd.DataFrame([new_row])],
            ignore_index=True
        )


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

# =============================
# 🔹 借金計算（完全版）
# =============================
if st.session_state.df is not None:

    df = st.session_state.df.copy()
    income_df = st.session_state.income_df.copy()

    income_df["日付"] = pd.to_datetime(income_df["日付"], errors="coerce")

    df["支払月"] = pd.to_datetime(df["ファイル"].astype(str).str[:6], format="%Y%m", errors="coerce")
    df.loc[df["カード"] == "EPOS", "支払月"] += pd.DateOffset(months=1)

    df["支払日"] = df["支払月"].dt.to_period("M").dt.to_timestamp()
    df.loc[df["カード"] == "JAL", "支払日"] += pd.Timedelta(days=9)
    df.loc[df["カード"] == "EPOS", "支払日"] += pd.Timedelta(days=26)

    target_date = pd.to_datetime(st.date_input("借金計算日"))

    total_expense = df[
        (df["支払日"] <= target_date) &
        (df["区分"].fillna("").str.strip() == "自費")
    ]["ご利用金額"].sum()

    total_income = income_df[
        income_df["日付"] <= target_date
    ]["金額"].sum()

    debt = total_expense - total_income

    st.subheader("総合借金")
    st.metric("借金", f"{debt:,.0f} 円")
    st.write(f"支出合計: {total_expense:,.0f} 円")
    st.write(f"収入合計: {total_income:,.0f} 円")

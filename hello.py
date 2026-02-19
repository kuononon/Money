import pandas as pd
# Excelファイルを読み込み
df = pd.read_excel("202602_DC.xlsx",skiprows=[1],usecols="B,C,D,G")

# お支払日をExcelの日付形式からdatetimeに変換
df["お支払日"] = pd.to_datetime(df["お支払日"], origin="1899-12-30", unit="D")
# ご利用日をExcelの日付形式からdatetimeに変換
df["ご利用日"] = pd.to_datetime(df["ご利用日"], origin="1899-12-30", unit="D")

# ご利用金額（円）を数値に変換
df["ご利用金額（円）"] = df["ご利用金額（円）"].astype("Int64")

monthly_sum = (
    df.groupby(df["お支払日"].dt.to_period("M"))["ご利用金額（円）"]
      .sum()
)

print(monthly_sum)

# お支払日を"YYYY-MM-DD"形式の文字列に変換
df["お支払日"] = df["お支払日"].dt.strftime("%Y-%m-%d")
# ご利用日を"YYYY-MM-DD"形式の文字列に変換
df["ご利用日"] = df["ご利用日"].dt.strftime("%Y-%m-%d")
# ご利用金額（円）をカンマ区切りの文字列に変換し、末尾に"円"を追加
df["ご利用金額（円）"] = df["ご利用金額（円）"].apply(lambda x: f"{x:,}円")

# データの先頭5行を表示
print(df.head())
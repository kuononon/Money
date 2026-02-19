import pandas as pd
# Excelファイルを読み込み
df = pd.read_excel("202602_DC.xlsx")

# データの先頭5行を表示
print(df.head())
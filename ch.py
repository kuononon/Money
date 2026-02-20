import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd

df = None

def load_csv():
    global df

    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    df = pd.read_csv(file_path, encoding="cp932")

    # 表を更新
    show_table(df)

def show_table(dataframe):
    # 既存の表を削除
    for widget in table_frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(table_frame)
    tree.pack(fill="both", expand=True)

    tree["column"] = list(dataframe.columns)
    tree["show"] = "headings"

    # 列名表示
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    # データ表示
    for index, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

root = tk.Tk()
root.title("CSV表示ツール")
root.geometry("1000x600")

tk.Button(root, text="CSV読み込み", command=load_csv).pack(pady=10)

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True)

root.mainloop()
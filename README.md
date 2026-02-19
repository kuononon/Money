家計簿アプリへようこそ
ここではExelで取得した支払い明細からさまざまな処理を行います。
1. 月別の合計金額
2. 自費の合計金額


備忘録
1. "import pandas as np"でpandasを入れられない...
N VS Code内でのPythonとzsh(Mac OS)でのPythonとバージョンが違っていることが判明
A Command+Shift+Pを押し上部画面からPythonインタープリンタを選択
  VS Codeで用いているPytohnのverを選ぶ
  VS Code内のPythonのverを調べた時のパスをコピーしそれを"(---) -m pip install pandas"のようにターミナルで打つ
  これからpandasなどのパッケージを入れるときはパスを入れてからコマンドを打つ
Perfect
2. Exelコマンド
skiprows=[1] 2行目は飛ばして読み込める
header=1 2行目から読み込める
usecols="A,B" A,B列を読み込む

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]
(https://colab.research.google.com/github/ユーザー名/リポジトリ名/blob/main/ファイル名.ipynb)


家計簿アプリへようこそ
ここではcsvで取得した支払い明細からさまざまな処理を行います.
1. csvの編集　csvをダウンロードし主に費目を編集したcsvファイルをダウンロードする
2. 現金の支出をcsvファイルに上書きする.
3. 二つのcsvファイルをまとめ,お支払日中にまとめる
4. 得たcsvファイルから費目別合計,使える金額,借金,カード会社別の自費と生活費をまとめる.
5. 銀行やバイト代の収入,手持ち現金(現金,paypay)を入れる場所を作る. 収入の表を作る.
6. 水道代とガス代と家賃の支払い期限ごとに,その時までの予想使用金額を計算する.可能なら選択した日までの使用金額 
   や借金を計算できるようにする.
7. 目標生活費と使った生活費の差額計算
8. できるならcsvの出力はログインIDなどを連携することで勝手にcsv取得できるようにする.

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
3. Pysimple GUI クリックなどで直感で動かせるようにする
4. Exelなどを開くためにopenpyxlのパッケージを入れる
5. tkinterはpython3.9.6に入っているのでimport tkinterで入れよう
6. tkinterもいいがデスクトップアプリはあまり見た目が良くない.よってstreamlitを使うことでwebサイトとして立  
   ち上げ,csvファイルを編集できるようにする.常にwebサイトは開けないがrun中は開ける.
7. streamlitのプログラムを実行するコマンドはpython3 -m streamlit run chat4.pyをターミナルで実行する.

新出言語
Local URL = 自分のパソコンで見るようのURL
Network URL = 他の端末から開くためのURL


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]
(https://colab.research.google.com/github/ユーザー名/リポジトリ名/blob/main/ファイル名.ipynb)

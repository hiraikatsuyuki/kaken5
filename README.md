# kaken5

## 概要

- KAKENのデータを研究機関間で比較するための分析ツールです。
- https://www.ura.niigata-u.ac.jp/kaken3/ をPHPからPythonに移植したものです。 
- PythonのウェブアプリケーションのフレームワークFlaskで作っています。
- C4RAのKAKENテーブルが保存されているMariaDBがローカルで動いていることが前提です。
- 自分の環境では https://github.com/c4ra/kaken_parse_grants_masterxml/blob/master/config.ipynb で作ったconfig.iniを、このフォルダと同じ高さの階層のsettingsというフォルダに置いています。config.iniの置き場所は、各自で修正をお願いします。

## 作業手順

- Anaconda promptを開始
- Anacondaの仮想環境をひとつ適当な名前で作成する(たとえばkaken5とします)
- 作った仮想環境(kaken5)をactivateする
- requitements.txtに記載されたのパッケージを追加する
- python main.pyを実行
- http://127.0.0.1:5000/ に適当なブラウザでアクセスする

## 今後の予定

- 分科だけでなく、分野と細目でも集計できるようにする
- AWSかどこかのPaaSにデプロイできるようにする
- 他にもいろいろあるけどとりあえず

# HinodeDB
## 概要
Heliophysics event knowledgebase(HEK)からダウンロードしたデータセットをHinodeによって観測されたデータと統合するプロジェクト

## ディレクトリ構成
<pre>
├── FL
│   └── HEKからダウンロードした
├── README.md
├── eis
│   ├── EISによって観測されたデータ群
├── environment-hinode.txt(本プロジェクトの実行に使用した環境)
├── flare_labeled
│   ├── ラベル付けされた衛星観測データの出力先
├── logs
│   ├── 実行ログの出力先
├── memo_inada.txt
├── sot_fg
│   ├── SOT_FGによって観測されたデータ群
├── sot_sp
│   ├── SOT_SPによって観測されたデータ群
├── src_dataset
│   ├── 実行用コード
└── xrt
    ├── XRTによって観測されたデータ群
</pre>
## ToDo
* [x] うるう秒の修正
* [ ] SOLへのColumn追加(取得日時含む)
* [ ] テーブル構成の統一
* [ ] 48番のデータ列を空白に
後期以降
* [ ] FL,AR,CHの統合
* [ ] SWANによるFLの照合
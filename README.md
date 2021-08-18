# HinodeDB
## 概要
Heliophysics event knowledgebase(HEK)からダウンロードしたデータセットをHinodeによって観測されたデータと統合するプロジェクト

## ディレクトリ構成
+ HinodeDB
    + sot_sp
        + .sot_spによって観測されたデータ群
    + sot_fg
        + sot_fgによって観測されたデータ群
    + eis
        + eisによって観測されたデータ群
    + xrt
        + xrtによって観測されたデータ群
    + flare
        + HEKからダウンロードしたデータ群(download_sol_table.pyによってDL可能)
    + src_dataset
        + データセットの作成に必要なスクリプト
"""
ラベル付されたデータとSOL一覧のテーブルを入力して、必要なデータだけのSOLTableを作成するスクリプト
第1引数: ラベル付けされたデータ
第2引数: SOL一覧のテーブル
第3引数: イベントの種類
"""

import pandas as pd
import sys
from itertools import chain



def main():
    args = sys.argv[1:]
    labeled_data_path = args[0]
    year = labeled_data_path[-8:-4]
    sol_data_path = args[1]
    contents = args[2]
    filepath  = args[3]
    hinode_df = initialize_hinode_df(labeled_data_path)
    sol_df = initialize_sol_df(sol_data_path)
    if (contents=="FL"):
        flares = extract_flares(hinode_df)
        print(flares)
        event_df = sol_df.query("index in @flares")
    elif (contents=="AR"):
        pass # TODO:ARの場合の処理
    elif(contents=="CH"):
        pass # TODO:CHのときの処理
    event_df.to_csv(filepath)


def initialize_hinode_df(filepath):
    hinode_df = pd.read_csv(filepath)
    hinode_df = hinode_df.dropna(how="any")
    return hinode_df

def initialize_sol_df(filepath):
    sol_df = pd.read_csv(filepath,index_col=1)
    return sol_df

def extract_flares(hinode_df):
    flares = [column.split("   ") for column in hinode_df["Flare"]]
    flares = list(chain.from_iterable(flares))
    flares = [flare[:-5] for flare in flares]
    print(flares)
    return set(flares)

main()
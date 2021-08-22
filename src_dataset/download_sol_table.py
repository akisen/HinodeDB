"""
download_dataset.py:HEK(Heliophysics event knowledgebase)からデータをダウンロードするスクリプト
第一引数にダウンロードしたいデータを選択する。
ex)python3 download_dateset.py FL

"""

import argparse
import calendar
import datetime
import logging
import time

import pandas as pd
from dateutil.relativedelta import relativedelta
from retry import retry
from sunpy.net import hek
from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument('contents')

args = parser.parse_args()

contents = args.contents

logger = logging.getLogger()
client = hek.HEKClient()
years = [2010+i for i in range(7)]
months = [i+1 for i in range(12)]


def main():
    with tqdm(total=len(years)*len(months)) as pbar:
        for year in years:
            if(contents == "FL"):
                contents_df = initialize_flare_df()
            elif(contents == "AR"):
                pass  # TODO:ARの場合の初期化
            elif(contents == "CH"):
                pass  # TODO:CHの場合の初期化
            for month in months:
                pbar.update(1)
                for i in range(3):  # 一月単位だとデータ量が多すぎてサーバエラーが帰ってくるため
                    tstart = datetime.date(year, month, i*10+1)
                    tend = tstart + relativedelta(days=9)
                    if(tstart.day == 21):
                        tend = get_last_date(tend)  # 月末ならば末日までダウンロードに変更
                    if(contents == "FL"):
                        contents_df = pd.concat(
                            [contents_df, download_flare(tstart, tend)])
                    elif(contents == "AR"):
                        pass  # TODO:ARの場合のダウンロード
                    elif(contents == "CH"):
                        pass  # TODO:CHの場合のダウンロード
                    # print(contents_df)
                    time.sleep(3600)
            if (contents == "FL"):
                contents_df.drop('event_clippedtemporal', axis=1)
            contents_df.set_index("SOL_standard")
            contents_df = add_require_columns(contents_df)
            contents_df = contents_df.sort_index(axis=1,)
            filename = "../{0}/SOL_all_{0}{1}.csv".format(contents, year)
            contents_df.to_csv(filename, index=False)


def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])


@retry(delay=300, backoff=300, logger=logger)
def download_flare(tstart, tend):
    event_type = 'FL'
    results = client.search(hek.attrs.Time(tstart, tend),
                            hek.attrs.EventType(event_type))
    tqdm.write(str(results[0]["SOL_standard"]))
    return results.to_pandas()


def initialize_flare_df():
    event_type = 'FL'
    columns = client.search(hek.attrs.Time(
        "2010-05-01", "2010-05-02"), hek.attrs.EventType(event_type)).to_pandas().columns
    flare_df = pd.DataFrame(index=[], columns=columns)
    return flare_df


def add_require_columns(contents_df):
    with open("all_columns.txt") as f:
        all_columns = f.read().splitlines()
    for column in all_columns:
        if column not in contents_df.columns:
            contents_df[column] = ""
    contents_df["file_generating_date"] = datetime.datetime.today().strftime("%Y-%m-%d")
    return contents_df


main()

"""
download_dataset.py:HEK(Heliophysics event knowledgebase)からデータをダウンロードするスクリプト
第一引数にダウンロードしたいデータを選択する。
ex)python3 download_dateset.py FL

"""

import datetime
from sunpy.net import hek
import pandas as pd
import time
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('contents' )

args = parser.parse_args()

contents = args.contents

client = hek.HEKClient()
years=[2010+i for i in range(9)]
months = [i+1 for i in range(12)]

def main ():
    with tqdm(total = len(years)*len(months)) as pbar:
        for year in years:
            for month  in months:
                pbar.update(1)
                for i in range(3): #一月単位だとデータ量が多すぎてサーバエラーが帰ってくるため
                    tstart = datetime.date(year,month,i*10+1)
                    tend = tstart + relativedelta(days=9)
                    if(tstart.day==21):
                        tend = get_last_date(tend)# 月末ならば末日までダウンロードに変更
                    if(contents=="FL"):
                        if("contents_df" in locals()):
                            contents_df = pd.concat([contents_df,download_flare(tstart,tend)])
                            print("contents_df exists")
                            # print(download_flare(tstart,tend))
                            time.sleep(1800)
                        else:
                            contents_df = download_flare(tstart,tend)
                            print("contents_df not exists")
                    elif(contents=="AR"):
                        pass # TODO:ARの場合のダウンロード
                    elif(contents=="CH"):
                        pass # TODO:CHの場合のダウンロード
                    print(contents_df)
                    filename = "../{0}/SOL_all_{0}{1}.csv".format(contents,year)
                    contents_df.to_csv(filename)
            

def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])


def download_flare(tstart,tend):
    event_type = 'FL'
    results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
    tqdm.write(str(results[0]["SOL_standard"]))
    return results.to_pandas()



main()
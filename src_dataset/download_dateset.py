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
years=[2010+i for i in range(10)]
months = [i+1 for i in range(12)]

def main ():
    with tqdm(total = len(years)*len(months)) as pbar:
        for year in years:
            contents_df =initialize_flare_df()
            print(contents_df)
            for month  in months:
                pbar.update(1)
                for i in range(3): #一月単位だとデータ量が多すぎてサーバエラーが帰ってくるため
                    tstart = datetime.date(year,month,i*10+1)
                    tend = tstart + relativedelta(days=9)
                    if(tstart.day==21):
                        tend = get_last_date(tend)# 月末ならば末日までダウンロードに変更
                    if(contents=="FL"):
                        contents_df = download_flare(tstart,tend,contents_df)
                    elif(contents=="AR"):
                        pass # TODO:ARの場合のダウンロード
                    elif(contents=="CH"):
                        pass # TODO:CHの場合のダウンロード
                time.sleep(300)
            filename = "../{0}/{0}{1}.csv".format(contents,year)
            contents_df.to_csv(filename)
            print(filename)
            

def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])

def initialize_flare_df():
    if(contents=="FL"):
        keys =["SOL_standard","fl_goescls","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","hpc_coord","event_starttime","event_endtime","search_observatory"]
    elif("AR"):
        pass    # TODO:ARの場合の初期化
    elif("CH"):
        pass    # TODO:CHの場合の初期化
    flare_df =pd.DataFrame(columns=keys)
    return flare_df

def download_flare(tstart,tend,flare_df):
    keys =["SOL_standard","fl_goescls","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","hpc_coord","event_starttime","event_endtime","search_observatory"]
    event_type = 'FL'
    results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
    tqdm.write(str(results[0]["SOL_standard"]))
    for result in results:
        tmp_se=pd.Series([result[key] for key in keys],index =flare_df.columns)
        flare_df=flare_df.append(tmp_se,ignore_index=True)
    return flare_df


def download_colona_hole(tstart,tend,flare_df):
    pass #TODO:CHの場合のダウンロード

def download_active_region(tstart,tend,flare_df):
    pass #TODO: ARの場合のダウンロード

#TODO:CMEのダウンロードについてはFlareが終わってから実装します(小松)
def download_CME():
    # # event_type = 'CE'
    # keys =["SOL_standard","cme_accel","cme_angularwidth","cme_mass","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","event_starttime","event_endtime","search_observatory"]
    # results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
    # for result in results:
    #     tmp_se=pd.Series([result[key] for key in keys],index =Flaredf.columns)
    #     Flaredf=Flaredf.append(tmp_se,ignore_index=True)
    # while (tstart< TEND):
    #     print(tstart)
    #     results = client.search(hek.attrs.Time(tstart,tstart+ relativedelta(months=1)),hek.attrs.EventType(event_type))

    #     for result in results:
    #         tmp_se=pd.Series([result[key] for key in keys],index =Flaredf.columns)
    #         Flaredf=Flaredf.append(tmp_se,ignore_index=True)
    #     tstart=tstart+ relativedelta(months=1)
    #     time.sleep(10)
    pass

main()
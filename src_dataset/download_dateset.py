import datetime
from sunpy.net import hek
import pandas as pd
import time
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

client = hek.HEKClient()
years=[2012+i for i in range(8)]
months = [i+1 for i in range(12)]
keys =["SOL_standard","fl_goescls","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","hpc_coord","event_starttime","event_endtime","search_observatory"]

def main ():
    with tqdm(total = len(years)*len(months)) as pbar:
        for year in years:
            flare_df =pd.DataFrame(columns=keys)
            for month  in months:
                pbar.update(1)
                for i in range(3):
                    tstart = datetime.date(year,month,i*10+1)
                    tend = tstart + relativedelta(days=9)
                    if(tstart.day==21):
                        tend = get_last_date(tend)# 月末ならば末日までダウンロードに変更
                    flare_df = download_flare(tstart,tend,flare_df)
                time.sleep(300)
            filename = "../flare/Flare{}.csv".format(year)
            print(filename)
            flare_df.to_csv(filename)

def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])

def download_flare(tstart,tend,flare_df):
    event_type = 'FL'
    results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
    tqdm.write(str(results[0]["SOL_standard"]))
    for result in results:
        tmp_se=pd.Series([result[key] for key in keys],index =flare_df.columns)
        flare_df=flare_df.append(tmp_se,ignore_index=True)
    return flare_df

#TODO:CMEのダウンロードについてはFlareが終わってから実装します
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
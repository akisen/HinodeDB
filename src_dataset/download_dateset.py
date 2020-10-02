import datetime
from sunpy.net import hek
import pandas as pd
import time
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from dateutil.relativedelta import relativedelta

def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])
client = hek.HEKClient()
years=[2010+i for i in range(10)]
months = [i+1 for i in range(12)]
for year in years:
    keys =["SOL_standard","fl_goescls","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","event_starttime","event_endtime","search_observatory"]
    Flaredf =pd.DataFrame(columns=keys)
    for month  in months:
        tstart = datetime.date(year,month,1)
        tend = tstart + relativedelta(months=1)
        event_type = 'FL'
        results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
        print(results)
        for result in results:
            tmp_se=pd.Series([result[key] for key in keys],index =Flaredf.columns)
            Flaredf=Flaredf.append(tmp_se,ignore_index=True)
        time.sleep(600)
        # event_type = 'CE'
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
    filename = "../flare/Flare{}.csv".format(year)
    print(filename)
    Flaredf.to_csv(filename)
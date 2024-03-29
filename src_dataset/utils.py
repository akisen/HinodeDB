import sunpy
import pandas as pd
import time
import datetime
import pickle
def convert_time(previous_df):
    converted_df = previous_df
    time_series = previous_df["DATE_OBS"]
    time_series = time_series +946652400 #UNIX時間(1970/1/1からの経過時間に合わせるために加算)
    time_series = time_series.map(lambda time: datetime.datetime.fromtimestamp(time))
    time_series = time_series.map(add_leap_second)
    converted_df["DATE_OBS"] = time_series
    time_series = previous_df["DATE_END"]
    time_series = time_series +946652400 #UNIX時間(1970/1/1からの経過時間に合わせるために加算)
    time_series = time_series.map(lambda time: datetime.datetime.fromtimestamp(time))
    time_series = time_series.map(add_leap_second)
    converted_df["DATE_END"] = time_series
    return converted_df
def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj,f)
def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data
def add_leap_second(time):
    if(time>datetime.date(2006,1,1)):
        time+=datetime.timedelta(seconds=1)
    if(time>datetime.date(2009,1,1)):
        time+=datetime.timedelta(seconds=1)
    if(time>datetime.date(2012,7,1)):
        time+=datetime.timedelta(seconds=1)
    if(time>datetime.date(2015,7,1)):
        time+=datetime.timedelta(seconds=1)
    if(time>datetime.date(2017,1,1)):
        time+=datetime.timedelta(seconds=1)
    return time
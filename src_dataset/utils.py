import sunpy
import pandas as pd
import time
import datetime
hinode_path = "../eis/EIS_2010.csv"
swan_path = "../dataverse_files/SWAN/partition1/1.csv"
def convert_time(previous_df):
    converted_df = previous_df
    time_series = previous_df["DATE_OBS"]
    time_series = time_series +946652400 #UNIX時間(1970/1/1からの経過時間に合わせるために加算)
    time_series = time_series.map(lambda time: datetime.datetime.fromtimestamp(time))
    converted_df["DATE_OBS"] = time_series
    return converted_df
hinode_df= pd.read_csv(hinode_path)
swan_df = pd.read_table(swan_path)
# print(convert_time(hinode_df))
print(swan_df)
import sunpy.coordinates
import sunpy.map
from astropy.coordinates import SkyCoord
import astropy.units as u
import datetime
import sys
import pandas as pd
from sunpy.coordinates import frames
import glob
import glob
import utils
from shapely.geometry import Polygon

YEARS = [2010+i for i in range(10)]
SOT_SP_PATH = "../sot_sp/SOTSP_*.csv"
SOT_FG_PATH = "../sot_fg/SOTFG_*.csv"
EIS_PATH = "../eis/EIS_*.csv"
XRT_PATH = "../xrt/XRT_*.csv"
FLARE_PATH = "../flare/Flare2010.csv"

def path_to_dic(path_str):
    paths = sorted(glob.glob(path_str))
    paths_dic = {path.split("/")[-1][-8:-4]:path for path in paths}
    return paths_dic

def read_flare_csv(path_str):
    flare_df = pd.read_csv(FLARE_PATH,index_col=0)
    flare_df = flare_df.query('search_observatory=="SDO"')
    flare_df = flare_df.dropna(subset=["fl_goescls"])
    flare_df = flare_df.reset_index(drop=True)
    return flare_df

def add_flare_series(df):
    df["CFlare"] = [ [] for i in range(len(df))]
    df["MFlare"] = [ [] for i in range(len(df))]
    df["XFlare"] = [ [] for i in range(len(df))]
    return df

def line_to_polygon_flare(line):
    ll_x = line["boundbox_c1ll"]
    ll_y = line["boundbox_c2ll"]
    ur_x = line["boundbox_c1ur"]
    ur_y = line["boundbox_c2ur"]
    polygon = Polygon([(ll_x,ll_y),(ll_x,ur_y),(ur_x,ur_y),(ur_x,ll_y)])
    return polygon

def line_to_polygon_hinode (line):
    ll = [line["XCEN"]-line["FOVX"]//2,line["XCEN"]+line["FOVX"]//2]
    ur =[line["YCEN"]-line["FOVY"]//2,line["YCEN"]+line["FOVY"]//2]
    c=SkyCoord(ll*u.arcsec,ur*u.arcsec,frame = frames.Helioprojective,obstime= line["DATE_OBS"],observer="earth")
    c = c.transform_to(frames.HeliographicStonyhurst)
    # print(c)
    ll_x = c.lat[0].value
    ll_y = c.lon[0].value
    ur_x = c.lat[1].value
    ur_y = c.lon[1].value
    polygon = Polygon([(ll_x,ll_y),(ll_x,ur_y),(ur_x,ur_y),(ur_x,ll_y)])
    return polygon

def is_intersection(polygonA,polygonB):
    return polygonA.intersection(polygonB)

def is_in_time (hinode_line,flare_line):
    hinode_start = hinode_line["DATE_OBS"]
    hinode_end = hinode_line["DATE_END"]
    flare_start =  datetime.datetime.strptime(flare_line["event_starttime"],"%Y-%m-%dT%H:%M:%S")
    flare_end = datetime.datetime.strptime(flare_line["event_endtime"],"%Y-%m-%dT%H:%M:%S")
    print(flare_start,hinode_start,hinode_end,flare_end)
    return flare_start < hinode_start and hinode_end<flare_end

def main():
    sot_sp_paths_dic = path_to_dic(SOT_SP_PATH)#各年度でPathを格納した辞書を作成
    sot_fg_paths_dic = path_to_dic(SOT_FG_PATH)
    eis_paths_dic = path_to_dic(EIS_PATH)
    xrt_path_dic =path_to_dic(XRT_PATH)
    flare_df = read_flare_csv(FLARE_PATH)
    sot_fg_2010 = pd.read_csv(sot_fg_paths_dic["2010"])
    sot_fg_2010 = add_flare_series(sot_fg_2010)
    sot_fg_2010 = utils.convert_time(sot_fg_2010)
    flare_polygon =line_to_polygon_flare(flare_df.iloc[0])
    hinode_polygon = line_to_polygon_hinode(sot_fg_2010.loc[0])
    for i in range(len(flare_df)):
        flare_line = flare_df.loc[i]
        flare_polygon = line_to_polygon_flare(flare_line)
        # print("flare:"+str(flare_polygon))
        for j in range(len(sot_fg_2010)):
            hinode_line = sot_fg_2010.loc[j]
            hinode_polygon = line_to_polygon_hinode(hinode_line)
            print(is_in_time(hinode_line,flare_line))
            if is_in_time(hinode_line,flare_line) and is_intersection(hinode_polygon,flare_polygon):
                print("intersection")


main()
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
from shapely.geometry import Polygon,Point

YEARS = [2010+i for i in range(10)]
SOT_SP_PATH = "sot_sp/SOTSP_*.csv"
SOT_FG_PATH = "sot_fg/SOTFG_*.csv"
EIS_PATH = "eis/EIS_*.csv"
XRT_PATH = "xrt/XRT_*.csv"
FLARE_PATH = "flare/Flare*.csv"

def path_to_dic(path_str):
    paths = sorted(glob.glob(path_str))
    paths_dic = {path.split("/")[-1][-8:-4]:path for path in paths}
    return paths_dic

def read_flare_csv(path_str):
    flare_df = pd.read_csv(path_str,index_col=0)
    flare_df = flare_df.query('search_observatory=="SDO"')
    flare_df = flare_df.dropna(subset=["fl_goescls"])
    flare_df = flare_df.reset_index(drop=True)
    return flare_df

def add_flare_series(df):
    df["CFlare"] = [ [] for i in range(len(df))]
    df["MFlare"] = [ [] for i in range(len(df))]
    df["XFlare"] = [ [] for i in range(len(df))]
    return df

def initialize_hinode_df(path):
    hinode_df = pd.read_csv(path) #TODO:各年度、各データに対して網羅的にデータフレームを作成するように変更
    hinode_df = hinode_df.dropna(axis=0,how="any")
    hinode_df = hinode_df.reset_index(drop=True)
    hinode_df = add_flare_series(hinode_df)
    hinode_df = utils.convert_time(hinode_df)

    return hinode_df

def line_to_point_flare(line):
    point = line.hpc_coord[6:-1].split(" ")
    point = [float(p) for p in point]#Int型に型変換
    point = Point(point)
    return point

def line_to_polygon_flare(line):
    ll_x = line.boundbox_c1ll
    ll_y = line.boundbox_c2ll
    ur_x = line.boundbox_c1ur
    ur_y = line.boundbox_c2ur
    polygon = Polygon([(ll_x,ll_y),(ll_x,ur_y),(ur_x,ur_y),(ur_x,ll_y)])
    return polygon

def line_to_polygon_hinode (line):
    x = [line.XCEN-(line.FOVX//2),line.XCEN+(line.FOVX//2)]
    y =[line.YCEN-(line.FOVY//2),line.YCEN+(line.FOVY//2)]
    print(x,y)
    c=SkyCoord(x*u.arcsec,y*u.arcsec,frame = frames.Helioprojective,obstime= line.DATE_OBS,observer="earth")
    c = c.transform_to(frames.HeliographicStonyhurst)#TODO: 天球外が撮影範囲に入っているときに変換した際にNaNがはいってしまう→相談(なくすor丸め込む)
    # print(c)
    ll_x = c.lat[0].value
    ll_y = c.lon[0].value
    ur_x = c.lat[1].value
    ur_y = c.lon[1].value
    print(ll_x,ll_y,ur_x,ur_y)
    polygon = Polygon([(ll_x,ll_y),(ll_x,ur_y),(ur_x,ur_y),(ur_x,ll_y)])
    return polygon

def is_contained(polygon,point):
    return polygon.contains(point)

def is_in_time (hinode_line,flare_line):
    hinode_obs = hinode_line.DATE_OBS
    hinode_end = hinode_line.DATE_END
    flare_start =  datetime.datetime.strptime(flare_line.event_starttime,"%Y-%m-%dT%H:%M:%S")
    flare_end = datetime.datetime.strptime(flare_line.event_endtime,"%Y-%m-%dT%H:%M:%S")
    print(flare_start,hinode_obs,flare_end)
    return flare_start <= hinode_obs < flare_end

def main():
    sot_sp_paths_dic = path_to_dic(SOT_SP_PATH)#各年度でPathを格納した辞書を作成
    sot_fg_paths_dic = path_to_dic(SOT_FG_PATH)
    eis_paths_dic = path_to_dic(EIS_PATH)
    xrt_path_dic =path_to_dic(XRT_PATH)
    hinode_dics = [sot_sp_paths_dic,sot_fg_paths_dic,eis_paths_dic,xrt_path_dic]
    flare_path_dic = path_to_dic(FLARE_PATH)
    for year in YEARS:
        print(year)
        flare_df = read_flare_csv(flare_path_dic[str(year)])
        for hinode_dic in hinode_dics:
            if (hinode_dic.__len__()==7 and year > 2016): #sot_fgのデータが2016年分までしかないため
                continue
            else:
                hinode_df = initialize_hinode_df(hinode_dic[str(year)])
                for flare_line in flare_df.itertuples():
                    flare_point = line_to_point_flare(flare_line)
                    # print(point)
                    # flare_polygon = line_to_polygon_flare(flare_line)
                    # print(flare_polygon)
                    for hinode_line in hinode_df.itertuples():
                        hinode_polygon = line_to_polygon_hinode(hinode_line)
                        if is_in_time(hinode_line,flare_line) and is_contained(hinode_polygon,flare_point):
                            print("intersection")
                        else:
                            print("not intersection")


main()
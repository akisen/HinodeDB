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
from tqdm import tqdm
YEARS = [2010+i for i in range(10)]
SOT_SP_PATH = "sot_sp/SOTSP_*.csv"
SOT_FG_PATH = "sot_fg/SOTFG_*.csv"
EIS_PATH = "eis/EIS_*.csv"
XRT_PATH = "xrt/XRT_*.csv"
FLARE_PATH = "flare/Flare*.csv"

def main():
    sot_sp_paths_dic = path_to_dic(SOT_SP_PATH)#各年度でPathを格納した辞書を作成
    sot_fg_paths_dic = path_to_dic(SOT_FG_PATH)
    eis_paths_dic = path_to_dic(EIS_PATH)
    xrt_path_dic =path_to_dic(XRT_PATH)
    hinode_dics = [sot_sp_paths_dic,sot_fg_paths_dic,eis_paths_dic,xrt_path_dic]
    flare_path_dic = path_to_dic(FLARE_PATH)
    for year in YEARS:
        flare_df = read_flare_csv(flare_path_dic[str(year)])
        for hinode_dic in hinode_dics:
            if (hinode_dic.__len__()==7 and year > 2016): #sot_fgのデータが2016年分までしかないため
                continue
            else:
                hinode_df = initialize_hinode_df(hinode_dic[str(year)])
                with tqdm(total = len(flare_df)) as pbar:
                    for flare_line in flare_df.itertuples():
                        flare_point = line_to_point_flare(flare_line)
                        for hinode_line in hinode_df.itertuples():
                            hinode_polygon = line_to_polygon_hinode(hinode_line)
                            if is_in_time(hinode_line,flare_line) and is_contained(hinode_polygon,flare_point):
                                add_flare_label(hinode_line,flare_line)
                                write_log(hinode_line,flare_line,hinode_dic[str(year)])
                        pbar.update(1)
                utils.pickle_dump(hinode_df,"pickles/{}pickle".format(hinode_dic[str(year)].split("/")[-1][:-3]))
                export_csv(hinode_df,hinode_dic[str(year)])
                
def path_to_dic(path_str):
    paths = sorted(glob.glob(path_str))
    paths_dic = {path.split("/")[-1][-8:-4]:path for path in paths}
    return paths_dic

def read_flare_csv(path_str):
    flare_df = pd.read_csv(path_str,index_col=0)
    flare_df = flare_df.drop(flare_df.index[flare_df["boundbox_c1ll"]<=-90])# 観測座標がおかしい行の削除
    flare_df = flare_df.drop_duplicates() # 重複行の削除
    flare_df = flare_df.dropna(subset=["fl_goescls"]) #GOESクラスが入っていない行を削除
    flare_df = flare_df.reset_index(drop=True)
    return flare_df

def add_flare_series(df):
    df["BFlare"] = [ [] for i in range(len(df))]
    df["CFlare"] = [ [] for i in range(len(df))]
    df["MFlare"] = [ [] for i in range(len(df))]
    df["XFlare"] = [ [] for i in range(len(df))]
    return df

def initialize_hinode_df(path):
    hinode_df = pd.read_csv(path)
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
    ll_x = line.XCEN-(line.FOVX//2)
    ur_x = line.XCEN+(line.FOVX//2)
    ll_y = line.YCEN-(line.FOVY//2)
    ur_y = line.YCEN+(line.FOVY//2)
    polygon = Polygon([(ll_x,ll_y),(ll_x,ur_y),(ur_x,ur_y),(ur_x,ll_y)])
    return polygon

def is_contained(polygon,point):
    return polygon.contains(point)

def is_in_time (hinode_line,flare_line):
    hinode_obs = hinode_line.DATE_OBS
    hinode_end = hinode_line.DATE_END
    flare_start =  datetime.datetime.strptime(flare_line.event_starttime,"%Y-%m-%dT%H:%M:%S")
    flare_end = datetime.datetime.strptime(flare_line.event_endtime,"%Y-%m-%dT%H:%M:%S")
    return flare_start <= hinode_obs < flare_end

def add_flare_label(hinode_line,flare_line):
    flare_class = flare_line.fl_goescls[0]
    flare_label = "{}:{}".format(flare_line.SOL_standard,flare_line.fl_goescls)
    if(flare_class == "B"):
        hinode_line.BFlare.append(flare_label)
        tqdm.write("B:{}".format(flare_label))
    elif(flare_class == "C"):
        hinode_line.CFlare.append(flare_label)
        tqdm.write("C:{}".format(flare_label))
    elif(flare_class == "M"):
        hinode_line.MFlare.append(flare_label)
        tqdm.write("M:{}".format(flare_label))
    elif(flare_class == "`X"):
        hinode_line.XFlare.append(flare_label)
        tqdm.write("X:{}".format(flare_label))

def write_log(hinode_line,flare_line,hinode_path):
    logtext = "intersection\nflare_time{}-{}\nflare_point:{}\nhinode_time{}\nhinode_polygon:XCEN{},YCEN{},FOVX{},FOVY{}".format(flare_line.event_starttime,flare_line.event_endtime,flare_line.hpc_coord,hinode_line.DATE_OBS,hinode_line.XCEN,hinode_line.YCEN,hinode_line.FOVX,hinode_line.FOVY)
    tqdm.write(logtext)
    logpath = "logs/log_{}txt".format(hinode_path.split("/")[-1][:-3])
    with open (logpath,"a") as f:
        print(logtext,file = f)

def export_csv(hinode_df,old_path):
    hinode_df["BFlare"] = hinode_df["BFlare"].map(lambda x:"   ".join(x))#リストのままだとCSVに書き出しできないのでタブ区切りに変換
    hinode_df["CFlare"] = hinode_df["CFlare"].map(lambda x:"   ".join(x))
    hinode_df["MFlare"] = hinode_df["MFlare"].map(lambda x:"   ".join(x))
    hinode_df["XFlare"] = hinode_df["XFlare"].map(lambda x:"   ".join(x))
    new_path = "flare_labeled/{}".format(old_path.split("/")[-1])
    hinode_df.to_csv(new_path)




main()
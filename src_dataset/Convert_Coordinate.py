"""
Hinodeの観測データとHekの観測データからともに観測している部分を抽出し、Hinode観測データに追記したものを出力するスクリプト
---
ディレクトリ構成
HinodeDB/
    ├sot_sp/
        └sot_spによって観測されたデータ群
    ├sot_fg/
        └sot_fgによって観測されたデータ群
    ├eis/
        └eisによって観測されたデータ群
    ├xrt
        └xrtによって観測されたデータ群
    ├FL
        └HEKからダウンロードしたデータ群(download_sol_table.pyによってDL可能)
    ├src_dataset
        └データセットの作成に必要なスクリプト(本スクリプトを含む)
---
"""

import datetime
import glob
import sys

import astropy.units as u
import pandas as pd
import sunpy.coordinates
import sunpy.map
from astropy.coordinates import SkyCoord
from shapely.geometry import Point, Polygon
from sunpy.coordinates import frames
from tqdm import tqdm

import utils

YEARS = [2010+i for i in range(10)]
SOT_SP_PATH = "sot_sp/SOTSP_*.csv"
SOT_FG_PATH = "sot_fg/SOTFG_*.csv"
EIS_PATH = "eis/EIS_*.csv"
XRT_PATH = "xrt/XRT_*.csv"
FLARE_PATH = "FL/SOL_all_FL*.csv"


def main():
    sot_sp_paths_dic = path_to_dic(SOT_SP_PATH)  # 各年度でPathを格納した辞書を作成
    sot_fg_paths_dic = path_to_dic(SOT_FG_PATH)
    eis_paths_dic = path_to_dic(EIS_PATH)
    xrt_path_dic = path_to_dic(XRT_PATH)
    hinode_dics = [sot_sp_paths_dic,
                   sot_fg_paths_dic, eis_paths_dic, xrt_path_dic]
    flare_path_dic = path_to_dic(FLARE_PATH)
    for year in YEARS:
        #TODO:AR,CHへの分岐を追加
        flare_df = read_flare_csv(flare_path_dic[str(year)])
        for hinode_dic in hinode_dics:
            if (hinode_dic.__len__() == 7 and year > 2016):  # sot_fgのデータが2016年分までしかないため
                continue
            else:
                hinode_df = initialize_hinode_df(hinode_dic[str(year)])
                with tqdm(total=len(flare_df), desc="{}".format(hinode_dic[str(year)])) as pbar:
                    for flare_row in flare_df.itertuples():
                        flare_point = row_to_point_flare(flare_row)
                        for hinode_row in hinode_df.itertuples():
                            hinode_polygon = row_to_polygon_hinode(hinode_row)
                            if is_in_time(hinode_row, flare_row) and is_contained(hinode_polygon, flare_point):
                                add_flare_label(hinode_row, flare_row)
                                write_log(hinode_row, flare_row,
                                          hinode_dic[str(year)])
                        pbar.update(1)
                # utils.pickle_dump(hinode_df,"pickles/{}pickle".format(hinode_dic[str(year)].split("/")[-1][:-3]))
                export_csv(hinode_df, hinode_dic[str(year)])


def path_to_dic(path_str):
    paths = sorted(glob.glob(path_str))
    paths_dic = {path.split("/")[-1][-8:-4]: path for path in paths}
    return paths_dic


def read_flare_csv(path_str):
    flare_df = pd.read_csv(path_str, index_col=0)
    flare_df = flare_df.drop(
        flare_df.index[flare_df["boundbox_c1ll"] <= -90])  # 観測座標がおかしい行の削除
    flare_df = flare_df.drop_duplicates()  # 重複行の削除
    flare_df = flare_df.dropna(subset=["fl_goescls"])  # GOESクラスが入っていない行を削除
    flare_df = flare_df.reset_index(drop=True)
    return flare_df


def add_flare_series(df):
    df["BFlare"] = [[] for i in range(len(df))]
    df["CFlare"] = [[] for i in range(len(df))]
    df["MFlare"] = [[] for i in range(len(df))]
    df["XFlare"] = [[] for i in range(len(df))]
    return df


def initialize_hinode_df(path):
    hinode_df = pd.read_csv(path)
    hinode_df = hinode_df.dropna(axis=0, how="any")
    hinode_df = hinode_df.reset_index(drop=True)
    hinode_df = add_flare_series(hinode_df)
    hinode_df = utils.convert_time(hinode_df)
    return hinode_df


def row_to_point_flare(row):
    point = row.hpc_coord[6:-1].split(" ")
    point = [float(p) for p in point]  # Int型に型変換
    point = Point(point)
    return point


def row_to_polygon_flare(row):
    ll_x = row.boundbox_c1ll
    ll_y = row.boundbox_c2ll
    ur_x = row.boundbox_c1ur
    ur_y = row.boundbox_c2ur
    polygon = Polygon([(ll_x, ll_y), (ll_x, ur_y), (ur_x, ur_y), (ur_x, ll_y)])
    return polygon


def row_to_polygon_hinode(row):
    ll_x = row.XCEN-(row.FOVX//2)
    ur_x = row.XCEN+(row.FOVX//2)
    ll_y = row.YCEN-(row.FOVY//2)
    ur_y = row.YCEN+(row.FOVY//2)
    polygon = Polygon([(ll_x, ll_y), (ll_x, ur_y), (ur_x, ur_y), (ur_x, ll_y)])
    return polygon


def is_contained(polygon, point):
    return polygon.contains(point)


def is_in_time(hinode_row, flare_row):
    hinode_obs = hinode_row.DATE_OBS
    hinode_end = hinode_row.DATE_END
    flare_start = datetime.datetime.strptime(
        flare_row.event_starttime, "%Y-%m-%dT%H:%M:%S")
    flare_end = datetime.datetime.strptime(
        flare_row.event_endtime, "%Y-%m-%dT%H:%M:%S")
    return flare_start <= hinode_obs < flare_end


def add_flare_label(hinode_row, flare_row):
    flare_class = flare_row.fl_goescls[0]
    flare_label = "{}:{}".format(flare_row.SOL_standard, flare_row.fl_goescls)
    if(flare_class == "B"):
        hinode_row.BFlare.append(flare_label)
        tqdm.write("B:{}".format(flare_label))
    elif(flare_class == "C"):
        hinode_row.CFlare.append(flare_label)
        tqdm.write("C:{}".format(flare_label))
    elif(flare_class == "M"):
        hinode_row.MFlare.append(flare_label)
        tqdm.write("M:{}".format(flare_label))
    elif(flare_class == "`X"):
        hinode_row.XFlare.append(flare_label)
        tqdm.write("X:{}".format(flare_label))


def write_log(hinode_row, flare_row, hinode_path):
    logtext = "intersection\nflare_time{}-{}\nflare_point:{}\nhinode_time{}\nhinode_polygon:XCEN{},YCEN{},FOVX{},FOVY{}".format(
        flare_row.event_starttime, flare_row.event_endtime, flare_row.hpc_coord, hinode_row.DATE_OBS, hinode_row.XCEN, hinode_row.YCEN, hinode_row.FOVX, hinode_row.FOVY)
    tqdm.write(logtext)
    logpath = "logs/log_{}txt".format(hinode_path.split("/")[-1][:-3])
    with open(logpath, "a") as f:
        print(logtext, file=f)


def export_csv(hinode_df, old_path):
    hinode_df["BFlare"] = hinode_df["BFlare"].map(
        lambda x: "   ".join(x))  # リストのままだとCSVに書き出しできないのでタブ区切りに変換
    hinode_df["CFlare"] = hinode_df["CFlare"].map(lambda x: "   ".join(x))
    hinode_df["MFlare"] = hinode_df["MFlare"].map(lambda x: "   ".join(x))
    hinode_df["XFlare"] = hinode_df["XFlare"].map(lambda x: "   ".join(x))
    new_path = "flare_labeled/{}".format(old_path.split("/")[-1])
    hinode_df.to_csv(new_path)


main()

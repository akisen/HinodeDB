from astropy.wcs.utils import wcs_to_celestial_frame
import sunpy.coordinates
import sunpy.map
from sunpy.data.sample import AIA_171_IMAGE
from astropy.coordinates import SkyCoord
import astropy.units as u
import pandas as pd
from sunpy.coordinates import frames
path = "../sot_sp/SOTSP_2010.csv"
sot_sp_df = pd.read_csv(path)
# c = Skycoord()
s=pd.Series(sot_sp_df.loc[0])
hinode_ll = [s["XCEN"]-s["FOVX"]//2,s["XCEN"]+s["FOVX"]//2]
hinode_ur =[s["YCEN"]-s["FOVY"]//2,s["YCEN"]+s["FOVY"]//2]
hinode_coords =SkyCoord(hinode_ll*u.arcsec,hinode_ur*u.arcsec,frame = frames.Helioprojective,obstime= "2010-01-01",observer="earth")
transformed_hinode_coords = hinode_coords.transform_to(frames.HeliographicStonyhurst)
print(transformed_hinode_coords)
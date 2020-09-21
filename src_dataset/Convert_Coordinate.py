from astropy.wcs.utils import wcs_to_celestial_frame
# import sunpy.coordinates
import sunpy.map
from sunpy.data.sample import AIA_171_IMAGE
from astropy.coordinates import SkyCoord
import astropy.units as u
amap = sunpy.map.Map(AIA_171_IMAGE)
print(wcs_to_celestial_frame(amap.wcs))
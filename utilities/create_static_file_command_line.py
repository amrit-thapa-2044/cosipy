"""
 This file reads the DEM of the study site and the shapefile and creates the needed static.nc
"""

import xarray as xr
import numpy as np
import netCDF4
import os

static_folder = '../data/static/'

dem_path_tif_to_shrink = static_folder + 'Rofental_DEM.tif'
dem_path_tif = static_folder + 'Hintereisferner_DEM.tif'
shape_path = static_folder + 'HEF_Flaeche2018.shp'

### for shrinking the input DEM file to a smaller DEM
longitude_upper_left = '10.72'
latitude_upper_left = '46.82'
longitude_lower_right = '10.795'
latitude_lower_right = '46.78'

### intermediate files
dem_path = static_folder + 'dem.nc'
aspect_path = static_folder + 'aspect.nc'
mask_path = static_folder + 'mask.nc'
slope_path = static_folder + 'slope.nc'

### path were the static.nc file is saved
output_path = static_folder + 'static.nc'

os.system('gdal_translate -r cubicspline -projwin ' + longitude_upper_left + ' ' + latitude_upper_left + ' ' +
          longitude_lower_right + ' ' + latitude_lower_right + ' ' + dem_path_tif_to_shrink + ' ' + dem_path_tif)
os.system('gdal_translate -of NETCDF ' + dem_path_tif + ' ' + dem_path)
os.system('gdaldem slope -of NETCDF ' + dem_path + ' ' + slope_path + ' -s 111120')
os.system('gdaldem aspect -of NETCDF ' + dem_path + ' ' + aspect_path)
os.system('gdalwarp -of NETCDF -cutline ' + shape_path + ' ' + dem_path_tif + ' ' + mask_path)

dem = xr.open_dataset(dem_path)
aspect = xr.open_dataset(aspect_path)
mask = xr.open_dataset(mask_path)
slope = xr.open_dataset(slope_path)

mask=mask.Band1.values
mask[mask==np.nan]=-9999
mask[mask>0]=1

ds = xr.Dataset()
ds.coords['lon'] = dem.lon.values
ds.lon.attrs['standard_name'] = 'lon'
ds.lon.attrs['long_name'] = 'longitude'
ds.lon.attrs['units'] = 'degrees_east'

ds.coords['lat'] = dem.lat.values
ds.lat.attrs['standard_name'] = 'lat'
ds.lat.attrs['long_name'] = 'latitude'
ds.lat.attrs['units'] = 'degrees_north'

def insert_var(ds, var, name, units, long_name):
    ds[name] = (('lat','lon'), var)
    ds[name].attrs['units'] = units
    ds[name].attrs['long_name'] = long_name
    ds[name].attrs['_FillValue'] = -9999

insert_var(ds, dem.Band1.values,'HGT','meters','meter above sea level')
insert_var(ds, aspect.Band1.values,'ASPECT','degress','Aspect of slope')
insert_var(ds, slope.Band1.values,'SLOPE','degress','Terrain slope')
insert_var(ds, mask,'MASK','boolean','Glacier mask')

ds.to_netcdf(output_path)
os.system('rm '+ dem_path + ' ' + aspect_path + ' ' + mask_path + ' ' + slope_path)

print("Study area consists of ", np.nansum(mask[mask==1]), " glacier points")
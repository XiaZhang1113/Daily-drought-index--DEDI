import netCDF4
import numpy as np
import pandas as pd
from datetime import datetime


#-------------------------------------------------------------------------------
def cal_climatology(aetdir,petdir,years):

    '''
     Calculate the multi-year climatic mean and standard deviation of the the difference between actual and potential evapotranspiration (the period 1979-2008 used in this study)
     pay attention to convert unit to mm and fluxes transfer direction.
     Please see tha details in the ERA5 documentation. 
     https://apps.ecmwf.int/codes/grib/param-db/?id=182
     https://apps.ecmwf.int/codes/grib/param-db/?id=228251

     years: the studied period
     lon: the longitude of the studied area
     lat: the latitude of the studied area
     aetdir: the file path of actual evapotranspiration
     petdir: the file path of potential evapotranspiration
     outfile: the file path of outputing DEDI values
     diff: the difference between actual and potential evapotranspiration
     diff_clim_mean: the multi-year climatic mean
     diff_clim_std: the multi-year climatic standard deviation
    '''

    clim_years = 30
    for yr in range(clim_years):
        aetfile = netCDF4.Dataset(aetdir+'era5_daily_actual_evaporation_%04d.nc'%(years[yr]),mode = 'r')
        petfile = netCDF4.Dataset(petadir+'era5_daily_potential_evaporation_%04d.nc'%(years[yr]),mode = 'r')
    
        aet = aetfile.variables['e'][:]
        pet = petfile.variables['pev'][:]
    
        diff = aet*(-1000)-pet*(-1000) 
        sz = diff.shape
        
        if yr == 0:
           diff_clim = np.full([clim_years,sz[0],sz[1],sz[2]],np.nan)
    
        diff_clim[yr,:,:,:] = diff
        del aet, pet, diff
    
    diff_clim_mean = np.squeeze(np.nanmean(diff_clim,axis=0))
    diff_clim_std = np.squeeze(np.nanstd(diff_clim,axis=0))
    
    return (diff_clim_mean, diff_clim_std)


# ------------------------------------------------------------------------------
def cal_DEDI(aetdir,petdir,years,diff_clim_mean,diff_clim_std,lon,lat,outfile):

    '''
     Calculate Daily Evapotranspiration Deficit Index (DEDI)
    '''

    for yr in range(len(years)):
        aetfile = netCDF4.Dataset(aetdir+'era5_daily_actual_evaporation_%04d.nc'%(years[yr]),mode = 'r')
        petfile = netCDF4.Dataset(petadir+'era5_daily_potential_evaporation_%04d.nc'%(years[yr]),mode = 'r')
    
        aet = aetfile.variables['e'][:]
        pet = petfile.variables['pev'][:]
    
        diff = aet*(-1000)-pet*(-1000) 

        DEDI = (diff - diff_clim_mean)/diff_clim_std
    
        # save as netcdf files
        time = pd.date_range(datetime(years[yr], 1, 1), datetime(years[yr], 12, 31), freq='D')     
        f = netCDF4.Dataset(outfile+'ERA5_DEDI_global_%04d_daily.nc'%(years[yr]), mode='w',format='NETCDF4') 
        dimT = DEDI.shape[0]
        dimY = DEDI.shape[1]
        dimX = DEDI.shape[2]
        
        f.createDimension('longitude', dimX)
        f.createDimension('latitude', dimY)
        f.createDimension('time', None)
        
        f.createVariable('longitude', 'f', ('longitude'))
        f.createVariable('latitude', 'f', ('latitude'))
        f.createVariable('time','int', ('time'))
        f.createVariable('DEDI', 'f', ('time', 'latitude', 'longitude'))
        
        f.variables['longitude'].units = 'degrees_east'
        f.variables['longitude'].long_name = 'longitude'
        f.variables['latitude'].units = 'degrees_north'
        f.variables['latitude'].long_name = 'latitude'
        f.variables['time'].units = 'days since %04d-01-01'%(years[yr])
        f.variables['time'].long_name = 'time'
        f.variables['DEDI'].units = '-'
        f.variables['DEDI'].long_name = 'Daily Evapotranspiration Deficit Index'
        
        f.variables['DEDI'][:] = DEDI[:]
        f.variables['longitude'][:] = lon
        f.variables['latitude'][:] = lat
        f.variables['time'] = time       
        
        f.close()
        


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    aetdir = './aet/'
    petdir = './pet/'
    outfile = './DEDI/'
    
    years = np.arange(1979,2021+1)
    # get lon and lat 
    datafile = netCDF4.Dataset(aetdir + 'era5_daily_actual_evaporation_1979.nc','r')
    lon = datafile.variables['longitude'][:]
    lat = datafile.variables['latitude'][:]
    
    [clim_mean,clim_std] = cal_climatology(aetdir,petdir,years)
    cal_DEDI(aetdir,petdir,years,clim_mean,clim_std,lon,lat,outfile)
    
    print('Completed!')
    


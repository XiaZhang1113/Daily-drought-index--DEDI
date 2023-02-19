import netCDF4
import numpy as np
import pandas as pd
from datetime import datetime


#-------------------------------------------------------------------------------
def cal_aetminuspet(aetdir,petdir,years):

    '''
     Calculate the difference between actual and potential evapotranspiration;
     pay attention to convert unit to mm and fluxes transfer direction.
     Please see tha details in the ERA5 documentation. 
     https://apps.ecmwf.int/codes/grib/param-db/?id=182
     https://apps.ecmwf.int/codes/grib/param-db/?id=228251

     aetdir: the file path of actual evapotranspiration
     petdir: the file path of potential evapotranspiration
     years: the studied period
     diff_all: the difference between actual and potential evapotranspiration during the studied period
    '''

    for yr in range(len(years)):
        aetfile = netCDF4.Dataset(aetdir+'era5_daily_actual_evaporation_%04d.nc'%(years[yr]),mode = 'r')
        petfile = netCDF4.Dataset(petadir+'era5_daily_potential_evaporation_%04d.nc'%(years[yr]),mode = 'r')
    
        aet = aetfile.variables['e'][:]
        pet = petfile.variables['pev'][:]
    
        diff = aet*(-1000)-pet*(-1000) 
    
        # initialize arrays
        if yr == 0:
           sz = diff.shape
           diff_all = np.full([len(years),366,sz[1],sz[2]],np.nan)
    
        if (years[yr] % 4 == 0) and (years[yr] % 100 != 0) or (years[yr] % 400 == 0): 
           print('leap year',years[yr])
        else:
           print('nonleap year',years[yr])
           diff = np.insert(diff,59,np.nan,axis=0) #make the arrays dimension-matching
    
        diff_all[yr,:,:,:] = diff
     
        del aet,pet,diff
    
        return diff_all


# ------------------------------------------------------------------------------
def cal_climatology(diff_all):

    '''
     Calculate the multi-year climatic mean and standard deviation of the the difference between actual and potential evapotranspiration (the period 1979-2008 used in this study)

     diff_all: the difference between actual and potential evapotranspiration during the studied period
     clim_mean: the multi-year climatic mean
     clim_std: the multi-year climatic standard deviation
    '''

    clim_years = 30
    clim_mean = np.mean(diff_all[0:clim_years,:,:,:],axis=0)
    clim_std = np.std_all(diff_all[0:clim_years,:,:,:], ddof = 1 ,axis=0)
    
    return (clim_mean,clim_std)


# ------------------------------------------------------------------------------
def cal_DEDI(diff_all,clim_mean,clim_std,years,lon,lat,outfile):

    '''
     Calculate Daily Evapotranspiration Deficit Index (DEDI)

     diff_all: the difference between actual and potential evapotranspiration during the studied period
     clim_mean: the multi-year climatic mean
     clim_std: the multi-year climatic standard deviation
     years: the studied period
     lon: the longitude of the studied area
     lat: the latitude of the studied area
     outfile: the file path of outputing DEDI values
    '''

    sz = diff_all.shape
    for yr in range(len(years)):
        DEDI = (diff_all[yr,:,:,:] - clim_mean)/clim_std
    
        if (years[yr] % 4 == 0) and (years[yr] % 100 != 0) or (years[yr] % 400 == 0): 
           print('leap year',years[yr])
        else:
           print('nonleap year',years[yr])
           DEDI = np.delete(DEDI,59,axis=0) # remove the added nan in 29 February during nonleap years
    
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
    
    diff = cal_aetminuspet(aetdir,petdir,years)
    [clim_mean,clim_std] = cal_climatology(diff)
    cal_DEDI(diff,clim_mean,clim_std,years,lon,lat,outfile)
    
    print('Completed!')
    

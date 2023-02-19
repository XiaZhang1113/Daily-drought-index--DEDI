#! /bin/sh

for year in  `seq 1979 2021`
do
    echo $year  

    cdo -b F64 mergetime ./aet/daily/era5_daily_Evaporation_${year}*.nc ./aet/daily/era5_daily_Evaporation_${year}.nc

    cdo -b F64 mergetime ./pet/daily/era5_daily_Potential_evaporation_${year}*.nc ./pet/daily/era5_daily_Potential_evaporation_${year}.nc

done



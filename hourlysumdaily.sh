#! /bin/sh


for year in  `seq 1979 2021`
do
    echo $year

    for month in `seq -f '%02g' 1 12`
    do
        echo $month

        cdo -b F64 daysum ./aet/hourly/era5_hourly_Evaporation_${year}_${month}.nc ./aet/daily/era5_daily_Evaporation_${year}_${month}.nc

        cdo -b F64 daysum ./pet/hourly/era5_hourly_Potential_evaporation_${year}_${month}.nc ./pet/daily/era5_daily_Potential_evaporation_${year}_${month}.nc

    done

done

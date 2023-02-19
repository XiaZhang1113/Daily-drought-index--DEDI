# Please see more details about downloading ERA5 datasets at https://cds.climate.copernicus.eu/api-how-to

import cdsapi

c = cdsapi.Client()

var = "Evaporation"
varsave = var

years = [x for x in map(str, range(1979, 2021+1))]
#years =  ['2002']

months = [
          '01', '02', '03',
	  '04', '05', '06',
	  '07', '08', '09',
	  '10', '11', '12'
         ]

for yr in years:
    for mn in months:
        print(yr)
        
        c.retrieve(
        	'reanalysis-era5-single-levels',
        	{
        
        		'product_type': 'reanalysis', 
        		'format': 'netcdf', 
        		'variable': var,
        		'year': [yr],
                        'month': [mn],
        		'day': [
        			'01', '02', '03',
        			'04', '05', '06',
        			'07', '08', '09',
        			'10', '11', '12',
        			'13', '14', '15',
        			'16', '17', '18',
        			'19', '20', '21',
        			'22', '23', '24',
        			'25', '26', '27',
        			'28', '29', '30',
        			'31',
        			],
        		'time':[
        			'00:00', '01:00', '02:00',
        			'03:00', '04:00', '05:00',
        			'06:00', '07:00', '08:00',
        			'09:00', '10:00', '11:00',
        			'12:00', '13:00', '14:00',
        			'15:00', '16:00', '17:00',
        			'18:00', '19:00', '20:00',
        			'21:00', '22:00', '23:00',
        			],
        
        	},
        
                'era5_hourly_' + varsave + '_' + yr + '_' + mn + '.nc')
        
        
        	
        





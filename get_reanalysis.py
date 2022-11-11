import numpy as np
from netCDF4 import Dataset
import glob
import sys
import matplotlib.pyplot as plt

data_dir = '/badc/ecmwf-era-interim/data/gg/{}/{}/{}/{}/'
cvars_to_get = ['CAPE', 'BLH', 'U10', 'V10', 'D2', 'T2', 'SSTK']
pvars_to_get = ['U', 'V']#,'D', 'R', 'Q', 'T', 'W']
plevs_to_get = [1000.0, 950.,]# 875., 850., 800., 700., 500., 300., 250.]
#starting by getting daily means, could in the future separate into daytime/nighttime means
#256 x 512 on gaussian grid
def get_column_data(day, month, year):
	cvars_to_get = ['CAPE', 'BLH', 'U10', 'V10', 'D2', 'T2', 'SSTK']
	data_dir = '/badc/ecmwf-era-interim/data/gg/{}/{}/{}/{}/'
	column_dict = {}
	for var in cvars_to_get:
		column_dict[var] = []
	data_dir = data_dir.format('fs', year, month, day)
	for filename in  sorted(glob.glob(data_dir + '*.nc')):
		print(filename)
		ecmwf_data = Dataset(filename, mode = 'r')
		latitudes = ecmwf_data['latitude'][:]
		longitudes = ecmwf_data['longitude'][:]
		
		for var in cvars_to_get:
			column_dict[var].append(ecmwf_data[var][:][0][0])
		ecmwf_data.close()
	for var in column_dict.keys():
		column_dict[var] = np.nanmean(column_dict[var], axis = 0)
		column_dict[var] = np.hstack((column_dict[var][:, 256:], column_dict[var][:, :256]))
		column_dict[var] = np.flip(column_dict[var], axis = 0)
	column_dict['lats'] = latitudes
	column_dict['lons'] = longitudes
	return column_dict

def calc_theta(T, p):
	theta = T * (1000 * 100. / P * 100) ** (.286)
	return theta

#plevels [1000.0, 975.0, 950.0, 925.0, 900.0, 875.0, 850.0, 825.0, 800.0, 775.0, 750.0, 700.0, 650.0, 600.0, 550.0, 500.0, 450.0, 400.0, 350.0, 300.0, 250.0, 225.0, 200.0, 175.0, 150.0, 125.0, 100.0, 70.0, 50.0, 30.0, 20.0, 10.0, 7.0, 5.0, 3.0, 2.0, 1.0]

def get_profile_data(day, month, year):
	#global data_dir, pvars_to_get, plevs_to_get
	data_dir = '/badc/ecmwf-era-interim/data/gg/{}/{}/{}/{}/'
	pvars_to_get = ['U', 'V']#,'D', 'R', 'Q', 'T', 'W']
	plevs_to_get = [1000.0, ]#950., 875., 850., 800., 700., 500., 300., 250.]
	profile_dict = {}
	for var in pvars_to_get:
		for lev in plevs_to_get:
			profile_dict['{}_{}'.format(var, lev)] = []
	data_dir = data_dir.format('ap', year, month, day)
	for filename in sorted(glob.glob(data_dir + '*.nc')):
		print(filename)
		ecmwf_data = Dataset(filename, mode = 'r')
		pressures = ecmwf_data['p'][:].tolist()
		for var in pvars_to_get:
			temp_data = ecmwf_data[var][:][0]
			for lev in plevs_to_get:
				i_lev = pressures.index(lev)
				profile_dict['{}_{}'.format(var, lev)].append(temp_data[i_lev, :, :])
	for var in profile_dict.keys():
		profile_dict[var] =  np.array(profile_dict[var]).transpose(1,2,0)
		profile_dict[var] = np.hstack((profile_dict[var][:,256:,: ], profile_dict[var][:, :256,:]))
		profile_dict[var] = np.flip(profile_dict[var], axis = 0)
		profile_dict[var] = profile_dict[var].transpose(2,0,1)
	profile_dict['lats'] = ecmwf_data['latitude'][:]
	profile_dict['lons'] = ecmwf_data['longitude'][:]
	return profile_dict

def get_uv_data(day,month, year):
	#global data_dir, pvars_to_get, plevs_to_get
	data_dir = '/gws/nopw/j04/eo_shared_data_vol2/scratch/pete_nut/era5/{}_{}'
	pvars_to_get = ['u', 'v']#,'D', 'R', 'Q', 'T', 'W']
	plevs_to_get = [1000.0, ]#950., 875., 850., 800., 700., 500., 300., 250.]
	profile_dict = {}
	for var in pvars_to_get:
		for lev in plevs_to_get:
			profile_dict[var] = []
	data_dir = data_dir.format(year, month)
	for filename in sorted(glob.glob(data_dir + '*.nc')):
		print(filename)
		ecmwf_data = Dataset(filename, mode = 'r')
		print(ecmwf_data)
		#pressures = ecmwf_data['p'][:].tolist()
		for var in pvars_to_get:
			temp_data = ecmwf_data[var]
			#print(np.shape(ecmwf_data[var]))
			for lev in plevs_to_get:
				profile_dict['{}'.format(var)].append(temp_data[(int(day)-1)*24:int(day)*24,:, :])
	profile_dict['lats'] = ecmwf_data['latitude'][:]
	profile_dict['lons'] = ecmwf_data['longitude'][:]
	return profile_dict




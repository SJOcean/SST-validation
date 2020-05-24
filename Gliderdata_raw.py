# -*- coding: utf-8 -*-
# Seaglider measurements original data process
# Horizontal and vetical grouping, data quality check
# Original code
# Author: Sunjing

# D:\Studies\Marinår3\MAR311\data\glider\2018\raw\sg573\deployment_1

import buoyancy_glider_utils as bgu  # This package can be downloaded from github
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
import numpy as np
import pandas as pd
from scipy import interpolate

#####################################
# Load data by using Luke's package #
#####################################

fname = 'p573*.nc'              # example of series glider datasets names, directory may be added 

dat = bgu.seaglider.load_basestation_netCDF_files(fname,verbose=True)
dfs = dat.load_multiple_vars([
    'temperature',
    'surface_curr_east',
    'surface_curr_north',
    'log_gps_lat',
    'log_gps_lon',
    'log_gps_time',
])

######################################################
# Organize data time points by selecting merge time  #
# at the surface where the glider send gps positions #
###################################################### 

df = dfs['ctd_data_point']
df['temp_clean'] = bgu.cleaning.rolling_window(df.temperature, func=np.median, window=4) # data cleaning
dfg = dfs['gps_info']
grp = dfg.groupby('dives').last() # group 
grp['surface_time'] = grp.log_gps_time_raw.astype('timedelta64[s]') + np.datetime64('1970-01-01 00:00:00')
dfs['string']['surface_time']=grp.surface_time.values
dfs['string']['surface_lon']=grp.log_gps_lon.values
dfs['string']['surface_lat']=grp.log_gps_lat.values

##################################################
# Grid measurements vertically                   #
# Group depth in wished grids and calculate mean #
# values of measurements (temperature here), and #
# time and coordinates                           #
##################################################

grpd =  df.groupby('dives')
bins = [0, 3,14,17,1000]  
cut_idx = pd.cut(df.ctd_depth, bins) 
grp_cut = df.groupby(['dives', cut_idx])
gsst=grp_cut.temp_clean.mean() 
gsst1 = gsst.unstack().iloc[:, 0]
#gsst2 = gsst.unstack().iloc[:,1]
gsst3 = gsst.unstack().iloc[:,2]
#gsst4 = gsst.unstack().iloc[:,3]

dfs['string']['depth_avg_lat']=grpd.latitude.mean()
dfs['string']['depth_avg_lon']=grpd.longitude.mean()
dfs['string']['depth_avg_time']=grpd.ctd_time_raw.mean().astype('timedelta64[s]') + np.datetime64('1970-01-01 00:00:00')
dfs['string']['depth']=grpd.ctd_depth.max()
dfs['string']['sst1'] = gsst1
#dfs['string']['sst2'] = gsst2
dfs['string']['sst3'] = gsst3
#dfs['string']['sst4'] = gsst4

df_g = dfs['string'].set_index('surface_time')
pd.to_pickle(df_g,'df_gTime_of_deployment.pkl') # name the new dataframe only for this deployment
gld_time = xr.Dataset({'start_time': dat.time.series.loc[0], 
                      'end_time':dat.time.series.loc[len(dat.time.series)-1]})
pd.to_pickle(gld_time,'gld_timeTime_of_deployment.pkl') # Save this deployment time as a seperate dataframe for future use

##################
# cleaning check #
##################

# For one profile 

divespike=df.loc[df['dives']==96.5]
divespike=divespike.append(df.loc[df['dives']==97])
plt.figure('cleaning check dive0920-21')
plt.plot(divespike.temperature,divespike.ctd_depth,'k')
#plt.plot(dive0920.temp_clean,dive0920.temperature,'r')
plt.ylim(200,0)

# For the whole deployment 

plt.figure('Cleaning comparison')
plt.plot(df.temp_clean,'r',label='temp_clean')
plt.plot(df.temperature,'k',label='temperature')


####################################
# Some information check, such as: #
# number of dives, Glider depth,   #
# temperature ets. along time      #
####################################

# Depth plot

plt.figure()
plt.ylim([1000,0])
plt.title('Deployment_1 dives')
plt.xlabel('Time')
plt.ylabel('Depth')
plt.plot(df.ctd_time,df.ctd_depth)

dv = df.dives
# bgu.plot(df.ctd_time,df.ctd_depth,df.temp_clean,cmap=cmo.thermal)

custom_bin = np.r_[np.arange(0, 1000, 1)]
temp_gridded = bgu.grid_data(td, y, df.temperature, bins=custom_bin, as_xarray=True)
bgu.plot(temp_gridded.interpolate_na(dim='level_1', limit=1),cmap=cmo.thermal)


##################################################
# Find Bathymetry depth under glider deployments #
##################################################

dfgeo=xr.open_dataset('GEBCO_2014_2D_-10.0_-60.0_80.0_-5.0.nc')
df_g=pd.read_pickle('df_gTime_of_deployment.pkl')

geo = []
for i in range(len(df_g)):
    #print (df_g.index[i])
    ds_col = dfgeo.sel(lon=df_g.surface_lon.values[i],
                lat=df_g.surface_lat.values[i],method='nearest')
    # pad / ffill: propagate last valid index value forward
    # backfill / bfill: propagate next valid index value backward
    geo += ds_col,
geo = xr.concat(geo,dim='time')

    
west = df_g.surface_lon.min()-1
east = df_g.surface_lon.max()+1
south = df_g.surface_lat.min()-1
north = df_g.surface_lat.max()+1
geo=dfgeo.sel(lat=slice(south,north),lon=slice(west,east))
f=interpolate.interp2d(df_g.surface_lon,df_g.surface_lat,df_g.depth,kind='linear')
bamth=f(geo.lon,geo.lat)

plt.figure('Bathymetry and glider depth comparison')
plt.plot(df_g.depth.values*(-1),'k',label='Glider depth')
plt.plot(bamth[:,0],'b',label='Bathymetry depth')

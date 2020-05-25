# -*- coding: utf-8 -*-
# Created on Wed Apr 24 08:40:33 2019 
#
# In this script:
# 1. calculating mean values of MUR, OSTIA and REMSS SSTs, 
# 2. combining 3 satellite products together with Seaglider measurements, sharing
# same time index and coordinates. 
#
# MUR calculated seperately because of MUR use night time 
# Author: Sun-Jing


import matplotlib as mpl
#import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime,timedelta
import seawater as sw


            ##########################
            # Seaglider measurements #
            ##########################

ds=np.load('df_gTimeofdeployment.pkl')
ds.drop
ndays = np.unique(ds.index.dayofyear)
startDay = datetime(ds.index.year[0],1,1)
                  
             ###################################################
             # MUR SST: mean, standard derivation, max and min #
             ###################################################

sst_mur=pd.read_pickle('sst_murTimeofdeployment.pkl')
df1 = pd.DataFrame({'sst1meanM':[],'sst3meanM':[],'stdsst1M':[],'stdsst3M':[],
                   'lon_mean':[],'lon_max':[],'lon_min':[],
                   'lat_mean':[],'lat_max':[],'lat_min':[],
                   'est_cur_mean':[],'est_cur_std':[],
                   'nor_cur_mean':[],'nor_cur_std':[],
                   'mur_sst_mean':[],'mur_sst_std':[],
                   'dist_mean_mur':[],'dist_std_mur':[],'dist_max_mur':[],'dist_min_mur':[]})
for n in ndays:
    startTime = (startDay+timedelta(np.float(n)-1)-timedelta(hours=3)).strftime("%Y-%m-%d %H:00")
    endTime = (startDay+timedelta(np.float(n)-1)+timedelta(hours=21)).strftime("%Y-%m-%d %H:00")
    df1 = df1.append({'sst1meanM': ds[startTime:endTime].sst1.mean(),
                    'sst3meanM':ds[startTime:endTime].sst3.mean(),
                    'stdsst1M': ds[startTime:endTime].sst1.std(),
                    'stdsst3M':ds[startTime:endTime].sst3.std(),
                    'lon_mean':ds[startTime:endTime].surface_lon.mean(),
                    'lon_max':ds[startTime:endTime].surface_lon.max(),
                    'lon_min':ds[startTime:endTime].surface_lon.min(),
                    'lat_mean':ds[startTime:endTime].surface_lat.mean(),
                    'lat_max':ds[startTime:endTime].surface_lat.max(),
                    'lat_min':ds[startTime:endTime].surface_lat.min(),
                    'est_cur_mean':ds[startTime:endTime].surface_curr_east.mean(),
                    'est_cur_std':ds[startTime:endTime].surface_curr_east.std(),
                    'nor_cur_mean':ds[startTime:endTime].surface_curr_north.mean(),
                    'nor_cur_std':ds[startTime:endTime].surface_curr_north.std(),
                    'mur_sst_mean':sst_mur[startTime:endTime].analysed_sst.mean(),
                    'mur_sst_std':sst_mur[startTime:endTime].analysed_sst.std(),
                    'dist_mean_mur':(sw.dist(np.r_[sst_mur[startTime:endTime].lon.mean(), ds[startTime:endTime].surface_lon.values],
                     np.r_[sst_mur[startTime:endTime].lat.mean(),ds[startTime:endTime].surface_lat.values],
                     units='km')[0]).mean(),
                    'dist_std_mur':(sw.dist(np.r_[sst_mur[startTime:endTime].lon.mean(), ds[startTime:endTime].surface_lon.values],
                     np.r_[sst_mur[startTime:endTime].lat.mean(),ds[startTime:endTime].surface_lat.values],
                     units='km')[0]).std(),
                     'dist_max_mur':(sw.dist(np.r_[sst_mur[startTime:endTime].lon.mean(), ds[startTime:endTime].surface_lon.values],
                     np.r_[sst_mur[startTime:endTime].lat.mean(),ds[startTime:endTime].surface_lat.values],
                     units='km')[0]).max(),
                     'dist_min_mur':(sw.dist(np.r_[sst_mur[startTime:endTime].lon.mean(), ds[startTime:endTime].surface_lon.values],
                     np.r_[sst_mur[startTime:endTime].lat.mean(),ds[startTime:endTime].surface_lat.values],
                     units='km')[0]).min()}, 
                     ignore_index=True)

df1.index=np.unique(ds.index.date)

             ################################################################
             # OSTIA and REMSS SSTs: mean, standard derivation, max and min #
             ################################################################


sst_ostia=pd.read_pickle('sst_OstiaTimeofdeployment.pkl')
sst_remss=pd.read_pickle('sst_remssTimeofdeployment.pkl')

df2 = pd.DataFrame({'sst1mean':[],'sst3mean':[],'stdsst1':[],'stdsst3':[],
                   'ostia_sst_mean':[],'ostia_sst_std':[],
                   'dist_mean_ostia':[],'dist_std_ostia':[],'dist_max_ostia':[],'dist_min_ostia':[],
                   'remss_sst_mean':[],'remss_sst_std':[],
                   'dist_mean_remss':[],'dist_std_remss':[],'dist_max_remss':[],'dist_min_remss':[]})
for n in ndays:
    selDay = (startDay+timedelta(np.float(n)-1)).strftime("%Y-%m-%d")
    df2 = df2.append({'sst1mean':ds[selDay].sst1.mean(), 'sst3mean':ds[selDay].sst3.mean(),         
                    'stdsst1':ds[selDay].sst1.std(),'stdsst3':ds[selDay].sst3.std(),                 
                    'ostia_sst_mean':sst_ostia[selDay].analysed_sst.mean(),
                    'ostia_sst_std':sst_ostia[selDay].analysed_sst.std(),
                    'dist_mean_ostia':(sw.dist(np.r_[sst_ostia[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_ostia[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).mean(),
                    'dist_std_ostia':(sw.dist(np.r_[sst_ostia[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_ostia[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).std(),
                     'dist_max_ostia':(sw.dist(np.r_[sst_ostia[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_ostia[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).max(),
                     'dist_min_ostia':(sw.dist(np.r_[sst_ostia[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_ostia[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).min(),
                    'remss_sst_mean':sst_remss[selDay].analysed_sst.mean(),
                    'remss_sst_std':sst_remss[selDay].analysed_sst.std(),
                    'dist_mean_remss':(sw.dist(np.r_[sst_remss[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_remss[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).mean(),
                    'dist_std_remss':(sw.dist(np.r_[sst_remss[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_remss[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).std(),
                     'dist_max_remss':(sw.dist(np.r_[sst_remss[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_remss[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).max(),
                     'dist_min_remss':(sw.dist(np.r_[sst_remss[selDay].lon.mean(), ds[selDay].surface_lon.values],
                     np.r_[sst_remss[selDay].lat.mean(),ds[selDay].surface_lat.values],
                     units='km')[0]).min()},                                
                     ignore_index=True)

df2.index=np.unique(ds.index.date)
df=pd.concat([df1,df2],axis=1)

df.to_pickle('GliderDataFrameTimeofdeployment.pkl')


       #################################################################
       # MUR Time difference versus OSTIA and REMSS check all together #
       #################################################################


# This could also be plotted in different ways, this is just for checking the effect
# of different time colocation. 

s = 15
ss=10
m = 20
b = 30
plt.figure('Time collocating differences')
mpl.rc('axes',titlesize=b)
mpl.rc('legend',fontsize=s)
mpl.rc('xtick',labelsize=s)
mpl.rc('ytick',labelsize=s)
plt.plot(df.sst1meanM,'ro-',label='Glider mean value in time corresponded with MUR SST')
plt.plot(df.sst1mean,'go-',label='Glider mean value in time corresponded with OSTIA and REMSS')
plt.ylabel('Temperature C',fontsize=s)
plt.title('Time window difference comparison',fontsize=m)
plt.legend(loc='lower left',shadow=True)
plt.xticks(rotation=20)
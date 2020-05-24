# -*- coding: utf-8 -*-
# Download MUR data with selected time and coordinates
# correspond to Seaglider deployments: Seaglider datapints and satellite 
# observations colocation
# Author: Sun-Jing (Defination of function part is from Marjolaine Krug)


import xarray as xr
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime


#########################################################
# Load processed Seaglider data, both measurements      #
# dataframe and time dataframe, convert to right format #
#########################################################

df_g=pd.read_pickle('df_gTime_of_deployment.pkl')

# Glider time format conversion can be conducted as needed when colocation, lines below may not
# always be need 

gld_time = pd.read_pickle('gld_timeTime_of_deployment.pkl') 
gld_time=gld_time.to_array() 
gld_time=gld_time.values.astype('datetime64[s]').tolist() # converting to datetime

######################################################################
# Define function for find wished MUR data with time and coordinates #
######################################################################

def getMur(ts,west,east,south,north,fnameOut):
    
    url="https://podaac-opendap.jpl.nasa.gov:443/opendap/allData/ghrsst/data/GDS2/L4/GLOB/JPL/MUR/v4.1/"
     # Example download website
    
    xds = []
    tstamp = []
    
    for i in range(len(ts)):
        print ("Mur file "+str(i)+" of "+str(len(ts)))
        ts_dum = pd.to_datetime(ts[i])
        ts_dum=ts_dum.round('3H')
        yy="%4d" %ts_dum.timetuple()[0]
        mm="%02d" %ts_dum.timetuple()[1]
        dd="%02d" %ts_dum.timetuple()[2]
        doy="%03d" %ts_dum.timetuple()[7]
        print (yy+"/"+doy+"/"+yy+mm+dd)
        tstamp.append(pd.to_datetime(datetime(int(yy),int(mm),int(dd))))
        fnameOut2 = ""+yy+mm+dd+"090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"
        if os.path.exists(fnameOut2)==False:
            fname = url+yy+"/"+doy+"/"+yy+mm+dd+"090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"
            ds_sst = xr.open_dataset(fname)
            ds_sst = ds_sst.sel(lat=slice(south,north),lon=slice(west,east))
            ds_sst.to_netcdf(fnameOut2)
        else:
            ds_sst = xr.open_dataset(fnameOut2)
        xds += ds_sst,
    xds = xr.concat(xds, dim='time')
    xds['time']=pd.to_datetime(tstamp)
    xds.to_netcdf(fnameOut)


# Domain of extraction

west = df_g.surface_lon.min()-1
east = df_g.surface_lon.max()+1
south = df_g.surface_lat.min()-1
north = df_g.surface_lat.max()+1

###############################################################################
# Deciding downloaded data saving directory, time range and interval of data, #
# finaly download data by using the defined function                          #
###############################################################################

pnameOut = "Diractory/Mur"
ts=pd.date_range(start='start_time',end='end_fime',freq='D')
getMur(ts,west,east,south,north,pnameOut)


#############################################################################
# Now MUR files have downloaded at the pre-decided directory, read and load #
# all datasets as an xarray dataset                                         #
#############################################################################

MFdatadir = 'MUR_datasets_standart_names*.nc'
mfdata = xr.open_mfdataset(MFdatadir)

##############################################################################
# From the Seaglider deployment dataframe time index, find the corresponding #
# time data points of MUR datasets                                           #
##############################################################################

xds = []
for i in range(len(df_g)):
    #print (df_g.index[i])
    ds_col = mfdata.sel(time=str(df_g.index[i]), lon=df_g.surface_lon.values[i],
                lat=df_g.surface_lat.values[i], method='nearest')
    xds += ds_col,

xds = xr.concat(xds, dim='time')
sst_mur_Timeofdeploymnet = xds.analysed_sst -273.15 # Temperature were in Kelvin
sst_mur_Timeofdeploymnet = xr.DataArray.to_dataframe(sst_mur_Timeofdeploymnet)
pd.to_pickle(sst_mur_Timeofdeploymnet,'sst_mur_Timeofdeploymnet')



####################################################
# Check the Seaglider-Satellite colocation results #
####################################################
 
route= plt.figure()
plt.title('Satellite SST nearest points route compare glider Timeofdeploymnet')
plt.xlabel('Longitude')
plt.ylabel('Latitude') 
sat = plt.plot(sst_mur_Timeofdeploymnet.lon,sst_mur_Timeofdeploymnet.lat,'r',label='Satellite')
gli = plt.plot(df_g.surface_lon,df_g.surface_lat,'y',label='Glider')
plt.legend(loc='upper left', shadow=True, fontsize='x-large')
plt.savefig('Nearest points comparison Timeofdeploymnet')


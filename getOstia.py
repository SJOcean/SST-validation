# -*- coding: utf-8 -*-
# Download OSTIA data with selected time and coordinates
# correspond to Seaglider deployments: Seaglider datapints and satellite 
# observations colocation
# Author: Sun-Jing (Defination of function part is from Marjolaine Krug)

import xarray as xr
import pandas as pd
import os

#########################################################
# Load processed Seaglider data, both measurements      #
# dataframe and time dataframe, convert to right format #
#########################################################

df_g=pd.read_pickle('df_gTimeofdeployment.pkl')

# Glider time format conversion can be conducted as needed when colocation, lines below may not
# always be need 

gld_time = pd.read_pickle('gld_timeTimeofdeployment.pkl') 
gld_time=gld_time.to_array() 
gld_time=gld_time.values.astype('datetime64[s]').tolist() # converting to datetime



######################################################################
# Define function for find wished OSTIA data with time and coordinates #
######################################################################

def getOstia(ts,west,east,south,north,fnameOut):
    
    from datetime import datetime
    url="https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/L4/GLOB/UKMO/OSTIA/"
    # Example download website
    
    xds = []
    tstamp = []
    for i in range(len(ts)):
        print ("Ostia file "+str(i)+" of "+str(len(ts)))
        ts_dum = pd.to_datetime(ts[i])
        ts_dum=ts_dum.round('3H')
        yy="%4d" %ts_dum.timetuple()[0]
        mm="%02d" %ts_dum.timetuple()[1]
        dd="%02d" %ts_dum.timetuple()[2]
        doy="%03d" %ts_dum.timetuple()[7]
        print (yy+"/"+doy+"/"+yy+mm+dd)
        tstamp.append(pd.to_datetime(datetime(int(yy),int(mm),int(dd))))
        fnameOut2 = ""+yy+mm+dd+"-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc.bz2"                
        if os.path.exists(fnameOut2)==False:
            fname = url+yy+"/"+doy+"/"+yy+mm+dd+"-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc.bz2"
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

pnameOut = "Diractory/OSTIA"
ts=pd.date_range(start='start_time',end='end_fime',freq='D')
getOstia(ts,west,east,south,north,pnameOut)


###############################################################################
# Now OSTIA files have downloaded at the pre-decided directory, read and load #
# all datasets as an xarray dataset                                           #
###############################################################################

MFdatadir = 'OSTIA_datasets_standart_names*.nc.bz2'
mfdata = xr.open_mfdataset(MFdatadir)
mfdata = xr.open_mfdataset(MFdatadir)

# OSTIA dataset time is not in datetime format, it is needed to be converted 
mfdata.time.values=[pd.to_datetime(str(i)) for i in mfdata.time.values]

##############################################################################
# From the Seaglider deployment dataframe time index, find the corresponding #
# time data points of OSTIA datasets                                           #
##############################################################################

xds = []
for i in range(len(df_g)): #df_g:glider data
    #print (df.index[i])
    ds_col = mfdata.sel(time=str(df_g.index[i]), lon=df_g.surface_lon.values[i],
                lat=df_g.surface_lat.values[i], method='nearest')
    xds += ds_col,


xds = xr.concat(xds, dim='time')
sst_Ostia = xds.analysed_sst -273.15
sst_Ostia = xr.DataArray.to_dataframe(sst_Ostia)
pd.to_pickle(sst_Ostia,'sst_OstiaTimeofdeployment.pkl')


########################################
# Get values of analysis errors fields #
########################################

error_ostiaTimeofdeployment = xds.analysis_error 
error_ostiaTimeofdeployment = xr.DataArray.to_dataframe(error_ostiaTimeofdeployment)
error_ostiaTimeofdeployment = error_ostiaTimeofdeployment.dropna()
pd.to_pickle(error_ostiaTimeofdeployment,'error_ostiaTimeofdeployment')


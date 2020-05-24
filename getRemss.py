# -*- coding: utf-8 -*-
# Download REMSS data with selected time and coordinates
# correspond to Seaglider deployments: Seaglider datapints and satellite 
# observations colocation
# Author: Sun-Jing (Defination of function part is from Marjolaine Krug)


import ftplib as fb
import sys
import xarray as xr
import pandas as pd
from datetime import datetime

#############################################################################
# It is different when finding and downloading REMSS datasets.              #
# First, ask for a username and keyword via mail, then download as follows: #
#############################################################################

ftp = fb.FTP("ftp.remss.com")
ftp.login("received user name", "received keyword")
data = []
ftp.cwd('/sst/daily/mw_ir/v05.0//netcdf/2012/')  # Example website
ftp.dir(data.append)

########################################################################
# Define function for find wished REMSS data with time and coordinates #
########################################################################

def getRemss(ftp,ts,fname):  
    for i in range(len(ts)):
        ts_dum = pd.to_datetime(ts[i])
        ts_dum=ts_dum.round('3H')
        print ("Remss file "+str(i)+" of "+str(len(ts)))
        yy="%4d" %ts_dum.timetuple()[0]
        mm="%02d" %ts_dum.timetuple()[1]
        dd="%02d" %ts_dum.timetuple()[2]
        try:
            fname = yy+mm+dd+"120000-REMSS-L4_GHRSST-SSTfnd-MW_IR_OI-GLOB-v02.0-fv05.0.nc"
            ftp.retrbinary("RETR " + fname ,open(fname, 'wb').write)
        except:
            print ("Error")
            
ts=pd.date_range(start='start time',end='endtime',freq='D')

pname='defined_standard_remss_file_name.nc'
getRemss(ftp,ts,pname)

# getRemss(ftp,ts,'20120617120000-REMSS-L4_GHRSST-SSTfnd-MW_IR_OI-GLOB-v02.0-fv05.0.nc')
# This is what has been worked and looks making no sense with the file name. Try line above first

ftp.quit()


####################################################
# Load processed Seaglider data, both measurements #
####################################################

df_g=pd.read_pickle('df_gTimeofdeployment.pkl')


###############################################################################
# Now REMSS files have downloaded at the pre-decided directory, read and load #
# all datasets as an xarray dataset                                           #
###############################################################################

MFdatadir = 'Standard_REMSS_file_name*.nc'
mfdata = xr.open_mfdataset(MFdatadir)

# Domain of extraction
west = df_g.surface_lon.min()-1
east = df_g.surface_lon.max()+1
south = df_g.surface_lat.min()-1
north = df_g.surface_lat.max()+1

mfdata  = mfdata.sel(lat=slice(south,north),lon=slice(west,east))

##############################################################################
# From the Seaglider deployment dataframe time index, find the corresponding #
# time data points of REMSS datasets                                         #
##############################################################################

xds = []
for i in range(len(df_g)):
    #print (df_g.index[i])
    ds_col = mfdata.sel(time=str(df_g.index[i]), lon=df_g.surface_lon.values[i],
                lat=df_g.surface_lat.values[i], method='nearest')
    xds += ds_col,

xds = xr.concat(xds, dim='time')
sst_remss = xds.analysed_sst -273.15 # REMSS SST also in Kelvin 
sst_remss = xr.DataArray.to_dataframe(sst_remss)
pd.to_pickle(sst_remss,'sst_remssTimeofdeployment.pkl')


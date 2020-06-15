# -*- coding: utf-8 -*-

##################################################################
## Created on Thu Jul 18 17:08:00 2019                          ##  
## Author: Sun Jing, based on Marjolaine Krug's map plot script ## 
##################################################################

import matplotlib.pyplot as plt
import numpy as np
import cartopy as cp
from cartopy.io import shapereader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import xarray as xr
import pandas as pd
import matplotlib as mpl



#########################
## Load Seaglider data ##
#########################

G15_543=pd.read_pickle('df_g2015_sg543.pkl')
G15_573=pd.read_pickle('df_g2015_sg573.pkl')
G17=pd.read_pickle('df_g2017.pkl')
G1809=pd.read_pickle('df_g201809.pkl')
G1810=pd.read_pickle('df_g201810.pkl')
G19_573=pd.read_pickle('df_g2019_sg573.pkl')
G19_574=pd.read_pickle('df_g2019_sg574.pkl')



#####################################################
## Define region for/and selecting from GEBCO data ##
## and define a function of reading in coastline   ##
#####################################################

west =  23; east = 35; north = -27; south = -36 
dfgeo=xr.open_dataset('GEBCO_2014_2D_-10.0_-60.0_80.0_-5.0.nc')
geo=dfgeo.sel(lat=slice(south,north),lon=slice(west,east))


def makeMap(west,east,north,south):
    shp = shapereader.Reader('Arbitary directory/southAfrica_land.shp')
    ax = plt.axes((0.1, 0.135, 0.8, 0.8),projection=cp.crs.PlateCarree())
    ax.set_extent([west,east,south,north], crs=cp.crs.PlateCarree())
    beige = [0.9375, 0.9375, 0.859375]
    for record, geometry in zip(shp.records(), shp.geometries()):
       ax.add_geometries([geometry], cp.crs.PlateCarree(), facecolor=beige,
	                      edgecolor='black')
    ax.set_xticks(np.arange(west,east,1.0), crs=cp.crs.PlateCarree())
    ax.set_yticks(np.arange(south,north,1.0), crs=cp.crs.PlateCarree())
    gl = ax.gridlines(crs=cp.crs.PlateCarree(), draw_labels=False,
	                  linewidth=0.12, color='k',alpha=0.5, linestyle='-')
    gl.xlabels_top = False
    gl.ylabels_right = False
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    return ax



##########################################################################
## Map plotting: plotting coastline marked with citiies with predefined ##
## function,and contours of GEBCO bathymetry on the map                 ##
##########################################################################
    
    
lon_formatter =LongitudeFormatter(number_format='.1f', degree_symbol='$^o$',
                                       dateline_direction_label=True)
lat_formatter = LatitudeFormatter(number_format='.1f', degree_symbol='$^o$')

cities={}
cities['name']=['Richards Bay','Durban','East London','Port Elizabeth']
cities['longitude'] = [32.0383, 31.0218, 27.8546, 25.6022, 18.4241]
cities['latitude'] =  [-28.7807,-29.8587,-33.0292,-33.9608,-33.9249]

plt.rcParams['contour.negative_linestyle'] = 'solid'
s = 15; ss=10; m = 20; b = 30
fig = plt.figure(figsize =(8., 8.),facecolor='white',edgecolor='black')
ax = makeMap(west,east,north,south)
ax.plot(cities['longitude'],cities['latitude'],'kd',markersize=6)
ax.xaxis.set_tick_params(labelsize=m)
ax.yaxis.set_tick_params(labelsize=m)

for k in range(len(cities['name'])):
	plt.text(cities['longitude'][k]+0.25,cities['latitude'][k]+0.15,cities['name'][k],ha='right',fontsize=12)



cs =plt.contourf(geo.lon.values, geo.lat.values,geo.elevation.values, levels=[-3000,-1000,-400,-100,0],
    colors=['#949494', '#c0c0c0', '#CeCeCe','#f6f6f6'], extend='both') 
cs.cmap.set_under('#808080')
cs.changed()
cbar = plt.colorbar(cs, orientation='horizontal',fraction=0.03)
cbar.set_label('Depth [m]',fontsize=m)


mpl.rc('axes',titlesize=m)
mpl.rc('legend',fontsize=s)
mpl.rc('xtick',labelsize=m)
mpl.rc('ytick',labelsize=m)
ax.plot(G15_543.surface_lon,G15_543.surface_lat,'rv',label='2015 sg_543',markersize=3.5)
ax.plot(G15_573.surface_lon,G15_573.surface_lat,'r+',label='2015 sg_573',markersize=3.5)
ax.plot(G17.surface_lon,G17.surface_lat,'mx',label='2017',markersize=3.5)
ax.plot(G1809.surface_lon,G1809.surface_lat,'yv',label='2018-09',markersize=3.5)
ax.plot(G1810.surface_lon,G1810.surface_lat,'y.',label='2018-10',markersize=3.5)
ax.plot(G19_573.surface_lon,G19_573.surface_lat,'bv',label='2019 sg_573',markersize=3)
ax.plot(G19_574.surface_lon,G19_574.surface_lat,'b.',label='2019 sg_574',markersize=4)
ax.set_title('Deployment [2015-2019]')
ax.legend(loc='upper left')



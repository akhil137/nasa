import os
import glob
from traffic_bias import generate_average_hourly_traffic
from traffic_bias import traffic_bias_weights
from filtering import clean_frame
from filtering import weighted_average
from filtering import data_matrix
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
from itertools import chain

import numpy as np
import pandas as pd
from datetime import datetime



#1. define the data path and airport
datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'
airport_abbrv = 'JFK'

#get all the airports which are sub-dirs to datadir
#airports=[ap for ap in os.listdir(datadir) \
#if os.path.isdir(os.path.join(datadir,ap))]

airport = 'K' + airport_abbrv

years=[yr for yr in os.listdir(os.path.join(datadir,airport)) \
	if os.path.isdir(os.path.join(datadir,airport,yr))]



# Only ever done once
# #move files that have less than 24 obs
# dest='/Users/ashah/NoBackup/code/nasa/data/METAR/LessThan24Obs/'
# #do recursive for every year, but only once
# year='2013'
# filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
# l=[a for a in filelist if len(clean_frame(a))<24]
# [shutil.move(a,dest) for a in l]
# #now move files that have less than 24 obs once we remove duplicate obs in the same hour
#  for year in years:
# 	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
# 	l=[a for a in filelist if data_matrix(clean_frame(a))['TemperatureF'].shape[1] != 24]
# 	[shutil.move(a,dest) for a in l]





#create a dictionary of feature matrices for every year
dmlist = list()
dfall = pd.DataFrame() #data frame of all data
for year in years:
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	for filepath in filelist:
		dmlist.append(data_matrix(clean_frame(filepath)))
		dfall=dfall.append(clean_frame(filepath))
	#dmlist.append([data_matrix(clean_frame(filepath)) for filepath in filelist])
#flatten list
#dmlist = list(chain(*dmlist))
dfall['year']=[pd.to_datetime(a).year for a in dfall['date']]
dmdict=dict()
pcadict=dict()


for i, key in enumerate(dmlist[0].keys()):
		dmdict[key]=[a[key] for a in dmlist if a[key].shape[1]==24]
		dmdict[key]=np.vstack(dmdict[key])
		pca=PCA(n_components=3)
		pcadict[key]=pca.fit_transform(scale(dmdict[key]))



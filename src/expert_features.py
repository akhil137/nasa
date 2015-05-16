#extract 'expert' features according to: 
#-Chop up day into 3 hours blocks (ref: avijit for 3)
#-Take 3hour min/max of visibility, wind-speed and arrivals at {EWR, JFK, LGA}
#-cluster at each airport individually (total 24 features)
#-cluster using features from all airports (total 24x3 features): regional clusters

import os
import glob
from traffic_bias import generate_hourly_traffic
from traffic_bias import traffic_bias_weights
from filtering import clean_frame
from filtering import weighted_average
from filtering import data_matrix
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import scale
import numpy as np
import pandas as pd
from datetime import datetime


#input data source = METAR + ASPM.

#1. loop thru airports {JFK, LGA, EWR}
#2. loop thru years 2010-2013
#3. for a given airport and day (single METAR file)
#--produce a clean data frame
#from plot.py


def extract_expert_features(airport_abbrv,block_size=3):

	#get all the airports which are sub-dirs to datadir
	#airports=[ap for ap in os.listdir(datadir) \
	#if os.path.isdir(os.path.join(datadir,ap))]

	airport = 'K' + airport_abbrv

	years=[yr for yr in os.listdir(os.path.join(datadir,airport)) \
		if os.path.isdir(os.path.join(datadir,airport,yr))]
	dfall = pd.DataFrame() #data frame of all data
	dmlist = list()
	for year in years:
		filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
		for filepath in filelist:
			dfall=dfall.append(clean_frame(filepath))
			dmlist.append(data_matrix(clean_frame(filepath)))

	##############################################################
	############ EXTRACT FEATURES ############
	##############################################################
	#build some 3hour-block features
	#block_size = 3
	#but only do it if we have 24 obs that day (otherwise don't include that day)
	#note block_size divides 24 evenly

	#get list of dates when we have a full set of 24 obs/day
	fullDay=[a for a in dmlist if (a['Wind_SpeedMPH'].shape[1]==24 and \
		a['VisibilityMPH'].shape[1]==24)]

	#From METAR this are '%Y-%m-%d' format
	fullDayDates=pd.to_datetime([a['date'] for a in fullDay])
	#Convert to '%d/%m/%y' to key traffic Data frame (date format for ASPM)
	METARdates=[d.strftime('%m/%d/%Y') for d in fullDayDates]

	wind_speed_list_max=[np.max(a['Wind_SpeedMPH'].reshape(-1,block_size),1) for a in fullDay]
				
	#now stack rows: columns are 3 hour (or generally block_size) blocks
	wind_speed_max=np.vstack(wind_speed_list_max)
	#do same for visibility
	vis_list_min=[np.min(a['VisibilityMPH'].reshape(-1,block_size),1) for a in fullDay]
				

	vis_min = np.vstack(vis_list_min)



	#get traffic - note this takes all CSV files from 2010-2013
	#and generates a two-level (day, hour) dataframe with Departures and Arrivals
	trafDF=generate_hourly_traffic(airport_code = airport_abbrv)
	#Now only select dates that were used for METAR data
	trafDF=trafDF.ix[METARdates]
	#now create an numpy array to reshape and block max like above features
	#.unstack() gives Hour as columns, Dates as rows
	#.A selects arrivals
	#.as_matrix() now gives a [#dates,#hours] matrix
	#.reshape now reshapes it to [#dates,8,3] and we max on the last axis 'axis=2'
	#TODO: unstack gives NaN, figure out why
	#beacuase the ASPM data has some missing values
	#find these missing hours via: 
	#tmp=trafDF.A.unstack().as_matrix()
	#np.where(np.isnan(tmp)); for example we'll get 44,3 and
	#use max that ingores nan
	#Yikes: nanmax won't fix cases like LGA which have
	#so much missing data that a three hour-block may look like [nan,nan,nan]
	#arrivals_max=np.nanmax(trafDF.A.unstack().as_matrix().reshape(-1,8,3),axis=2)
	#Thus we zero-out any occurence of nan
	arrivals_max=np.max(np.nan_to_num(trafDF.A.unstack().as_matrix().reshape(-1,8,3)),axis=2)
	#now make a data matrix
	datMat=np.concatenate((vis_min,wind_speed_max,arrivals_max),axis=1)
	#and the date matrix
	dayMat=np.asarray(METARdates).reshape(-1,1)

	airport_features={'dates':dayMat,'data':datMat}

	return airport_features


#feature names: 'timeBlock_4_MinVisibility', etc
#chop up 24 hours obs into blcok sizes
block_size=3
featureNames = ['Min_Visibility','Max_Wind_Speed', 'Max_Arrivals']
features=list()
for a in featureNames:
	for i in range(24/block_size):
		features.append('timeBlock_'+str(i+1)+'_'+a)


#now cluster
datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'

for airport_code in ['JFK','LGA','EWR']:
	afeat = extract_expert_features(airport_code,block_size)
	dayMat = afeat['dates']
	datMat = afeat['data']

	number_of_clusters=[5,10,20]
	for numclusters in number_of_clusters:
		kmeans = KMeans(init='k-means++', n_clusters=numclusters, n_init=10)
		#scale 
		labels=kmeans.fit_predict(scale(datMat))
		#The webapp preferes cluster labels to start at 1
		labels=labels.reshape(labels.shape[0],1)+1
		#concatenate
		kmeans_output = np.hstack((dayMat,labels,datMat))
		#write to file
		outfile = airport_code+'expert_kmeans'+'_'+str(numclusters)+'.csv'
		head = 'date,cluster,' + ','.join(features)
		np.savetxt(outfile,kmeans_output,fmt='%s', delimiter=',', header=head)


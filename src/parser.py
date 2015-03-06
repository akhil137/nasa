import os
import glob
import numpy as np
import pandas as pd


import os
import glob

datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'

#get all the airports which are sub-dirs to datadir
airports=[ap for ap in os.listdir(datadir) \
if os.path.isdir(os.path.join(datadir,ap))]

airport = 'KJFK'

years=[yr for yr in os.listdir(os.path.join(datadir,airport)) \
	if os.path.isdir(os.path.join(datadir,airport,yr))]



def day_summarization(filename,weights):
	"""Take a csv file of METAR data for a day at single site
	and parse appropriate columns and perform summarization

	Keyword arguments: 
	filename -- string: name of csv file 
	
	return a single row (summarization) pandas dataframe 
	"""

	df = pd.read_csv(filename)
	#get date from first entry (row) of DateUTC column
	date = df['DateUTC<br />'][0].split(' ')[0]
	
	#drop the following columns
	timeLabel = df.columns.values[0] #fluctuates from 'TimeEST' to 'TimeEDT'
	"""
	dropLabels = ['FullMetar','DateUTC<br />', timeLabel, \
	'Wind Direction','Gust SpeedMPH','Events','Conditions', \
	'WindDirDegrees', 'Sea Level PressureIn', 'Dew PointF']
	"""
	dropLabels = ['FullMetar', 'DateUTC<br />', \
	'Wind Direction','Gust SpeedMPH','Events','Conditions', \
	'WindDirDegrees', 'Sea Level PressureIn', 'Dew PointF']

	df.drop(labels=dropLabels,axis=1,inplace=True)
	
	#convert non-numeric entries like 'Calm' in Windspeed to NaN
	#then replace all NaN with 0 (including Precipitation)
	df = df.convert_objects(convert_numeric=True)
	df.fillna(0, inplace=True)
	
	#TODO: weighted average of data
	#weights determined by time period of interest 
	#e.g. if interested for 1000, weight +/- 2hr these unity
	#less weight for other times before after
	if not weights.any():
		weights=np.ones(24)

	#METAR can have more than 24 obs (multiple obs per hour)
	#Sow we'll create another column called Hour to weight it
	#properly with traffic biasing
	#The hour entry in the Hour column will allow us to assign
	#the same weight for multiple obs in the same hour
	df['Hour']=[a.hour for a in pd.to_datetime(df[timeLabel])]
	df['weights']=[weights[a] for a in df['Hour']]


	#now return the weighted average
	wdf=pd.DataFrame()
	#need to drop time string column before arithmetic
	df.drop(labels=timeLabel,axis=1,inplace=True)

	for a in df.columns.values:
		wdf[a] = [df[a].dot(df.weights).sum()/df.weights.sum()]

	wdf.drop(labels=['Hour','weights'],axis=1,inplace=True)
	#return weighted average
	return wdf

#create the data matrix
data = list()
day = list()
for year in years:
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	data.append([day_summarization(filepath).as_matrix() for filepath \
	in filelist])
	#store filenames (e.g. dates)
	day.append([filepath.split('/')[-1] for filepath in filelist])
	

datMat = np.vstack(data)
dayMat = np.hstack(day)

#To later concatenate, requires 1d array to be 2d
#e.g. must have dayMat.shape = [nsamples,1]
dayMat=dayMat.reshape(dayMat.shape[0],1)

#Now cluster scaled data
#kmeans algo
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

numclusters=10
kmeans = KMeans(init='k-means++', n_clusters=numclusters, n_init=10)
#scale 
labels=kmeans.fit_predict(scale(datMat))
labels=labels.reshape(labels.shape[0],1)

#concatenate
kmeans_output = np.hstack((dayMat,labels,datMat))
#write to file
np.savetxt('kmeans_JFK.csv',kmeans_output,fmt='%s', delimiter=',')

	
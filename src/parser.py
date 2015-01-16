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



def day_summarization(filename=None):
	"""Take a csv file of METAR data for a day at single site
	and parse appropriate columns and perform summarization

	Keyword arguments: 
	filename -- string: name of csv file 
	
	return pandas dataframe 
	"""

	df = pd.read_csv(filename)
	#get date from first entry (row) of DateUTC column
	date = df['DateUTC<br />'][0].split(' ')[0]
	
	#drop the following columns
	timeLabel = df.columns.values[0] #fluctuates from 'TimeEST' to 'TimeEDT'
	dropLabels = ['FullMetar','DateUTC<br />', timeLabel, \
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

	#for now pick noon time
	return df.iloc[11,:]

#create the data matrix
data=list()
day = list()
for year in years:
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	data.append([day_summarization(filepath).as_matrix() for filepath \
	in filelist])
	#store filenames (e.g. dates)
	day.append([filepath.split('/')[-1] for filepath in filelist])
	

datMat = np.vstack(data)
dayMat = np.hstack(day)
#for later concatenation
dayMat=dayMat.reshape(dayMat.shape[0],1)
#cluster
#kmeans
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale

numclusters=10
kmeans = KMeans(init='k-means++', n_clusters=numclusters, n_init=10)
labels=kmeans.fit_predict(scale(datMat))
labels=labels.reshape(labels.shape[0],1)

kmeans_output = np.hstack((dayMat,labels,datMat))
np.savetxt('kmeans_JFK.csv',kmeans_output,fmt='%s', delimiter=',')

	
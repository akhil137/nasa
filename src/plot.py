import matplotlib.pyplot as plt
#"ref: http://matplotlib.org/examples/style_sheets/plot_bmh.html"
#doesn't work with our version of matplotlib
# plt.style.use('bmh')
# def plot_hist_data_matrix(dm):
	


#box-plot of daily variation of a feature
#@param dm: data_matrix from filtering.py
#@param scale: boolean, if True, then scale input using standard scalar
#x-axis: records, e.g. day 1, day 2, etc.
#y-axis: box-plot value
#title: name of feature, years
#only the first 35 days (the full range is 365*4 days)
plt.figure()
plt.boxplot(dmdict['TemperatureF'])
plt.title('TemperatureF variation')
#plt.xlabel('day')
#plt.xticks(np.arange(start=1,stop=35,step=7))
plt.show()
#scatter plot of feature vs feature


#boxplot - hourly variation
#x-axis - hour of day
plt.figure()
plt.boxplot(dmdict['TemperatureF'])
plt.title('JFK: Hourly temperature variation between 2010-2013')
plt.xlabel('Hour')
plt.ylabel('Temperature[F]')
#plt.xticks(np.arange(start=1,stop=35,step=7))
plt.show()


#boxplot - yearly variation
#x-axis - hour of day
plt.figure()
plt.boxplot(dmdict['TemperatureF'].T)
plt.title('JFK: Daily temperature variation between 2010-2013')
plt.xlabel('day')
plt.ylabel('Temperature[F]')
step_size=np.round(dmdict['TemperatureF'].shape[0]/10)
stop=dmdict['TemperatureF'].shape[0]
plt.xticks(np.arange(start=1,step=step_size,stop=stop))
plt.show()


def plot_year_variation(key):
	plt.figure()
	plt.boxplot(dmdict[key].T)
	plt.title('JFK: Daily '+key+' variation between 2010-2013')
	plt.xlabel('day')
	plt.ylabel(key)
	step_size=np.round(dmdict[key].shape[0]/10)
	stop=dmdict[key].shape[0]
	plt.xticks(np.arange(start=1,step=step_size,stop=stop))
	plt.show()

#cleanest way to do it
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
import matplotlib.pyplot as plt

#1. define the data path and airport
datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'
airport_abbrv = 'JFK'

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


dfall['year']=[pd.to_datetime(a).year for a in dfall['date']]

features=['Humidity', 'PrecipitationIn', 'TemperatureF','VisibilityMPH', 'Wind_SpeedMPH']

#yearly variation of all features above
axdict=dict()
#plt.figure(1)
for i,f in enumerate(features):
	ax=plt.subplot(2,3,i)
	ax.set_ylabel(f)
	#ax.set_xlabel('year')
	axdict[f]=dfall.boxplot(column=f,by='year',ax=ax)#,layout=(3,2))
plt.show()

#scatter plots of feature combinations taken two at a time
import itertools

plt.figure(2)
for i,f in enumerate(itertools.combinations(features,2)):
	plt.figure(2)
	ax=plt.subplot(3,4,i)
	dfall.plot(kind='scatter',x=f[0],y=f[1],ax=ax)
	print f[0] + f[1]
plt.show()

#hourly variation of all features above
plt.figure(3)
for i,f in enumerate(features):
	plt.figure(3)
	ax=plt.subplot(2,3,i)
	dfall.boxplot(column=f,by='Hour',ax=ax)
plt.show()


#plot pca
dmdict=dict()
pcadict=dict()

for i, key in enumerate(dmlist[0].keys()):
		#only include days which have exactly 24 obs 
		#two days had 23 since dropping visibility > 10
		dmdict[key]=[a[key] for a in dmlist if a[key].shape[1]==24]
		dmdict[key]=np.vstack(dmdict[key])
		pca=PCA(n_components=3)
		pcadict[key]=pca.fit_transform(scale(dmdict[key]))

for i, key in enumerate(pcadict.keys()):
		plt.figure(4)
		ax=plt.subplot(2,3,i)
		ax.set_title(key+' PCA component variation 2010-2013')
		ax.boxplot(pcadict[key])
plt.show()

#get categorical data
def get_events(filename):
	"""Take a csv file of METAR data for a day at single site
	and parse appropriate columns
	Keyword arguments: 
	@filename -- string: name of csv file
	@returns -- pandas data frame

	"""
	df = pd.read_csv(filename)
	#get date from first entry (row) of DateUTC column
	df['date'] = df['DateUTC<br />'][0].split(' ')[0]
	
	
	#drop the following columns
	dropLabels = ['FullMetar', 'DateUTC<br />', \
	'Wind Direction','Gust SpeedMPH', \
	'WindDirDegrees', 'Sea Level PressureIn', 'Dew PointF', \
	'TemperatureF',  'Humidity','VisibilityMPH', \
    'Wind SpeedMPH', 'PrecipitationIn']

	df.drop(labels=dropLabels,axis=1,inplace=True)
	
	#add hour column
	timeLabel = df.columns.values[0] 
	df['Hour'] = pd.to_datetime(df[timeLabel]).dt.hour
	#drop timelabel column since we don't use anything beyond hour
	df.drop(labels=timeLabel,axis=1,inplace=True)

	return df

dfcat=pd.DataFrame()
for year in years:
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	for filepath in filelist:
		dfcat=dfcat.append(get_events(filepath))

#list of unique events/condition categories
pd.unique(dfcat.Conditions)
pd.unique(dfcat.Events)
#summary stats of non-na events
dfcat.Events.describe() #

#get dates belogining to an event category
group=dfcat.groupby('Events')
pd.unique(group.get_group('Snow').date)
#dict where keys are events
eventDateDict=dict()
for key in pd.unique(dfcat.Events).tolist():
		if not pd.isnull(key):
			eventDateDict[key]=pd.unique(group.get_group(key).date)

#now create a dictionary where the keys are dates (close to a calendar view)
groupDate=dfcat.groupby('date')
dateEventDict=dict()
for key in pd.unique(dfcat.date).tolist():
		if not pd.isnull(key):
			dateEventDict[key]=pd.unique(groupDate.get_group(key).Events.dropna()).tolist()

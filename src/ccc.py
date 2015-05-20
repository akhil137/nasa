"""
Generate a concurrency table of METAR Conditions given date-cluster assignment
writen by: Akhil Shah (RAND)
date-modified: May 19, 2015
"""
import os
import glob


import numpy as np
import pandas as pd

#Input: 
#@cluters: csv file - first column is 'date' column and second is 'cluster' column
#@airport_abbrv: list - e.g. ['JFK','EWR']; enable us to fetch the METAR file using this and date from above
#Procedure:
#1. extract years and dates from @clusters
#2. create filelist of METAR files to read using above and @airport_abbrv
#3.


def get_day_clusters(filename):
	"""Take a csv file of cluster results
	and generate date-cluster dictionary
	Keyword arguments: 
	@filename -- string: name of cluster results csv file
	@returns -- dictionary with keys=dates, value = cluster label
	"""
	df = pd.read_csv(filename,index_col=0) #set date column to row index
	return df.iloc[:,0].to_dict() #set dict values to the first column of df (second col of csv)


def list_METAR_files_of_cluster(day_cluster_dict,datadir,airport_abbrv):
	"""
	Keyword arguments: 
	@day_cluster_dict -dict: output of get_day_clusters
	@datadir - string: path to METAR files
	@airport_abbrv - string: e.g. 'JFK'
	@returns - list: absolute file location on your disk
	"""
	dates=pd.to_datetime(day_cluster_dict.keys())
	METARdates=[d.strftime('%Y_%m_%d') for d in dates]
	filelist=[os.path.join(datadir,'K'+airport_abbrv,\
		d.split('_')[0],d+'.txt') for d in METARdates]
	return filelist








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
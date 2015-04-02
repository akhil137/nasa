"""
Collections of functions to:
0. clean METAR data
1. transform to a numerical matrix (for machine learning)
2. reduce multiple obs to a single ob for a given day
"""
import pandas as pd
import numpy as np
import pdb

def clean_frame(filename):
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
	'Wind Direction','Gust SpeedMPH','Events','Conditions', \
	'WindDirDegrees', 'Sea Level PressureIn', 'Dew PointF']

	df.drop(labels=dropLabels,axis=1,inplace=True)
	
	#convert non-numeric entries like 'Calm' in Windspeed to NaN
	#then replace all NaN with 0 (including Precipitation)
	df = df.convert_objects(convert_numeric=True)
	df.fillna(0, inplace=True)

	#remove spaces in column names and replace with '_'
	cols = df.columns
	cols = cols.map(lambda x: x.replace(' ', '_') if \
		isinstance(x, (str, unicode)) else x)
	df.columns = cols

	#now remove rows that have negative values in any column
	##TODO: investigate package 'numexpr' and pass to engine param below
	df=df.query(' >= 0 & '.join(df.columns.tolist()[1:]) + '>= 0', engine='python')

	#also remove rows where visibility is greater than 10 (these are errors?)
	df=df.query('VisibilityMPH <= 10')

	#add hour column
	timeLabel = df.columns.values[0] 
	df['Hour'] = pd.to_datetime(df[timeLabel]).dt.hour
	#drop timelabel column since we don't use anything beyond hour
	df.drop(labels=timeLabel,axis=1,inplace=True)

	return df

def data_matrix(dataframe):
	"""
	returns a dictionary of row vectors; feature data
	so you can stack these rows for each day
	"""
	df=dataframe.copy()
	
	#get the hour
	#df['Hour']=[a.hour for a in pd.to_datetime(df[timeLabel])]
	#drop multiple obs in the same Hour
	df.drop_duplicates(subset='Hour',inplace=True)
	#drop time labels and Hour label
	df.drop(labels=['date','Hour'],axis=1,inplace=True)
	dm = dict()
	#convert numerical values to float for scaling and pca
	for i, key in enumerate(df.columns):
		dm[key]=df.iloc[:,i].values.astype('float').flatten()
		dm[key]=dm[key].reshape(1,dm[key].shape[0])
	return dm



def weighted_average(dataframe,weights):
	"""Take a METAR data frame and perform summarization
	with weighted average. Uniform weights can be set as:
	#weights=np.ones(24)

	Keyword arguments: 
	@dataframe -- pandas data frame (ideally output of clean_frame)
	@weights -- numpy array of weights
	@returns a single row (summarization) pandas dataframe 
	"""
	df = dataframe.copy()

	#timeLabel = df.columns.values[0] #fluctuates from 'TimeEST' to 'TimeEDT'

	#METAR can have more than 24 obs (multiple obs per hour)
	#Sow we'll create another column called Hour to weight it
	#properly with traffic biasing
	#The hour entry in the Hour column will allow us to assign
	#the same weight for multiple obs in the same hour
	#df['Hour']=[a.hour for a in pd.to_datetime(df[timeLabel])]
	df['weights']=[weights[a] for a in df['Hour']]

	#now return the weighted average
	wdf=pd.DataFrame()
	#need to drop time string column before arithmetic
	df.drop(labels=['date'],axis=1,inplace=True)

	for a in df.columns.values:
		wdf[a] = [df[a].dot(df.weights).sum()/df.weights.sum()]

	wdf.drop(labels=['Hour','weights'],axis=1,inplace=True)
	#return weighted average
	return wdf


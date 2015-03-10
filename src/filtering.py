"""
Collections of functions to reduce multiple obs 
to a single ob for a given day
"""
import pandas as pd

def weighted_average(filename,weights):
	"""Take a csv file of METAR data for a day at single site
	and parse appropriate columns and perform summarization
	with weighted average.  If no weights are supplied
	they are assumed to be unity.

	Keyword arguments: 
	@filename -- string: name of csv file 
	@weights -- numpy array of weights
	
	@returns a single row (summarization) pandas dataframe 
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
	#uniform weights can be set as:
	#weights=np.ones(24)

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


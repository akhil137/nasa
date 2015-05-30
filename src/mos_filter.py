import pandas as pd
import numpy as np
import os

datadir='/Users/ashah/NoBackup/code/nasa/data/MOS/'
airport_abbrv = 'JFK'

#MOS data can be thought of as multi-index with 4 levels:
#run day
#-run hour
#--forecast day
#---forecast hour
#Our heuristic is that we choose only those run day/hour that are
#closest in time to a given forecast day/hour
#The MOS model runs every 6 hours, forecasting out to {+6,+9,+12,...+72} hours
#Thus for a given forecast day/hour, we should choose run day/hour that are 
#9 hours or less behind.

def extract_mos_features(airport_abbrv):
	airport = 'K' + airport_abbrv
	filename = os.path.join(datadir,airport+'.csv')

	#read in the csv but don't index
	df=pd.read_csv(filename,index_col=False)

	#now create pandas datetime columns for run and forecast times
	df['rtime']=pd.to_datetime(df.runtime)
	df['fotime']=pd.to_datetime(df.ftime)

	#now filter s.t. we only keep rows that satisfy above 9 hour or less
	df_filtered=df[df.fotime-df.rtime <= pd.Timedelta('9 hours')]

	#----DEPRECATE BELOW----
	# #get and form the above levels as tuples
	# rd, rt =zip(*[a.split(' ') for a in df.runtime])
	# fd, ft =zip(*[a.split(' ') for a in df.ftime])
	# tup=list(zip(*[rd,rt,fd,ft]))
	# index=pd.MultiIndex.from_tuples(tup,names=['runday','runhour','fday','fhour'])

	# #index the dataframe
	# df_indexed=df.set_index(index)

	#----DEPRECATE ABOVE----

	#now add forecast date and hour columns
	df_filtered['fdate']=[a.date() for a in df_filtered.fotime]
	df_filtered['fhour']=[a.hour for a in df_filtered.fotime]

	#drop columns below keeping only numerical
	dropLabels = ['station', 'model', 'runtime', 'ftime',\
	'n_x', 'cld', 'snw', 'cig', 'obv','typ']

	df_filtered.drop(labels=dropLabels,axis=1,inplace=True)

	#drop further columns since they are all NA once we restrict to tighest horizon
	#verify this for each airport using: df_filtered.isnull().sum()
	dropNAcols= ['p06','p12','q06','q12','t06','t12']
	df_filtered.drop(labels=dropNAcols,axis=1,inplace=True)

	#keep only those features we'll cluster on (following METAR expert judgement)
	dropNonclust = ['tmp','dpt','wdr','rtime','fotime']
	df_filtered.drop(labels=dropNonclust,axis=1,inplace=True)

	#index the rows with the date
	df_filtered.set_index(keys='fdate',inplace=True,drop=True)

	#create a list of dataframes each belonging to a given hour
	hour_group=df_filtered.groupby('fhour')
	hours=pd.unique(df_filtered.fhour)
	dfflist=[hour_group.get_group(a) for a in hours]
	colnames=dfflist[0].columns.values.tolist()
	#name each of these different dataframes with column-names + hour
	cnamelist=[[c+str(h) for c in colnames] for h in hours]
	for i,a in enumerate(cnamelist): 
	    dfflist[i].columns=cnamelist[i]
	    dfflist[i].drop(cnamelist[i][-1],axis=1,inplace=True)

	#now join these
	dffj=pd.DataFrame()
	return dffj.join(dfflist)



#for clustering in other environments create csv
nyregion_airports=['JFK','LGA','EWR']

for airport_code in nyregion_airports:
	print 'extracting %s' %(airport_code)
	df_filtered_joined=extract_mos_features(airport_code)
	#save all of these features to csv - note there will be many NA's
	fn=open('./'+ airport_code +'_MOS_filtered_features.csv','w')
	df_filtered_joined.to_csv(fn,index=False)
	fn.close()

#cluster
datmat=df_filtered_joined.values
#turn nan to 0
datmat=np.nan_to_num(datmat)
daymat=[a.strftime('%m/%d/%Y') for a in df_filtered_joined.index.get_values()]



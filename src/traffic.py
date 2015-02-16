import numpy as np
import pandas as pd
import glob
import os

fn = './ASPM-2013-1.csv'
df = pd.read_csv(fn)
#Slice rows that match JFK and keep only necessary columns
#Note: Facility values have extra whitespace
dfJ = df[df.Facility == ' JFK'].loc[:,['Date','Hour','ScheduledDepartures','ScheduledArrivals']]
#Make a multi-index data-frame
dfJts=dfJ.set_index(['Date','Hour'])

#we can inspect the indexing
dfJts.index
dfJts.index.names

#rename columns for easy plotting
dfJts.columns=['D','A']

#and we can perform summary stats over the level

#how similar are the days (averaged over 24 hours)
dfJts.groupby(level='Date').mean()
dfJts.groupby(level='Date').std()

#a hack to boxplot daily variation in 1st column
dfJts.iloc[:,0:1].groupby(level='Date').boxplot(subplots=False,rot=270,fontsize=8)

#Here is a visualization of the traffic weights, 
#with each hour showing variation in days
dfJts.iloc[:,0:1].groupby(level='Hour').boxplot(subplots=False,rot=270,fontsize=8)


#What we really want are the weights for each hour
weights=dfJts.groupby(level='Hour').mean()
depWeights=weights.D/weights.D.sum()

#to iterate over csv files and append all JFK data to data frame
datadir='/Users/ashah/NoBackup/code/nasa/data/ASPM_CSV'
filelist = glob.glob(os.path.join(datadir,'*.csv'))
trafficDF = pd.DataFrame()
for fn in filelist:
	df = pd.read_csv(fn)
	dfJ = df[df.Facility == ' JFK'].loc[:,['Date','Hour','ScheduledDepartures','ScheduledArrivals']]
	dfJts=dfJ.set_index(['Date','Hour'])
	dfJts.columns=['D','A']
	trafficDF = trafficDF.append(dfJts)

#note we can slice by any date
trafficDF.loc['12/31/2010']

#pickle this out and store for later usage
trafficDF.to_pickle(os.path.join(datadir,'JFK_traffic.pkl'))
#unpickle later as such
#df=pickle.load(open('JFK_traffic.pkl','rb'))

#compute weights
weightsAll=trafficDF.groupby(level='Hour').mean()
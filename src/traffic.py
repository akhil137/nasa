import numpy as np
import pandas as pd

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



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


#drop columns below keeping only numerical
dropLabels = ['station', 'model', 'runtime', 'ftime', 'n_x',\
'tmp', 'dpt', 'cld', 'wdr', 'snw', 'cig', 'vis', 'obv','typ']

df_filtered.drop(labels=dropLabels,axis=1,inplace=True)

#save all of these features to csv - note there will be many NA's
fn=open('./'+ airport +'_MOS_filtered_features.csv','w')
df_filtered.to_csv(fn,index=False)
fn.close()


"""
Generate a concurrency table of METAR Conditions given date-cluster assignment
writen by: Akhil Shah (RAND)
date-modified: May 19, 2015
"""
import os
import glob
import numpy as np
import pandas as pd
from collections import Counter

#Input: 
#@cluters: csv file - first column is 'date' column and second is 'cluster' column
#@airport_abbrv: list - e.g. ['JFK','EWR']; enable us to fetch the METAR file using this and date from above
#Procedure:
#1. extract years and dates from @clusters
#2. create filelist of METAR files to read using above and @airport_abbrv
#3.


def get_cluster_members(filename):
	"""Take a csv file of cluster results
	and generate date-cluster dictionary
	Keyword arguments: 
	@filename -- string: name of cluster results csv file
	@returns -- dictionary with keys=dates, value = cluster label
	"""
	df = pd.read_csv(filename,index_col=0) #set date column to row index
	cluster_group = df.groupby('cluster')
	cluster_day = dict()
	for cluster_label in pd.unique(df.cluster):
		cluster_day[cluster_label] = \
		cluster_group.get_group(cluster_label).index.values.tolist() 

	#return df.iloc[:,0].to_dict() #set dict values to the first column of df (second col of csv)
	return cluster_day


def list_METAR_files_of_cluster(cluster_day,datadir,airport_abbrv):
	"""
	Keyword arguments: 
	@day_cluster_dict -dict: output of get_cluster_members
	@datadir - string: path to METAR files
	@airport_abbrv - string: e.g. 'JFK'
	@returns - list: absolute file location on your disk
	"""
	dates = [cluster_day[k] for k in cluster_day.keys()]
	dates=pd.to_datetime([item for sublist in dates for item in sublist])
	METARdates=[d.strftime('%Y_%m_%d') for d in dates]
	ac='K'+airport_abbrv
	filelist=[os.path.join(datadir,ac,\
		d.split('_')[0],ac+'_'+d+'.txt') for d in METARdates]
	return filelist


def get_events(filename):
	"""Take a csv file of METAR data for a day at single site
	and parse appropriate columns
	Keyword arguments: 
	@filename -- string: name of csv file
	@returns -- pandas data frame of Events and Conditions from METAR

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


#---script---
#--outputs concurenccy tables formatted for LaTeX



datadir = '/Users/ashah/NoBackup/code/nasa/data/METAR/'
cluster_results_dir = '/Users/ashah/NoBackup/code/nasa/results'
#define tex output file to write concurrency table to
filename = os.path.join(cluster_results_dir,'concurrency.tex')
texfile = open(filename,'w')

#--for now: only run this for 5-cluster kmeans results
num_clusters = 5
for airport_abbrv in ['JFK','EWR','LGA']:
	cluster_files=glob.glob(os.path.join(cluster_results_dir,\
		airport_abbrv+'*'+str(num_clusters)+'.csv'))
	
	#use the cluster results file to get a cluster-date dictionary	
	for f in cluster_files:

		cluster_day = get_cluster_members(f)
		#now get the corresponding list of METAR files
		filelist = list_METAR_files_of_cluster(cluster_day,datadir,airport_abbrv)

		#now read the METAR data to get events and conditions categoricals
		dfcat=pd.DataFrame()
		for filepath in filelist:
			dfcat=dfcat.append(get_events(filepath))

		#Loop through dates and count conditions
		#date_cond is dictionary with
		#keys = dates
		#values = Counter object with condition keys and count values
		date_cond=dict() 
		 
		gd=dfcat.groupby('date')
		for key in pd.unique(dfcat['date']).tolist():
			date = pd.to_datetime(key).strftime('%m/%d/%Y')
			date_cond[date]=Counter(gd.get_group(key).Conditions)


		texfile.write('Condition Concurrency Tables for airport:%s' \
		% airport_abbrv)
		texfile.write('Using results from:%s\n' % f)

		#Loop through dates and count conditions
		#cluster_cond is a dictionary with
		#keys = cluster labels
		#values = Counter object with condition keys and count values
		#aggregrated over all days that are part of the given cluster label
		
		##--ALL---##
		#for a given day, store all 24 of the observed conditions
		cluster_cond=dict()
		cluster_total=Counter()
		for cluster_label in cluster_day.keys():
			for date in cluster_day[cluster_label]:
				cluster_total += date_cond[date]
			cluster_cond[cluster_label] = cluster_total

		#for easy manipulation - store as a dataframe
		ccc = pd.DataFrame(cluster_cond)
		texfile.write('Day-Aggregrated counts:\n')
		ccc.to_latex(buf=texfile)
		
		##--MOST---##
		#for a given day, store the most common condition
		cluster_cond_most=dict()
		cluster_total=Counter()
		for cluster_label in cluster_day.keys():
			for date in cluster_day[cluster_label]:
				condition, count = date_cond[date].most_common()[0]
				cluster_total += Counter({condition:count})
			cluster_cond_most[cluster_label] = cluster_total

		#for easy manipulation - store as a dataframe
		ccc_most = pd.DataFrame(cluster_cond_most)
		texfile.write('Day-Most frequent counts:\n')
		ccc_most.to_latex(buf=texfile)

		##--LEAST---##
		#for a given day, store the least common condition
		cluster_cond_least=dict()
		cluster_total=Counter()
		for cluster_label in cluster_day.keys():
			for date in cluster_day[cluster_label]:
				condition, count = date_cond[date].most_common()[-1]
				cluster_total += Counter({condition:count})
			cluster_cond_least[cluster_label] = cluster_total

		#for easy manipulation - store as a dataframe
		
		ccc_least = pd.DataFrame(cluster_cond_least)
		texfile.write('Day-Least frequent counts:\n')
		ccc_least.to_latex(buf=texfile)

texfile.close()






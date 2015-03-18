"""
script to cluster similar days for JFK
"""
import os
import glob
from traffic_bias import generate_average_hourly_traffic
from traffic_bias import traffic_bias_weights
from filtering import clean_frame
from filtering import weighted_average
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import scale
import numpy as np
from datetime import datetime


#1. define the data path and airport
datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'
airport_abbrv = 'JFK'

#get all the airports which are sub-dirs to datadir
#airports=[ap for ap in os.listdir(datadir) \
#if os.path.isdir(os.path.join(datadir,ap))]

airport = 'K' + airport_abbrv

years=[yr for yr in os.listdir(os.path.join(datadir,airport)) \
	if os.path.isdir(os.path.join(datadir,airport,yr))]

#2. generate weights
average_traffic = generate_average_hourly_traffic(airport_abbrv)
weights = traffic_bias_weights(average_traffic)

#pickle out weigts since they are static

#3. create the filtered data matrix from every METAR file datadir
data = list()
day = list()
for year in years:
	print 'parsing METAR year %s', year
	#list of all files
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	#filter each file
	data.append([weighted_average(clean_frame(filepath),weights).values.flatten() \
		for filepath in filelist])
	#extract dates from filenames and store
	date_formater = lambda x: datetime.strptime\
	(x.split('/')[-1].split('.')[0][5:],'%Y_%m_%d')\
	.strftime('%m/%d/%Y')

	day.append([date_formater(filepath) for filepath in filelist])
	

#stack individual data rows into matrices and days into a vector
datMat = np.vstack(data)
dayMat = np.hstack(day)
#To later concatenate, requires 1d array to be 2d
#e.g. must have dayMat.shape = [nsamples,1]
dayMat=dayMat.reshape(dayMat.shape[0],1)

#rows where there are negative values 
#(all should be positive for our features)
bad_rows = np.where(datMat<0)[0]
datMat = np.delete(datMat,bad_rows,axis=0)
dayMat = np.delete(dayMat,bad_rows,axis=0)




#4. cluster scaled data
#kmeans algo
number_of_clusters=[5,10,20]
for numclusters in number_of_clusters:
	kmeans = KMeans(init='k-means++', n_clusters=numclusters, n_init=10)
	#scale 
	labels=kmeans.fit_predict(scale(datMat))
	labels=labels.reshape(labels.shape[0],1)

	#concatenate
	kmeans_output = np.hstack((dayMat,labels,datMat))
	#write to file
	outfile = airport+'trafficBias_kmeans'+'_'+str(numclusters)+'.csv'
	features = weighted_average(clean_frame(filepath),weights).columns.tolist()
	head = 'date,cluster,' + ','.join(features)
	np.savetxt(outfile,kmeans_output,fmt='%s', delimiter=',', header=head)

#dbscan
db=DBSCAN(eps=0.3, min_samples=10).fit(scale(datMat))
db_labels=db.labels_
nc=len(set(db_labels))-(1 if -1 in db_labels else 0)
db_labels=db_labels.reshape(db_labels.shape[0],1)
dbscan_output = np.hstack((dayMat,db_labels,datMat))
outfile = airport+'trafficBias_dbscan_'+str(nc)+'.csv'
np.savetxt(outfile,dbscan_output,fmt='%s', delimiter=',', header=head)


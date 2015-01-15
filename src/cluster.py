import csv
import os
import glob
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
#from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'
#airport='KSFO'

#get all the airports which are sub-dirs to datadir
airports=[ap for ap in os.listdir(datadir) \
if os.path.isdir(os.path.join(datadir,ap))]

years=[yr for yr in os.listdir(datadir) \
if os.path.isdir(os.path.join(datadir,yr))]

#pick a year - TBD loop over years too
#at each airport we choose a year and loop thru 365 days
data=[]
year='2013'
#we have 77 airports
#for airport in airports:
#to test a single airport
for airport in [airports[0]]:
	#filename=airport+"_"+year+"_"+date+".txt" 
	years=[yr for yr in os.listdir(os.path.join(datadir,airport)) \
	if os.path.isdir(os.path.join(datadir,airport,yr))]
	
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	for filepath in filelist:
		with open(filepath,'rU') as csvfile:
			csvreader=csv.reader(csvfile)
			csvreader.next() # pop off blank line
			csvreader.next() # pop off header
			for line in csvreader:
				try:
					if line:
						data.append([airport,line[0],line[1],line[3], \
							line[4],line[5], line[14]])
					
				except Exception, e:
					print airport 
					print line
					raise e
				
a, t, temp, hum, p, v, d = zip(*data)
temp=np.asarray(temp,dtype='float')
d=[el.strip('<br />') for el in d] #get rid of some nonsense

import pandas
import matplotlib.pyplot as plt
dpan=pandas.to_datetime(d)
temppan=pandas.Series(temp,dpan)
temppan.plot()
plt.xlabel('time')
plt.ylabel('Temperature [F]')
plt.title('Temperature at ABQ in 2013')
plt.show()

#oh ya pymetar
import pymetar #pip install this if needed
#fetch it
r=pymetar.ReportFetcher('KRDU')
r.FetchReport()
#from here
r.baseurl


#parse it
p=pymetar.ReportParser(r.report)
p.ParseReport()
p.Report.humid
p.Report.getCloudinfo()





#each day we get an hourly time-series of weather data

#dirtree=os.walk(datadir)


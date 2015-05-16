# -*- coding: utf-8 -*-
"""
  Traffic bias weights generator
  ~~~~~~~~~~~~~~

  Generates weights for each hour from ASPM traffic data. 
  Our dataset encompasses daily scheduled departure and arrival
  between 2010-2013.  Assumes data is in csv format and parsed with
  Kenny's parser.

  Two main functions:
  1. generate_average_hourly_traffic -

  @param: string for airport code
  @returns: pandas data frame of hourly mean depatures and arrivals

  2. get_traffic_bias_weights - 

  @param: pandas data frame of hourly mean departures and arrivals
  @returns: normalized weights



  :copyright: (c) 2015 by Akhil Shah, Kenneth Kuhn, RAND Corp.
  
"""
import pandas as pd
import glob
import os

def generate_average_hourly_traffic(airport_code = 'JFK', data_dir = None):
	if not data_dir:
		# datadir='/Users/ashah/NoBackup/code/nasa/data/ASPM_CSV'
		datadir='/Users/kkuhn/Desktop/csv_ASPM'
	filelist = glob.glob(os.path.join(datadir,'*.csv'))
	trafficDF = pd.DataFrame()
	for fn in filelist:
		df = pd.read_csv(fn)
		#csv files have a whitespace before airport code in Facility 
		dfJ = df[df.Facility == ' '+ airport_code].loc[:,['Date','Hour','ScheduledDepartures','ScheduledArrivals']]
		dfJts=dfJ.set_index(['Date','Hour'])
		dfJts.columns=['D','A']
		trafficDF = trafficDF.append(dfJts)

	avg_traffic = trafficDF.groupby(level='Hour').mean()
	return avg_traffic


def traffic_bias_weights(frame):
	weights = (frame.D + frame.A)/(frame.D.sum() + frame.A.sum())
	return weights.as_matrix()



def generate_hourly_traffic(airport_code = 'JFK', data_dir = None):
	"""
	returns a large data frame with all dates and hours arrival and departures
	""" 
	if not data_dir:
		# datadir='/Users/ashah/NoBackup/code/nasa/data/ASPM_CSV'
		datadir='/Users/kkuhn/Desktop/csv_ASPM'
	filelist = glob.glob(os.path.join(datadir,'*.csv'))
	trafficDF = pd.DataFrame()
	for fn in filelist:
		df = pd.read_csv(fn)
		#csv files have a whitespace before airport code in Facility 
		dfJ = df[df.Facility == ' '+ airport_code].loc[:,['Date','Hour','ScheduledDepartures','ScheduledArrivals']]
		dfJts=dfJ.set_index(['Date','Hour'])
		dfJts.columns=['D','A']
		trafficDF = trafficDF.append(dfJts)

	#avg_traffic = trafficDF.groupby(level='Hour').mean()
	return trafficDF





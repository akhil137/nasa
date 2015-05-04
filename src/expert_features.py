#extract 'expert' features according to: 
#-Chop up day into 3 hours blocks (ref: avijit for 3)
#-Take 3hour min/max of visibility, wind-speed and arrivals at {EWR, JFK, LGA}
#-cluster at each airport individually (total 24 features)
#-cluster using features from all airports (total 24x3 features): regional clusters


#input data source = METAR + ASPM

#1. loop thru airports {JFK, LGA, EWR}
#2. loop thru years 2010-2013
#3. for a given airport and day (single METAR file)
#--produce a clean data frame
#from plot.py
datadir='/Users/ashah/NoBackup/code/nasa/data/METAR/'
airport_abbrv = 'JFK'

#get all the airports which are sub-dirs to datadir
#airports=[ap for ap in os.listdir(datadir) \
#if os.path.isdir(os.path.join(datadir,ap))]

airport = 'K' + airport_abbrv

years=[yr for yr in os.listdir(os.path.join(datadir,airport)) \
	if os.path.isdir(os.path.join(datadir,airport,yr))]
dfall = pd.DataFrame() #data frame of all data
dmlist = list()
for year in years:
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	for filepath in filelist:
		dfall=dfall.append(clean_frame(filepath))
		dmlist.append(data_matrix(clean_frame(filepath)))


#build some 3hour-block features
block_size = 3
#but only do it if we have 24 obs that day (otherwise don't include that day)
#note block_size divides 24 evenly
wind_speed_list_max=[np.max(a['Wind_SpeedMPH'].reshape(-1,block_size),1) for a in dmlist \
			if a['Wind_SpeedMPH'].shape[1]==24]
#now stack rows: columns are 3 hour (or generally block_size) blocks
wind_speed_max=np.vstack(wind_speed_list_max)
#do same for visibility
vis_list_min=[np.min(a['VisibilityMPH'].reshape(-1,block_size),1) for a in dmlist \
			if a['VisibilityMPH'].shape[1]==24]

vis_min = np.vstack(vis_list_min)

#get traffic - note this takes all CSV files from 2010-2013
#and generates a two-level (day, hour) dataframe with Departures and Arrivals
trafDF=generate_hourly_traffic(airport_code = airport_abbrv)
#now create an numpy array to reshape and block max like above features
#.unstack() gives Hour as columns, Dates as rows
#.A selects arrivals
#.as_matrix() now gives a [#dates,#hours] matrix
#.reshape now reshapes it to [#dates,8,3] and we max on the last axis 'axis=2'
arrivals_max=np.max(trafDF.unstack().A.as_matrix().reshape(-1,8,3),axis=2)

#now make a data matrix
#TODO: figure out how to consistently select same dates for wind,vis,arrivals
datmat=np.concatenate((vis_min,wind_speed_max),axis=1)
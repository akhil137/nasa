import matplotlib.pyplot as plt
"ref: http://matplotlib.org/examples/style_sheets/plot_bmh.html"

plt.style.use('bmh')
def plot_hist_data_matrix(dm):
	


#box-plot of daily variation of a feature
#@param dm: data_matrix from filtering.py
#@param scale: boolean, if True, then scale input using standard scalar
#x-axis: records, e.g. day 1, day 2, etc.
#y-axis: box-plot value
#title: name of feature, years
#only the first 35 days (the full range is 365*4 days)
plt.figure()
plt.boxplot(dmdict['TemperatureF'])
plt.title('TemperatureF variation')
#plt.xlabel('day')
#plt.xticks(np.arange(start=1,stop=35,step=7))
plt.show()
#scatter plot of feature vs feature


#boxplot - hourly variation
#x-axis - hour of day
plt.figure()
plt.boxplot(dmdict['TemperatureF'])
plt.title('JFK: Hourly temperature variation between 2010-2013')
plt.xlabel('Hour')
plt.ylabel('Temperature[F]')
#plt.xticks(np.arange(start=1,stop=35,step=7))
plt.show()


#boxplot - yearly variation
#x-axis - hour of day
plt.figure()
plt.boxplot(dmdict['TemperatureF'].T)
plt.title('JFK: Daily temperature variation between 2010-2013')
plt.xlabel('day')
plt.ylabel('Temperature[F]')
step_size=np.round(dmdict['TemperatureF'].shape[0]/10)
stop=dmdict['TemperatureF'].shape[0]
plt.xticks(np.arange(start=1,step=step_size,stop=stop))
plt.show()


def plot_year_variation(key):
	plt.figure()
	plt.boxplot(dmdict[key].T)
	plt.title('JFK: Daily '+key+' variation between 2010-2013')
	plt.xlabel('day')
	plt.ylabel(key)
	step_size=np.round(dmdict[key].shape[0]/10)
	stop=dmdict[key].shape[0]
	plt.xticks(np.arange(start=1,step=step_size,stop=stop))
	plt.show()

#cleanest way to do it
dfall = pd.DataFrame() #data frame of all data
for year in years:
	filelist=glob.glob(os.path.join(datadir,airport,year,'*.txt'))
	for filepath in filelist:
		dfall=dfall.append(clean_frame(filepath))

dfall['year']=[pd.to_datetime(a).year for a in dfall['date']]

features=['Humidity', 'PrecipitationIn', 'TemperatureF','VisibilityMPH', 'Wind_SpeedMPH']

plt.figure(1)
for i,f in enumerate(features):
	plt.figure(1)
	ax=plt.subplot(2,3,i)
	df.boxplot(column=f,by='year',ax=ax)
plt.show()

#scatter plots
import itertools
plt.figure(2)
for i,f in enumerate(itertools.combinations(features,2)):
	plt.figure(2)
	ax=plt.subplot(3,4,i)
	df.plot(kind='scatter',x=f[0],y=f[1],ax=ax)
	print f[0] + f[1]
plt.show()







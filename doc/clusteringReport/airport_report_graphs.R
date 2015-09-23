#
# FIGURE 1: Boxplots of arrivals and departures, by hour, at JFK
#
# Load in the arrivals and departures, by hour, at JFK
ASPM_dir = "/Volumes/NASA_data_copy/data_raw/airport_traffic/ASPM/csv_ASPM/"
JFK_arr = c()
JFK_dep = c()
JFK_hour = c()
for (years_ind in 2010:2013) {
	for (file_ind in 1:36) {
		fname = paste(ASPM_dir,"ASPM-",years_ind,"-",file_ind,".csv",sep="")
		cur_data = read.csv(fname)
		cur_data = cur_data[cur_data$Facility==" JFK",]
		JFK_arr = c(JFK_arr,cur_data$ScheduledArrivals)
		JFK_dep = c(JFK_dep,cur_data$ScheduledDepartures)
		JFK_hour = c(JFK_hour,cur_data$GMTHour)
	}
}
# Make the plot
JFK = data.frame(arrivals=JFK_arr,departures=JFK_dep,hour=JFK_hour)
library(ggplot2)
library(gridExtra)
JFK$hour = as.factor(JFK$hour)
graph1 = ggplot(JFK,aes(hour,arrivals))+geom_boxplot(fill="orange")
graph2 = ggplot(JFK,aes(hour,departures))+geom_boxplot(fill="orange")
graph1 = graph1+labs(x="Hour (GMT)",y="Scheduled Arrivals at JFK")
graph2 = graph1+labs(x="Hour (GMT)",y="Scheduled Departures at JFK")
graph1 = graph1+theme_bw()
graph2 = graph2+theme_bw()
# Save the plot
pdf("/Users/kkuhn/Desktop/Fig1.pdf",width=8,height=4)
graph1
dev.off()

#
# FIGURE 2: Barchart of variance explained by various principal components
#
# Load in weather data for JFK
METAR_dir = "/Volumes/NASA_data_copy/data_raw/airport_weather/METAR/KJFK/"
wind_speed = matrix(-999,nrow=1461,ncol=70)
temperature = matrix(-999,nrow=1461,ncol=70)
visibility = matrix(-999,nrow=1461,ncol=70)
precipitation = matrix(-999,nrow=1461,ncol=70)
filled_ind = 1
years = c("2010","2011","2012","2013")
months = c("01","02","03","04","05","06","07","08","09","10","11","12")
for (year_ind in 1:4) {
	for (month_ind in 1:12) {
		days = c("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28")
		if (month_ind %in% c(1,3,5,7,8,10,12)) { days=c(days,"29","30","31") }
		if (month_ind %in% c(4,6,9,11)) { days=c(days,"29","30") }
		if (month_ind==2 & year_ind==3) { days=c(days,"29") }
		for (day_ind in 1:length(days)) {
			fname = paste(METAR_dir,years[year_ind],"/KJFK_",years[year_ind],"_",months[month_ind],"_",days[day_ind],".txt",sep="")
			cur_data = read.csv(fname)
			wind_speed[filled_ind,1:length(cur_data$Wind.SpeedMPH)] = cur_data$Wind.SpeedMPH
			temperature[filled_ind,1:length(cur_data$TemperatureF)] = cur_data$TemperatureF
			visibility[filled_ind,1:length(cur_data$VisibilityMPH)] = cur_data$VisibilityMPH
			precipitation[filled_ind,1:length(cur_data$PrecipitationIn)] = cur_data$PrecipitationIn
			filled_ind = filled_ind+1
		}
	}
}
# Every day has at least 19 observations.  Throw out the rest; we can't have missing data.
wind_speed = wind_speed[,1:19]
temperature = temperature[,1:19]
visibility = visibility[,1:19]
precipitation = precipitation[,1:19]
# Find principal components and proportion of variance explained
pca1 = prcomp(wind_speed,scale=TRUE)
vars1 = apply(pca1$x,2,var)  
props1 = vars1/sum(vars1)
pca2 = prcomp(temperature,scale=TRUE)
vars2 = apply(pca2$x,2,var)  
props2 = vars2/sum(vars2)
pca3 = prcomp(visibility,scale=TRUE)
vars3 = apply(pca3$x,2,var)  
props3 = vars3/sum(vars3)
pca4 = prcomp(precipitation,scale=TRUE)
vars4 = apply(pca4$x,2,var)  
props4 = vars4/sum(vars4)
cats = c(rep("wind speed",5),rep("temperature",5),rep("visibility",5),rep("precipitation",5))
principals = data.frame(vari=cats,index_v=rep(c(1:5),4),var_exp=c(props1[1:5],props2[1:5],props3[1:5],props4[1:5]))
# Make the desired bar chart
graph1 = ggplot(principals,aes(x=index_v,y=var_exp))+geom_bar(stat="identity",fill="orange")+facet_wrap(~vari,nrow=1)
graph1 = graph1+labs(x="Principal Component",y="Percent of Variance Explained")
graph1 = graph1+theme_bw()
# Save the plot
pdf("/Users/kkuhn/Desktop/Fig2.pdf",width=8,height=4)
graph1
dev.off()

#
# FIGURES 3 and 4: Boxplots of various weather observations by hour and month
#
# Load in weather data for JFK
METAR_dir = "/Volumes/NASA_data_copy/data_raw/airport_weather/METAR/KJFK/"
wind_speed = c()
temperature = c()
visibility = c()
precipitation = c()
relevant_hour = c()
relevant_month = c()
years = c("2010","2011","2012","2013")
months = c("01","02","03","04","05","06","07","08","09","10","11","12")
for (year_ind in 1:4) {
	for (month_ind in 1:12) {
		days = c("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28")
		if (month_ind %in% c(1,3,5,7,8,10,12)) { days=c(days,"29","30","31") }
		if (month_ind %in% c(4,6,9,11)) { days=c(days,"29","30") }
		if (month_ind==2 & year_ind==3) { days=c(days,"29") }
		for (day_ind in 1:length(days)) {
			fname = paste(METAR_dir,years[year_ind],"/KJFK_",years[year_ind],"_",months[month_ind],"_",days[day_ind],".txt",sep="")
			cur_data = read.csv(fname)
			colnames(cur_data)[1] = "Hour"
			num_point = min(length(cur_data$Wind.SpeedMPH),length(cur_data$Hour))
			wind_speed = c(wind_speed,cur_data$Wind.SpeedMPH[1:num_point])
			temperature = c(temperature,cur_data$TemperatureF[1:num_point])
			visibility = c(visibility,cur_data$VisibilityMPH[1:num_point])
			precipitation = c(precipitation,cur_data$PrecipitationIn[1:num_point])
			relevant_hour = c(relevant_hour,as.character(cur_data$Hour[1:num_point]))
			relevant_month = c(relevant_month,rep(month_ind,num_point))
		}
	}
}
# Reformat the data
reform = data.frame(month=relevant_month,hour=relevant_hour,wind=wind_speed,temp=temperature,vis=visibility,precip=precipitation)
reform$hour = sub(":"," ",reform$hour)
find_pm = grep("PM",reform$hour)
reform$hour = as.numeric(substr(reform$hour,1,2))
reform$hour[find_pm] = reform$hour[find_pm]+12
reform$hour[reform$hour==12] = 99
reform$hour[reform$hour==24] = 12
reform$hour[reform$hour==99] = 24
reform$hour = as.factor(reform$hour)
reform$month = as.factor(reform$month)
reform$wind[reform$wind==-9999] = NA
reform$temp[reform$temp==-9999] = NA
reform$vis[reform$vis==-9999] = NA
# Make the boxplot figures
library(ggplot2)
library(gridExtra)
graph1 = ggplot(reform,aes(hour,wind))+geom_boxplot(fill="orange",outlier.size=0.5)
graph1 = graph1+scale_y_continuous(limits=quantile(reform$wind,c(0.01,0.99),na.rm=T))
graph1 = graph1+labs(x="Hour (Local Time)",y="Wind Speed (knots) at JFK")
graph1 = graph1+theme_bw()
graph2 = ggplot(reform,aes(hour,temp))+geom_boxplot(fill="orange",outlier.size=0.5)
graph2 = graph2+labs(x="Hour (Local Time)",y="Temperature (deg. F) at JFK")
graph2 = graph2+scale_y_continuous(limits=quantile(reform$temp,c(0.01,0.99),na.rm=T))
graph2 = graph2+theme_bw()
graph3 = ggplot(reform,aes(hour,vis))+geom_boxplot(fill="orange",outlier.size=0.5)
graph3 = graph3+labs(x="Hour (Local Time)",y="Visibility at JFK")
graph3 = graph3+scale_y_continuous(limits=quantile(reform$vis,c(0.01,0.99),na.rm=T))
graph3 = graph3+theme_bw()
graph4 = ggplot(reform,aes(hour,precip))+geom_boxplot(fill="orange",outlier.size=0.5)
graph4 = graph4+labs(x="Hour (Local Time)",y="Precipitation (in.) at JFK")
graph4 = graph4+scale_y_continuous(limits=quantile(reform$precip,c(0.01,0.99),na.rm=T))
graph4 = graph4+theme_bw()
graph5 = ggplot(reform,aes(month,wind))+geom_boxplot(fill="orange",outlier.size=0.5)
graph5 = graph5+labs(x="Month",y="Wind Speed (knots) at JFK")
graph5 = graph5+scale_y_continuous(limits=quantile(reform$wind,c(0.01,0.99),na.rm=T))
graph5 = graph5+theme_bw()
graph6 = ggplot(reform,aes(month,temp))+geom_boxplot(fill="orange",outlier.size=0.5)
graph6 = graph6+labs(x="Month",y="Temperature (deg. F) at JFK")
graph6 = graph6+scale_y_continuous(limits=quantile(reform$temp,c(0.01,0.99),na.rm=T))
graph6 = graph6+theme_bw()
graph7 = ggplot(reform,aes(month,vis))+geom_boxplot(fill="orange",outlier.size=0.5)
graph7 = graph7+labs(x="Month",y="Visibility at JFK")
graph7 = graph7+scale_y_continuous(limits=quantile(reform$vis,c(0.01,0.99),na.rm=T))
graph7 = graph7+theme_bw()
graph8 = ggplot(reform,aes(month,precip))+geom_boxplot(fill="orange",outlier.size=0.5)
graph8 = graph8+labs(x="Month",y="Precipitation (in.) at JFK")
graph8 = graph8+scale_y_continuous(limits=quantile(reform$precip,c(0.01,0.99),na.rm=T))
graph8 = graph8+theme_bw()
# Save the boxplots
pdf("/Users/kkuhn/Desktop/Fig3.pdf",width=10,height=10)
grid.arrange(graph1,graph2,graph3,graph4,ncol=2)
dev.off()
pdf("/Users/kkuhn/Desktop/Fig4.pdf",width=8,height=8)
grid.arrange(graph5,graph6,graph7,graph8,ncol=2)
dev.off()

#
# ACTUAL CLUSTERING BELOW THIS LINE
#
#
# TABLE 3: Feature of k medoids
# Figures 5 and 6: Avg silhouette width as a function of k for NY and JFK models
#
# Pull out data on the scheduled arrivals at JFK, EWR, and LGA
ASPM_dir = "/Volumes/NASA_data_copy/data_raw/airport_traffic/ASPM/csv_ASPM/"
JFK_date = c()
JFK_hour = c()
JFK_arri = c()
EWR_date = c()
EWR_hour = c()
EWR_arri = c()
LGA_date = c()
LGA_hour = c()
LGA_arri = c()
for (years_ind in 2010:2013) {
	for (file_ind in 1:36) {
		fname = paste(ASPM_dir,"ASPM-",years_ind,"-",file_ind,".csv",sep="")
		cur_data = read.csv(fname)
		JFK_data = cur_data[cur_data$Facility==" JFK",]
		EWR_data = cur_data[cur_data$Facility==" EWR",]
		LGA_data = cur_data[cur_data$Facility==" LGA",]
		JFK_date = c(JFK_date,as.character(JFK_data$Date))
		JFK_hour = c(JFK_hour,JFK_data$GMTHour)
		JFK_arri = c(JFK_arri,JFK_data$ScheduledArrivals)
		EWR_date = c(EWR_date,as.character(EWR_data$Date))
		EWR_hour = c(EWR_hour,EWR_data$GMTHour)
		EWR_arri = c(EWR_arri,EWR_data$ScheduledArrivals)
		LGA_date = c(LGA_date,as.character(LGA_data$Date))
		LGA_hour = c(LGA_hour,LGA_data$GMTHour)
		LGA_arri = c(LGA_arri,LGA_data$ScheduledArrivals)
	}
}
# Define features based on the scheduled arrivals at JFK, EWR, and LGA
filled_ind = 1
JFK_arrivals = matrix(-999,nrow=1461,ncol=4)
EWR_arrivals = matrix(-999,nrow=1461,ncol=4)
LGA_arrivals = matrix(-999,nrow=1461,ncol=4)
years = c("2010","2011","2012","2013")
months = c("01","02","03","04","05","06","07","08","09","10","11","12")
for (year_ind in 1:4) {
	for (month_ind in 1:12) {
		days = c("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28")
		if (month_ind %in% c(1,3,5,7,8,10,12)) { days=c(days,"29","30","31") }
		if (month_ind %in% c(4,6,9,11)) { days=c(days,"29","30") }
		if (month_ind==2 & year_ind==3) { days=c(days,"29") }
		for (day_ind in 1:length(days)) {
			cur_date = paste(months[month_ind],days[day_ind],years[year_ind],sep="/")
			focus = which(JFK_date==cur_date & JFK_hour>9.5 & JFK_hour<12.5)
			JFK_arrivals[filled_ind,1] = sum(JFK_arri[focus])
			focus = which(JFK_date==cur_date & JFK_hour>12.5 & JFK_hour<15.5)
			JFK_arrivals[filled_ind,2] = sum(JFK_arri[focus])
			focus = which(JFK_date==cur_date & JFK_hour>15.5 & JFK_hour<18.5)
			JFK_arrivals[filled_ind,3] = sum(JFK_arri[focus])
			focus = which(JFK_date==cur_date & JFK_hour>18.5 & JFK_hour<21.5)
			JFK_arrivals[filled_ind,4] = sum(JFK_arri[focus])
			focus = which(EWR_date==cur_date & EWR_hour>9.5 & EWR_hour<12.5)
			EWR_arrivals[filled_ind,1] = sum(EWR_arri[focus])
			focus = which(EWR_date==cur_date & EWR_hour>12.5 & EWR_hour<15.5)
			EWR_arrivals[filled_ind,2] = sum(EWR_arri[focus])
			focus = which(EWR_date==cur_date & EWR_hour>15.5 & EWR_hour<18.5)
			EWR_arrivals[filled_ind,3] = sum(EWR_arri[focus])
			focus = which(EWR_date==cur_date & EWR_hour>18.5 & EWR_hour<21.5)
			EWR_arrivals[filled_ind,4] = sum(EWR_arri[focus])
			focus = which(LGA_date==cur_date & LGA_hour>9.5 & LGA_hour<12.5)
			LGA_arrivals[filled_ind,1] = sum(LGA_arri[focus])
			focus = which(LGA_date==cur_date & LGA_hour>12.5 & LGA_hour<15.5)
			LGA_arrivals[filled_ind,2] = sum(LGA_arri[focus])
			focus = which(LGA_date==cur_date & LGA_hour>15.5 & LGA_hour<18.5)
			LGA_arrivals[filled_ind,3] = sum(LGA_arri[focus])
			focus = which(LGA_date==cur_date & LGA_hour>18.5 & LGA_hour<21.5)
			LGA_arrivals[filled_ind,4] = sum(LGA_arri[focus])
			filled_ind = filled_ind+1
		}
	}
}
# Pull out data on the forecast weather at JFK, EWR, and LGA
LAMP_dir = "/Volumes/NASA_data_copy/data_raw/airport_weather/LAMP/"
JFK_data = read.csv(paste(LAMP_dir,"KJFK.csv",sep=""),row.names=NULL)
EWR_data = read.csv(paste(LAMP_dir,"KEWR.csv",sep=""),row.names=NULL)
LGA_data = read.csv(paste(LAMP_dir,"KLGA.csv",sep=""),row.names=NULL)
# Define features based on the forecast weather at JFK, EWR, and LGA
filled_ind = 1
JFK_vis = matrix("xxx",nrow=1461,ncol=4)
JFK_wds = matrix(-999,nrow=1461,ncol=4)
JFK_wdr = matrix(-999,nrow=1461,ncol=4)
EWR_vis = matrix("xxx",nrow=1461,ncol=4)
EWR_wds = matrix(-999,nrow=1461,ncol=4)
EWR_wdr = matrix(-999,nrow=1461,ncol=4)
LGA_vis = matrix("xxx",nrow=1461,ncol=4)
LGA_wds = matrix(-999,nrow=1461,ncol=4)
LGA_wdr = matrix(-999,nrow=1461,ncol=4)
years = c("2010","2011","2012","2013")
months = c("01","02","03","04","05","06","07","08","09","10","11","12")
hours = c("00:00:00+00","06:00:00+00","12:00:00+00","18:00:00+00")
last_day_str = "2009-12-31"
for (year_ind in 1:4) {
	for (month_ind in 1:12) {
		days = c("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28")
		if (month_ind %in% c(1,3,5,7,8,10,12)) { days=c(days,"29","30","31") }
		if (month_ind %in% c(4,6,9,11)) { days=c(days,"29","30") }
		if (month_ind==2 & year_ind==3) { days=c(days,"29") }
		for (day_ind in 1:length(days)) {
			cur_day_str = paste(years[year_ind],"-",months[month_ind],"-",days[day_ind],sep="")
			model_time = paste(last_day_str," 12:00:00+00",sep="")
			target_str = paste(cur_day_str," 00:00:00+00",sep="")
			focus = which(JFK_data$model==model_time & JFK_data$runtime==target_str)
			if (length(focus)==1) {
				JFK_vis[filled_ind,1] = as.character(JFK_data$vis[focus])
				JFK_wds[filled_ind,1] = JFK_data$wsp[focus]
				JFK_wdr[filled_ind,1] = JFK_data$wdr[focus]
			}
			focus = which(EWR_data$model==model_time & EWR_data$runtime==target_str)
			if (length(focus)==1) {
				EWR_vis[filled_ind,1] = as.character(EWR_data$vis[focus])
				EWR_wds[filled_ind,1] = EWR_data$wsp[focus]
				EWR_wdr[filled_ind,1] = EWR_data$wdr[focus]
			}
			focus = which(LGA_data$model==model_time & LGA_data$runtime==target_str)
			if (length(focus)==1) {
				LGA_vis[filled_ind,1] = as.character(LGA_data$vis[focus])
				LGA_wds[filled_ind,1] = LGA_data$wsp[focus]
				LGA_wdr[filled_ind,1] = LGA_data$wdr[focus]
			}
			model_time = paste(last_day_str," 18:00:00+00",sep="")
			target_str = paste(cur_day_str," 06:00:00+00",sep="")
			focus = which(JFK_data$model==model_time & JFK_data$runtime==target_str)
			if (length(focus)==1) {
				JFK_vis[filled_ind,2] = as.character(JFK_data$vis[focus])
				JFK_wds[filled_ind,2] = JFK_data$wsp[focus]
				JFK_wdr[filled_ind,2] = JFK_data$wdr[focus]
			}
			focus = which(EWR_data$model==model_time & EWR_data$runtime==target_str)
			if (length(focus)==1) {
				EWR_vis[filled_ind,2] = as.character(EWR_data$vis[focus])
				EWR_wds[filled_ind,2] = EWR_data$wsp[focus]
				EWR_wdr[filled_ind,2] = EWR_data$wdr[focus]
			}
			focus = which(LGA_data$model==model_time & LGA_data$runtime==target_str)
			if (length(focus)==1) {
				LGA_vis[filled_ind,2] = as.character(LGA_data$vis[focus])
				LGA_wds[filled_ind,2] = LGA_data$wsp[focus]
				LGA_wdr[filled_ind,2] = LGA_data$wdr[focus]
			}
			model_time = paste(cur_day_str," 00:00:00+00",sep="")
			target_str = paste(cur_day_str," 12:00:00+00",sep="")
			focus = which(JFK_data$model==model_time & JFK_data$runtime==target_str)
			if (length(focus)==1) {
				JFK_vis[filled_ind,3] = as.character(JFK_data$vis[focus])
				JFK_wds[filled_ind,3] = JFK_data$wsp[focus]
				JFK_wdr[filled_ind,3] = JFK_data$wdr[focus]
			}
			focus = which(EWR_data$model==model_time & EWR_data$runtime==target_str)
			if (length(focus)==1) {
				EWR_vis[filled_ind,3] = as.character(EWR_data$vis[focus])
				EWR_wds[filled_ind,3] = EWR_data$wsp[focus]
				EWR_wdr[filled_ind,3] = EWR_data$wdr[focus]
			}
			focus = which(LGA_data$model==model_time & LGA_data$runtime==target_str)
			if (length(focus)==1) {
				LGA_vis[filled_ind,3] = as.character(LGA_data$vis[focus])
				LGA_wds[filled_ind,3] = LGA_data$wsp[focus]
				LGA_wdr[filled_ind,3] = LGA_data$wdr[focus]
			}
			model_time = paste(cur_day_str," 06:00:00+00",sep="")
			target_str = paste(cur_day_str," 18:00:00+00",sep="")
			focus = which(JFK_data$model==model_time & JFK_data$runtime==target_str)
			if (length(focus)==1) {
				JFK_vis[filled_ind,4] = as.character(JFK_data$vis[focus])
				JFK_wds[filled_ind,4] = JFK_data$wsp[focus]
				JFK_wdr[filled_ind,4] = JFK_data$wdr[focus]
			}
			focus = which(EWR_data$model==model_time & EWR_data$runtime==target_str)
			if (length(focus)==1) {
				EWR_vis[filled_ind,4] = as.character(EWR_data$vis[focus])
				EWR_wds[filled_ind,4] = EWR_data$wsp[focus]
				EWR_wdr[filled_ind,4] = EWR_data$wdr[focus]
			}
			focus = which(LGA_data$model==model_time & LGA_data$runtime==target_str)
			if (length(focus)==1) {
				LGA_vis[filled_ind,4] = as.character(LGA_data$vis[focus])
				LGA_wds[filled_ind,4] = LGA_data$wsp[focus]
				LGA_wdr[filled_ind,4] = LGA_data$wdr[focus]
			}
			last_day_str = cur_day_str
			filled_ind = filled_ind+1
		}
	}
}
# Combine and save feature data
features = data.frame(JFK_arrivals,EWR_arrivals,LGA_arrivals,
	JFK_vis,EWR_vis,LGA_vis,JFK_wdr,EWR_wdr,LGA_wdr,JFK_wds,EWR_wds,LGA_wds)
colnames(features) = c("JFK_arr_1","JFK_arr_2","JFK_arr_3","JFK_arr_4",
	"EWR_arr_1","EWR_arr_2","EWR_arr_3","EWR_arr_4","LGA_arr_1","LGA_arr_2","LGA_arr_3","LGA_arr_4",
	"JFK_vis_1","JFK_vis_2","JFK_vis_3","JFK_vis_4","EWR_vis_1","EWR_vis_2","EWR_vis_3","EWR_vis_4",
	"LGA_vis_1","LGA_vis_2","LGA_vis_3","LGA_vis_4","JFK_wdr_1","JFK_wdr_2","JFK_wdr_3","JFK_wdr_4",
	"EWR_wdr_1","EWR_wdr_2","EWR_wdr_3","EWR_wdr_4","LGA_wdr_1","LGA_wdr_2","LGA_wdr_3","LGA_wdr_4",
	"JFK_wds_1","JFK_wds_2","JFK_wds_3","JFK_wds_4","EWR_wds_1","EWR_wds_2","EWR_wds_3","EWR_wds_4",
	"LGA_wds_1","LGA_wds_2","LGA_wds_3","LGA_wds_4")
#save(features,file="/Users/kkuhn/Desktop/features.Rdata")
#load("/Users/kkuhn/Desktop/features.Rdata")
# Note NA's and convert categorical data to numeric data
features[features==-999] = NA
features[features=="xxx"] = NA
for (i1 in 13:24) { features[,i1]=as.character(features[,i1]) }
features[features=="BL"] = "0"
features[features=="BR"] = "1"
features[features=="FG"] = "2"
features[features=="HZ"] = "3"
features[features=="N "] = "4"
for (i1 in 13:24) { features[,i1]=as.numeric(features[,i1]) }
# Pick out JFK data
JFK_features = c(1:4,13:16,25:28,37:40)
JFK_df = features[,JFK_features]
# Fit PAM models and save silhouette widths
library(cluster)
sils = c(rep(-999,49))
JFK_sils = c(rep(-999,49))
for (i1 in 2:50) {
	pam_model = pam(x=features,k=i1,metric="manhattan",stand=TRUE,do.swap=FALSE)
	JFK_model = pam(x=JFK_df,k=i1,metric="manhattan",stand=TRUE,do.swap=FALSE)
	sils[i1-1] = pam_model$silinfo$avg.width
	JFK_sils[i1-1] = JFK_model$silinfo$avg.width
}
# Plot silhouette widths
pam_data = data.frame(k=c(2:50),sils=sils,JFK_sils=JFK_sils)
library(ggplot2)
pam_data = pam_data[1:29,]
graph1 = ggplot(pam_data,aes(x=k,y=sils))+geom_line(color="orange")+geom_point(color="orange")
graph1 = graph1+labs(x="Number of Clusters",y="Average Silhouette Width")
graph1 = graph1+theme_bw()
graph2 = ggplot(pam_data,aes(x=k,y=JFK_sils))+geom_line(color="orange")+geom_point(color="orange")
graph2 = graph2+labs(x="Number of Clusters",y="Average Silhouette Width")
graph2 = graph2+theme_bw()
# Save the plot
pdf("/Users/kkuhn/Desktop/Fig5.pdf",width=8,height=4)
graph1
dev.off()
pdf("/Users/kkuhn/Desktop/Fig6.pdf",width=8,height=4)
graph2
dev.off()
# Fit the k=10 model
pam_model = pam(x=features,k=10,metric="manhattan",stand=TRUE,do.swap=FALSE)
date_list = seq(as.Date("2010/1/1"), as.Date("2013/12/31"),"day")
med_dates = date_list[pam_model$id.med]
med_JFK_arr = round(apply(features[pam_model$id.med,1:4],1,sum),1)
med_EWR_arr = round(apply(features[pam_model$id.med,5:8],1,sum),1)
med_LGA_arr = round(apply(features[pam_model$id.med,9:12],1,sum),1)
med_JFK_wsp = round(apply(features[pam_model$id.med,37:40],1,mean),1)
med_EWR_wsp = round(apply(features[pam_model$id.med,41:44],1,mean),1)
med_LGA_wsp = round(apply(features[pam_model$id.med,45:48],1,mean),1)
x=data.frame(date=med_dates,JFK_arr=med_JFK_arr,EWR_arr=med_EWR_arr,LGA_arr=med_LGA_arr,
	JFK_wsp=med_JFK_wsp,EWR_wsp=med_EWR_wsp,LGA_wsp=med_LGA_wsp)
x









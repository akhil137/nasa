

setwd("~/NoBackup/code/nasa/data/")

####################################################
#~~~~~~~~~~~~~ ADVISORY data ~~~~~~~~~~~~~~~~~~~~~~#
####################################################
#read in data
dat<-read.csv("./advy_2010_2014/advisory_details_report_20100101_20100331.csv")

#only need some columns for gdp related data
gdpcols<-c("SendDate.Time.UTC",
"AdvisoryType",
"Derived.BgnDate.Time.UTC",
"Derived.EndDate.Time.UTC",
"ControlElement",
"Average.Delay",
"Delay.Asgmt.Mode"
)

#perhaps understand more columns later
# gdpcols<-c("AdvisoryDate.UTC",
# "AdvisoryType",
# "Derived.BgnDate.Time.UTC",
# "Derived.EndDate.Time.UTC",
# "ControlElement",
# "Average.Delay",
# "Comments",
# "Delay.Asgmt.Mode",
# "Delay.Asgmt.Table.Applies.To",
# "Dep.Scope",
# "Impacting.Condition",
# )
#various times
# gdpcols<-c("AdvisoryDate.UTC",
# "AdvisoryType",
# "Derived.BgnDate.Time.UTC",
# "Derived.EndDate.Time.UTC",
# "GDP.Bgn.Date.Time.UTC",
# "GDP.End.Date.Time.UTC",
# "GDPX.Bgn.Date.Time.UTC",
# "GDPX.End.Date.Time.UTC",
# "ControlElement",
# "Eff.Bgn.Date.Time.UTC",
# "Eff.End.Date.Time.UTC",
# "Valid.Bgn.Date.Time.UTC",
# "Valid.End.Date.Time.UTC")

#Valid.Bgn and End time fields are empty for GDP at {EWR,JFK,LGA}


#subset on these columns
dat.gdpcols<-dat[,gdpcols]
#check that's what we actually got
colnames(dat.gdpcols)

#subset on GDP and GDP CNX 
#derive by unique(dat.gdpcols$AdvisoryType)
dat.gdp<-dat.gdpcols[dat.gdpcols$AdvisoryType == "GDP" | dat.gdpcols$AdvisoryType == "GDP CNX",]

#subset on airport
dat.gdp.ewr<-dat.gdp[dat.gdp$ControlElement=="EWR/ZNY",]

#create vectors of timestamps and GDP values
gdp.time<-as.POSIXct(dat.gdp.ewr$Derived.BgnDate.Time.UTC,tz="UTC")
gdp.bin<-factor(dat.gdp.ewr$AdvisoryType)
gdp.end.time<-as.POSIXct(dat.gdp.ewr$Derived.EndDate.Time.UTC,tz="UTC")



#a helper function to create a seq of hours between
#gdp begin and end times.
#each hour will then be appended with array of GDP or GDP CNX.
#we can then see the sequence of different TMI applied to any 
#given hour slot.
library(xts)
#will return a xts object (time-indexed matrix)
gdpseq<-function(beginTime,endTime,statusFactor){
	tmp<-seq(beginTime,endTime,"hour")
	xts(rep(statusFactor,length(tmp)),tmp)
}
#create a list of xts objects created above
#each entry of the list correponds to an xts object
#and there are as many entries as there are 
#gdp.time/gdp.end.time values (start/stop times)
emptyList<-list()
listGrow<-function(x){emptyList[[x]]=gdpseq(gdp.time[x],gdp.end.time[x],gdp.bin[x])}
gdplist<-sapply(seq(length(gdp.time)),listGrow)

#now when we rbind to get a single time series
gdp.status<-do.call(rbind,gdplist)

####################################################
#~~~~~~~~~~~~~ TRAFFIC data ~~~~~~~~~~~~~~~~~~~~~~~#
####################################################
#read in aspm data
aspm<-read.csv("./ASPM_csv/ASPM-2010-1.csv")

#ASPM columns of relevance
aspmCols<-c("Date",
	"GMTHour",
	"Facility",
	"ScheduledArrivals",
	"AverageAirborneDelay")

#subset on these cols
aspm.relcols<-aspm[,aspmCols]
#watch out for blank space in front of facility code
aspm.ewr<-aspm.relcols[aspm.relcols$Facility==" EWR",]
x<-paste(aspm.ewr$Date,aspm.ewr$GMTHour)
#create vector timestamps
traffic.date<-as.POSIXct(strptime(x,format="%m/%d/%Y %H"),tz="GMT")

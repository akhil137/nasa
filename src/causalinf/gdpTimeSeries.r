
#function to read and filter TMI advisory data by GDP and airport
#inputs: advisory filename and airport zone (e.g. "EWR/ZNY")
#outputs: "gdp object" with begin/end times and gdp status
#usage: gdp<-getGDP("advisoryFile","EWR/ZNY")
getGDP<-function(filename,apZone){
	dat<-read.csv(filename)

	#enumerate columns we care about
	gdpcols<-c("SendDate.Time.UTC",
	"AdvisoryType",
	"Derived.BgnDate.Time.UTC",
	"Derived.EndDate.Time.UTC",
	"ControlElement",
	"Average.Delay",
	"Delay.Asgmt.Mode"
	)

	#subset on these columns
	dat.gdpcols<-dat[,gdpcols]
	
	#subset on "GDP" and "GDP CNX" 
	#derived by unique(dat.gdpcols$AdvisoryType)
	dat.gdp<-dat.gdpcols[dat.gdpcols$AdvisoryType == "GDP" | dat.gdpcols$AdvisoryType == "GDP CNX",]

	#subset on airport/zone
	#for example "EWR/ZNY"
	dat.gdp.ap<-dat.gdp[dat.gdp$ControlElement==apZone,]

	#create vectors of timestamps and GDP values
	gdp.start.time<-as.POSIXct(dat.gdp.ap$Derived.BgnDate.Time.UTC,tz="UTC")
	gdp.status<-as.factor(dat.gdp.ap$AdvisoryType)
	gdp.end.time<-as.POSIXct(dat.gdp.ap$Derived.EndDate.Time.UTC,tz="UTC")

	#output a list of these objects
	list("startTime"=gdp.start.time,
		"endTime"=gdp.end.time,
		"status"=gdp.status
		)
}

#funtion to assemble a GDP status time series (ts)
#note: leverages xts library for creating an "hourly" ts 
#between the start/end times repeating the staus for
#each hour in betweeen (see "gdpseq" helper function)

#input: gdp object created by getGDP function
#output: a single xts object (a ts)
#usage: gdpTS<-makeGDPTimeSeries(gdp)

makeGDPTimeSeries<-function(gdp){
	
	#create a list of xts objects created above
	#each entry of the list correponds to an xts object
	#and there are as many entries as there are 
	#gdp.time/gdp.end.time values (start/stop times)
	gdplist<-list()

	gdplist<-lapply(seq(length(gdp$startTime)),
					function(x){gdpseq(gdp$startTime[x],
							gdp$endTime[x],
							gdp$status[x])}
					)

	#now when we rbind to get a single time series
	do.call(rbind,gdplist)
}

#helper function
#will return a xts object filling in (by repeating)
#the gdp status for every hour between start/stop times
gdpseq<-function(beginTime,endTime,statusFactor){
	library(xts)	
	tmp<-seq(beginTime,endTime,"hour")
	xts(rep(as.factor(statusFactor),length(tmp)),tmp)
}




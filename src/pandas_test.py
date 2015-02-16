#group-by in pandas
import numpy as np
import pandas as pd

from np.random  import rand, randn



dates=pd.date_range('1/1/2015', periods=24, freq='H')
ts=pd.Series(10*rand(len(dates)) + randn(len(dates)),index=dates)
#flat averaging
ts.resample('D', how=np.mean)

#flat averaging w/group-by
grouper=pd.TimeGrouper(freq='D')
tsd=ts.groupby(grouper)
tsd.mean()


#read in cluster results
import pandas as pd
import numpy as np
import sklearn.metrics as sklm
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import glob
import os

def get_labels_features(filename):
	"""Take a csv file of cluster results
	and generate date-cluster dictionary
	Keyword arguments: 
	@filename -- string: name of cluster results csv file
	@returns -- dictionary with keys=dates, value = cluster label
	"""
	df = pd.read_csv(filename,index_col=0) #set date column to row index
	labels = df.loc[:,'cluster'].as_matrix()
	#drop the cluster column
	df.drop(labels=['cluster'],axis=1,inplace=True)
	#write out feature matrix
	features = df.as_matrix()
	return labels, features


#to compute silhoutte-score for each sample

def compute_sil_score_vector(filelist):
	"""returns dictionary indexed by num_clusters and 
	values which are vectors of silscore for all samples
	"""
	silscore = dict()
	for f in filelist:
		y, X = get_labels_features(f)
		num_clusters = np.unique(y).shape[0]
		silscore[num_clusters]= sklm.silhouette_samples(X,y)

	return silscore


	
#script to plot silhouette scores

cluster_results_dir = '/Users/ashah/NoBackup/code/nasa/results'


for airport_abbrv in ['JFK','EWR','LGA','NYRegion']:
	filelist=glob.glob(os.path.join(cluster_results_dir,airport_abbrv+'*.csv'))
	silscore = compute_sil_score_vector(filelist)
	#setup plots
	fig, ax1 = plt.subplots(1,1)
	ax1.set_ylim([-0.2,1])
	ax1.set_xlim([1,25])
	ax1.set_title("The silhouette plot for the various clusters of %s"\
	 % airport_abbrv)
	#generate num-clusters and mean-silscore
	nc,ms = zip(*[(k,v.mean()) for k,v in silscore.iteritems()])
	ax1.set_ylabel("Average silhouette coefficient")
	ax1.scatter(nc,ms, marker='.', s=60, lw=0, alpha=0.7)
	plot_filename = os.path.join(cluster_results_dir,airport_abbrv+'_expert_silscore')
	plt.savefig(plot_filename,ext='png',transparent=True)



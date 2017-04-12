import sys

if (sys.version_info > (3, 0)):
	from .priority_queue import MyPriorityQueue
	from .value_normalization_misc import SimMeasureNotSupportedException
else:
	from priority_queue import MyPriorityQueue
	from value_normalization_misc import SimMeasureNotSupportedException

from py_stringmatching.similarity_measure.jaro_winkler import JaroWinkler
from py_stringmatching.similarity_measure.levenshtein import Levenshtein
from py_stringmatching.similarity_measure.jaccard import Jaccard
from py_stringmatching.tokenizer.qgram_tokenizer import QgramTokenizer

# Class to perform hierarchical clustering on vals 
class HierarchicalClustering(object):
	_default_sim_measure_str = '3gram Jaccard'
	_default_linkage = 'single'
	_default_thr = 0.7

    
	def __init__(self, vals):
		self.vals = sorted(vals, key = lambda x: x.lower(), reverse=True)
		# Initializing acceptable parameters for linkage, string sim 
		self.show = False
		qgtok = QgramTokenizer(qval = 3, padding = True)
		jaccard_sim = Jaccard()
		Jaccard3Gram = lambda x, y: jaccard_sim.get_sim_score(qgtok.tokenize(x), qgtok.tokenize(y))
		self.str_sims = {
			'Jaro-Winkler': JaroWinkler().get_sim_score,
			'Levenshtein': Levenshtein().get_sim_score, 
			'3gram Jaccard': Jaccard3Gram
		}
		self.linkages = ['single', 'average', 'complete']

        
	def init_clustering(self):
        # This function initializes clustids from 1...no of values and updates clusts  
		# Value -> cluster id
		self.val_to_clustid_map = {}
		# Cluster id -> list of values in cluster
		self.clusts = {}
		clst_cntr = 1
		for val in self.vals:
			self.val_to_clustid_map[val] = clst_cntr
			self.clusts[clst_cntr] = [val,]
			clst_cntr += 1

            
	def get_sim_measure(self, sim_measure_str):
        # Returns corresponding str_sim function based on sim_measure_str
		if sim_measure_str in self.str_sims:
			return self.str_sims[sim_measure_str]
		else:
			raise SimMeasureNotSupportedException("Similarity measure named %s is not supported. Supported similarity measures are %s"%(sim_measure_str, str(self.str_sims.keys())))

            
	def calc_dists(self, sim_measure_str = None):
        # Returns a dictionary with key -> unordered pair of values , value -> distance between values based on sim_measure
		self.sim_measure = self.get_sim_measure(sim_measure_str if sim_measure_str is not None else HierarchicalClustering._default_sim_measure_str)
		# Unordered pair of values -> string similarity distance
		self.dists = {}
		for i in range(0, len(self.vals)):
			vi = self.vals[i]
			for j in range(i+1, len(self.vals)):
				vj = self.vals[j]
				curdist = 1. - self.sim_measure(vi, vj)
				self.dists[frozenset([vi, vj])] = curdist
		return self.dists

	def create_dendrogram(self, sim_measure = None, linkage = None, precalc_dists = None, max_clust_size = -1):
        # Returns a dendrogram which is a list of tuples-each tuple of form((merged cluster, delt cluster),distance btw clusters)
        
        # Initializations and calculate initial distances between dataset value pairs if not calculated before
		self.max_clust_size = max_clust_size if max_clust_size != -1 else len(self.vals)
		self.dend = []
		if self.max_clust_size == 1:
			return self.dend
		self.linkage = linkage if linkage is not None else HierarchicalClustering._default_linkage
		self.init_clustering()
		# Unordered pair of values -> string distance
		self.dists = precalc_dists if precalc_dists is not None else self.calc_dists(sim_measure)
        # Initialize a priority queue which always pops the task with minimum cluster distance.
		myq = MyPriorityQueue()

        # Add initial set of value pair distances to the priority queue tasks
		for i in range(0, len(self.vals)):
			vi = self.vals[i]
			for j in range(i+1, len(self.vals)):
				vj = self.vals[j]
				curdist = self.dists[frozenset([vi, vj])]
				(cidi, cidj) = tuple(sorted([self.val_to_clustid_map[vi], self.val_to_clustid_map[vj]]))
				myq.add_task((cidi, cidj), curdist)
        # Dictionary containing the blocked cluster pairs and the distances between them
		blkdpairs = {}

        #Loop through the queue until queue becomes empty or sum of sizes of the two most min clusters > maxclustsize
        #Stopping the clustering as soon as possible using above mentioned conditions
		while not myq.is_empty():
			nextclustpair = myq.pop_task()
			if ( len(self.clusts[nextclustpair[1][0]]) + len(self.clusts[nextclustpair[1][1]]) ) > self.max_clust_size:
				blkdpairs[nextclustpair[1]] = nextclustpair[0]
				continue

			# MERGE CLUSTER and add entry to dendrogram
			min_clust_size = len(self.vals)
			second_min_clust_size = len(self.vals)
			mrgd_clust_id = nextclustpair[1][0]
			mrgd_clust = self.clusts[mrgd_clust_id]
			delt_clust_id = nextclustpair[1][1]
			delt_clust = self.clusts[delt_clust_id]
			self.dend.append(((list(mrgd_clust), list(delt_clust)), nextclustpair[0]));
			mrgd_clust.extend(delt_clust)
			new_clust = mrgd_clust
            
            # Initializing minclustsize and secondminclustsize 
			if len(new_clust) < min_clust_size:
				second_min_clust_size = min_clust_size
				min_clust_size = len(new_clust)
            
            # After merging clusters, loop through all other clusters to update distances between them and the merged cluster
			for other_clust_id in self.clusts:
				if other_clust_id in [mrgd_clust_id, delt_clust_id]:
					continue

                # Pop the (otherclustid,mrgd clustid) pair from priority queue    
				(cid1, cid2) = (other_clust_id, mrgd_clust_id) if other_clust_id < mrgd_clust_id else (mrgd_clust_id, other_clust_id)
				try:
					new_dist = myq.remove_task((cid1, cid2))
				except KeyError:
					new_dist = blkdpairs[(cid1, cid2)]
                
                # Pop the (otherclustid,delt clustid) pair from priority queue
				other_link_inx = (other_clust_id, delt_clust_id) if other_clust_id < delt_clust_id else (delt_clust_id, other_clust_id)
				try:
					other_clust_dist = myq.remove_task(other_link_inx)
				except KeyError:
					other_clust_dist = blkdpairs[other_link_inx]
                
                # Update distance based on chosen linkage criteria and add the task into priority queue
				if self.linkage == 'average':
					new_dist = ( ( len(self.clusts[cid1]) * len(self.clusts[cid2]) * new_dist ) + ( len(self.clusts[other_clust_id]) * len(self.clusts[delt_clust_id]) * other_clust_dist)) / ( len(self.clusts[other_clust_id]) * ( len(self.clusts[delt_clust_id]) + len(self.clusts[mrgd_clust_id]) ) )
				elif self.linkage == 'complete':
					new_dist = max(new_dist, other_clust_dist)
				elif self.linkage == 'single':
					new_dist = min(new_dist, other_clust_dist)
                
				if (cid1, cid2) in blkdpairs:
					blkdpairs[(cid1, cid2)] = new_dist
				else:
					myq.add_task((cid1, cid2), new_dist)

                # Check if otherclust is smaller than minclustsize and update minclustsize and secondminclustsize
				if len(self.clusts[other_clust_id]) < min_clust_size:
					second_min_clust_size = min_clust_size
					min_clust_size = len(self.clusts[other_clust_id])    
				elif len(self.clusts[other_clust_id]) < second_min_clust_size:
					second_min_clust_size = len(self.clusts[other_clust_id]) 
            
            # Update clusts{} with the new merged cluster and remove delt_cluster
			self.clusts[mrgd_clust_id] = new_clust
			self.clusts.pop(delt_clust_id, None)
            
            # Stop clustering if sum of the two most minsizedclusters > maxclustsize
			if min_clust_size + second_min_clust_size > self.max_clust_size:
				break
		return self.dend

    
	def lambdahac_dendrogram(self, dend = None, thr = None):
        # Takes the dendrogram created previously in create_dendrogram function and applies the distance threshold parameter to create the val_to_clustid_map. Clustering done till clustdist <= thr 
		self.thr = thr if thr is not None else HierarchicalClustering._default_thr
		self.stop_when = lambda x: x[0] > self.thr
		if dend is not None:
			self.dend = dend
		self.init_clustering()

		for jj in range(len(self.dend)):
			((c1, c2), dist) = self.dend[jj]
			if self.stop_when((dist,)):
				break
			cc = c2
			if self.val_to_clustid_map[c1[0]] < self.val_to_clustid_map[c2[0]]:
				for vv in c2: self.val_to_clustid_map[vv] = self.val_to_clustid_map[c1[0]]
			else:
				for vv in c1: self.val_to_clustid_map[vv] = self.val_to_clustid_map[c2[0]]

		return self.val_to_clustid_map

	def lambdahac(self, sim_measure = None, linkage = None, thr = None, precalc_dists = None, max_clust_size = -1):
		self.dend = self.create_dendrogram(sim_measure, linkage, precalc_dists, max_clust_size)
		return self.lambdahac_dendrogram(self.dend, thr)

	def get_clusters(self):
        # Returns a cluster to values map from the val_to_clust_id map generated by lambdahac_dendrogram()
		clustid_to_val_map = {}
		for kk in self.val_to_clustid_map:
			if self.val_to_clustid_map[kk] not in clustid_to_val_map:
				clustid_to_val_map[self.val_to_clustid_map[kk]] = []
			clustid_to_val_map[self.val_to_clustid_map[kk]].append(kk)
		clstlst = sorted([sorted(vv) for vv in list(clustid_to_val_map.values())], key=lambda x: x[0].lower())
		res = {}
		for clst in clstlst:
			res[clst[0]] = clst
		return res

	def cluster(self, sim_measure = None, linkage = None, thr = None, precalc_dists = None):
        # Base function that calls create_dendrogram, lambdahac_dendrogram and get_clusters()
		self.create_dendrogram(sim_measure, linkage, precalc_dists, -1)
		self.lambdahac_dendrogram(self.dend, thr)
		return self.get_clusters()


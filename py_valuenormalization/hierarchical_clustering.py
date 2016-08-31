from priority_queue import MyPriorityQueue
from value_normalization_misc import SimMeasureNotSupportedException

from py_stringmatching.similarity_measure.jaro_winkler import JaroWinkler
from py_stringmatching.similarity_measure.levenshtein import Levenshtein
from py_stringmatching.similarity_measure.jaccard import Jaccard
from py_stringmatching.tokenizer.qgram_tokenizer import QgramTokenizer

class HierarchicalClustering(object):
	def __init__(self, vals):
		self.vals					= sorted(vals, reverse=True)
		# whether to show debugging info or not	
		self.show					= False

		jarowinkler_sim				= JaroWinkler()
		levenshtein_sim				= Levenshtein()
		qgtok						= QgramTokenizer(qval = 3, padding = False)
		jaccard_sim					= Jaccard()
		Jaccard3Gram				= lambda x, y: jaccard_sim.get_sim_score(qgtok.tokenize(x), qgtok.tokenize(y))

		self.str_sims				= {
			'Jaro-Winkler':		JaroWinkler().get_sim_score,
			'Levenshtein':		Levenshtein().get_sim_score, 
			'3gram Jaccard':	Jaccard3Gram
		}

		self.linkages				= ['single', 'average', 'complete']

	def init_clustering(self):
		# value -> cluster id
		self.val_to_clustid_map		= {}
		# cluster id -> list of values
		self.clusts					= {}

		clst_cntr	= 1
		for val in self.vals:
			self.val_to_clustid_map[val]		= clst_cntr
			self.clusts[clst_cntr]				= [val,]
			clst_cntr += 1

	def get_sim_measure(self, sim_measure_str):
		if sim_measure_str in self.str_sims:
			return self.str_sims[sim_measure_str]
		else:
			raise SimMeasureNotSupportedException("Similarity measure named %s is not supported. Supported similarity measures are %s"%(sim_measure_str, str(self.str_sims.keys())))

	def calc_dists(self, sim_measure_str = None):
		self.sim_measure				= self.get_sim_measure(sim_measure_str) if sim_measure_str is not None else self.get_sim_measure('jarowinkler')
		
		# unordered pair of values -> string distance
		self.dists					= {}
		for i in range(0, len(self.vals)):
			vi								= self.vals[i]
			for j in range(i+1, len(self.vals)):
				vj								= self.vals[j]
				curdist							= 1. - self.sim_measure(vi, vj)
				self.dists[frozenset([vi, vj])]	= curdist

		return self.dists

	def create_dendrogram(self, sim_measure = None, linkage = None, precalc_dists = None, max_clust_size = -1):
		self.max_clust_size		= max_clust_size if max_clust_size != -1 else len(self.vals)
		self.dend				= []
		if self.max_clust_size == 1:
			return self.dend

		self.linkage			= linkage if linkage is not None else 'single'

		self.init_clustering()
		# unordered pair of values -> string distance
		self.dists				= precalc_dists if precalc_dists is not None else self.calc_dists(sim_measure)
		# unordered pair of cluster labels -> cluster distance
		self.clust_dists		= {}
		myq						= MyPriorityQueue()

		tmp_cntr				= 0

		for i in range(0, len(self.vals)):
			tmp_cntr += 1

			vi		= self.vals[i]
			for j in range(i+1, len(self.vals)):
				vj		= self.vals[j]
				curdist										= self.dists[frozenset([vi, vj])]
				(cidi, cidj)								= tuple(sorted([self.val_to_clustid_map[vi], self.val_to_clustid_map[vj]]))
				self.clust_dists[(cidi, cidj)]				= curdist
				myq.add_task((cidi, cidj), curdist)

		blkdpairs		= {}

		while not myq.is_empty():
			nextclustpair		= myq.pop_task()

			if ( len(self.clusts[nextclustpair[1][0]]) + len(self.clusts[nextclustpair[1][1]]) ) > self.max_clust_size:
				blkdpairs[nextclustpair[1]]		= nextclustpair[0]
				continue

			### MERGE CLUSTER ###
			mrgd_clust_id		= nextclustpair[1][0]
			mrgd_clust			= self.clusts[mrgd_clust_id]
			delt_clust_id		= nextclustpair[1][1]
			delt_clust			= self.clusts[delt_clust_id]

			self.dend.append(((list(mrgd_clust), list(delt_clust)), nextclustpair[0]));

			min_clust_size		= len(self.vals)
			min_sum_clust_pair	= len(self.vals)

			mrgd_clust.extend(delt_clust)
			new_clust			= mrgd_clust

			if len(new_clust) < min_clust_size:
				min_clust_size		= len(new_clust)

			new_clust_dists		= {}
			for other_clust_id in self.clusts:
				if other_clust_id in [mrgd_clust_id, delt_clust_id]:
					continue

				(cid1, cid2)		= (other_clust_id, mrgd_clust_id) if other_clust_id < mrgd_clust_id else (mrgd_clust_id, other_clust_id)
				try:
					new_dist			= myq.remove_task((cid1, cid2))
				except KeyError:
					new_dist			= blkdpairs[(cid1, cid2)]

				other_link_inx		= (other_clust_id, delt_clust_id) if other_clust_id < delt_clust_id else (delt_clust_id, other_clust_id)
				try:
					other_clust_dist	= myq.remove_task(other_link_inx)
				except KeyError:
					other_clust_dist	= blkdpairs[other_link_inx]

				if self.linkage == 'average':		new_dist		= ( 
						( len(self.clusts[cid1]) * len(self.clusts[cid2]) * new_dist ) + 
						( len(self.clusts[other_clust_id]) * len(self.clusts[delt_clust_id]) * other_clust_dist)
						) / ( len(self.clusts[other_clust_id]) * ( len(self.clusts[delt_clust_id]) + len(self.clusts[mrgd_clust_id]) ) )
				elif self.linkage == 'complete':	new_dist		= max(new_dist, other_clust_dist)
				elif self.linkage == 'single':		new_dist		= min(new_dist, other_clust_dist)

				if (cid1, cid2) in blkdpairs:
					blkdpairs[(cid1, cid2)]		= new_dist
				else:
					myq.add_task((cid1, cid2), new_dist)

				if len(self.clusts[other_clust_id]) < min_clust_size:
					min_clust_size		= len(self.clusts[other_clust_id])
				if ( len(self.clusts[other_clust_id]) + len(new_clust_dists) ) < min_sum_clust_pair:
					min_sum_clust_pair		= ( len(self.clusts[other_clust_id]) + len(new_clust_dists) )

			self.clusts[mrgd_clust_id]		= new_clust
			self.clusts.pop(delt_clust_id, None)

			if min_clust_size >= self.max_clust_size or min_sum_clust_pair > self.max_clust_size:
				break

		return self.dend

	def lambdahac_dendrogram(self, dend = None, thr = None):
		self.thr			= thr if thr is not None else 0.7
		self.stop_when		= lambda x: x[0] > self.thr
		if dend is not None:
			self.dend			= dend

		self.init_clustering()

		for jj in range(len(self.dend)):
			((c1, c2), dist)		= self.dend[jj]
			if self.stop_when((dist,)):
				break
			cc		= c2
			if self.val_to_clustid_map[c1[0]] < self.val_to_clustid_map[c2[0]]:
				for vv in c2: self.val_to_clustid_map[vv]		= self.val_to_clustid_map[c1[0]]
				else:
					for vv in c1: self.val_to_clustid_map[vv]		= self.val_to_clustid_map[c2[0]]

		return self.val_to_clustid_map

	def lambdahac(self, sim_measure = None, linkage = None, thr = None, precalc_dists = None, max_clust_size = -1):
		self.dend		= self.create_dendrogram(sim_measure, linkage, precalc_dists, max_clust_size)
		return self.lambdahac_dendrogram(self.dend, thr)
		
	def get_clusters(self):
		clustid_to_val_map		= {}
		for kk in self.val_to_clustid_map:
			if self.val_to_clustid_map[kk] not in clustid_to_val_map:
				clustid_to_val_map[self.val_to_clustid_map[kk]]	= []
			clustid_to_val_map[self.val_to_clustid_map[kk]].append(kk)
		clstlst					= sorted([sorted(vv) for vv in list(clustid_to_val_map.values())], key=lambda x: x[0].lower())
		res						= {}
		for clst in clstlst:
			res[clst[0]]			= clst
		return res

	def hac(self, sim_measure = None, linkage = None, thr = None, precalc_dists = None):
		self.create_dendrogram(sim_measure, linkage, precalc_dists, -1)
		self.lambdahac_dendrogram(self.dend, thr)
		return self.get_clusters()


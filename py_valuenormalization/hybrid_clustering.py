import sys
from copy import deepcopy

if (sys.version_info > (3, 0)):
	from .priority_queue import MyPriorityQueue
	from .value_normalization_misc import SimMeasureNotSupportedException
	from .value_normalization_misc import Utils
	from .hierarchical_clustering import HierarchicalClustering
else:
	from priority_queue import MyPriorityQueue
	from value_normalization_misc import SimMeasureNotSupportedException
	from value_normalization_misc import Utils
	from hierarchical_clustering import HierarchicalClustering

from py_stringmatching.similarity_measure.jaro_winkler import JaroWinkler
from py_stringmatching.similarity_measure.levenshtein import Levenshtein
from py_stringmatching.similarity_measure.jaccard import Jaccard
from py_stringmatching.tokenizer.qgram_tokenizer import QgramTokenizer

class HybridClustering(HierarchicalClustering):
	def __init__(self, vals, cost_model, default_sim_measure_str = None, default_linkage = None, default_thr = None):
		super(HybridClustering, self).__init__(vals)
		self.cost_model				= cost_model
		if default_sim_measure_str is not None:
			HierarchicalClustering._default_sim_measure_str	= default_sim_measure_str
		if default_linkage is not None:
			HierarchicalClustering._default_linkage			= default_linkage
		if default_thr is not None:
			HierarchicalClustering._default_thr				= default_thr

	def shotgun_create_dendrogram(self, sim_measure_str = None, linkage = None, precalc_dists = None, thr = None, max_clust_size = -1):
		self.max_clust_size		= max_clust_size if max_clust_size != -1 else len(self.vals)
		self.dend				= []
		if self.max_clust_size == 1:
			return (self.dend_hist, self.vals, self.dists)

		self.sim_measure_str	= sim_measure_str if sim_measure_str is not None else HierarchicalClustering._default_sim_measure_str
		self.linkage			= linkage if linkage is not None else HierarchicalClustering._default_linkage
		self.thr				= thr if thr is not None else HierarchicalClustering._default_thr
		self.stop_when			= lambda x: x[0] > self.thr

		self.init_clustering()

		self.dists				= precalc_dists if precalc_dists is not None else self.calc_dists(self.sim_measure_str)
		self.clust_dists		= {}
		self.dend_hist			= {}
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

			cur_vthr						= len(self.clusts[nextclustpair[1][0]]) + len(self.clusts[nextclustpair[1][1]]) - 1
			if cur_vthr not in self.dend_hist and cur_vthr > (max(self.dend_hist.keys()) if len(self.dend_hist) > 0 else 0):
				dc_clusts						= deepcopy(self.clusts)
				dc_dend							= deepcopy(self.dend)
				dc_myq							= myq.copy_q() #deepcopy(myq)
				dc_myq.add_task(nextclustpair[1], nextclustpair[0])
				self.dend_hist[cur_vthr]				= (dc_clusts, dc_dend, dc_myq)

			if ( len(self.clusts[nextclustpair[1][0]]) + len(self.clusts[nextclustpair[1][1]]) ) > self.max_clust_size:
				blkdpairs[nextclustpair[1]]		= nextclustpair[0]
				continue

			if self.stop_when(nextclustpair):
				break

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
				else:								new_dist		= min(new_dist, other_clust_dist)

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

		cur_vthr					= max([len(clst) for clst in self.clusts.values()])
		if cur_vthr not in self.dend_hist and cur_vthr > (max(self.dend_hist.keys()) if len(self.dend_hist) > 0 else 0):
			self.dend_hist[cur_vthr]			= (deepcopy(self.clusts), deepcopy(self.dend), myq.copy_q())

		return (self.dend_hist, self.vals, self.dists)

	##################### MODIFIED UP TO HERE
	######################### CONTINUE FROM HERE ON!!!!!!!!!!!!!!!
	def shotgun_lambdahac_dendrogram(self, dend):
		self.init_clustering()

		for jj in range(len(dend)):
			((c1, c2), dist)		= dend[jj]
			if self.stop_when((dist,)):
				break
			cc		= c2
			if self.val_to_clustid_map[c1[0]] < self.val_to_clustid_map[c2[0]]:
				for vv in c2: self.val_to_clustid_map[vv]		= self.val_to_clustid_map[c1[0]]
				else:
					for vv in c1: self.val_to_clustid_map[vv]		= self.val_to_clustid_map[c2[0]]

		return self.val_to_clustid_map

	def shotgun_lambdahac_continue_from_dendrogram(self, max_clust_size):
		clszlim				= max(self.dend_hist.keys())

		self.init_clustering()

		if max_clust_size == 1 or max_clust_size >= clszlim:
			dend				= self.dend_hist[min(max_clust_size, clszlim)][1]
		else:
			mcs					= sorted(filter(lambda x: x >= max_clust_size, self.dend_hist.keys()))[0]
			dend				= self.shotgun_complete_dendrogram(max_clust_size, mcs)
		return self.shotgun_lambdahac_dendrogram(dend)
		
	def shotgun_complete_dendrogram(self, max_clust_size, mcs):
		(clusts, dend, myq)		= self.dend_hist[mcs]

		blkdpairs		= {}

		while not myq.is_empty():
			nextclustpair		= myq.pop_task()

			if ( len(clusts[nextclustpair[1][0]]) + len(clusts[nextclustpair[1][1]]) ) > max_clust_size:
				blkdpairs[nextclustpair[1]]		= nextclustpair[0]
				continue

			### MERGE CLUSTER ###
			mrgd_clust_id		= nextclustpair[1][0]
			mrgd_clust			= clusts[mrgd_clust_id]
			delt_clust_id		= nextclustpair[1][1]
			delt_clust			= clusts[delt_clust_id]

			dend.append(((list(mrgd_clust), list(delt_clust)), nextclustpair[0]));

			min_clust_size		= len(self.vals)
			min_sum_clust_pair	= len(self.vals)

			mrgd_clust.extend(delt_clust)
			new_clust			= mrgd_clust

			if len(new_clust) < min_clust_size:
				min_clust_size		= len(new_clust)

			new_clust_dists		= {}
			for other_clust_id in clusts:
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
						( len(clusts[cid1]) * len(clusts[cid2]) * new_dist ) + 
						( len(clusts[other_clust_id]) * len(clusts[delt_clust_id]) * other_clust_dist)
						) / ( len(clusts[other_clust_id]) * ( len(clusts[delt_clust_id]) + len(clusts[mrgd_clust_id]) ) )
				elif self.linkage == 'complete':	new_dist		= max(new_dist, other_clust_dist)
				else:								new_dist		= min(new_dist, other_clust_dist)

				if (cid1, cid2) in blkdpairs:
					blkdpairs[(cid1, cid2)]		= new_dist
				else:
					myq.add_task((cid1, cid2), new_dist)

				if len(clusts[other_clust_id]) < min_clust_size:
					min_clust_size		= len(clusts[other_clust_id])
				if ( len(clusts[other_clust_id]) + len(new_clust_dists) ) < min_sum_clust_pair:
					min_sum_clust_pair		= ( len(clusts[other_clust_id]) + len(new_clust_dists) )

			clusts[mrgd_clust_id]		= new_clust
			clusts.pop(delt_clust_id, None)

			if min_clust_size >= max_clust_size or min_sum_clust_pair > max_clust_size:
				break

		return dend

	def cluster(self, sim_measure = None, linkage = None, precalc_dists = None, thr = None, max_clust_size = -1):
		approx_costs		= {}
		min_cost_lambda		= None
		min_cost			= None

		self.shotgun_create_dendrogram(sim_measure, linkage, precalc_dists, thr, max_clust_size)

		max_lambda			= max(self.dend_hist.keys())

		for lambda_i in range(1, max_lambda + 1):
			self.shotgun_lambdahac_continue_from_dendrogram(lambda_i)

			clusts					= self.get_clusters()
			alpha					= Utils.alpha_lambda_WP(lambda_i, self.cost_model['purity']['aa'], self.cost_model['purity']['bb'])

			from action_cost_approx_functions import approximate_edit_cost
			stm_capacity			= 7
			mrg_chunk_topk			= 3
			default_tau0			= 0.5
			default_xi				= 0.3

			(approx_cost, 
					est_spl_cost, 
					est_mrg_cost, 
					est_slamg_cost, 
					est_scamg_cost,
					rr, fcc)							= approximate_edit_cost(
							list(clusts.values()), 
							alpha, 
							w1=stm_capacity,
							w2=mrg_chunk_topk,
							tau=default_tau0, 
							xi=default_xi,
							user=self.cost_model['user'], 
							show=False, 
							mm=len(self.vals),
							cur_lambda=lambda_i,
							f_alpha=None
						)
			if min_cost is None or min_cost > approx_cost:
				min_cost				= approx_cost
				min_cost_lambda			= lambda_i
				best_clusts				= self.get_clusters()

		return (best_clusts, min_cost_lambda)




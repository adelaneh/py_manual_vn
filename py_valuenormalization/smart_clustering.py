import sys

if (sys.version_info > (3, 0)):
	from .hierarchical_clustering import HierarchicalClustering
else:
	from hierarchical_clustering import HierarchicalClustering

class SmartClustering(HierarchicalClustering):
	def __init__(self, vals, training_pairs):
		super(SmartClustering, self).__init__(vals)
		self.training_pairs = training_pairs

	def cluster(self):
        # Initializations
		sample_vals = self.vals
		sample_size = len(sample_vals)
		clust_settings = []
		best_agrscore = 0
		best_clusts = None
		stop_ths = [0.1 * jj for jj in range(1, 11)]
        
        # Create dendrogram for each possible combination of sim_measure, linkage.
		for simk in self.str_sims:
			dists = self.calc_dists(simk)
			for lnk in self.linkages:
				dend = self.create_dendrogram(precalc_dists = dists, linkage = lnk)
                
                # Stop clustering based on different thresholds at interval of 0.1
				for thr in stop_ths:
					vtc = self.lambdahac_dendrogram(dend = dend, thr = thr)
					agrscore = self.calc_agreement_score()
                    # Evaluate and track the minimum agreement score cluster setting
					if agrscore[2] > best_agrscore:
						best_clusts = self.get_clusters()
						best_agrscore = agrscore[2]
					clust_settings.append((agrscore, simk, lnk, thr))

		sorted_clust_settings = sorted(clust_settings, key=lambda x: x[0][2])
		best_setting = sorted_clust_settings[-1]
		return (best_clusts, best_setting)
    
    # Calculates the agreement score
	def calc_agreement_score(self):
		acc, tptn = 0., 0.
		for (cm1, cm2) in self.training_pairs:
			if (self.val_to_clustid_map[cm1] == self.val_to_clustid_map[cm2]) == (self.training_pairs[(cm1, cm2)]):
				tptn += 1.
		return (tptn, len(self.training_pairs), tptn / len(self.training_pairs))


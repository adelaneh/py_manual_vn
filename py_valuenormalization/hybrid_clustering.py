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
        #Call to base class init
        super(HybridClustering, self).__init__(vals)
        self.cost_model = cost_model
        if default_sim_measure_str is not None:
            HierarchicalClustering._default_sim_measure_str = default_sim_measure_str
        if default_linkage is not None:
            HierarchicalClustering._default_linkage = default_linkage
        if default_thr is not None:
            HierarchicalClustering._default_thr = default_thr

    def shotgun_create_dendrogram(self, sim_measure_str = None, linkage = None, precalc_dists = None, thr = None, max_clust_size = -1):
        #Initializations
        self.max_clust_size = max_clust_size if max_clust_size != -1 else len(self.vals)
        self.dend = []
        self.dend_hist = {} 
        myq = MyPriorityQueue()        
        self.sim_measure_str = sim_measure_str if sim_measure_str is not None else HierarchicalClustering._default_sim_measure_str
        self.linkage = linkage if linkage is not None else HierarchicalClustering._default_linkage
        self.thr = thr if thr is not None else HierarchicalClustering._default_thr
        self.stop_when = lambda x: x[0] > self.thr
        
        self.init_clustering()
        self.dists = precalc_dists if precalc_dists is not None else self.calc_dists(self.sim_measure_str)

        
        # IF maxclustsize is 1, return empty list
        if self.max_clust_size == 1:
            return (self.dend_hist, self.vals, self.dists)
        
        blkdpairs = {}        
        # Initialize priority queue with tasks
        tmp_cntr = 0

        for i in range(0, len(self.vals)):
            tmp_cntr += 1
            vi = self.vals[i]
            for j in range(i+1, len(self.vals)):
                vj = self.vals[j]
                curdist = self.dists[frozenset([vi, vj])]
                (cidi, cidj) = tuple(sorted([self.val_to_clustid_map[vi], self.val_to_clustid_map[vj]]))
                myq.add_task((cidi, cidj), curdist)
        
        # Loop until queue is empty and append to dendrogram the new cluster
        while not myq.is_empty():
            nextclustpair = myq.pop_task()
            
            # Append the current dend, priorityqueue, clusts if the length of new cluster is greater than the cluster of max size
            cur_vthr = len(self.clusts[nextclustpair[1][0]]) + len(self.clusts[nextclustpair[1][1]]) - 1
            if cur_vthr not in self.dend_hist and cur_vthr > (max(self.dend_hist.keys()) if len(self.dend_hist) > 0 else 0):
                dc_clusts = deepcopy(self.clusts)
                dc_dend = deepcopy(self.dend)
                dc_myq = myq.copy_q() 
                dc_myq.add_task(nextclustpair[1], nextclustpair[0])
                self.dend_hist[cur_vthr] = (dc_clusts, dc_dend, dc_myq)
            
            # Add to blocked pairs if length of new cluster > maxclustsize
            if ( len(self.clusts[nextclustpair[1][0]]) + len(self.clusts[nextclustpair[1][1]]) ) > self.max_clust_size:
                blkdpairs[nextclustpair[1]] = nextclustpair[0]
                continue
            
            # Stop dendrogram if distance > threshold
            if self.stop_when(nextclustpair):
                break
            ### MERGE CLUSTER ###
            mrgd_clust_id = nextclustpair[1][0]
            mrgd_clust = self.clusts[mrgd_clust_id]
            delt_clust_id = nextclustpair[1][1]
            delt_clust = self.clusts[delt_clust_id]
            
            # Append to dendrogram next pair of clusters to be merged
            self.dend.append(((list(mrgd_clust), list(delt_clust)), nextclustpair[0]));
            
            # Maintain the sizes of least two clusters and stop clustering when sum of their sizes > maxclustsize
            min_clust_size = len(self.vals)
            min_second_clust_size = len(self.vals)
            mrgd_clust.extend(delt_clust)
            new_clust = mrgd_clust
            if len(new_clust) < min_clust_size:
                min_clust_size = len(new_clust)
                
            # Update distances of other clusters with merged cluster in the priority queue    
            for other_clust_id in self.clusts:
                if other_clust_id in [mrgd_clust_id, delt_clust_id]:
                    continue
                (cid1, cid2) = (other_clust_id, mrgd_clust_id) if other_clust_id < mrgd_clust_id else (mrgd_clust_id, other_clust_id)
                try:
                    new_dist = myq.remove_task((cid1, cid2))
                except KeyError:
                    new_dist = blkdpairs[(cid1, cid2)]

                other_link_inx = (other_clust_id, delt_clust_id) if other_clust_id < delt_clust_id else (delt_clust_id, other_clust_id)
                try:
                    other_clust_dist = myq.remove_task(other_link_inx)
                except KeyError:
                    other_clust_dist = blkdpairs[other_link_inx]

                if self.linkage == 'average': 
                    new_dist = ( ( len(self.clusts[cid1]) * len(self.clusts[cid2]) * new_dist ) + 
                        ( len(self.clusts[other_clust_id]) * len(self.clusts[delt_clust_id]) * other_clust_dist)
                        ) / ( len(self.clusts[other_clust_id]) * ( len(self.clusts[delt_clust_id]) + len(self.clusts[mrgd_clust_id]) ) )
                elif self.linkage == 'complete':
                    new_dist = max(new_dist, other_clust_dist)
                else:
                    new_dist= min(new_dist, other_clust_dist)

                if (cid1, cid2) in blkdpairs:
                    blkdpairs[(cid1, cid2)] = new_dist
                else:
                    myq.add_task((cid1, cid2), new_dist)
                
                # Update the min sized two clusters
                if len(self.clusts[other_clust_id]) < min_clust_size:
                    min_second_clust_size = min_clust_size
                    min_clust_size = len(self.clusts[other_clust_id])
                elif  len(self.clusts[other_clust_id])  < min_second_clust_size:
                    min_second_clust_size = len(self.clusts[other_clust_id])

            self.clusts[mrgd_clust_id] = new_clust
            self.clusts.pop(delt_clust_id, None)

            if (min_second_clust_size + min_clust_size) > self.max_clust_size:
                break

        cur_vthr = max([len(clst) for clst in self.clusts.values()])
        if cur_vthr not in self.dend_hist and cur_vthr > (max(self.dend_hist.keys()) if len(self.dend_hist) > 0 else 0):
            self.dend_hist[cur_vthr] = (deepcopy(self.clusts), deepcopy(self.dend), myq.copy_q())

        return (self.dend_hist, self.vals, self.dists)
    

    # Use dendrogram to merge clusters and generate the corresponding val_to_clustid_map                      
    def shotgun_lambdahac_dendrogram(self, dend):                  
        self.init_clustering()
        for jj in range(len(dend)):
            ((c1, c2), dist) = dend[jj]
            if self.stop_when((dist,)):
                break
            cc = c2
            if self.val_to_clustid_map[c1[0]] < self.val_to_clustid_map[c2[0]]:
                for vv in c2: self.val_to_clustid_map[vv] = self.val_to_clustid_map[c1[0]]
                else:
                    for vv in c1: self.val_to_clustid_map[vv] = self.val_to_clustid_map[c2[0]]
        return self.val_to_clustid_map

    
    # Takes a maxclustsize as input, then chooses a right dendrogram from dend_hist{} and returns the val_to_clustid map of the corresponding dendrogram                   
    def shotgun_lambdahac_continue_from_dendrogram(self, max_clust_size):                
        clszlim = max(self.dend_hist.keys())
        self.init_clustering()
        
        # Chooses the right dendrogram from dend_hist              
        if max_clust_size == 1 or max_clust_size >= clszlim:
            dend = self.dend_hist[min(max_clust_size, clszlim)][1]
        else:
            mcs = sorted(filter(lambda x: x >= max_clust_size, self.dend_hist.keys()))[0]
            dend = self.shotgun_complete_dendrogram(max_clust_size, mcs)
        # Return the val_to_clustid map of the dendrogram              
        return self.shotgun_lambdahac_dendrogram(dend)

    
    # Complete a dendrogram with dend_hist['maxclustsize']
    def shotgun_complete_dendrogram(self, max_clust_size, mcs):
        (clusts, dend, myq) = self.dend_hist[mcs]
        blkdpairs = {}

        while not myq.is_empty():
            nextclustpair = myq.pop_task()
            if ( len(clusts[nextclustpair[1][0]]) + len(clusts[nextclustpair[1][1]]) ) > max_clust_size:
                blkdpairs[nextclustpair[1]] = nextclustpair[0]
                continue

            ### MERGE CLUSTER ###
            mrgd_clust_id = nextclustpair[1][0]
            mrgd_clust = clusts[mrgd_clust_id]
            delt_clust_id = nextclustpair[1][1]
            delt_clust = clusts[delt_clust_id]
            
            # Append to dendrogram the next pair of clusters to be merged           
            dend.append(((list(mrgd_clust), list(delt_clust)), nextclustpair[0]));
            
            # Track the size of the two least sized clusters          
            min_clust_size = len(self.vals)

            mrgd_clust.extend(delt_clust)
            new_clust = mrgd_clust

            if len(new_clust) < min_clust_size:
                min_clust_size = len(new_clust)
            
            # Update distances between other clusters and merged cluster in priority queue
            for other_clust_id in clusts:
                if other_clust_id in [mrgd_clust_id, delt_clust_id]:
                    continue

                (cid1, cid2) = (other_clust_id, mrgd_clust_id) if other_clust_id < mrgd_clust_id else (mrgd_clust_id, other_clust_id)
                try:
                    new_dist = myq.remove_task((cid1, cid2))
                except KeyError:
                    new_dist = blkdpairs[(cid1, cid2)]

                other_link_inx = (other_clust_id, delt_clust_id) if other_clust_id < delt_clust_id else (delt_clust_id, other_clust_id)
                try:
                    other_clust_dist = myq.remove_task(other_link_inx)
                except KeyError:
                    other_clust_dist = blkdpairs[other_link_inx]

                if self.linkage == 'average': 
                    new_dist = ( 
                        ( len(clusts[cid1]) * len(clusts[cid2]) * new_dist ) + 
                        ( len(clusts[other_clust_id]) * len(clusts[delt_clust_id]) * other_clust_dist)
                        ) / ( len(clusts[other_clust_id]) * ( len(clusts[delt_clust_id]) + len(clusts[mrgd_clust_id]) ) )
                elif self.linkage == 'complete':
                    new_dist = max(new_dist, other_clust_dist)
                else:
                    new_dist = min(new_dist, other_clust_dist)
                    
                if (cid1, cid2) in blkdpairs:
                    blkdpairs[(cid1, cid2)] = new_dist
                else:
                    myq.add_task((cid1, cid2), new_dist)

                if len(clusts[other_clust_id]) < min_clust_size:
                    min_clust_size = len(clusts[other_clust_id])

            clusts[mrgd_clust_id] = new_clust
            clusts.pop(delt_clust_id, None)

            if min_clust_size >= max_clust_size:
                break

        return dend

    
    def cluster(self, sim_measure = None, linkage = None, precalc_dists = None, thr = None, max_clust_size = -1):
        approx_costs = {}
        min_cost_lambda = None
        min_cost = None
        
        # Create dend_hist{} with list of dendrograms for different maxclustsize
        self.shotgun_create_dendrogram(sim_measure, linkage, precalc_dists, thr, max_clust_size)

        # Loop from 1 to max(dend_hist.keys()) and find the clustering with minimum cost
        max_lambda = max(self.dend_hist.keys()) if len(self.dend_hist) > 0 else 0
        best_clusts = self.get_clusters()
        min_cost_lambda = 1
        for lambda_i in range(1, max_lambda + 1):
            # Complete the dendrogram for each maxclustsize from 1 to max(dend_hist.keys())
            self.shotgun_lambdahac_continue_from_dendrogram(lambda_i)

            clusts = self.get_clusters()
            alpha = Utils.alpha_lambda_WP(lambda_i, self.cost_model['purity']['aa'], self.cost_model['purity']['bb'])
            
            # Calculate merge, split costs associated with the current clustering
            from action_cost_approx_functions import approximate_edit_cost
            stm_capacity = 7
            mrg_chunk_topk = 3
            default_tau0 = 0.5
            default_xi = 0.3

            (approx_cost, 
                    est_spl_cost, 
                    est_mrg_cost, 
                    est_slamg_cost, 
                    est_scamg_cost,
                    rr, fcc) = approximate_edit_cost(
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
            
            # Track minimum cost and get the best clustering setting
            if min_cost is None or min_cost > approx_cost:
                min_cost = approx_cost
                min_cost_lambda = lambda_i
                best_clusts = self.get_clusters()

        return (best_clusts, min_cost_lambda)

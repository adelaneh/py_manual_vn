import unittest

from nose.tools import *

from py_valuenormalization import MyPriorityQueue
from py_valuenormalization import HierarchicalClustering
from py_valuenormalization import HybridClustering
from py_valuenormalization import SimMeasureNotSupportedException
from py_valuenormalization.value_normalization_misc import Utils

class HybridClusteringTests(unittest.TestCase):
    def setUp(self):
        self.vals = ['Haldis restaurant', 'Haldis cafe', 'Indian cuisine', 'India house', 'Bombay bazaar', 'Tulsi', 'Amber restaurant']
        self.vals2 = ['Panasonic', 'Pioneer', 'Ultrasone', 'Sony', 'Audeze', 'Beats', '66Audio', 'Soundpeats', 'Soundintone']
        self.vals3 = ['Apple Incorporated', 'Apple', 'Apple Inc', 'Amazon', 'Juniper Networks', 'Mathworks', 'Matlab', 'Cisco Networks', 'A10 networks', 'Zendesk', 'Zenith']
        self.vals4 = ['Raghu', 'Ram', 'John', 'Johnson', 'Sorenson', 'Sorensen']
        self.vals5 = ['University of Washington', 'UW', 'University of California', 'University of Southern California', 'UM ann arbor', 'University of Arizona', 'Arizona State University']
        self.val_to_clustid_map = {}
        self.costmodel = Utils.get_default_cost_model()
    
    def test_vals3(self):
        self.hybhac = HybridClustering(self.vals3, self.costmodel)
        
        self.dists = self.hybhac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(self.dists.values()), 0.590909090)
        
        #testcase to check with default settings -> sim_measure - 3gram Jaccard, thr = 0.7, linkage = single, max_clust_size = length(inputs)
        dend_hist = self.hybhac.shotgun_create_dendrogram()
        
        self.assertEqual(dend_hist[0][1][0], {1: ['Zenith'],
 2: ['Zendesk'],
 3: ['Matlab'],
 4: ['Mathworks'],
 5: ['Juniper Networks'],
 6: ['Cisco Networks'],
 7: ['Apple Incorporated'],
 8: ['Apple Inc'],
 9: ['Apple'],
 10: ['Amazon'],
 11: ['A10 networks']})      
        self.assertEqual(dend_hist[0][1][1], [])
        
        self.assertEqual(dend_hist[0][2][0], {1: ['Zenith'],
 2: ['Zendesk'],
 3: ['Matlab'],
 4: ['Mathworks'],
 5: ['Juniper Networks'],
 6: ['Cisco Networks'],
 7: ['Apple Incorporated', 'Apple Inc'],
 9: ['Apple'],
 10: ['Amazon'],
 11: ['A10 networks']})
        self.assertEqual(dend_hist[0][2][1], [((['Apple Incorporated'], ['Apple Inc']), 0.5909090909090908)])
        
        self.assertEqual(dend_hist[0][3][0], {1: ['Zenith'],
 2: ['Zendesk'],
 3: ['Matlab'],
 4: ['Mathworks'],
 5: ['Juniper Networks', 'Cisco Networks', 'A10 networks'],
 7: ['Apple Incorporated', 'Apple Inc', 'Apple'],
 10: ['Amazon']})
        self.assertEqual(dend_hist[0][3][1], [((['Apple Incorporated'], ['Apple Inc']), 0.5909090909090908),
 ((['Apple Incorporated', 'Apple Inc'], ['Apple']), 0.6153846153846154),
 ((['Juniper Networks'], ['Cisco Networks']), 0.64),
 ((['Juniper Networks', 'Cisco Networks'], ['A10 networks']),
  0.6956521739130435)])
        
        
        #checking continue_from_dendrogram for all maxclustsizes from 1 to max of dend_hist
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(1)
        self.assertEqual(valmap, {'A10 networks': 11,
 'Amazon': 10,
 'Apple': 9,
 'Apple Inc': 8,
 'Apple Incorporated': 7,
 'Cisco Networks': 6,
 'Juniper Networks': 5,
 'Mathworks': 4,
 'Matlab': 3,
 'Zendesk': 2,
 'Zenith': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(2)
        self.assertEqual(valmap, {'A10 networks': 11,
 'Amazon': 10,
 'Apple': 9,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 5,
 'Juniper Networks': 5,
 'Mathworks': 4,
 'Matlab': 3,
 'Zendesk': 2,
 'Zenith': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(3)
        self.assertEqual(valmap, {'A10 networks': 5,
 'Amazon': 10,
 'Apple': 7,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 5,
 'Juniper Networks': 5,
 'Mathworks': 4,
 'Matlab': 3,
 'Zendesk': 2,
 'Zenith': 1})
        
        ##testcase to check the best clusters returned
        (clusters, maxclustsize) = self.hybhac.cluster()
        self.assertEqual(clusters, {'A10 networks': ['A10 networks', 'Cisco Networks', 'Juniper Networks'],
 'Amazon': ['Amazon'],
 'Apple': ['Apple', 'Apple Inc', 'Apple Incorporated'],
 'Mathworks': ['Mathworks'],
 'Matlab': ['Matlab'],
 'Zendesk': ['Zendesk'],
 'Zenith': ['Zenith']})
        
        self.assertEqual(maxclustsize, 3)
        
        
    def test_vals(self):
        self.hybhac = HybridClustering(self.vals, self.costmodel)
        
        self.dists = self.hybhac.calc_dists('Jaro-Winkler')
        self.assertAlmostEqual(min(self.dists.values()), 0.1077922077)
        
        #testcase to check with  sim_measure - Jaro Winkler, thr = 0.5, linkage = single, max_clust_size = 5
        dend_hist = self.hybhac.shotgun_create_dendrogram(sim_measure_str = 'Jaro-Winkler', thr = 0.5, max_clust_size = 5)
        
        self.assertEqual(dend_hist[0][1][0], {1: ['Tulsi'],
 2: ['Indian cuisine'],
 3: ['India house'],
 4: ['Haldis restaurant'],
 5: ['Haldis cafe'],
 6: ['Bombay bazaar'],
 7: ['Amber restaurant']})      
        self.assertEqual(dend_hist[0][1][1], [])
        
        self.assertEqual(dend_hist[0][2][0], {1: ['Tulsi'],
 2: ['Indian cuisine', 'India house'],
 4: ['Haldis restaurant', 'Haldis cafe'],
 6: ['Bombay bazaar'],
 7: ['Amber restaurant']})
        self.assertEqual(dend_hist[0][2][1], [((['Indian cuisine'], ['India house']), 0.10779220779220777),
 ((['Haldis restaurant'], ['Haldis cafe']), 0.15270350564468216)])
        
        self.assertEqual(dend_hist[0][4][0], {1: ['Tulsi'],
 2: ['Indian cuisine', 'India house'],
 4: ['Haldis restaurant', 'Haldis cafe', 'Amber restaurant'],
 6: ['Bombay bazaar']})
        self.assertEqual(dend_hist[0][4][1], [((['Indian cuisine'], ['India house']), 0.10779220779220777),
 ((['Haldis restaurant'], ['Haldis cafe']), 0.15270350564468216),
 ((['Haldis restaurant', 'Haldis cafe'], ['Amber restaurant']),
  0.3430258467023174)])
        
        self.assertEqual(dend_hist[0][5][0], {1: ['Tulsi'],
 2: ['Indian cuisine',
  'India house',
  'Haldis restaurant',
  'Haldis cafe',
  'Amber restaurant'],
 6: ['Bombay bazaar']})
        self.assertEqual(dend_hist[0][5][1], [((['Indian cuisine'], ['India house']), 0.10779220779220777),
 ((['Haldis restaurant'], ['Haldis cafe']), 0.15270350564468216),
 ((['Haldis restaurant', 'Haldis cafe'], ['Amber restaurant']),
  0.3430258467023174),
 ((['Indian cuisine', 'India house'],
   ['Haldis restaurant', 'Haldis cafe', 'Amber restaurant']),
  0.41414141414141425)])
           
        
        #checking continue_from_dendrogram for all maxclustsizes from 1 to max of dend_hist
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(1)
        self.assertEqual(valmap, {'Amber restaurant': 7,
 'Bombay bazaar': 6,
 'Haldis cafe': 5,
 'Haldis restaurant': 4,
 'India house': 3,
 'Indian cuisine': 2,
 'Tulsi': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(2)
        self.assertEqual(valmap, {'Amber restaurant': 6,
 'Bombay bazaar': 6,
 'Haldis cafe': 4,
 'Haldis restaurant': 4,
 'India house': 2,
 'Indian cuisine': 2,
 'Tulsi': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(3)
        self.assertEqual(valmap, {'Amber restaurant': 4,
 'Bombay bazaar': 6,
 'Haldis cafe': 4,
 'Haldis restaurant': 4,
 'India house': 2,
 'Indian cuisine': 2,
 'Tulsi': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(4)
        self.assertEqual(valmap, {'Amber restaurant': 4,
 'Bombay bazaar': 6,
 'Haldis cafe': 4,
 'Haldis restaurant': 4,
 'India house': 2,
 'Indian cuisine': 2,
 'Tulsi': 1})
        
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(5)
        self.assertEqual(valmap, {'Amber restaurant': 2,
 'Bombay bazaar': 6,
 'Haldis cafe': 2,
 'Haldis restaurant': 2,
 'India house': 2,
 'Indian cuisine': 2,
 'Tulsi': 1})
        
        ##testcase to check the best clusters returned
        (clusters, maxclustsize) = self.hybhac.cluster(sim_measure = 'Jaro-Winkler', thr = 0.5, max_clust_size = 5)
        self.assertEqual(clusters, {'Amber restaurant': ['Amber restaurant',
  'Haldis cafe',
  'Haldis restaurant',
  'India house',
  'Indian cuisine'],
 'Bombay bazaar': ['Bombay bazaar'],
 'Tulsi': ['Tulsi']})
        
        self.assertEqual(maxclustsize, 5)
        
        
        
    def test_vals2(self):
        self.hybhac = HybridClustering(self.vals2, self.costmodel)
        
        self.dists = self.hybhac.calc_dists('Levenshtein')
        self.assertAlmostEqual(min(self.dists.values()), 0.5454545454545)
        
        #testcase to check with  sim_measure - Levenshtein, thr = 0.75, linkage = single, max_clust_size = 7
        dend_hist = self.hybhac.shotgun_create_dendrogram(sim_measure_str = 'Levenshtein', thr = 0.75, max_clust_size = 7)
        
        self.assertEqual(dend_hist[0][1][0], {1: ['Ultrasone'],
 2: ['Soundpeats'],
 3: ['Soundintone'],
 4: ['Sony'],
 5: ['Pioneer'],
 6: ['Panasonic'],
 7: ['Beats'],
 8: ['Audeze'],
 9: ['66Audio']})      
        self.assertEqual(dend_hist[0][1][1], [])
        
        
        self.assertEqual(dend_hist[0][2][0], {1: ['Ultrasone'],
 2: ['Soundpeats', 'Soundintone'],
 4: ['Sony'],
 5: ['Pioneer'],
 6: ['Panasonic'],
 7: ['Beats'],
 8: ['Audeze'],
 9: ['66Audio']})
        self.assertEqual(dend_hist[0][2][1], [((['Soundpeats'], ['Soundintone']), 0.5454545454545454)])
        
        
        self.assertEqual(dend_hist[0][3][0], {1: ['Ultrasone', 'Panasonic'],
 2: ['Soundpeats', 'Soundintone', 'Beats'],
 4: ['Sony'],
 5: ['Pioneer'],
 8: ['Audeze'],
 9: ['66Audio']})
        self.assertEqual(dend_hist[0][3][1], [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Soundpeats', 'Soundintone'], ['Beats']), 0.6),
 ((['Ultrasone'], ['Panasonic']), 0.6666666666666666)])
        
        
        self.assertEqual(dend_hist[0][4][0], {1: ['Ultrasone', 'Panasonic'],
 2: ['Soundpeats', 'Soundintone', 'Beats', 'Sony'],
 5: ['Pioneer'],
 8: ['Audeze'],
 9: ['66Audio']})
        self.assertEqual(dend_hist[0][4][1], [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Soundpeats', 'Soundintone'], ['Beats']), 0.6),
 ((['Ultrasone'], ['Panasonic']), 0.6666666666666666),
 ((['Soundpeats', 'Soundintone', 'Beats'], ['Sony']), 0.7)])
        
        
        self.assertEqual(dend_hist[0][5][0], {1: ['Ultrasone', 'Panasonic'],
 2: ['Soundpeats', 'Soundintone', 'Beats', 'Sony', 'Audeze'],
 5: ['Pioneer'],
 9: ['66Audio']})
        self.assertEqual(dend_hist[0][5][1], [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Soundpeats', 'Soundintone'], ['Beats']), 0.6),
 ((['Ultrasone'], ['Panasonic']), 0.6666666666666666),
 ((['Soundpeats', 'Soundintone', 'Beats'], ['Sony']), 0.7),
 ((['Soundpeats', 'Soundintone', 'Beats', 'Sony'], ['Audeze']), 0.7)])
        
        
        self.assertEqual(dend_hist[0][6][0], {1: ['Ultrasone', 'Panasonic'],
 2: ['Soundpeats', 'Soundintone', 'Beats', 'Sony', 'Audeze', 'Pioneer'],
 9: ['66Audio']})
        self.assertEqual(dend_hist[0][6][1], [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Soundpeats', 'Soundintone'], ['Beats']), 0.6),
 ((['Ultrasone'], ['Panasonic']), 0.6666666666666666),
 ((['Soundpeats', 'Soundintone', 'Beats'], ['Sony']), 0.7),
 ((['Soundpeats', 'Soundintone', 'Beats', 'Sony'], ['Audeze']), 0.7),
 ((['Soundpeats', 'Soundintone', 'Beats', 'Sony', 'Audeze'], ['Pioneer']),
  0.7142857142857143)])
        
        
        
           
        
        #checking continue_from_dendrogram for all maxclustsizes from 1 to max of dend_hist
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(1)
        self.assertEqual(valmap, {'66Audio': 9,
 'Audeze': 8,
 'Beats': 7,
 'Panasonic': 6,
 'Pioneer': 5,
 'Sony': 4,
 'Soundintone': 3,
 'Soundpeats': 2,
 'Ultrasone': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(2)
        self.assertEqual(valmap, {'66Audio': 8,
 'Audeze': 8,
 'Beats': 7,
 'Panasonic': 1,
 'Pioneer': 4,
 'Sony': 4,
 'Soundintone': 2,
 'Soundpeats': 2,
 'Ultrasone': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(3)
        self.assertEqual(valmap, {'66Audio': 8,
 'Audeze': 8,
 'Beats': 2,
 'Panasonic': 1,
 'Pioneer': 4,
 'Sony': 4,
 'Soundintone': 2,
 'Soundpeats': 2,
 'Ultrasone': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(4)
        self.assertEqual(valmap, {'66Audio': 8,
 'Audeze': 8,
 'Beats': 2,
 'Panasonic': 1,
 'Pioneer': 5,
 'Sony': 2,
 'Soundintone': 2,
 'Soundpeats': 2,
 'Ultrasone': 1})
        
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(5)
        self.assertEqual(valmap, {'66Audio': 9,
 'Audeze': 2,
 'Beats': 2,
 'Panasonic': 1,
 'Pioneer': 5,
 'Sony': 2,
 'Soundintone': 2,
 'Soundpeats': 2,
 'Ultrasone': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(6)
        self.assertEqual(valmap, {'66Audio': 9,
 'Audeze': 2,
 'Beats': 2,
 'Panasonic': 1,
 'Pioneer': 2,
 'Sony': 2,
 'Soundintone': 2,
 'Soundpeats': 2,
 'Ultrasone': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(7)
        self.assertEqual(valmap, {'66Audio': 2,
 'Audeze': 2,
 'Beats': 2,
 'Panasonic': 1,
 'Pioneer': 2,
 'Sony': 2,
 'Soundintone': 2,
 'Soundpeats': 2,
 'Ultrasone': 1})
        

        
        ##testcase to check the best clusters returned
        (clusters, maxclustsize) = self.hybhac.cluster(sim_measure = 'Levenshtein', thr = 0.75, max_clust_size = 7)
        self.assertEqual(clusters, {'66Audio': ['66Audio', 'Audeze'],
 'Beats': ['Beats', 'Soundintone', 'Soundpeats'],
 'Panasonic': ['Panasonic', 'Ultrasone'],
 'Pioneer': ['Pioneer', 'Sony']} )
        
        self.assertEqual(maxclustsize, 3) 
        
    
    
    def test_vals4(self):
        self.hybhac = HybridClustering(self.vals4, self.costmodel)
        
        self.dists = self.hybhac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(self.dists.values()), 0.4615384615)
        
        #testcase to check with  sim_measure - 3gram Jaccard, thr = 0.75, linkage = complete, max_clust_size = 5
        dend_hist = self.hybhac.shotgun_create_dendrogram(sim_measure_str = '3gram Jaccard', thr = 0.8, max_clust_size = 7, linkage = 'complete')
        
        self.assertEqual(dend_hist[0][1][0], {1: ['Sorenson'],
 2: ['Sorensen'],
 3: ['Ram'],
 4: ['Raghu'],
 5: ['Johnson'],
 6: ['John']})      
        self.assertEqual(dend_hist[0][1][1], [])
        
        
        self.assertEqual(dend_hist[0][3][0], {1: ['Sorenson', 'Sorensen'], 3: ['Ram', 'Raghu'], 5: ['Johnson', 'John']})
        self.assertEqual(dend_hist[0][3][1], [((['Sorenson'], ['Sorensen']), 0.46153846153846156),
 ((['Johnson'], ['John']), 0.5),
 ((['Ram'], ['Raghu']), 0.8)])
          
        
           
        
        #checking continue_from_dendrogram for all maxclustsizes from 1 to max of dend_hist
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(1)
        self.assertEqual(valmap, {'John': 6, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 2, 'Sorenson': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(2)
        self.assertEqual(valmap, {'John': 5, 'Johnson': 5, 'Raghu': 3, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(3)
        self.assertEqual(valmap, {'John': 5, 'Johnson': 5, 'Raghu': 3, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})
        
        
        
        ##testcase to check the best clusters returned
        (clusters, maxclustsize) = self.hybhac.cluster(sim_measure = '3gram Jaccard', thr = 0.8, max_clust_size = 7, linkage = 'complete')
        self.assertEqual(clusters, {'John': ['John', 'Johnson'],
 'Raghu': ['Raghu', 'Ram'],
 'Sorensen': ['Sorensen', 'Sorenson']} )
        
        self.assertEqual(maxclustsize, 2)
        
        
        
        
        
    def test_vals5(self):
        self.hybhac = HybridClustering(self.vals5, self.costmodel)
        
        self.dists = self.hybhac.calc_dists('Jaro-Winkler')
        self.assertAlmostEqual(min(self.dists.values()), 0.0712406015)
        
        #testcase to check with  sim_measure - Jaro-Winkler, thr = 0.4, linkage = average, max_clust_size = 4
        dend_hist = self.hybhac.shotgun_create_dendrogram(sim_measure_str = 'Jaro-Winkler', thr = 0.4, max_clust_size = 4, linkage = 'average')
        
        self.assertEqual(dend_hist[0][1][0], {1: ['UW'],
 2: ['University of Washington'],
 3: ['University of Southern California'],
 4: ['University of California'],
 5: ['University of Arizona'],
 6: ['UM ann arbor'],
 7: ['Arizona State University']})      
        self.assertEqual(dend_hist[0][1][1], [])
        
        
        self.assertEqual(dend_hist[0][2][0], {1: ['UW'],
 2: ['University of Washington'],
 3: ['University of Southern California'],
 4: ['University of California', 'University of Arizona'],
 6: ['UM ann arbor'],
 7: ['Arizona State University']})
        self.assertEqual(dend_hist[0][2][1], [((['University of California'], ['University of Arizona']),
  0.07124060150375944)])
        
        
        self.assertEqual(dend_hist[0][3][0], {1: ['UW'],
 2: ['University of Washington'],
 3: ['University of Southern California',
  'University of California',
  'University of Arizona'],
 6: ['UM ann arbor'],
 7: ['Arizona State University']})
        self.assertEqual(dend_hist[0][3][1], [((['University of California'], ['University of Arizona']),
  0.07124060150375944),
 ((['University of Southern California'],
   ['University of California', 'University of Arizona']),
  0.10023543707754234)])
        
        
        self.assertEqual(dend_hist[0][5][0], {1: ['UW'],
 2: ['University of Washington',
  'University of Southern California',
  'University of California',
  'University of Arizona'],
 6: ['UM ann arbor', 'Arizona State University']})
        self.assertEqual(dend_hist[0][5][1], [((['University of California'], ['University of Arizona']),
  0.07124060150375944),
 ((['University of Southern California'],
   ['University of California', 'University of Arizona']),
  0.10023543707754234),
 ((['University of Washington'],
   ['University of Southern California',
    'University of California',
    'University of Arizona']),
  0.1116522366522367),
 ((['UM ann arbor'], ['Arizona State University']), 0.3657407407407408)])
        
        
           
        
        #checking continue_from_dendrogram for all maxclustsizes from 1 to max of dend_hist
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(1)
        self.assertEqual(valmap, {'Arizona State University': 7,
 'UM ann arbor': 6,
 'UW': 1,
 'University of Arizona': 5,
 'University of California': 4,
 'University of Southern California': 3,
 'University of Washington': 2})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(2)
        self.assertEqual(valmap, {'Arizona State University': 6,
 'UM ann arbor': 6,
 'UW': 1,
 'University of Arizona': 4,
 'University of California': 4,
 'University of Southern California': 2,
 'University of Washington': 2})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(3)
        self.assertEqual(valmap, {'Arizona State University': 6,
 'UM ann arbor': 6,
 'UW': 1,
 'University of Arizona': 3,
 'University of California': 3,
 'University of Southern California': 3,
 'University of Washington': 2})
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(4)
        self.assertEqual(valmap, {'Arizona State University': 6,
 'UM ann arbor': 6,
 'UW': 1,
 'University of Arizona': 2,
 'University of California': 2,
 'University of Southern California': 2,
 'University of Washington': 2})
        
        
        valmap = self.hybhac.shotgun_lambdahac_continue_from_dendrogram(5)
        self.assertEqual(valmap, {'Arizona State University': 6,
 'UM ann arbor': 6,
 'UW': 1,
 'University of Arizona': 2,
 'University of California': 2,
 'University of Southern California': 2,
 'University of Washington': 2})
        
        
        
        ##testcase to check the best clusters returned
        (clusters, maxclustsize) = self.hybhac.cluster(sim_measure = 'Jaro-Winkler', thr = 0.4, max_clust_size = 4, linkage = 'average')
        self.assertEqual(clusters, {'Arizona State University': ['Arizona State University', 'UM ann arbor'],
 'UW': ['UW'],
 'University of Arizona': ['University of Arizona',
  'University of California',
  'University of Southern California',
  'University of Washington']} )
        
        self.assertEqual(maxclustsize, 4)
        
        
import unittest

from nose.tools import *

from py_valuenormalization import MyPriorityQueue
from py_valuenormalization import HierarchicalClustering
from py_valuenormalization import SimMeasureNotSupportedException

""" We have a total of six testcases written as functions of HierarchicalClusteringTests class.
Each testcase function operates on different set of input values and different linkage, sim measure.

Under every testcase function, these are the tests covered,
Calculate distances between all value pairs and assert for min distance value pair.
Create dendrogram for different maxclustsize values and assert the dendrogram value. 
For each dendrogram created in previous test, we get the valtoclustidmap based on various thresholds and assert on  the value of valtoclustidmap.
Threshold is typically decided after looking at the dendrogram and deciding upto which distance value , we would like to cluster.
There is also a direct cluster() test on the values which needs to return expected cluster values.

Overview: 
    (<Test_function_name> - Operating Dataset, Linkage, Sim_measure )
    test_sample() - dataset: vals , linkage:single , sim_measure: Jaccard
    test_brands_single() - dataset: vals2, linkage:single , sim_measure: Jaccard
    test_firms_complete() - dataset: vals3, linkage:complete , sim_measure: Jaccard 
    test_names_average() - dataset: vals4, linkage:average , sim_measure: Jaccard 
    test_venues_average_jarowinkler() - dataset: vals5, linkage:average , sim_measure: jaro-winkler
    test_big10_average_levenshtein() - dataset: vals6, linkage:average , sim_measure: Levenshtein

Details:
    test_sample():
        Calculate distances between each pair of values in dataset and assert for minimum value pair.
        Create dendrogram with maxclustsize = 3 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7, 0.6, 1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 2 and assert dendrogram value.        
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value. 
        Create dendrogram with maxclustsize = 1 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value.     

    test_brands_single():
        Calculate distances between each pair of values in dataset and assert for minimum value pair.
        Create dendrogram with maxclustsize = 13 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.6,0.9,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 3 and assert dendrogram value.        
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value. 
        Create dendrogram with maxclustsize = 6 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value. 
        Create dendrogram with maxclustsize = 5 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,1.0 and asserting on the values.
        Create dendrogram with maxclustsize = 1 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value.
            
    test_firms_complete():
        Calculate distances between each pair of values in dataset and assert for minimum value pair.
        Create dendrogram with maxclustsize = 11 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.6,0.9,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 7 and assert dendrogram value.        
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.4,0.8,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 3 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,1.0 and asserting on the values.
            
    test_names_average():
        Calculate distances between each pair of values in dataset and assert for minimum value pair.
        Create dendrogram with maxclustsize = 6 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.9,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 4 and assert dendrogram value.        
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.5,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 3 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,1.0,0.4 and asserting on the values. 
        Create dendrogram with maxclustsize = 1 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7 and asserting on the value.
    
    test_venues_average_jarowinkler():
        Calculate distances between each pair of values in dataset and assert for minimum value pair.
        Create dendrogram with maxclustsize = 7 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.4,0.3 and asserting on the values. 
        Create dendrogram with maxclustsize = 4 and assert dendrogram value.        
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.3,0.05,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 2 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.3,0.7,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 1 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value.
    
    test_big10_average_levenshtein():
        Calculate distances between each pair of values in dataset and assert for minimum value pair.
        Create dendrogram with maxclustsize = 7 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,0.5,0.8 and asserting on the values. 
        Create dendrogram with maxclustsize = 4 and assert dendrogram value.        
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.7,1.0 and asserting on the values. 
        Create dendrogram with maxclustsize = 2 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 0.6,0.7 and asserting on the values. 
        Create dendrogram with maxclustsize = 1 and assert dendrogram value.
            Creating valtoclustidmap using dendrogram in above step with thresholds 1.0 and asserting on the value.
    """

class HierarchicalClusteringTests(unittest.TestCase):
    def setUp(self):
        self.vals = ['wisconsin','wisc','university']
        self.vals2 = ['Arrow Shed', 'Arrow','Arta','Arte italica','cooper cooler','cooper caseys','caseys','florida','floris','heineken','highland','metra','metro']
        self.vals3 = ['Apple Incorporated', 'Apple', 'Apple Inc', 'Amazon', 'Juniper Networks', 'Mathworks', 'Matlab', 'Cisco Networks', 'A10 networks', 'Zendesk', 'Zenith']
        self.vals4 = ['Raghu', 'Ram', 'John', 'Johnson', 'Sorenson', 'Sorensen']
        self.vals5 = ['Dept of computersciences', 'Computer sciences department', 'Johnson street', 'Johnson st', 'Wall street', 'Univ avenue', 'University of wisc madison']
        self.vals6 = ['University of wisc madison', 'Michigan st', 'Michigan ann arbor', 'UW Madison', 'UM ann arbor', 'UW', 'UNL']
        self.val_to_clustid_map = {}
    
    def test_sample(self):
        self.hac = HierarchicalClustering(self.vals)
        
        ### testcase to check the distances between value pairs
        self.dists = self.hac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(self.dists.values()), 0.69230769)
        
                          
        ### testcase to check create_dendrogram with maxclustsize = total no of inputs(3)
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 3)
        self.assertEqual(dend, [((['wisconsin'], ['wisc']), 0.6923076923076923),
 ((['wisconsin', 'wisc'], ['university']), 1.0)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'university': 3, 'wisc': 1, 'wisconsin': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.6)
        self.assertEqual(self.val_to_clustid_map, {'university': 3, 'wisc': 2, 'wisconsin': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'university': 1, 'wisc': 1, 'wisconsin': 1})
        
        
            
            
        ### testcase to check create_dendrogram with maxclustsize = 2
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 2)
        self.assertEqual(dend, [((['wisconsin'], ['wisc']), 0.6923076923076923)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'university': 3, 'wisc': 1, 'wisconsin': 1})
            
            
            
            
        ### testcase to check create_dendrogram with maxclustsize = 1
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 1)
        self.assertEqual(dend, [])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'university': 3, 'wisc': 2, 'wisconsin': 1})
        
        
     
        
    def test_brands_single(self):
        self.hac = HierarchicalClustering(self.vals2)

       
        ### testcase to check the distances calculated
        self.dists = self.hac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(self.dists.values()), 0.5625)
        
                          
        ### testcase to check create_dendrogram with maxclustsize = total no of inputs(13)
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 13)
        self.assertEqual(dend, [((['cooper caseys'], ['caseys']), 0.5625),
 ((['floris'], ['florida']), 0.5833333333333333),
 ((['metro'], ['metra']), 0.6),
 ((['cooper cooler'], ['cooper caseys', 'caseys']), 0.6190476190476191),
 ((['Arrow Shed'], ['Arrow']), 0.6428571428571428),
 ((['Arte italica'], ['Arta']), 0.75),
 ((['Arte italica', 'Arta'], ['Arrow Shed', 'Arrow']), 0.8181818181818181),
 ((['metro', 'metra'], ['Arte italica', 'Arta', 'Arrow Shed', 'Arrow']),
  0.9166666666666666),
 ((['metro', 'metra', 'Arte italica', 'Arta', 'Arrow Shed', 'Arrow'],
   ['floris', 'florida']),
  0.9285714285714286),
 ((['metro',
    'metra',
    'Arte italica',
    'Arta',
    'Arrow Shed',
    'Arrow',
    'floris',
    'florida'],
   ['cooper cooler', 'cooper caseys', 'caseys']),
  0.9333333333333333),
 ((['highland'], ['heineken']), 0.9473684210526316),
 ((['metro',
    'metra',
    'Arte italica',
    'Arta',
    'Arrow Shed',
    'Arrow',
    'floris',
    'florida',
    'cooper cooler',
    'cooper caseys',
    'caseys'],
   ['highland', 'heineken']),
  0.9523809523809523)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 12,
 'Arrow Shed': 12,
 'Arta': 11,
 'Arte italica': 10,
 'caseys': 7,
 'cooper caseys': 7,
 'cooper cooler': 7,
 'florida': 5,
 'floris': 5,
 'heineken': 4,
 'highland': 3,
 'metra': 1,
 'metro': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.6)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 13,
 'Arrow Shed': 12,
 'Arta': 11,
 'Arte italica': 10,
 'caseys': 8,
 'cooper caseys': 8,
 'cooper cooler': 7,
 'florida': 5,
 'floris': 5,
 'heineken': 4,
 'highland': 3,
 'metra': 1,
 'metro': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.9)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 10,
 'Arrow Shed': 10,
 'Arta': 10,
 'Arte italica': 10,
 'caseys': 7,
 'cooper caseys': 7,
 'cooper cooler': 7,
 'florida': 5,
 'floris': 5,
 'heineken': 4,
 'highland': 3,
 'metra': 1,
 'metro': 1})
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 1,
 'Arrow Shed': 1,
 'Arta': 1,
 'Arte italica': 1,
 'caseys': 1,
 'cooper caseys': 1,
 'cooper cooler': 1,
 'florida': 1,
 'floris': 1,
 'heineken': 1,
 'highland': 1,
 'metra': 1,
 'metro': 1})
 
        
           
            
        ### testcase to check create_dendrogram with maxclustsize = 3
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 3)
        self.assertEqual(dend, [((['cooper caseys'], ['caseys']), 0.5625),
 ((['floris'], ['florida']), 0.5833333333333333),
 ((['metro'], ['metra']), 0.6),
 ((['cooper cooler'], ['cooper caseys', 'caseys']), 0.6190476190476191),
 ((['Arrow Shed'], ['Arrow']), 0.6428571428571428),
 ((['Arte italica'], ['Arta']), 0.75),
 ((['highland'], ['heineken']), 0.9473684210526316)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 12,
 'Arrow Shed': 12,
 'Arta': 10,
 'Arte italica': 10,
 'caseys': 7,
 'cooper caseys': 7,
 'cooper cooler': 7,
 'florida': 5,
 'floris': 5,
 'heineken': 3,
 'highland': 3,
 'metra': 1,
 'metro': 1})
            
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 6
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 6)
        self.assertEqual(dend, [((['cooper caseys'], ['caseys']), 0.5625),
 ((['floris'], ['florida']), 0.5833333333333333),
 ((['metro'], ['metra']), 0.6),
 ((['cooper cooler'], ['cooper caseys', 'caseys']), 0.6190476190476191),
 ((['Arrow Shed'], ['Arrow']), 0.6428571428571428),
 ((['Arte italica'], ['Arta']), 0.75),
 ((['Arte italica', 'Arta'], ['Arrow Shed', 'Arrow']), 0.8181818181818181),
 ((['metro', 'metra'], ['Arte italica', 'Arta', 'Arrow Shed', 'Arrow']),
  0.9166666666666666),
 ((['floris', 'florida'], ['cooper cooler', 'cooper caseys', 'caseys']),
  0.9333333333333333),
 ((['highland'], ['heineken']), 0.9473684210526316)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 1,
 'Arrow Shed': 1,
 'Arta': 1,
 'Arte italica': 1,
 'caseys': 5,
 'cooper caseys': 5,
 'cooper cooler': 5,
 'florida': 5,
 'floris': 5,
 'heineken': 3,
 'highland': 3,
 'metra': 1,
 'metro': 1})
        
        
                          
        ### testcase to check create_dendrogram with maxclustsize = 5
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 5)
        self.assertEqual(dend, [((['cooper caseys'], ['caseys']), 0.5625),
 ((['floris'], ['florida']), 0.5833333333333333),
 ((['metro'], ['metra']), 0.6),
 ((['cooper cooler'], ['cooper caseys', 'caseys']), 0.6190476190476191),
 ((['Arrow Shed'], ['Arrow']), 0.6428571428571428),
 ((['Arte italica'], ['Arta']), 0.75),
 ((['Arte italica', 'Arta'], ['Arrow Shed', 'Arrow']), 0.8181818181818181),
 ((['metro', 'metra'], ['floris', 'florida']), 0.9333333333333333),
 ((['highland'], ['heineken']), 0.9473684210526316),
 ((['highland', 'heineken'], ['cooper cooler', 'cooper caseys', 'caseys']),
  1.0)])
        
        clust = self.hac.cluster(sim_measure = '3gram Jaccard', linkage = 'single', thr = 0.7)
        self.assertEqual(clust, {'Arrow': ['Arrow', 'Arrow Shed'],
 'Arta': ['Arta'],
 'Arte italica': ['Arte italica'],
 'caseys': ['caseys', 'cooper caseys', 'cooper cooler'],
 'florida': ['florida', 'floris'],
 'heineken': ['heineken'],
 'highland': ['highland'],
 'metra': ['metra', 'metro']} )
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 10,
 'Arrow Shed': 10,
 'Arta': 10,
 'Arte italica': 10,
 'caseys': 3,
 'cooper caseys': 3,
 'cooper cooler': 3,
 'florida': 1,
 'floris': 1,
 'heineken': 3,
 'highland': 3,
 'metra': 1,
 'metro': 1})
        
         
            
        ### testcase to check create_dendrogram with maxclustsize = 1
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'single', precalc_dists = self.dists, max_clust_size = 1)
        self.assertEqual(dend, [])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Arrow': 13,
 'Arrow Shed': 12,
 'Arta': 11,
 'Arte italica': 10,
 'caseys': 9,
 'cooper caseys': 8,
 'cooper cooler': 7,
 'florida': 6,
 'floris': 5,
 'heineken': 4,
 'highland': 3,
 'metra': 2,
 'metro': 1})
        
        
    def test_firms_complete(self):
        self.hac = HierarchicalClustering(self.vals3)

       
        ### testcase to check the distances calculated
        self.dists = self.hac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(self.dists.values()), 0.59090909)
        
                          
        ### testcase to check create_dendrogram with maxclustsize = total no of inputs(11)
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'complete', precalc_dists = self.dists, max_clust_size = 11)
        self.assertEqual(dend, [((['Apple Incorporated'], ['Apple Inc']), 0.5909090909090908),
 ((['Juniper Networks'], ['Cisco Networks']), 0.64),
 ((['Juniper Networks', 'Cisco Networks'], ['A10 networks']), 0.72),
 ((['Apple Incorporated', 'Apple Inc'], ['Apple']), 0.7727272727272727),
 ((['Zenith'], ['Zendesk']), 0.7857142857142857),
 ((['Mathworks'], ['Juniper Networks', 'Cisco Networks', 'A10 networks']),
  0.7916666666666666),
 ((['Apple Incorporated', 'Apple Inc', 'Apple'], ['Amazon']),
  0.962962962962963),
 ((['Zenith', 'Zendesk'], ['Matlab']), 1.0),
 ((['Zenith', 'Zendesk', 'Matlab'],
   ['Mathworks', 'Juniper Networks', 'Cisco Networks', 'A10 networks']),
  1.0),
 ((['Zenith',
    'Zendesk',
    'Matlab',
    'Mathworks',
    'Juniper Networks',
    'Cisco Networks',
    'A10 networks'],
   ['Apple Incorporated', 'Apple Inc', 'Apple', 'Amazon']),
  1.0)])
        
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 11,
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

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.6)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 11,
 'Amazon': 10,
 'Apple': 9,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 6,
 'Juniper Networks': 5,
 'Mathworks': 4,
 'Matlab': 3,
 'Zendesk': 2,
 'Zenith': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.9)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 4,
 'Amazon': 10,
 'Apple': 7,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 4,
 'Juniper Networks': 4,
 'Mathworks': 4,
 'Matlab': 3,
 'Zendesk': 1,
 'Zenith': 1})
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 1,
 'Amazon': 1,
 'Apple': 1,
 'Apple Inc': 1,
 'Apple Incorporated': 1,
 'Cisco Networks': 1,
 'Juniper Networks': 1,
 'Mathworks': 1,
 'Matlab': 1,
 'Zendesk': 1,
 'Zenith': 1})
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 7
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'complete', precalc_dists = self.dists, max_clust_size = 7)
        self.assertEqual(dend, [((['Apple Incorporated'], ['Apple Inc']), 0.5909090909090908),
 ((['Juniper Networks'], ['Cisco Networks']), 0.64),
 ((['Juniper Networks', 'Cisco Networks'], ['A10 networks']), 0.72),
 ((['Apple Incorporated', 'Apple Inc'], ['Apple']), 0.7727272727272727),
 ((['Zenith'], ['Zendesk']), 0.7857142857142857),
 ((['Mathworks'], ['Juniper Networks', 'Cisco Networks', 'A10 networks']),
  0.7916666666666666),
 ((['Apple Incorporated', 'Apple Inc', 'Apple'], ['Amazon']),
  0.962962962962963),
 ((['Zenith', 'Zendesk'], ['Matlab']), 1.0),
 ((['Zenith', 'Zendesk', 'Matlab'],
   ['Mathworks', 'Juniper Networks', 'Cisco Networks', 'A10 networks']),
  1.0)])
        
        
        
        ### testcase to check lambda_hac_dendrogram with different thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 11,
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

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.4)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 11,
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
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 4,
 'Amazon': 10,
 'Apple': 7,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 4,
 'Juniper Networks': 4,
 'Mathworks': 4,
 'Matlab': 3,
 'Zendesk': 1,
 'Zenith': 1})
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 1,
 'Amazon': 7,
 'Apple': 7,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 1,
 'Juniper Networks': 1,
 'Mathworks': 1,
 'Matlab': 1,
 'Zendesk': 1,
 'Zenith': 1})
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 3
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'complete', precalc_dists = self.dists, max_clust_size = 3)
        self.assertEqual(dend, [((['Apple Incorporated'], ['Apple Inc']), 0.5909090909090908),
 ((['Juniper Networks'], ['Cisco Networks']), 0.64),
 ((['Juniper Networks', 'Cisco Networks'], ['A10 networks']), 0.72),
 ((['Apple Incorporated', 'Apple Inc'], ['Apple']), 0.7727272727272727),
 ((['Zenith'], ['Zendesk']), 0.7857142857142857),
 ((['Matlab'], ['Mathworks']), 0.8125),
 ((['Zenith', 'Zendesk'], ['Amazon']), 1.0)])
        
        
        
        ### testcase to check lambda_hac_dendrogram with different thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 11,
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

        

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'A10 networks': 5,
 'Amazon': 1,
 'Apple': 7,
 'Apple Inc': 7,
 'Apple Incorporated': 7,
 'Cisco Networks': 5,
 'Juniper Networks': 5,
 'Mathworks': 3,
 'Matlab': 3,
 'Zendesk': 1,
 'Zenith': 1})
       
        clust = self.hac.cluster(sim_measure = '3gram Jaccard', linkage = 'complete', thr = 0.7)
        self.assertEqual(clust, {'A10 networks': ['A10 networks'],
 'Amazon': ['Amazon'],
 'Apple': ['Apple'],
 'Apple Inc': ['Apple Inc', 'Apple Incorporated'],
 'Cisco Networks': ['Cisco Networks', 'Juniper Networks'],
 'Mathworks': ['Mathworks'],
 'Matlab': ['Matlab'],
 'Zendesk': ['Zendesk'],
 'Zenith': ['Zenith']} )
        
        
        
        
    def test_names_average(self):
        self.hac = HierarchicalClustering(self.vals4)

       
        ### testcase to check the distances calculated
        self.dists = self.hac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(self.dists.values()), 0.46153846)
        
              
            
        ### testcase to check create_dendrogram with maxclustsize = total no of inputs(6)
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'average', precalc_dists = self.dists, max_clust_size = 6)
        self.assertEqual(dend, [((['Sorenson'], ['Sorensen']), 0.46153846153846156),
 ((['Johnson'], ['John']), 0.5),
 ((['Ram'], ['Raghu']), 0.8),
 ((['Sorenson', 'Sorensen'], ['Johnson', 'John']), 0.8469135802469135),
 ((['Sorenson', 'Sorensen', 'Johnson', 'John'], ['Ram', 'Raghu']), 1.0)])
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'John': 5, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.9)
        self.assertEqual(self.val_to_clustid_map, {'John': 1, 'Johnson': 1, 'Raghu': 3, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'John': 1, 'Johnson': 1, 'Raghu': 1, 'Ram': 1, 'Sorensen': 1, 'Sorenson': 1})
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 4
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'average', precalc_dists = self.dists, max_clust_size = 4)
        self.assertEqual(dend, [((['Sorenson'], ['Sorensen']), 0.46153846153846156),
 ((['Johnson'], ['John']), 0.5),
 ((['Ram'], ['Raghu']), 0.8),
 ((['Sorenson', 'Sorensen'], ['Johnson', 'John']), 0.8469135802469135)])
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'John': 5, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.5)
        self.assertEqual(self.val_to_clustid_map, {'John': 5, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'John': 1, 'Johnson': 1, 'Raghu': 3, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})
        
        
        clust = self.hac.cluster(sim_measure = '3gram Jaccard', linkage = 'average', thr = 0.5)
        self.assertEqual(clust, {'John': ['John', 'Johnson'],
 'Raghu': ['Raghu'],
 'Ram': ['Ram'],
 'Sorensen': ['Sorensen', 'Sorenson']} )
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 3
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'average', precalc_dists = self.dists, max_clust_size = 3)
        self.assertEqual(dend, [((['Sorenson'], ['Sorensen']), 0.46153846153846156),
 ((['Johnson'], ['John']), 0.5),
 ((['Ram'], ['Raghu']), 0.8)])
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'John': 5, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'John': 5, 'Johnson': 5, 'Raghu': 3, 'Ram': 3, 'Sorensen': 1, 'Sorenson': 1})
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.4)
        self.assertEqual(self.val_to_clustid_map, {'John': 6, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 2, 'Sorenson': 1})
        
        
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 1
        dend = self.hac.create_dendrogram(sim_measure = '3gram Jaccard', linkage = 'average', precalc_dists = self.dists, max_clust_size = 1)
        self.assertEqual(dend, [])
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'John': 6, 'Johnson': 5, 'Raghu': 4, 'Ram': 3, 'Sorensen': 2, 'Sorenson': 1})

        
        
        
        
    def test_venues_average_jarowinkler(self):
        self.hac = HierarchicalClustering(self.vals5)

       
        ### testcase to check the distances calculated
        self.dists = self.hac.calc_dists('Jaro-Winkler')
        self.assertAlmostEqual(min(self.dists.values()), 0.057142857)
        
        
        ### testcase to check create_dendrogram with maxclustsize = total no of inputs(7)
        dend = self.hac.create_dendrogram(sim_measure = 'Jaro-Winkler', linkage = 'average', precalc_dists = self.dists, max_clust_size = 7)
        self.assertEqual(dend, [((['Johnson street'], ['Johnson st']), 0.05714285714285716),
 ((['University of wisc madison'], ['Univ avenue']), 0.278088578088578),
 ((['Dept of computersciences'], ['Computer sciences department']),
  0.3007936507936507),
 ((['Wall street'], ['Johnson street', 'Johnson st']), 0.4192881192881193),
 ((['University of wisc madison', 'Univ avenue'],
   ['Dept of computersciences', 'Computer sciences department']),
  0.4750434750434751),
 ((['Wall street', 'Johnson street', 'Johnson st'],
   ['University of wisc madison',
    'Univ avenue',
    'Dept of computersciences',
    'Computer sciences department']),
  0.5231422898089565)])
        
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 1,
 'Dept of computersciences': 1,
 'Johnson st': 1,
 'Johnson street': 1,
 'Univ avenue': 1,
 'University of wisc madison': 1,
 'Wall street': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.4)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 6,
 'Dept of computersciences': 6,
 'Johnson st': 4,
 'Johnson street': 4,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.3)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 7,
 'Dept of computersciences': 6,
 'Johnson st': 4,
 'Johnson street': 4,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})
        
        
            
        ### testcase to check create_dendrogram with maxclustsize = 4
        dend = self.hac.create_dendrogram(sim_measure = 'Jaro-Winkler', linkage = 'average', precalc_dists = self.dists, max_clust_size = 4)
        self.assertEqual(dend, [((['Johnson street'], ['Johnson st']), 0.05714285714285716),
 ((['University of wisc madison'], ['Univ avenue']), 0.278088578088578),
 ((['Dept of computersciences'], ['Computer sciences department']),
  0.3007936507936507),
 ((['Wall street'], ['Johnson street', 'Johnson st']), 0.4192881192881193),
 ((['University of wisc madison', 'Univ avenue'],
   ['Dept of computersciences', 'Computer sciences department']),
  0.4750434750434751)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.3)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 7,
 'Dept of computersciences': 6,
 'Johnson st': 4,
 'Johnson street': 4,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})
        
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.05)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 7,
 'Dept of computersciences': 6,
 'Johnson st': 5,
 'Johnson street': 4,
 'Univ avenue': 3,
 'University of wisc madison': 2,
 'Wall street': 1})
            
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 2,
 'Dept of computersciences': 2,
 'Johnson st': 1,
 'Johnson street': 1,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})
                  
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 2
        dend = self.hac.create_dendrogram(sim_measure = 'Jaro-Winkler', linkage = 'average', precalc_dists = self.dists, max_clust_size = 2)
        self.assertEqual(dend, [((['Johnson street'], ['Johnson st']), 0.05714285714285716),
 ((['University of wisc madison'], ['Univ avenue']), 0.278088578088578),
 ((['Dept of computersciences'], ['Computer sciences department']),
  0.3007936507936507)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.3)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 7,
 'Dept of computersciences': 6,
 'Johnson st': 4,
 'Johnson street': 4,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})
        
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.7)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 6,
 'Dept of computersciences': 6,
 'Johnson st': 4,
 'Johnson street': 4,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})
            
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 6,
 'Dept of computersciences': 6,
 'Johnson st': 4,
 'Johnson street': 4,
 'Univ avenue': 2,
 'University of wisc madison': 2,
 'Wall street': 1})
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 1
        dend = self.hac.create_dendrogram(sim_measure = 'Jaro-Winkler', linkage = 'average', precalc_dists = self.dists, max_clust_size = 1)
        self.assertEqual(dend, [])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Computer sciences department': 7,
 'Dept of computersciences': 6,
 'Johnson st': 5,
 'Johnson street': 4,
 'Univ avenue': 3,
 'University of wisc madison': 2,
 'Wall street': 1})
        

        
        
    def test_big10_average_levenshtein(self):
        self.hac = HierarchicalClustering(self.vals6)

       
        ### testcase to check the distances calculated
        self.dists = self.hac.calc_dists('Levenshtein')
        self.assertAlmostEqual(min(self.dists.values()), 0.44444444)
        
        
        ### testcase to check create_dendrogram with maxclustsize = total no of inputs(7)
        dend = self.hac.create_dendrogram(sim_measure = 'Levenshtein', linkage = 'average', precalc_dists = self.dists, max_clust_size = 7)
        self.assertEqual(dend, [((['UM ann arbor'], ['Michigan ann arbor']), 0.4444444444444444),
 ((['UW'], ['UNL']), 0.6666666666666666),
 ((['UW Madison'], ['University of wisc madison']), 0.6923076923076923),
 ((['UM ann arbor', 'Michigan ann arbor'], ['Michigan st']),
  0.7222222222222223),
 ((['UW Madison', 'University of wisc madison'],
   ['UM ann arbor', 'Michigan ann arbor', 'Michigan st']),
  0.8188940688940688),
 ((['UW Madison',
    'University of wisc madison',
    'UM ann arbor',
    'Michigan ann arbor',
    'Michigan st'],
   ['UW', 'UNL']),
  0.9069177350427351)])
        
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 6,
 'UM ann arbor': 5,
 'UNL': 2,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 1})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.5)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 6,
 'UM ann arbor': 5,
 'UNL': 3,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 4})

        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 5,
 'UM ann arbor': 5,
 'UNL': 2,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 1})
        
        
            
            
            
        ### testcase to check create_dendrogram with maxclustsize = 4
        dend = self.hac.create_dendrogram(sim_measure = 'Levenshtein', linkage = 'average', precalc_dists = self.dists, max_clust_size = 4)
        self.assertEqual(dend, [((['UM ann arbor'], ['Michigan ann arbor']), 0.4444444444444444),
 ((['UW'], ['UNL']), 0.6666666666666666),
 ((['UW Madison'], ['University of wisc madison']), 0.6923076923076923),
 ((['UM ann arbor', 'Michigan ann arbor'], ['Michigan st']),
  0.7222222222222223),
 ((['UW Madison', 'University of wisc madison'], ['UW', 'UNL']),
  0.8760683760683761)])
        
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.7)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 6,
 'UM ann arbor': 5,
 'UNL': 2,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 1})
        
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 5,
 'UM ann arbor': 5,
 'UNL': 1,
 'UW': 1,
 'UW Madison': 1,
 'University of wisc madison': 1})
                  
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 2
        dend = self.hac.create_dendrogram(sim_measure = 'Levenshtein', linkage = 'average', precalc_dists = self.dists, max_clust_size = 2)
        self.assertEqual(dend, [((['UM ann arbor'], ['Michigan ann arbor']), 0.4444444444444444),
 ((['UW'], ['UNL']), 0.6666666666666666),
 ((['UW Madison'], ['University of wisc madison']), 0.6923076923076923)])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.6)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 6,
 'UM ann arbor': 5,
 'UNL': 3,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 4})
        
        
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 0.7)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 5,
 'Michigan st': 6,
 'UM ann arbor': 5,
 'UNL': 2,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 1})
            
        
        
        
        
        ### testcase to check create_dendrogram with maxclustsize = 1
        dend = self.hac.create_dendrogram(sim_measure = 'Levenshtein', linkage = 'average', precalc_dists = self.dists, max_clust_size = 1)
        self.assertEqual(dend, [])
        
        ### testcase to check lambdahac_dendrogam with diff thresholds
        self.val_to_clustid_map = self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
        self.assertEqual(self.val_to_clustid_map, {'Michigan ann arbor': 7,
 'Michigan st': 6,
 'UM ann arbor': 5,
 'UNL': 3,
 'UW': 2,
 'UW Madison': 1,
 'University of wisc madison': 4})
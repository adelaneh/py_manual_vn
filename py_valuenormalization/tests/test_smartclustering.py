import unittest

from nose.tools import *

from py_valuenormalization import MyPriorityQueue
from py_valuenormalization import HierarchicalClustering
from py_valuenormalization import HybridClustering
from py_valuenormalization import SmartClustering
from py_valuenormalization import SimMeasureNotSupportedException
from py_valuenormalization.value_normalization_misc import Utils

class SmartClusteringTests(unittest.TestCase):
    def setUp(self):
        self.vals = [ 'Sony', 'Audeze', 'Beats', '66Audio', 'Soundpeats', 'Soundintone']
        self.training_pairs = {("Sony","Audeze"): False, ("Sony","Beats"): False, ("Sony","66Audio"): False, ("Sony","Soundpeats"): False, ("Sony","Soundintone"): False,
 ("Audeze","Beats"): False, ("Audeze","66Audio"): True, ("Audeze","Soundpeats"): False, ("Audeze","Soundintone"): False,
 ("Beats","66Audio"): False, ("Beats","Soundpeats"): True, ("Beats","Soundintone"): False,
 ("66Audio","Soundpeats"): False, ("66Audio","Soundintone"): False,
 ("Soundpeats","Soundintone"): True
}
        
    def test_vals(self):
        self.smhac = SmartClustering(self.vals, self.training_pairs)
        
        ## SIMMEASURE = 3GRAM JACCARD
        dists = self.smhac.calc_dists('3gram Jaccard')
        self.assertAlmostEqual(min(dists.values()), 0.733333333333)
        
        
        ## dendrogram created for linkage = single and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'single')
        self.assertEqual(dend, [((['Soundpeats'], ['Beats']), 0.7333333333333334),
 ((['Soundpeats', 'Beats'], ['Soundintone']), 0.75),
 ((['Soundpeats', 'Beats', 'Soundintone'], ['Sony']), 0.875),
 ((['Audeze'], ['66Audio']), 0.9375),
 ((['Soundpeats', 'Beats', 'Soundintone', 'Sony'], ['Audeze', '66Audio']),
  0.95)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 3,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.9)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (10.0, 15, 0.6666666666666666))
        
        
        
        ## dendrogram created for linkage = complete and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'complete')
        self.assertEqual(dend, [((['Soundpeats'], ['Beats']), 0.7333333333333334),
 ((['Soundintone'], ['Sony']), 0.8823529411764706),
 ((['Audeze'], ['66Audio']), 0.9375),
 ((['Soundpeats', 'Beats'], ['Soundintone', 'Sony']), 1.0),
 ((['Soundpeats', 'Beats', 'Soundintone', 'Sony'], ['Audeze', '66Audio']),
  1.0)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 3,
 'Soundintone': 2,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.9)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 2,
 'Soundintone': 2,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (12.0, 15, 0.8))
        
        
        
        
        ## dendrogram created for linkage = average and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'average')
        self.assertEqual(dend, [((['Soundpeats'], ['Beats']), 0.7333333333333334),
 ((['Soundpeats', 'Beats'], ['Soundintone']), 0.8333333333333334),
 ((['Soundpeats', 'Beats', 'Soundintone'], ['Sony']), 0.9080882352941176),
 ((['Audeze'], ['66Audio']), 0.9375),
 ((['Soundpeats', 'Beats', 'Soundintone', 'Sony'], ['Audeze', '66Audio']),
  0.9933333333333333)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 3,
 'Soundintone': 2,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.9)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 3,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        
        
        
        ## SIMMEASURE = Levenshtein
        dists = self.smhac.calc_dists('Levenshtein')
        self.assertAlmostEqual(min(dists.values()), 0.545454545454)
        
        
        ## dendrogram created for linkage = single and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'single')
        self.assertEqual(dend, [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Soundpeats', 'Soundintone'], ['Beats']), 0.6),
 ((['Soundpeats', 'Soundintone', 'Beats'], ['Sony']), 0.7),
 ((['Soundpeats', 'Soundintone', 'Beats', 'Sony'], ['Audeze']), 0.7),
 ((['Soundpeats', 'Soundintone', 'Beats', 'Sony', 'Audeze'], ['66Audio']),
  0.7142857142857143)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.6)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 3,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.7)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 1,
 'Beats': 1,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (6.0, 15, 0.4))
        
        
        
        ## dendrogram created for linkage = complete and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'complete')
        self.assertEqual(dend, [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Audeze'], ['66Audio']), 0.7142857142857143),
 ((['Soundpeats', 'Soundintone'], ['Sony']), 0.7272727272727273),
 ((['Soundpeats', 'Soundintone', 'Sony'], ['Beats']), 1.0),
 ((['Soundpeats', 'Soundintone', 'Sony', 'Beats'], ['Audeze', '66Audio']),
  1.0)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.7)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 3,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(vtc, {'66Audio': 5,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (12.0, 15, 0.8))
        
        
        
        
        ## dendrogram created for linkage = average and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'average')
        self.assertEqual(dend, [((['Soundpeats'], ['Soundintone']), 0.5454545454545454),
 ((['Soundpeats', 'Soundintone'], ['Beats']), 0.703030303030303),
 ((['Audeze'], ['66Audio']), 0.7142857142857143),
 ((['Soundpeats', 'Soundintone', 'Beats'], ['Sony']), 0.7818181818181817),
 ((['Soundpeats', 'Soundintone', 'Beats', 'Sony'], ['Audeze', '66Audio']),
  0.852121212121212)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.7)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 3,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (13.0, 15, 0.8666666666666667))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.8)
        self.assertEqual(vtc, {'66Audio': 5,
 'Audeze': 5,
 'Beats': 1,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (11.0, 15, 0.7333333333333333))
        
        
        
        
        
        
        ## SIMMEASURE = Jaro-winkler
        dists = self.smhac.calc_dists('Jaro-Winkler')
        self.assertAlmostEqual(min(dists.values()), 0.161298701298)
        
        
        ## dendrogram created for linkage = single and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'single')
        self.assertEqual(dend, [((['Soundpeats'], ['Soundintone']), 0.16129870129870127),
 ((['Soundpeats', 'Soundintone'], ['Sony']), 0.2533333333333334),
 ((['Soundpeats', 'Soundintone', 'Sony'], ['66Audio']), 0.35497835497835506),
 ((['Soundpeats', 'Soundintone', 'Sony', '66Audio'], ['Audeze']),
  0.3571428571428571),
 ((['Soundpeats', 'Soundintone', 'Sony', '66Audio', 'Audeze'], ['Beats']),
  0.5444444444444445)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.3)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (11.0, 15, 0.7333333333333333))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.4)
        self.assertEqual(vtc, {'66Audio': 1,
 'Audeze': 1,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (6.0, 15, 0.4))
        
        
        
        ## dendrogram created for linkage = complete and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'complete')
        self.assertEqual(dend, [((['Soundpeats'], ['Soundintone']), 0.16129870129870127),
 ((['Soundpeats', 'Soundintone'], ['Sony']), 0.2606060606060606),
 ((['Audeze'], ['66Audio']), 0.3571428571428571),
 ((['Soundpeats', 'Soundintone', 'Sony'], ['Beats']), 1.0),
 ((['Soundpeats', 'Soundintone', 'Sony', 'Beats'], ['Audeze', '66Audio']),
  1.0)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.3)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (11.0, 15, 0.7333333333333333))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.4)
        self.assertEqual(vtc, {'66Audio': 5,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (12.0, 15, 0.8))
        
        
        
        
        ## dendrogram created for linkage = average and tests for agreementscore on different thresholds
        dend = self.smhac.create_dendrogram(precalc_dists = dists, linkage = 'average')
        self.assertEqual(dend, [((['Soundpeats'], ['Soundintone']), 0.16129870129870127),
 ((['Soundpeats', 'Soundintone'], ['Sony']), 0.2557575757575758),
 ((['Audeze'], ['66Audio']), 0.3571428571428571),
 ((['Soundpeats', 'Soundintone', 'Sony'], ['Audeze', '66Audio']),
  0.5795334295334295),
 ((['Soundpeats', 'Soundintone', 'Sony', 'Audeze', '66Audio'], ['Beats']),
  0.8363876863876863)])
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.3)
        self.assertEqual(vtc, {'66Audio': 6,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (11.0, 15, 0.7333333333333333))
        
        
        vtc = self.smhac.lambdahac_dendrogram(dend = dend, thr = 0.4)
        self.assertEqual(vtc, {'66Audio': 5,
 'Audeze': 5,
 'Beats': 4,
 'Sony': 1,
 'Soundintone': 1,
 'Soundpeats': 1})
        
        agrscore = self.smhac.calc_agreement_score()
        self.assertEqual(agrscore, (12.0, 15, 0.8))
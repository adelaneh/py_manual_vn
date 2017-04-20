import unittest

from nose.tools import *

from py_valuenormalization import MyPriorityQueue
from py_valuenormalization import HierarchicalClustering
from py_valuenormalization import SimMeasureNotSupportedException

class HierarchicalClusteringTestCases(unittest.TestCase):
	def setUp(self):
		self.vals				= ['aaa bbb', 'bbb aaa', 'abc ab acc']
		self.hac				= HierarchicalClustering(self.vals)
		self.dists				= self.hac.calc_dists('3gram Jaccard')

	def test_calc_dists(self):
		self.assertEqual(min(self.dists.values()), 0.875)

	@raises(SimMeasureNotSupportedException)
	def test_unsupported_sim_measure(self):
		dists					= self.hac.calc_dists('4gram Jaccard')

	def test_create_dendrogram(self):
		dend				= self.hac.create_dendrogram(precalc_dists = self.dists)

		self.assertEqual(str(dend), "[((['bbb aaa'], ['aaa bbb']), 0.875), ((['bbb aaa', 'aaa bbb'], ['abc ab acc']), 0.95)]")

	def test_lambdahac_dendrogram(self):
		dend				= self.hac.create_dendrogram(precalc_dists = self.dists)

		vtc					= self.hac.lambdahac_dendrogram(dend = dend)
		self.assertEqual(vtc, {'abc ab acc': 2, 'bbb aaa': 1, 'aaa bbb': 3})

		vtc					= self.hac.lambdahac_dendrogram(dend = dend, thr = 0.8)
		self.assertEqual(vtc, {'abc ab acc': 2, 'bbb aaa': 1, 'aaa bbb': 3})

		dend				= self.hac.create_dendrogram(precalc_dists = self.dists, max_clust_size = 2)

		vtc					= self.hac.lambdahac_dendrogram(dend = dend, thr = 1.0)
		self.assertEqual(vtc, {'abc ab acc': 2, 'bbb aaa': 1, 'aaa bbb': 1})

	def test_lambdahac(self):
		vtc					= self.hac.lambdahac('3gram Jaccard', 'single', 0.7)
		self.assertEqual(vtc, {'abc ab acc': 2, 'bbb aaa': 1, 'aaa bbb': 3})

		vtc					= self.hac.lambdahac('3gram Jaccard', 'single', 0.8)
		self.assertEqual(vtc, {'abc ab acc': 2, 'bbb aaa': 1, 'aaa bbb': 3})

		vtc					= self.hac.lambdahac('3gram Jaccard', 'single', 0.8, None, 1)
		self.assertEqual(vtc, {'abc ab acc': 2, 'bbb aaa': 1, 'aaa bbb': 3})



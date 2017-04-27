import unittest

from nose.tools import *
from py_valuenormalization import MyPriorityQueue
from py_valuenormalization import Utils
""" We have a total of seven testcases written as functions of MiscellaneousTestCases class.
Each testcase checks the functionality of a utility function under the Utils class

Overview: 
    (<Test_function_name> - Operating Dataset, Linkage, Sim_measure )
    test_readfile() - Reads 'sample_test.txt' as input and checks for the list of values returned
    test_readmapfromfile() - Reads 'sample_test2.txt' as input and checks for the dictionary of values returned
    test_alphalambdaWP() - Checks for the value returned by Utils.alpha_lambda_WP()
    test_fitlinear() - input list of tuples: lin_arr , Fits a linear model for the input tuple list
                       Checks functionality of Utils.fit_lin_leastsq()
    test_fitlinearnointercept() - input list of tuples: lin_arr2 , Fits a linear model for the input tuple list with no intercept.
                                  Checks functionality of Utils.fit_lin_nointercept_leastsq()
    test_fitquadnointercept() - input list of tuples: lin_arr3 , Fits a quadratic model for the input tuple list with no                                           intercept. Checks functionality of Utils.fit_quad_nointercept_leastsq()
    test_fitexp() - input list of tuples: lin_arr4 , Fits an exponential model for the input tuple list. Checks functionality of                       Utils.fit_exp_leastsq()
"""    
class MiscellaneousTestCases(unittest.TestCase):
    def setUp(self):
        self.lin_arr = [(1,5), (2,7) , (3,9) , (4,11)]
        self.lin_arr2 = [(1,2), (2,4) , (3,6) , (4,8)]
        self.lin_arr3 = [(1,2), (2,8) , (3,18) , (4,32)]
        self.lin_arr4 = [(1,1), (2,5) , (3,10) , (4,17)] 
        
    def test_readfile(self):
        vals = Utils.read_from_file('sample_test.txt')
        self.assertEqual(vals, ['Un', 'Univ', 'University', 'UW', 'UW madison'])
        
    def test_readmapfromfile(self):
        vals = Utils.read_map_from_file('sample_test2.txt')
        self.assertEqual(vals, {'Johnson': 'street', 'University': 'Wisc'})
        
    def test_alphalambdaWP(self):
        val = Utils.alpha_lambda_WP(5, 3, 2)
        self.assertEqual(val, 75 )
        
    def test_fitlinear(self):
        out1,out2 = Utils.fit_lin_leastsq(self.lin_arr)
        self.assertEqual(out1, 2.0 )
        self.assertEqual(out2, 3.0 )
        
    def test_fitlinearnointercept(self):
        out1 = Utils.fit_lin_nointercept_leastsq(self.lin_arr2)
        self.assertEqual(out1[0], 2.0 )
        
        
    def test_fitquadnointercept(self):
        out1 = Utils.fit_quad_nointercept_leastsq(self.lin_arr3)
        self.assertEqual(out1[0], 2.0 )
        
    def test_fitexp(self):
        out1,out2 = Utils.fit_exp_leastsq(self.lin_arr4)
        self.assertAlmostEqual(out1, 1.066186311)
        self.assertAlmostEqual(out2, 2.0417791409)

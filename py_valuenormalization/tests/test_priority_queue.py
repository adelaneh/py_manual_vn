import unittest

from nose.tools import *

from py_valuenormalization import MyPriorityQueue

""" We have a total of two testcases written as functions of MyPriorityQueueTestCases class.
The testcases check the functionality of add_task(), pop_task(), remove_task() functions of the MyPriorityQueue class

"""

class MyPriorityQueueTestCases(unittest.TestCase):
    def setUp(self):
        self.myq = MyPriorityQueue()

    def test_all(self):
        self.myq.add_task((1,2), 0.8)
        self.myq.add_task((1,3), 0.9)
        self.myq.add_task((1,4), 0.3)
        self.myq.add_task((2,3), 0.4)
        self.myq.add_task((3,4), 0.1)
        self.myq.add_task((2,4), 0.2)

        nent = self.myq.pop_task()[1]
        self.assertEqual(nent, (3,4))
        self.assertEqual(len(self.myq.pq), 5)

        nent = self.myq.remove_task((1,4))
        self.assertEqual(len(self.myq.pq), 5)

        nent = self.myq.pop_task()[1]
        self.assertEqual(nent, (2,4))
        self.assertEqual(len(self.myq.pq), 4)

    @raises(KeyError)
    def test_remove_task(self):
        self.myq.add_task((1,2), 0.8)
        self.myq.add_task((1,3), 0.9)
        self.myq.add_task((2,4), 0.2)

        self.assertEqual(len(self.myq.pq), 3)
        self.assertEqual(self.myq.is_empty(), False)

        self.myq.remove_task((1,2))
        self.myq.remove_task((1,3))
        self.myq.remove_task((2,4))

        self.assertEqual(len(self.myq.pq), 3)
        self.assertEqual(self.myq.is_empty(), True)

        nent = self.myq.pop_task()



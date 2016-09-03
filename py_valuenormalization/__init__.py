# coding=utf-8
import sys
if (sys.version_info > (3, 0)):
	import importlib
	importlib.reload(sys)
else:
	reload(sys)
	sys.setdefaultencoding("UTF-8")

from value_normalization_misc import *

from manual_value_normalization import *
from clustering_based_value_normalization import *
from cost_model_calibration import *

from priority_queue import *
from hierarchical_clustering import *
from smart_clustering import *
from hybrid_clustering import *

def read_from_file(path):
	return Utils.read_from_file(path)


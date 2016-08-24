# encoding=utf-8

import sys, os
from pprint import pprint
from time import sleep
import json
import ast

from scipy import *
from scipy import optimize
from scipy import stats
import numpy

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class WebPage(QWebPage):
	"""
	Makes it possible to use a Python logger to print javascript console messages
	"""
	def __init__(self, logger=None, parent=None):
		super(WebPage, self).__init__(parent)

	def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
		print("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))
		
class Window(QMainWindow):
	def __init__(self):
#		super(Window, self).__init__()

		QMainWindow.__init__(self)
		self.setAttribute(Qt.WA_DeleteOnClose, True)

		self.centralwidget = QWidget(self)
		self.centralwidget.setAttribute(Qt.WA_DeleteOnClose, True)

		self._layout = QVBoxLayout(self.centralwidget)
		self._layout.setMargin(0)

		self._view = QWebView()
#		self.resize(1100, 1500)
		self._view.setAttribute(Qt.WA_DeleteOnClose, True)

		self._layout.addWidget(self._view)
		self.setCentralWidget(self.centralwidget)

		self._view.page().settings().setObjectCacheCapacities(0, 0, 0)
		self._view.page().settings().setMaximumPagesInCache(0)
		self._view.page().settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

class ConsolePrinter(QObject):
	def __init__(self, parent=None):
#		super(ConsolePrinter, self).__init__(parent)
		QObject.__init__(self)
					
	@pyqtSlot(str)
	def text(self, message):
		print(message)

class Utils:
	@staticmethod
	def read_from_file(filename):
		vals		= []

		with open(filename) as f:
			for line in f:
				line		= line.strip()
				try:
					json_obj	= json.loads(line)
					for kk in json_obj:
						if kk.strip() is not u'':
							vals.append(kk.strip())
				except:
					if line not in ['', u'']:
						vals.append(unicode(line))
		return sorted([str(val) for val in vals], key=lambda s: s.lower())

	@staticmethod
	def alpha_lambda_WP(x, aa, bb):
		return aa * (x ** bb) if x != 1 else 1.

	@staticmethod
	def fit_exp_leastsq(d):
		fitfunc	= lambda p, x: p[0] + p[1] * x
		errfunc	= lambda p, x, y: (y - fitfunc(p, x))
		logx	= log10([x[0] for x in d])
		logy	= log10([x[1] for x in d])

		out,success = optimize.leastsq(errfunc, [1., -1.],args=(logx, logy),maxfev=3000)
		aa		= 10. ** out[0]
		bb		= out[1]

		return (aa, bb)

	@staticmethod
	def fit_lin_leastsq(d):
		fitfunc	= lambda p, x: p[0] * x + p[1]
		errfunc	= lambda p, x, y: (y - fitfunc(p, x))
		x		= array([xx[0] for xx in d])
		y		= array([xx[1] for xx in d])

		out,success	= optimize.leastsq(errfunc, [0., 0.],args=(x, y),maxfev=3000)

		return (out[0], out[1])

	@staticmethod
	def fit_lin_nointercept_leastsq(d):
		fitfunc = lambda p, x: p[0] * x
		errfunc = lambda p, x, y: (y - fitfunc(p, x))
		x	= array([xx[0] for xx in d])
		y	= array([xx[1] for xx in d])

		out,success = optimize.leastsq(errfunc, [0., ],args=(x, y),maxfev=3000)

		return (out[0],)

	@staticmethod
	def fit_quad_nointercept_leastsq(d):
		fitfunc = lambda p, x: p[0] * (x ** 2)
		errfunc = lambda p, x, y: (y - fitfunc(p, x))
		x	= array([xx[0] for xx in d])
		y	= array([xx[1] for xx in d])

		out,success = optimize.leastsq(errfunc, [0.,],args=(x, y),maxfev=3000)

		return (out[0],)

class SimMeasureNotSupportedException(Exception):
	def __init__(self, value):
		self.value		= value
	def __str__(self):
		return repr(self.value)



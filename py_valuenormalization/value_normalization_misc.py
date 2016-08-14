import sys, os
from pprint import pprint
from time import sleep
import json
import ast

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
		
class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()
		self.resize(1100, 1500)
		self.view = QWebView(self)

		layout = QVBoxLayout(self)
		layout.setMargin(0)
		layout.addWidget(self.view)
		QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

class ConsolePrinter(QObject):
	def __init__(self, parent=None):
		super(ConsolePrinter, self).__init__(parent)
					
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



import sys, os
from pprint import pprint
from time import sleep
import json
import ast

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

#QWebSettings.globalSettings().setAttribute(QWebSettings.LocalStorageEnabled, True)
#QWebSettings.globalSettings().setLocalStoragePath(os.getcwd())
#QWebSettings.globalSettings().setOfflineStoragePath(os.getcwd())
#QWebSettings.globalSettings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)

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
#		self.view.setPage(WebPage())

#		self.setupInspector()
#
#		self.splitter = QSplitter(self)
#		self.splitter.setOrientation(Qt.Vertical)

		layout = QVBoxLayout(self)
		layout.setMargin(0)
#		layout.addWidget(self.splitter)
		layout.addWidget(self.view)
		QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

#		self.splitter.addWidget(self.view)
#		self.splitter.addWidget(self.webInspector)
#
#	def setupInspector(self):
#		page = self.view.page()
#		page.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
#		self.webInspector = QWebInspector(self)
#		self.webInspector.setPage(page)
#
#		shortcut = QShortcut(self)
#		shortcut.setKey(Qt.Key_F12)
#		shortcut.activated.connect(self.toggleInspector)
#		self.webInspector.setVisible(True)
#
#	def toggleInspector(self):
#		self.webInspector.setVisible(not self.webInspector.isVisible())

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

class NormalizationApp(QObject):
	def __init__(self, vals, meta_file='html/meta.html', parent=None):
		super(NormalizationApp, self).__init__(parent)

		self.curpath			= os.path.abspath(os.path.dirname(__file__)) + "/"
		self.vals				= vals
		self.merged_clusters	= {}
		self.gmic				= 0
		self.result_clusters	= {}
		for val in vals:
			self.merged_clusters[val]	= [val,]

		self.meta		= open(self.curpath + meta_file).read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.app		= QApplication(sys.argv)
		self.app.setWindowIcon(QIcon(self.curpath + 'icons/uw3.png'))
		self.window		= Window()
		self.window.setWindowTitle("Manual Value Normalization")
		self.window.show()
		
		self.load_index()

	def reload_html_table(self, table_html):
		tab				= self.mainframe.documentElement().findFirst('tbody[id="values_to_norm_body"]')
		tab.evaluateJavaScript("this.innerHTML='%s';"%(table_html.replace('\n', '\\n'), ))

	def get_html_table(self):
		inp_val_table	= ""
		cnt				= 1
		for val in self.vals:
			inp_val_table	+= '<tr><th class="col-xs-2">%d</th><td class="col-xs-8">%s</td></tr>\n'%(cnt, val)
			cnt				+= 1
		return inp_val_table

	def run(self):
		self.app.exec_()

	def load_index(self):
		self.html		= self.meta 
		self.html		+= open(self.curpath + "html/index.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)
		self.html		= self.html.replace("@@INPUT_VALUES@@", self.get_html_table())

		self.window.view.loadFinished.connect(self.index_loaded)
		self.window.view.setHtml(self.html)

		self.printer	= ConsolePrinter()
		self.mainframe	= self.window.view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)
		self.mainframe.evaluateJavaScript("var vals=%s;"%(str([str(val) for val in self.vals]), ))

	@pyqtSlot()
	def index_loaded(self):
#		print("index loaded")
#		self.window.webInspector.setPage(self.window.view.page())

		# Set callback functions
		self.mainframe.addToJavaScriptWindowObject('norm_app', self)
		btn				= self.mainframe.documentElement().findFirst('button[id="start-local-merge-top"]')
		btn.evaluateJavaScript('this.onclick=norm_app.start_local_merging')
		btn				= self.mainframe.documentElement().findFirst('button[id="start-local-merge-bottom"]')
		btn.evaluateJavaScript('this.onclick=norm_app.start_local_merging')

	#########################################
	############## Local merge ##############
	#########################################
	@pyqtSlot()
	def start_local_merging(self, pgoffset=0):
		self.pgoffset	= pgoffset

		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var merged_clusters = %s</script>"""%(str(self.merged_clusters), )
		self.html		+= open(self.curpath + "html/local_merge.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.window.view.loadFinished.connect(self.local_merge_loaded)
		self.window.view.setHtml(self.html)

		self.mainframe	= self.window.view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str, int)
	def reload_local_merging(self, clusters, pgoffset):
		self.merged_clusters	= ast.literal_eval(clusters.__str__())
		
		self.start_local_merging(pgoffset) 

	@pyqtSlot()
	def local_merge_loaded(self):
#		print("local merge loaded")
#		self.window.webInspector.setPage(self.window.view.page())
		self.mainframe.evaluateJavaScript("window.scrollTo(0, %d);"%(self.pgoffset, ))
		return

	#########################################
	############# Global merge ##############
	#########################################
	@pyqtSlot(str)
	def start_global_merging(self, clusters):
		self.merged_clusters	= ast.literal_eval(clusters.__str__())
		if len(self.merged_clusters) < 2:
			self.finish_global_merging(clusters)
			return

		self.gmic				+= 1

		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var merged_clusters = %s</script>"""%(str(self.merged_clusters), )
		self.html		+= """<script type="text/javascript">var gmic = %d</script>"""%(self.gmic, )
		self.html		+= open(self.curpath + "html/global_merge.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.window.view.loadFinished.connect(self.global_merge_loaded)
		self.window.view.setHtml(self.html)

		self.mainframe	= self.window.view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str, str)
	def reload_global_merging(self, clusters, results):
		result_clusters	= ast.literal_eval(results.__str__())
		self.result_clusters.update(result_clusters)
		
		self.start_global_merging(clusters) 

	@pyqtSlot()
	def global_merge_loaded(self):
#		print("global merge loaded")
#		self.window.webInspector.setPage(self.window.view.page())
		self.mainframe.evaluateJavaScript("window.scrollTo(0, 0);")
		return

	#########################################
	############# Finish merge ##############
	#########################################
	@pyqtSlot(str)
	def finish_global_merging(self, clusters):
		self.merged_clusters	= ast.literal_eval(clusters.__str__())
		self.result_clusters.update(self.merged_clusters)

		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var merged_clusters = %s</script>"""%(str(self.result_clusters), )
		self.html		+= open(self.curpath + "html/result_summary.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.window.view.loadFinished.connect(self.result_summary_loaded)
		self.window.view.setHtml(self.html)

		self.mainframe	= self.window.view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str)
	def result_summary_loaded(self):
		self.mainframe.evaluateJavaScript("window.scrollTo(0, 0);")
		return

def normalize_values(vals):
	norm_app	= NormalizationApp(vals)
	norm_app.run()
	return norm_app.result_clusters

if __name__ == "__main__":
	if len(sys.argv) > 1:
		vals		= Utils.read_from_file(sys.argv[1])
		
	results		= normalize_values(vals)


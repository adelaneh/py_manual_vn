import sys, os
from pprint import pprint
from time import sleep
import ast

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

from value_normalization_misc import *

class ClusteringBasesValueNormalizationApp(QObject):
	def __init__(self, clusters, meta_file='html/meta.html', parent=None):
		super(ClusteringBasesValueNormalizationApp, self).__init__(parent)

		self.curpath			= os.path.abspath(os.path.dirname(__file__)) + "/"
		self.tosplit_clusters	= clusters
		self.vals				= list(self.tosplit_clusters.keys())
		self.gmic				= 0
		self.result_clusters	= {}

		self.meta		= open(self.curpath + meta_file).read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.app		= QApplication(sys.argv)
		self.app.setWindowIcon(QIcon(self.curpath + 'icons/uw3.png'))
		self.window		= Window()
		self.window.setWindowTitle("Clustering-based Value Normalization")
		self.window.show()
		
		self.load_understand_clusters()

	def get_html_table(self):
		inp_val_table	= ""
		cnt				= 1
		for val in self.vals:
			inp_val_table	+= '<tr><th class="col-xs-2">%d</th><td class="col-xs-8">%s</td></tr>\n'%(cnt, val)
			cnt				+= 1
		return inp_val_table

	def run(self):
		self.app.exec_()

	#########################################
	########## Understand clusters ##########
	#########################################
	def load_understand_clusters(self):
		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var merged_clusters = %s</script>"""%(str(self.tosplit_clusters), )
		self.html		+= open(self.curpath + "html/understand_clusters.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.window.view.loadFinished.connect(self.understand_clusters_loaded)
		self.window.view.setHtml(self.html)

		self.printer	= ConsolePrinter()
		self.mainframe	= self.window.view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot()
	def understand_clusters_loaded(self):
		self.mainframe.addToJavaScriptWindowObject('norm_app', self)
		btn				= self.mainframe.documentElement().findFirst('button[id="start-cleanup-btn"]')
		btn.evaluateJavaScript('this.onclick=norm_app.start_split_clusters')

	#########################################
	############# Split clusters ############
	#########################################
	@pyqtSlot()
	def start_split_clusters(self):
		self.split_clusters		= {}
		todelkks				= []
		for kk in self.tosplit_clusters:
			if len(self.tosplit_clusters[kk]) == 1:
				self.split_clusters[kk]		= self.tosplit_clusters[kk]
				todelkks.append(kk)
		for kk in todelkks:
			del self.tosplit_clusters[kk]

		if len(self.tosplit_clusters) == 0:
			self.merged_clusters		= self.split_clusters
			self.start_local_merging()
		else:
			self.load_split_clusters() 
		
	def load_split_clusters(self):
		self.html		= self.meta
		self.html		+= """<script type="text/javascript">var tosplit_clusters = %s</script>"""%(str(self.tosplit_clusters), )
		self.html		+= """<script type="text/javascript">var split_clusters = %s;</script>"""%(str(self.split_clusters), )
		self.current_clust_label_to_split		= sorted(self.tosplit_clusters.keys(), key = lambda x: x.lower())[0]
		self.html		+= """<script type="text/javascript">var curClusterLabel = \"%s\";</script>"""%(self.current_clust_label_to_split, )
		self.html		+= open(self.curpath + "html/split_clusters.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self.window.view.loadFinished.connect(self.split_clusters_loaded)
		self.window.view.setHtml(self.html)

		self.mainframe	= self.window.view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str)
	def reload_split_clusters(self, split_clusters):
		self.split_clusters	= ast.literal_eval(split_clusters.__str__())
		del self.tosplit_clusters[self.current_clust_label_to_split]

		if len(self.tosplit_clusters) == 0:
			self.merged_clusters		= self.split_clusters
			self.start_local_merging()
		else:
			self.load_split_clusters() 

	@pyqtSlot()
	def split_clusters_loaded(self):
		return

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

def normalize_clusters(clusters):
	norm_app	= ClusteringBasesValueNormalizationApp(clusters)
	norm_app.run()
	return norm_app.result_clusters



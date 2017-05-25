from multiprocessing import Queue, Process
import sys, os
from pprint import pprint
from time import sleep
from time import time as ts
import ast

from copy import deepcopy

#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt5.Qt import *
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
#from PyQt5.QtWidgets import *
#from PyQt5.QtWebKit import *
#from PyQt5.QtWebEngineWidgets import *

if (sys.version_info > (3, 0)):
	from .value_normalization_misc import *
	from .logger import *
else:
	from value_normalization_misc import *
	from logger import *

class ManualValueNormalizationApp(QObject, Logger):
	def __init__(self, clusters, meta_file='html/meta.html', parent=None):
		QObject.__init__(self)
		Logger.__init__(self, name="ManualValueNormalizationApp")

		self.curpath			= os.path.abspath(os.path.dirname(__file__))
		self.merged_clusters	= clusters
		self.vals				= sorted(list(self.merged_clusters.keys()), key = lambda x: x.lower())
		self.gmic				= 0
		self.result_clusters	= {}

		self.meta		= open(self.curpath + "/" + meta_file).read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

	def get_html_table(self):
		inp_val_table	= ""
		cnt				= 1
		for val in self.vals:
			inp_val_table	+= '<tr><th class="col-xs-2">%d</th><td class="col-xs-8">%s</td></tr>\n'%(cnt, val)
			cnt				+= 1
		return inp_val_table

	def run(self):
		global app
		app		= QApplication.instance()
		if app is None:
			app		= QApplication(sys.argv + ['--disable-web-security'])
		app.setWindowIcon(QIcon(self.curpath + '/icons/uw3.png'))
		self._window		= Window()
		self._window.setWindowTitle("Manual Value Normalization")
		self._window.setWindowState(Qt.WindowMaximized)

		self.load_understand_values()

		self._window.show()
		self._window.raise_()

		app.exec_()

        def client_script(self):
            qwebchannel_js = QFile(self.curpath + '/javascript/qwebchannel.js')
            if not qwebchannel_js.open(QIODevice.ReadOnly):
               raise SystemExit(
                      'Failed to load qwebchannel.js with error: %s' %
                  qwebchannel_js.errorString())
            qwebchannel_js = bytes(qwebchannel_js.readAll()).decode('utf-8')

            script = QWebEngineScript()
            script.setSourceCode(qwebchannel_js + '''
                var webchannel = new QWebChannel(qt.webChannelTransport, function(channel) {
                        channel.objects.printer.text('QWebCannel suxly loaded.');
                });
            ''')
            script.setName('qwc')
            script.setWorldId(QWebEngineScript.MainWorld)
            script.setInjectionPoint(QWebEngineScript.DocumentReady)
            script.setRunsOnSubFrames(True)
            return script

	#########################################
	########### Understand values ###########
	#########################################
	def load_understand_values(self):
		self.html		= self.meta 
		self.html		+= open(self.curpath + "/html/understand_values.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)
		self.html		= self.html.replace("@@INPUT_VALUES@@", self.get_html_table())

		self.printer	= ConsolePrinter()
		self._page	= WebPage()
		self._window._view.setPage(self._page)
                self._page.profile().scripts().insert(self.client_script())
                self._channel   = QWebChannel(self._page)
                self._page.setWebChannel(self._channel)
		self._channel.registerObject('printer', self.printer)
		self._channel.registerObject('norm_app', self)
		self._page.runJavaScript("var vals = %s;"%(str([str(val) for val in self.vals]), ))

		self._window._view.setHtml(self.html)

		self._window._view.loadFinished.connect(self.understand_values_loaded)

	@pyqtSlot()
	def understand_values_loaded(self):
                self._page.runJavaScript("var norm_app = webchannel.objects.norm_app;")
                self._page.runJavaScript("document.getElementById('start-local-merge-top').onclick=norm_app.start_local_merging;")
                self._page.runJavaScript("document.getElementById('start-local-merge-bottom').onclick=norm_app.start_local_merging;")

	#########################################
	############## Local merge ##############
	#########################################
	@pyqtSlot()
	def start_local_merging(self, pgoffset=0):
		self.pgoffset	= pgoffset

		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var merged_clusters = %s</script>"""%(str(self.merged_clusters), )
		self.html		+= open(self.curpath + "/html/local_merge.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.disconnect()
		self._window._view.loadFinished.connect(self.local_merge_loaded)
		self._window._view.setHtml(self.html)

	@pyqtSlot(str, int)
	def reload_local_merging(self, clusters, pgoffset):
		self.merged_clusters	= ast.literal_eval(clusters.__str__())
		
		self.start_local_merging(pgoffset) 

	@pyqtSlot()
	def local_merge_loaded(self):
                self._page.runJavaScript("var norm_app = webchannel.objects.norm_app;")
                self._page.runJavaScript("window.scrollTo(0, %d);"%(self.pgoffset, ))

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
		self.html		+= open(self.curpath + "/html/global_merge.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.disconnect()
		self._window._view.loadFinished.connect(self.global_merge_loaded)
		self._window._view.setHtml(self.html)

	@pyqtSlot(str, str)
	def reload_global_merging(self, clusters, results):
		result_clusters	= ast.literal_eval(results.__str__())
		self.result_clusters.update(result_clusters)
		
		self.start_global_merging(clusters) 

	@pyqtSlot()
	def global_merge_loaded(self):
                self._page.runJavaScript("var norm_app = webchannel.objects.norm_app;")
                self._page.runJavaScript("window.scrollTo(0, 0);")

	#########################################
	############# Finish merge ##############
	#########################################
	@pyqtSlot(str)
	def finish_global_merging(self, clusters):
		self.merged_clusters	= ast.literal_eval(clusters.__str__())
		self.result_clusters.update(self.merged_clusters)

		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var merged_clusters = %s</script>"""%(str(self.result_clusters), )
		self.html		+= open(self.curpath + "/html/result_summary.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.disconnect()
		self._window._view.loadFinished.connect(self.result_summary_loaded)
		self._window._view.setHtml(self.html)

	@pyqtSlot()
	def result_summary_loaded(self):
                self._page.runJavaScript("var norm_app = webchannel.objects.norm_app;")
                self._page.runJavaScript("window.scrollTo(0, 0);")

class ManualValueNormalizationAppProcess(Process):
	def __init__(self, clusters):
		self.queue		= Queue(1)
		super(ManualValueNormalizationAppProcess, self).__init__()
		self._clusters	= clusters
		self._ttf		= 0

	def run(self):
		norm_app	= ManualValueNormalizationApp(self._clusters)
		norm_app.run()
		if len(norm_app._log_entries) > 0 and norm_app._log_entries[-1][0] == 4:
			self._ttf	= norm_app._log_entries[-1][1] - norm_app._log_entries[0][1]
		res			= deepcopy(norm_app.result_clusters)
		del norm_app

		global app
		app					= QApplication.instance()
		app.exit()
		app.flush()
		app.quit()
		self.queue.put((res, self._ttf))

def normalize_values(vals):
	clusters	= {}
	for val in (vals.values() if isinstance(vals, dict) else vals):
		clusters[val]	= [val,]
	norm_app	= ManualValueNormalizationAppProcess(clusters)
	norm_app.run()
#	norm_app.start()
#	norm_app.join()
	return norm_app.queue.get()



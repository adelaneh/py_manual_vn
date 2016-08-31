import sys, os
from pprint import pprint
from time import sleep
import ast
import random as strandom

from copy import deepcopy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

from value_normalization_misc import *
from hierarchical_clustering import *

class CostModelCalibrationApp(QObject):
	def __init__(self, vals, meta_file='html/meta.html', parent=None):
#		super(CostModelCalibrationApp, self).__init__(parent)
		QObject.__init__(self)

		self.curpath			= os.path.abspath(os.path.dirname(__file__)) + "/"
		self.vals				= vals

		self.cost_model			= Utils.get_default_cost_model()

		self.training_pairs		= {}

		self.ua_match_opcnt		= 3
		self.ua_ispure_opcnt	= 3
		self.ua_finddom_opcnt	= 6

		self.meta				= open(self.curpath + meta_file).read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

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
			app		= QApplication(sys.argv)
		app.setWindowIcon(QIcon(self.curpath + 'icons/uw3.png'))
		self._window		= Window()
		self._window.setWindowTitle("Cost Model Calibration")
		self._window.setWindowState(Qt.WindowMaximized)

		self._window.show()
		self._window.raise_()

		self.load_understand_values()

		app.exec_()

	#########################################
	########### Understand values ###########
	#########################################
	def load_understand_values(self):
		self.html		= self.meta 
		self.html		+= open(self.curpath + "html/understand_values_to_calibrate.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)
		self.html		= self.html.replace("@@INPUT_VALUES@@", self.get_html_table())

		self._window._view.setHtml(self.html)

		self.printer	= ConsolePrinter()
		self.mainframe	= self._window._view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)
		self.mainframe.evaluateJavaScript("var vals = %s;"%(str([str(val) for val in self.vals]), ))

		self._window._view.loadFinished.connect(self.understand_values_loaded)

	@pyqtSlot()
	def understand_values_loaded(self):
		self.mainframe.addToJavaScriptWindowObject('calib_app', self)
		btn				= self.mainframe.documentElement().findFirst('button[id="start-calib-btn"]')
		btn.evaluateJavaScript('this.onclick=calib_app.estimate_purity_function')

	#########################################
	######### Cost Model Calibration ########
	#########################################
	######### 1. Estimate Purity Function ###
	#########################################
	@pyqtSlot()
	def estimate_purity_function(self):
		hac						= HierarchicalClustering(self.vals)
		dists					= hac.calc_dists('3gram Jaccard')
		sample_clust_size		= 3
		
		dend10					= hac.create_dendrogram(precalc_dists = dists, max_clust_size = 10)
		vtc10					= hac.lambdahac_dendrogram(dend=dend10)
		clusters10				= hac.get_clusters()
		self.clusters10			= clusters10

		samples_pe_clusts10		= {}
		pe_clusts				= [clt for blb, clt in clusters10.items() if len(clt) > 1]
		pe_clusts				= strandom.sample(pe_clusts, min(sample_clust_size, len(pe_clusts)))

		for ccl in pe_clusts:
			samples_pe_clusts10[ccl[0]]		= ccl

		dend20					= hac.create_dendrogram(precalc_dists = dists, max_clust_size = 20)
		vtc20					= hac.lambdahac_dendrogram(dend=dend20)
		clusters20				= hac.get_clusters()
		self.clusters20			= clusters20

		samples_pe_clusts20		= {}
		pe_clusts				= [clt for blb, clt in clusters20.items() if len(clt) > 1]
		pe_clusts				= strandom.sample(pe_clusts, min(sample_clust_size, len(pe_clusts)))

		for ccl in pe_clusts:
			samples_pe_clusts20[ccl[0]]		= ccl

		self.clusters			= clusters20
		self.cluster_purities	= {'clusters': [],'times': []}
		self.cur_cluster_label	= list(samples_pe_clusts10.keys())[0]

		self.html		= self.meta
		self.html		+= """<script type="text/javascript">var vals = %s</script>"""%(str(self.vals), )
		self.html		+= """<script type="text/javascript">var allClusts = %s</script>"""%(str(self.clusters), )
		self.html		+= """<script type="text/javascript">var samples_pe_clusts10 = %s</script>"""%(str(samples_pe_clusts10), )
		self.html		+= """<script type="text/javascript">var samples_pe_clusts20 = %s</script>"""%(str(samples_pe_clusts20), )
		self.html		+= """<script type="text/javascript">var cluster_purities = %s;</script>"""%(str(self.cluster_purities), )
		self.html		+= """<script type="text/javascript">var curClusterLabel = \"%s\";</script>"""%(self.cur_cluster_label, )
		self.html		+= open(self.curpath + "html/estimate_purity.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.connect(self.estimate_purity_function_loaded)
		self._window._view.setHtml(self.html)

		self.mainframe	= self._window._view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str, str)
	def estimate_purity_function_params(self, cps, domvals):
		self.cluster_purities = ast.literal_eval(cps.__str__())
		cluster_doment_vals = ast.literal_eval(domvals.__str__())

		for kk in cluster_doment_vals:
			cur_clust		= self.clusters10[kk] if kk in self.clusters10 else self.clusters20[kk]
			for vi1 in range(len(cur_clust)):
				for vi2 in range(vi1 + 1, len(cur_clust)):
					if cur_clust[vi1] in cluster_doment_vals[kk]:
						self.training_pairs[tuple(sorted([cur_clust[vi1], cur_clust[vi2]]))]   = cur_clust[vi2] in cluster_doment_vals[kk]

		####### ESTIMATE PURITY FUNCTION PARAMS ############
		dd							= [(1, 1),]
		dd.append((10, 1. * sum([self.cluster_purities['10'][2 * kk] for kk in range(len(self.cluster_purities['10']) / 2)]) 
							/ sum([self.cluster_purities['10'][2 * kk + 1] for kk in range(len(self.cluster_purities['10']) / 2)])))

		dd.append((20, 1. * sum([self.cluster_purities['20'][2 * kk] for kk in range(len(self.cluster_purities['20']) / 2)]) 
							/ sum([self.cluster_purities['20'][2 * kk + 1] for kk in range(len(self.cluster_purities['20']) / 2)])))

		(aa, bb)						= Utils.fit_exp_leastsq(dd)

		self.cost_model['purity']['aa']	= aa
		self.cost_model['purity']['bb']	= bb


		self.calibrate_ua_match()

	@pyqtSlot()
	def estimate_purity_function_loaded(self):
		return

	#########################################
	########### 2. Calibrate "match" ########
	#########################################
	@pyqtSlot()
	def calibrate_ua_match(self):
		self.recorded_resps		= {'clusters': [],'times': []}
		self.seq_counter		= self.ua_match_opcnt - 1

		self.html		= self.meta
		self.html		+= """<script type="text/javascript">var vals = %s</script>"""%(str(self.vals), )
		self.html		+= """<script type="text/javascript">var clusters = %s</script>"""%(str(self.clusters), )
		self.html		+= """<script type="text/javascript">var recorded_resps = %s;</script>"""%(str(self.recorded_resps), )
		self.html		+= """<script type="text/javascript">var seq_counter = %d;</script>"""%(self.seq_counter, )
		self.html		+= open(self.curpath + "html/ua_match.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.connect(self.calibrate_ua_match_loaded)
		self._window._view.setHtml(self.html)

		self.mainframe	= self._window._view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str, str)
	def estimate_ua_match_params(self, resps, tr_pairs):
		self.recorded_resps	= ast.literal_eval(resps.__str__())
		ua_match_tr_pairs	= ast.literal_eval(tr_pairs.__str__())

		for vpair in ua_match_tr_pairs:
			self.training_pairs[tuple(sorted(vpair[0]))]	= vpair[1] == "1"

		####### ESTIMATE MATCH PARAMS ############
		tss					= self.recorded_resps['times']
		ua_match_fitdata	= []
		opcnt				= len(tss)/2
		for jj in range(opcnt):
			ua_match_fitdata.append(( int(tss[2 * jj + 1]) - int(tss[2 * jj]) ) - ( self.cost_model['user']['rho_f'] + self.cost_model['user']['rho_s'] ))
		self.cost_model['user']['rho_m']	= 1. * sum(ua_match_fitdata)/len(ua_match_fitdata)

		self.calibrate_ua_ispure()

	@pyqtSlot()
	def calibrate_ua_match_loaded(self):
		return

	#########################################
	########### 3. Calibrate "ispure" #######
	#########################################
	@pyqtSlot()
	def calibrate_ua_ispure(self):
		self.recorded_resps		= {'clusters': [],'times': [], 'ispure': []}
		self.seq_counter		= self.ua_ispure_opcnt - 1

		self.html		= self.meta
		self.html		+= """<script type="text/javascript">var vals = %s</script>"""%(str(self.vals), )
		self.html		+= """<script type="text/javascript">var clusters = %s</script>"""%(str(self.clusters), )
		self.html		+= """<script type="text/javascript">var recorded_resps = %s;</script>"""%(str(self.recorded_resps), )
		self.html		+= """<script type="text/javascript">var seq_counter = %d;</script>"""%(self.seq_counter, )
		self.html		+= open(self.curpath + "html/ua_ispure.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.connect(self.calibrate_ua_ispure_loaded)
		self._window._view.setHtml(self.html)

		self.mainframe	= self._window._view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str)
	def estimate_ua_ispure_params(self, resps):
		self.recorded_resps	= ast.literal_eval(resps.__str__())

		uaclusts			= self.recorded_resps['clusters']
		uaispureyn			= self.recorded_resps['ispure']

		for kkinx in range(len(uaclusts)):
			ispureyn	= uaispureyn[kkinx]
			if ispureyn == '1':
				kk			= uaclusts[kkinx]
				cur_clust	= self.clusters[kk]
				for vi1 in range(len(cur_clust)):
					for vi2 in range(vi1 + 1, len(cur_clust)):
						self.training_pairs[tuple(sorted([cur_clust[vi1], cur_clust[vi2]]))]   = True


		####### ESTIMATE ISPURE PARAMS ############
		tss					= self.recorded_resps['times']
		(aa, bb)			= (self.cost_model['purity']['aa'], self.cost_model['purity']['bb'])

		ua_ispure_fitdata	= []
		opcnt				= len(tss)/2
		for jj in range(opcnt):
			cur_clustsize		= len(self.clusters[uaclusts[jj]])
			cur_ispureyn		= uaispureyn[jj]
			cur_x				= cur_clustsize if cur_ispureyn == '1' else Utils.alpha_lambda_WP(20, aa, bb) * cur_clustsize
			ua_ispure_fitdata.append((cur_x, ( int(tss[2 * jj + 1]) - int(tss[2 * jj]) ) - ( self.cost_model['user']['rho_f'] + self.cost_model['user']['rho_s'] )))


		(	self.cost_model['user']['gamma'], 
			self.cost_model['user']['gamma_0'])	= Utils.fit_lin_leastsq(ua_ispure_fitdata)


		self.calibrate_ua_finddoment()

	@pyqtSlot()
	def calibrate_ua_ispure_loaded(self):
		return

	#########################################
	########### 4. Calibrate "finddoment" ###
	#########################################
	@pyqtSlot()
	def calibrate_ua_finddoment(self):
		self.recorded_resps		= {'clusters': [],'times': []}
		self.seq_counter		= self.ua_finddom_opcnt - 1

		self.html		= self.meta
		self.html		+= """<script type="text/javascript">var vals = %s</script>"""%(str(self.vals), )
		self.html		+= """<script type="text/javascript">var clusters = %s</script>"""%(str(self.clusters), )
		self.html		+= """<script type="text/javascript">var recorded_resps = %s;</script>"""%(str(self.recorded_resps), )
		self.html		+= """<script type="text/javascript">var seq_counter = %d;</script>"""%(self.seq_counter, )
		self.html		+= open(self.curpath + "html/ua_finddom.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.loadFinished.connect(self.calibrate_ua_finddoment_loaded)
		self._window._view.setHtml(self.html)

		self.mainframe	= self._window._view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

	@pyqtSlot(str)
	def estimate_ua_finddom_params(self, resps):
		self.recorded_resps	= ast.literal_eval(resps.__str__())

		####### ESTIMATE ISPURE PARAMS ############
		tss					= self.recorded_resps['times']
		uaclusts			= self.recorded_resps['clusters']
		(aa, bb)			= (self.cost_model['purity']['aa'], self.cost_model['purity']['bb'])

		ua_finddom_fitdata	= []
		opcnt				= len(tss)/2
		for jj in range(opcnt):
			cur_clustsize		= len(self.clusters[uaclusts[jj]])
			ua_finddom_fitdata.append((cur_clustsize, ( int(tss[2 * jj + 1]) - int(tss[2 * jj]) ) - ( self.cost_model['user']['rho_f'] + self.cost_model['user']['rho_s'] )))

		(self.cost_model['user']['eta_1'], )	= Utils.fit_lin_nointercept_leastsq(ua_finddom_fitdata[:opcnt/2])
		(self.cost_model['user']['eta_2'], )	= Utils.fit_quad_nointercept_leastsq(ua_finddom_fitdata[opcnt/2 + 1:])

		self.done_calibration()

	@pyqtSlot()
	def calibrate_ua_finddoment_loaded(self):
		return

	#########################################
	########### Done Calibration ############
	#########################################
	@pyqtSlot()
	def done_calibration(self):
		self.html		= self.meta 
		self.html		+= """<script type="text/javascript">var cost_model = %s</script>"""%(str(self.cost_model), )
		self.html		+= open(self.curpath + "html/done_calibration.html").read().replace("@@CURRENT_DIR@@", "file://" + self.curpath)

		self._window._view.setHtml(self.html)

		self.mainframe	= self._window._view.page().mainFrame()
		self.mainframe.addToJavaScriptWindowObject('printer', self.printer)

def calibrate_normalization_cost_model(vals):
	calib_app			= CostModelCalibrationApp(vals)
	calib_app.run()
	cost_model			= deepcopy(calib_app.cost_model)
	training_pairs		= deepcopy(calib_app.training_pairs)
	del calib_app

	return (cost_model, training_pairs)



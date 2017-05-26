import sys, os
from pprint import pprint
from time import sleep
import json
import ast

from scipy import *
from scipy import optimize
from scipy import stats
import numpy

from PyQt5.Qt import *

class WebPage(QWebEnginePage):
    """
    Makes it possible to use a Python logger to print javascript console messages
    """
    def __init__(self, logger=None, parent=None):
        super(WebPage, self).__init__(parent)

    def javaScriptConsoleMessage(self, level, msg, lineNumber, sourceID):
        print("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))
        
class Window(QMainWindow):
    """
    Initializes the widget settings, attributes on window
    """   
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.centralwidget = QWidget(self)
        self.centralwidget.setAttribute(Qt.WA_DeleteOnClose, True)

        self._layout = QVBoxLayout(self.centralwidget)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._view = QWebEngineView()
        self._view.setAttribute(Qt.WA_DeleteOnClose, True)

        self._layout.addWidget(self._view)
        self.setCentralWidget(self.centralwidget)

class ConsolePrinter(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self)
                    
    @pyqtSlot(str)
    def text(self, message):
        print(message)

# Utility functions called in other modules
class Utils:
    @staticmethod
    # Reads from a textfile and returns a list of values
    def read_from_file(filename):
        vals = []

        with open(filename) as f:
            for line in f:
                line = line.strip()
                try:
                    json_obj = json.loads(line)
                    for kk in json_obj:
                        if kk.strip() is not u'':
                            vals.append(kk.strip())
                except:
                    if line not in ['', u'']:
                        vals.append(unicode(line))
        return sorted([str(val) for val in vals], key=lambda s: s.lower())
    
    # Reads from textfile (tab separated values on each line) and returns a dictionary of key, value pairs
    @staticmethod
    def read_map_from_file(filename):
        val_map = {}

        with open(filename) as f:
            for line in f:
                line = unicode(line.strip())
                if line not in ['', u'']:
                    toks = line.split('\t')
                    val_map[str(toks[0])] = str(toks[1])
        return val_map

    @staticmethod
    def alpha_lambda_WP(x, aa, bb):
        return aa * (x ** bb) if x != 1 else 1.
    
    # Fits a exponential model ( f(x) = a + x^b) for inputted (x,f(x)) tuple pairs
    # Returns (a,b)
    @staticmethod
    def fit_exp_leastsq(d):
        fitfunc = lambda p, x: p[0] + p[1] * x
        errfunc = lambda p, x, y: (y - fitfunc(p, x))
        logx = log10([x[0] for x in d])
        logy = log10([x[1] for x in d])

        out,success = optimize.leastsq(errfunc, [1., -1.],args=(logx, logy),maxfev=3000)
        aa = 10. ** out[0]
        bb = out[1]
        return (aa, bb)

    # Fits a linear model ( f(x) = a*x + b) for inputted (x,f(x)) tuple pairs
    # Returns (a,b)
    @staticmethod
    def fit_lin_leastsq(d):
        fitfunc = lambda p, x: p[0] * x + p[1]
        errfunc = lambda p, x, y: (y - fitfunc(p, x))
        x = array([xx[0] for xx in d])
        y = array([xx[1] for xx in d])

        out,success = optimize.leastsq(errfunc, [0., 0.],args=(x, y),maxfev=3000)
        return (out[0], out[1])

    # Fits a linear model with no intercept ( f(x) = a*x ) for inputted (x,f(x)) tuple pairs
    # Returns tuple (a,)
    @staticmethod
    def fit_lin_nointercept_leastsq(d):
        fitfunc = lambda p, x: p[0] * x
        errfunc = lambda p, x, y: (y - fitfunc(p, x))
        x = array([xx[0] for xx in d])
        y = array([xx[1] for xx in d])

        out,success = optimize.leastsq(errfunc, [0., ],args=(x, y),maxfev=3000)

        return (out[0],)
    
    # Fits a quadratic model with no intercept ( f(x) = a*(x^2) ) for inputted (x,f(x)) tuple pairs
    # Returns tuple (a,)
    @staticmethod
    def fit_quad_nointercept_leastsq(d):
        fitfunc = lambda p, x: p[0] * (x ** 2)
        errfunc = lambda p, x, y: (y - fitfunc(p, x))
        x = array([xx[0] for xx in d])
        y = array([xx[1] for xx in d])

        out,success = optimize.leastsq(errfunc, [0.,],args=(x, y),maxfev=3000)

        return (out[0],)
    
    # Returns defaultcost model used in Hybrid clustering for clustering evaluation
    @staticmethod
    def get_default_cost_model():
        return {
            'user': {
                'rho_f': 500,
                'rho_s': 500,
                'rho_m': 2000,
                'gamma': 250,
                'gamma_0': 650,
                'eta_1': 200,
                'eta_2': 0.3,
                'rho_r': 1500,
                'rho_z': 2500
            },
            'purity': {
                'aa': 1.,
                'bb': -.11
            }
        }



class SimMeasureNotSupportedException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


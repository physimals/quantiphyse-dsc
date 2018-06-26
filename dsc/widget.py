"""
Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

from PySide import QtGui

from quantiphyse.gui.widgets import QpWidget, Citation, TitleWidget
from quantiphyse.utils import get_plugins
from quantiphyse.utils.exceptions import QpException

from ._version import __version__

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class FabberDscWidget(QpWidget):
    """
    DSC modelling, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="DSC", icon="fabber",  group="DCE-MRI", desc="Bayesian DSC modelling", **kwargs)
        
    def init_ui(self):
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        try:
            self.FabberProcess = get_plugins("processes", "FabberProcess")[0]
        except:
            self.FabberProcess = None

        if self.FabberProcess is None:
            vbox.addWidget(QtGui.QLabel("Fabber core library not found.\n\n You must install Fabber to use this widget"))
            return
        
        title = TitleWidget(self, help="fabber-dsc", subtitle="DSC modelling using the Fabber process %s" % __version__)
        vbox.addWidget(title)
              
        cite = Citation(FAB_CITE_TITLE, FAB_CITE_AUTHOR, FAB_CITE_JOURNAL)
        vbox.addWidget(cite)

    def get_process(self):
        return self.FabberProcess(self.ivm)

    def batch_options(self):
        return "Fabber", self.get_rundata()

    def get_rundata(self):
        rundata = {}
        rundata["model-group"] = "dsc"
        rundata["save-mean"] = ""
        rundata["save-model-fit"] = ""
        rundata["noise"] = "white"
        rundata["max-iterations"] = "20"
        rundata["model"] = "dsc"
        return rundata

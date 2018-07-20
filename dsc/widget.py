"""
Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

from PySide import QtGui

from quantiphyse.gui.widgets import QpWidget, Citation, TitleWidget, RunBox
from quantiphyse.gui.options import OptionBox, ChoiceOption, NumericOption, BoolOption, VectorOption
from quantiphyse.utils import get_plugins, QpException

from ._version import __version__

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class FabberDscWidget(QpWidget):
    """
    DSC modelling, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="DSC", icon="fabber", group="DSC-MRI", desc="Bayesian modelling for DSC-MRI", **kwargs)
        
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

        hbox = QtGui.QHBoxLayout()

        self.options = OptionBox("Options")
        self.model = self.options.add("Model choice", ChoiceOption(["Classic", "Control point interpolation"], ["dsc", "dsc_cpi"]), key="model")
        self.model.sig_changed.connect(self._model_changed)

        self.options.add("TE (s)", NumericOption(minval=0, maxval=5, default=1), key="te")
        self.options.add("Time interval between volumes (s)", NumericOption(minval=0, maxval=10, default=1), key="delt")
        self.options.add("AIF", VectorOption([0, ]), ChoiceOption(["Signal", "Concentration"], [False, True]), keys=("aif", "aifconc"))

        hbox.addWidget(self.options)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        self.classic_options = OptionBox("Classic model")
        self.classic_options.add("Infer MTT", BoolOption(), key="infermtt")
        hbox.addWidget(self.classic_options)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        hbox = QtGui.QHBoxLayout()
        self.cpi_options = OptionBox("CPI model")
        self.cpi_options.setVisible(False)
        self.cpi_options.add("Number of control points", NumericOption(minval=3, maxval=20, default=5, intonly=True), key="num-cps")
        self.cpi_options.add("Infer control point time position", BoolOption(), key="infer-cpt")
        hbox.addWidget(self.cpi_options)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        run_box = RunBox(self.get_process, self.get_rundata)
        vbox.addWidget(run_box)

        vbox.addStretch(1)

    def get_process(self):
        return self.FabberProcess(self.ivm)

    def batch_options(self):
        return "Fabber", self.get_rundata()

    def get_rundata(self):
        rundata = {
            "model-group" : "dsc",
            "save-mean" : True,
            "save-model-fit" : True,
            "save-model-extras" : True,
            "noise": "white",
            "max-iterations": 20,
        }
        rundata.update(self.options.values())
        if self.model.value == "dsc":
            rundata.update(self.classic_options.values())
        elif self.model.value == "dsc_cpi":
            rundata.update(self.cpi_options.values())

        return rundata

    def _model_changed(self):
        self.classic_options.setVisible(self.model.value == "dsc")
        self.cpi_options.setVisible(self.model.value == "dsc_cpi")

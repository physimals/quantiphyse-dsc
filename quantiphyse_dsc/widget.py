"""
Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

from PySide import QtGui

from quantiphyse.gui.widgets import QpWidget, Citation, TitleWidget, RunWidget
from quantiphyse.gui.options import OptionBox, DataOption, ChoiceOption, NumericOption, BoolOption, VectorOption
from quantiphyse.utils import get_plugins

from ._version import __version__

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class AifWidget(QtGui.QWidget):
    """
    Widget allowing choice of AIF
    """
    def __init__(self, ivm):
        QtGui.QWidget.__init__(self)
        self.ivm = ivm

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.optbox = OptionBox()
        self.optbox.add("AIF source", ChoiceOption(["Global sequence of values", "Voxelwise image"], ["global", "voxelwise"]), key="aif_source")
        self.optbox.option("aif_source").sig_changed.connect(self._aif_source_changed)
        self.optbox.add("AIF", VectorOption([0, ]), key="aif")
        self.optbox.add("AIF image", DataOption(self.ivm), key="suppdata")
        self.optbox.add("AIF type", ChoiceOption(["DSC signal", "Concentration"], [False, True]), key="aifconc")
        vbox.addWidget(self.optbox)
        vbox.addStretch()
        self._aif_source_changed()
        
    def options(self):
        """ :return: Dictionary of options selected for the AIF"""
        opts = self.optbox.values()
        opts.pop("aif_source")
        return opts
        
    def  _aif_source_changed(self):
        global_aif = self.optbox.option("aif_source").value == "global"
        self.optbox.set_visible("aif", global_aif)
        self.optbox.set_visible("suppdata", not global_aif)

class DscOptionsWidget(QtGui.QWidget):
    """
    Widget allowing choice of DSC options
    """
    def __init__(self, ivm):
        QtGui.QWidget.__init__(self)
        self.ivm = ivm
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.optbox = OptionBox()

        self.optbox.add("DSC Data", DataOption(self.ivm), key="data")
        self.optbox.add("ROI", DataOption(self.ivm, rois=True, data=False), key="mask")
        self.optbox.add("Model choice", ChoiceOption(["Standard", "Control point interpolation"], ["dsc", "dsc_cpi"]), key="model")
        self.optbox.add("TE (s)", NumericOption(minval=0, maxval=0.1, default=0), key="te")
        self.optbox.add("Time interval between volumes (s)", NumericOption(minval=0, maxval=10, default=1), key="delt")
        self.optbox.add("Apply dispersion to AIF", BoolOption(), key="disp")
        self.optbox.add("Infer delay parameter", BoolOption(default=True), key="inferdelay")
        self.optbox.add("Infer arterial component", BoolOption(), key="inferart")
        self.optbox.add("Spatial regularization", BoolOption(default=True), key="spatial")
        self.optbox.option("model").sig_changed.connect(self._model_changed)

        vbox.addWidget(self.optbox)

        hbox = QtGui.QHBoxLayout()
        self.classic_options = OptionBox("Standard model")
        self.classic_options.add("Infer MTT", BoolOption(default=True), key="infermtt")
        self.classic_options.add("Infer lambda", BoolOption(default=True), key="inferlambda")
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

        vbox.addStretch()
        
    def options(self):
        """ :return: Dictionary of options selected for the DSC analysis"""
        opts = self.optbox.values()
        if opts["model"] == "dsc":
            opts.update(self.classic_options.values())
        elif opts["model"] == "dsc_cpi":
            opts.update(self.cpi_options.values())
        if opts.pop("spatial", False):
            opts["method"] = "spatialvb"
            opts["param-spatial-priors"] = "N+M"
        return opts
        
    def _model_changed(self):
        classic = self.optbox.option("model").value == "dsc"
        self.classic_options.setVisible(classic)
        self.cpi_options.setVisible(not classic)

class FabberDscWidget(QpWidget):
    """
    DSC modelling, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="DSC", icon="dsc", group="DSC-MRI", desc="Bayesian modelling for DSC-MRI", **kwargs)
        
    def init_ui(self):
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        try:
            proc = get_plugins("processes", "FabberProcess")[0]
        except:
            proc = None

        if proc is None:
            vbox.addWidget(QtGui.QLabel("Fabber core library not found.\n\n You must install Fabber to use this widget"))
            return
        
        title = TitleWidget(self, help="fabber-dsc", subtitle="Bayesian modelling for DSC-MRI %s" % __version__)
        vbox.addWidget(title)
              
        cite = Citation(FAB_CITE_TITLE, FAB_CITE_AUTHOR, FAB_CITE_JOURNAL)
        vbox.addWidget(cite)

        tabs = QtGui.QTabWidget()
        vbox.addWidget(tabs)
        self.dsc_widget = DscOptionsWidget(self.ivm)
        tabs.addTab(self.dsc_widget, "DSC Options")
        self.aif_widget = AifWidget(self.ivm)
        tabs.addTab(self.aif_widget, "AIF")
        vbox.addWidget(tabs)
        
        vbox.addWidget(RunWidget(self))

        vbox.addStretch(1)

    def processes(self):
        opts = {
            "model-group" : "dsc",
            "save-mean" : True,
            "save-model-fit" : True,
            "save-model-extras" : True,
            "noise": "white",
            "max-iterations": 20,
            "output-rename" : {
                "mean_cbf" : "rCBF",
                "mean_transitm" : "MTT",
                "mean_lambda" : "lam",
            }
        }
        opts.update(self.dsc_widget.options())
        opts.update(self.aif_widget.options())
        return {
            "Fabber" : opts
        }
"""
DSC Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""
import os.path

from .widget import FabberDscWidget

QP_MANIFEST = {
    "widgets" : [FabberDscWidget],
    "fabber_dirs" : [os.path.dirname(__file__)],
}

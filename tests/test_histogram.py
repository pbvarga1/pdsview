#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdsview import pdsview, histogram
import pytestqt
import pytest
import numpy as np
from matplotlib.lines import Line2D
from ginga.qtw.QtHelp import QtGui, QtCore
import os


FILE_1 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')

test_images = pdsview.ImageSet([FILE_1, FILE_2])
window = pdsview.PDSViewer(test_images)
image_view = window.pds_view


def test_model_init():
    model = histogram.HistogramModel(image_view)
    assert model._image_view == image_view
    assert model._views == set()
    assert model._cut_low is None
    assert model._cut_high is None
    assert model._bins == 100


def test_model_image_view():
    image_view = window.pds_view
    model = histogram.HistogramModel(image_view)
    model.image_view == image_view
    model.image_view == model._image_view
    # Test setter method
    image_view2 = pdsview.PDSViewer(pdsview.ImageSet([FILE_3])).pds_view
    model.image_view = image_view2
    assert model.image_view == image_view2


def test_model_cut_low():
    model = histogram.HistogramModel(image_view)
    assert model.cut_low == model.view_cuts[0]
    assert model.cut_low == model._cut_low
    # Test Setting
    model.cut_low = 42
    assert model.cut_low == 42
    assert model._cut_low == 42
    assert model.view_cuts[0] == 42


def test_model_cut_high():
    model = histogram.HistogramModel(image_view)
    assert model.cut_high is model.view_cuts[1]
    assert model.cut_high == model._cut_high
    # Test Setting
    model.cut_high = 42
    assert model.cut_high == 42
    assert model._cut_high== 42
    assert model.view_cuts[1] == 42


def test_model_cuts():
    def test_new_cuts(new_cuts, model):
        model.cuts = new_cuts
        assert model.cuts == new_cuts
        assert model.cut_low == new_cuts[0]
        assert model.cut_high == new_cuts[1]
        assert model.view_cuts == new_cuts
    model = histogram.HistogramModel(image_view)
    assert model.cuts == model.view_cuts
    # Test Setter
    test_new_cuts((24, 42), model)
    test_new_cuts((20, 42), model)
    test_new_cuts((20, 40), model)
    with pytest.warns(UserWarning):
        model.cuts = 42, 24
    assert model.cuts == (24, 42)


def test_model_view_cuts():
    model = histogram.HistogramModel(image_view)
    assert model.view_cuts == image_view.get_cut_levels()


def test_bins():
    model = histogram.HistogramModel(image_view)
    assert model.bins == model._bins
    # Test Setter
    model.bins = 42
    assert model.bins == 42
    assert model.bins == model._bins


def test_model_data():
    model = histogram.HistogramModel(image_view)
    assert np.array_equal(model.data, image_view.get_image().data)


def test_model_register():
    model = histogram.HistogramModel(image_view)
    mock_view = QtGui.QWidget()
    model.register(mock_view)
    assert mock_view in model._views


def test_model_unregister():
    model = histogram.HistogramModel(image_view)
    mock_view = QtGui.QWidget()
    model.register(mock_view)
    assert mock_view in model._views
    model.unregister(mock_view)
    assert mock_view not in model._views


def test_model_restore():
    model = histogram.HistogramModel(image_view)
    assert model.cuts == model.view_cuts
    image_view.cut_levels(24, 42)
    model.cuts = 10, 100
    model.restore()
    assert model.cuts == model.view_cuts


def test_model__set_view_cuts():
    model = histogram.HistogramModel(image_view)
    model._cut_low = 24
    model._cut_high = 42
    model._set_view_cuts()
    assert model.view_cuts == (24, 42)


def test_controller_set_cut_low():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_cut_low(24)
    assert model.cut_low == 24
    assert model.view_cuts[0] == 24


def test_controller_set_cut_high():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_cut_high(42)
    assert model.cut_high == 42
    assert model.view_cuts[1] == 42


def test_controller_set_cuts():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_cuts(10, 100)
    assert model.cut_low == 10
    assert model.cut_high == 100
    assert model.cuts == (10, 100)
    assert model.view_cuts == (10, 100)


def test_controller_set_bins():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_bins(50)
    assert model.bins == 50


def test_controller_restore():
    model = histogram.HistogramModel(image_view)
    def_cuts = model.view_cuts
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    model.cuts = 24, 42
    image_view.cut_levels(*def_cuts)
    test_controller.restore()
    assert model.cuts != (24, 42)
    assert model.cuts == def_cuts
    assert model.view_cuts == def_cuts



def test_histogram_init():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    assert test_hist.model == model
    assert test_hist in model._views
    assert test_hist.sizePolicy().hasHeightForWidth()
    assert test_hist._right_vline is None
    assert test_hist._left_vline is None


def test_histogram_set_vlines():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    assert isinstance(test_hist._left_vline, Line2D)
    assert isinstance(test_hist._right_vline, Line2D)
    assert test_hist._left_vline.get_xdata()[0] == model.cut_low
    assert test_hist._right_vline.get_xdata()[0] == model.cut_high


def test_histogram_change_cut_low():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    model._cut_low = 24
    test_hist.change_cut_low(draw=False)
    assert test_hist._left_vline.get_xdata()[0] == 24
    assert test_hist._right_vline.get_xdata()[0] == model.cut_high


def test_histogram_change_cut_high():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    model._cut_high = 42
    test_hist.change_cut_high(draw=False)
    assert test_hist._right_vline.get_xdata()[0] == 42
    assert test_hist._left_vline.get_xdata()[0] == model.cut_low


def test_histogram_change_cuts():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    model._cut_low = 24
    model._cut_high = 42
    test_hist.change_cuts()
    assert test_hist._left_vline.get_xdata()[0] == 24
    assert test_hist._right_vline.get_xdata()[0] == 42


def test_histogram_change_bins():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist.set_data()
    assert model.bins == 100
    assert len(test_hist._ax.patches) == 100
    model._bins = 50
    test_hist.change_bins()
    assert len(test_hist._ax.patches) == 50


# def test_histogram_move_line(qtbot):
#     window.show()
#     qtbot.addWidget(window)
#     qtbot.

"""
A little GUI that allows to load and look at OCT volumes stored
as 3D Numpy arrays.
"""
from __future__ import print_function

import sys

import os.path as op
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from glob import glob
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Button, Slider


class OCTViewer(object):
    def __init__(self, datapath):
        self.cubepaths = self.read_cubepaths(datapath)
        self.cubeidx = 0
        self.cube_original = None
        self.cube = None
        self.x = None
        self.y = None
        self.z = None
        self.threshold = 255
        self.init_gui()

    def init_gui(self):
        mpl.rcParams['toolbar'] = 'None'
        bkg_color = (0.9, 0.9, 0.9)
        self.fig = plt.figure('OCT Viewer', figsize=(7, 7),
                              facecolor=bkg_color)

        # scans and cube plots
        self.plt1 = self.fig.add_subplot(221)
        self.plt2 = self.fig.add_subplot(222)
        self.plt3 = self.fig.add_subplot(223)
        self.plt4 = self.fig.add_subplot(224, projection='3d')

        # Buttons
        self.fig.subplots_adjust(bottom=0.2)  # space for buttons
        axprev = self.fig.add_axes([0.4, 0.05, 0.1, 0.07])
        axnext = self.fig.add_axes([0.5, 0.05, 0.1, 0.07])
        self.bnext = Button(axnext, '>>', color='white')
        self.bnext.on_clicked(self.next_cube)
        self.bprev = Button(axprev, '<<', color='white')
        self.bprev.on_clicked(self.prev_cube)

        # Slider
        axthresh = self.fig.add_axes([0.1, 0.15, 0.8, 0.02])
        self.sthresh = Slider(axthresh, 'Thres', 0, 255, 255, '%3.0f',
                              color='lightgray')
        self.sthresh.on_changed(self.update_threshold)

        self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def read_cubepaths(self, datapath):
        inpath = op.join(datapath, '*.npy')
        return [fn for fn in glob(inpath)]

    def load_cube(self):
        assert self.cubepaths, "No cubes found! Correct data path?"
        path = self.cubepaths[self.cubeidx]
        name = op.basename(path).replace('.npy', '')
        self.fig.suptitle(name)
        self.cube_original = np.load(path)
        self.update_threshold(self.threshold, False)

    def init_cursor(self):
        if self.x is None:
            self.z, self.x, self.y = [s // 2 for s in self.cube.shape[:3]]

    def show_cube(self, threshold=120):
        self.plt4.clear()
        self.plt4.set_axis_off()
        return  # disabled for speed
        # self.plt4.set_xticks([])
        # self.plt4.set_yticks([])
        # self.plt4.set_zticks([])
        # cube = self.cube.max(axis=3)  # max of RGB
        cube = self.cube[:, :, :, 2]  # only blue channel
        xs, ys, zs = np.where(cube > threshold)
        colors = self.cube[cube > threshold] / 255.0
        self.plt4.scatter(zs, ys, xs, c=colors,
                         marker='.', alpha=0.3, linewidth=0.0)

    def show_scans(self):
        self.init_cursor()

        self.plt1.clear()
        self.plt2.clear()
        self.plt3.clear()

        self.plt1.axis('off')
        self.plt2.axis('off')
        self.plt3.axis('off')

        linecolor = (1, 1, 0, 0.2)
        self.plt1.imshow(self.cube[self.z, :, :], aspect='auto')
        self.plt1.axvline(x=self.x, color=linecolor)
        self.plt1.axhline(y=self.y, color=linecolor)
        self.plt2.imshow(self.cube[:, self.x, :], aspect='auto')
        self.plt2.axvline(x=self.x, color=linecolor)
        self.plt2.axhline(y=self.z, color=linecolor)
        self.plt3.imshow(self.cube[:, :, self.y], aspect='auto')
        self.plt3.axvline(x=self.y, color=linecolor)
        self.plt3.axhline(y=self.z, color=linecolor)

        self.fig.canvas.draw_idle()

    def next_cube(self, event=None):
        self.cubeidx = min(self.cubeidx + 1, len(self.cubepaths) - 1)
        self.load_cube()
        self.show_cube()
        self.show_scans()

    def prev_cube(self, event=None):
        self.cubeidx = max(self.cubeidx - 1, 0)
        self.load_cube()
        self.show_cube()
        self.show_scans()

    def on_key(self, event):
        if event.key == 'right':
            self.next_cube()
        if event.key == 'left':
            self.prev_cube()

    def on_hover(self, event):
        if event.button != 1:  # left mouse button
            return
        if event.inaxes == self.plt1.axes:
            self.x, self.y = int(event.xdata), int(event.ydata)
            self.show_scans()
        if event.inaxes == self.plt2.axes:
            self.x, self.z = int(event.xdata), int(event.ydata)
            self.show_scans()
        if event.inaxes == self.plt3.axes:
            self.y, self.z = int(event.xdata), int(event.ydata)
            self.show_scans()

    def update_threshold(self, val, redraw=True):
        self.threshold = int(val)
        self.cube = self.cube_original.copy()
        if self.threshold < 255:
            self.cube[:, :, :, 0] = 0
            threshold = self.threshold/255.0 * np.max(self.cube)
            self.cube[self.cube > threshold] = 255
        if redraw:
            self.show_scans()

    def run(self):
        self.load_cube()
        self.show_cube()
        self.show_scans()
        plt.show()


if __name__ == '__main__':
    datapath = '.' if len(sys.argv) < 2 else sys.argv[1]
    viewer = OCTViewer(datapath)
    viewer.run()

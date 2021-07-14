#!/usr/bin/python

from matplotlib import pyplot as plt

class Item():
    def __init__(self, *args, **kwargs) :
        pass

    def generate_ax(self):
       fig, ax = plt.subplots(1, 1,figsize=(20,10))
       self.ax = ax    
    
    def draw(self):
        pass
    
    def savefig(self,filename):
        print('in savefig')
        if (hasattr(self,'ax')) and (self.ax is not None):
            self.ax.get_figure().savefig(filename)


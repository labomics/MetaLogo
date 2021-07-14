#!/usr/bin/python
from character import Character
from item import Item

class Column(Item):

    def __init__(self, bases, weights, ax=None, v_margin=0.1, *args, **kwargs):
        super(Column, self).__init__(*args, **kwargs)
        self.bases = bases 
        self.weights = weights 
        self.v_margin = v_margin
        #self.path_hight, self.init_hight, self.target_height = self.get_heights()
        self.characters = []
        if ax == None:
            self.generate_ax()
        else:
            self.ax = ax
        self.generate_components()

    def generate_components(self):
        for base,weight in zip(self.bases,self.weights):
            character = Character(base,target_size=(1,weight),ax=self.ax)
            self.characters.append(character)
    
    #def get_heights(self):
    #    path_height = 0
    #    init_heigth = 0
    #    target_height = 0
    #    for character in self.characters:
    #        path_height += character.get_extents().height 
    #        init_heigth += character.init_size[1] + self.v_margin
    #        target_height += character.target_size[1] + self.v_margin
    #    
    #    return path_height, init_heigth, target_height
    
    #def transform(self):
    #    for character in self.characters:
    #        character.transform()
    
    #def get_coordinate(self,index):
    #    return self.characters[index].target_coordinate
    
    def draw(self):
        for character in self.characters:
            character.draw()


        


#!/usr/bin/python
from character import Character
from item import Item

class Column(Item):

    def __init__(self, bases, weights, ax=None, start_pos=(0,0), char_margin=0.02, *args, **kwargs):
        super(Column, self).__init__(*args, **kwargs)
        self.bases = bases 
        self.weights = weights 
        self.char_margin = char_margin
        self.start_pos = start_pos
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
    #        init_heigth += character.init_size[1] + self.char_margin
    #        target_height += character.target_size[1] + self.char_margin
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
    
    def compute_positions(self):
        start_pos = self.start_pos
        for character in self.characters:
            character.set_start_pos(start_pos)
            character.compute_positions()
            start_pos = (start_pos[0], start_pos[1] + character.get_height() + self.char_margin)
    
    def get_height(self):
        return sum([char.get_height() + self.char_margin for char in self.characters])
    def get_width(self):
        return max([char.get_width()  for char in self.characters])



        


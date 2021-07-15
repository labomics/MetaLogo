#!/usr/bin/python
from character import Character
from item import Item

class Column(Item):

    def __init__(self, bases, weights, ax=None, start_pos=(0,0), logo_type = 'Horizontal', char_margin=0.02, width=1, parent_start=(0,0), *args, **kwargs):
        super(Column, self).__init__(*args, **kwargs)
        self.bases = bases 
        self.weights = weights 
        self.width = width
        self.char_margin = char_margin
        self.start_pos = start_pos
        self.parent_start = parent_start
        self.logo_type = logo_type
        #self.path_hight, self.init_hight, self.target_height = self.get_heights()
        self.characters = []
        if ax == None:
            self.generate_ax()
        else:
            self.ax = ax
        self.generate_components()

    def generate_components(self):
        for base,weight in zip(self.bases,self.weights):
            character = Character(base,width=self.width,height=weight,ax=self.ax,
                                    logo_type=self.logo_type, parent_start=self.start_pos)
            self.characters.append(character)
    
    def draw(self):
        for character in self.characters:
            character.draw()
    
    def compute_positions(self):
        start_pos = self.start_pos
        for character in self.characters:
            character.set_start_pos(start_pos)
            character.set_parent_start(self.start_pos)
            if self.logo_type == 'Circle':
                character.set_deg(self.deg)
                character.set_width(self.width)
            character.compute_positions()
            start_pos = (start_pos[0], start_pos[1] + character.get_height() + self.char_margin)
    
    def get_height(self):
        return sum([char.get_height() + self.char_margin for char in self.characters])
    def get_width(self):
        return max([char.get_width()  for char in self.characters])



        


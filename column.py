#!/usr/bin/python
from character import Character

class Column:

    def __init__(self, characters, weights, v_margin):
        self.characters = characters
        self.weights = characters
        self.v_margin = v_margin
        self.path_hight, self.init_hight, self.target_height = self.get_heights()
    
    def get_heights(self):
        path_height = 0
        init_heigth = 0
        target_height = 0
        for character in self.characters:
            path_height += character.get_extents().height 
            init_heigth += character.init_size[1] + self.v_margin
            target_height += character.target_size[1] + self.v_margin
        
        return path_height, init_heigth, target_height
    
    def transform(self):
        for character in self.characters:
            character.transform()
    
    def get_coordinate(self,index):
        return self.characters[index].target_coordinate

        


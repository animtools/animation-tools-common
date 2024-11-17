from dataclasses import dataclass

@dataclass
class Rect:
    left: int
    top: int
    width: int 
    height: int

@dataclass
class RectF:
    left: float
    top: float
    width: float 
    height: float

    def scaled(self, scale:float):
        return RectF(self.left*scale, self.top*scale, self.width*scale, self.height*scale)
    
    def to_tuple(self):
        return (self.left, self.top, self.width, self.height)

@dataclass
class GridRectF(RectF):
    columns: int
    # rows: int
    def scaled(self, scale:float):
        return GridRectF(self.left*scale, self.top*scale, self.width*scale, self.height*scale, self.columns)


class QColor:
    NAMED_COLORS = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'darkgray': (64, 64, 64),
        'lightgray': (192, 192, 192),
        'transparent': (0, 0, 0, 0)
    }
    _parse_cache = {}

    def __init__(self, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                arg_low = arg.lower()
                if arg_low in QColor._parse_cache:
                    self.r, self.g, self.b, self.a = QColor._parse_cache[arg_low]
                    return
                
                if arg_low in QColor.NAMED_COLORS:
                    self.r, self.g, self.b = QColor.NAMED_COLORS[arg_low]
                    self.a = 255
                else:
                    h = arg.lstrip('#')
                    if len(h) == 6: 
                        self.r, self.g, self.b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                        self.a = 255
                    elif len(h) == 8: 
                        self.r, self.g, self.b, self.a = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
                    else: 
                        self.r = self.g = self.b = self.a = 255
                QColor._parse_cache[arg_low] = (self.r, self.g, self.b, self.a)
            elif isinstance(arg, QColor): 
                self.r, self.g, self.b, self.a = arg.r, arg.g, arg.b, arg.a
            elif isinstance(arg, (list, tuple)) and len(arg) >= 3:
                self.r, self.g, self.b = arg[:3]
                self.a = arg[3] if len(arg) > 3 else 255
            else: 
                self.r = self.g = self.b = self.a = 255
        elif len(args) >= 3: 
            self.r, self.g, self.b = args[:3]
            self.a = args[3] if len(args) > 3 else 255
        else: 
            self.r = self.g = self.b = 0; self.a = 255
    
    def to_pygame(self): return (self.r, self.g, self.b, self.a)
    def red(self): return self.r
    def green(self): return self.g
    def blue(self): return self.b
    def alpha(self): return self.a
    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a

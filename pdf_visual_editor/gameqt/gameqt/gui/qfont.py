import pygame

class QFont:
    _cache = {}
    
    def __init__(self, family="Arial", size=12): 
        self._family = family
        self._size = size
        self._bold = False
        self._italic = False
        
    def setPointSize(self, size): self._size = size
    def pointSize(self): return self._size
    def family(self): return self._family
    def setBold(self, b): self._bold = b
    def bold(self): return self._bold
    def setItalic(self, i): self._italic = i
    def italic(self): return self._italic
    
    def get_sys_font(self):
        from .qfontdatabase import QFontDatabase
        key = (self._family, self._size, self._bold)
        if key not in QFont._cache:
            custom_path = QFontDatabase.getFontPath(self._family)
            if custom_path:
                try:
                    f = pygame.font.Font(custom_path, self._size)
                    f.set_bold(self._bold)
                    QFont._cache[key] = f
                except Exception as e:
                    print(f"Failed to load custom font {self._family}: {e}")
                    QFont._cache[key] = pygame.font.SysFont(None, self._size, self._bold)
            else:
                QFont._cache[key] = pygame.font.SysFont(self._family if self._family != "Arial" else None, self._size, self._bold)
        return QFont._cache[key]

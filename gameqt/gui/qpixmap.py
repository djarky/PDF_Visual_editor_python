import pygame
from ..core import QSize, QRectF

class QImage:
    class Format:
        Format_RGB888 = 13
        Format_RGBA8888 = 26
    Format_RGB888 = 13
    Format_RGBA8888 = 26
    def __init__(self, *args):
        self.surface = None
        if len(args) == 1 and isinstance(args[0], pygame.Surface):
            self.surface = args[0]
        elif len(args) >= 3:
            if isinstance(args[0], (bytes, bytearray)):
                data, w, h, bpl, fmt = args
                mode = "RGBA" if fmt in (QImage.Format_RGBA8888, QImage.Format.Format_RGBA8888) else "RGB"
                self.surface = pygame.image.fromstring(bytes(data), (w, h), mode)
            else:
                w, h, fmt = args[:3]
                self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
    def isNull(self): return self.surface is None

class QPixmap:
    _image_cache = {}

    def __init__(self, arg=None, h=None):
        if h is not None:
             self.surface = pygame.Surface((arg, h), pygame.SRCALPHA)
        elif isinstance(arg, str): 
            if arg in QPixmap._image_cache:
                self.surface = QPixmap._image_cache[arg]
            else:
                try: 
                    self.surface = pygame.image.load(arg).convert_alpha()
                    QPixmap._image_cache[arg] = self.surface
                except: 
                    self.surface = None
        elif isinstance(arg, pygame.Surface): self.surface = arg
        elif isinstance(arg, QSize): self.surface = pygame.Surface((arg.width(), arg.height()), pygame.SRCALPHA)
        else: self.surface = None
    @staticmethod
    def fromImage(img): return QPixmap(img.surface) if hasattr(img, 'surface') else QPixmap()
    
    def _get_scaled_surface(self, w, h):
        """Internal method to get or create a cached scaled surface."""
        if not self.surface: return None
        if w <= 0 or h <= 0: return None
        
        # If size matches original, return original
        if w == self.width() and h == self.height():
            return self.surface
            
        # Check cache
        if not hasattr(self, '_scaled_cache'): self._scaled_cache = {}
        
        key = (w, h)
        if key in self._scaled_cache:
            return self._scaled_cache[key]
            
        # Create new scaled surface
        try:
            # Use smoothscale for quality, or scale for speed?
            # Smoothscale is better for text/PDF
            scaled = pygame.transform.smoothscale(self.surface, (w, h))
        except:
             # Fallback if smoothscale fails (e.g. 8-bit surface)
            scaled = pygame.transform.scale(self.surface, (w, h))
            
        # Add to cache (limit size)
        if len(self._scaled_cache) > 4:
            self._scaled_cache.clear()
        self._scaled_cache[key] = scaled
        return scaled

    def width(self): return self.surface.get_width() if self.surface else 0
    def height(self): return self.surface.get_height() if self.surface else 0
    def rect(self): return QRectF(0, 0, self.width(), self.height())
    def scaledToWidth(self, w, mode=None):
        if not self.surface or self.width() == 0: return self
        h = int(self.height() * (w / self.width())); return QPixmap(pygame.transform.smoothscale(self.surface, (w, h)))
    def toImage(self): return QImage(self.surface)
    def copy(self, rect):
        if not self.surface: return QPixmap()
        r = rect._to_pygame() if hasattr(rect, '_to_pygame') else (rect.toRect()._to_pygame() if hasattr(rect, 'toRect') else rect)
        # Ensure rect is within surface bounds to avoid pygame error
        surf_rect = self.surface.get_rect()
        clip_rect = surf_rect.clip(r)
        if clip_rect.width <= 0 or clip_rect.height <= 0:
            return QPixmap(pygame.Surface((1, 1), pygame.SRCALPHA))
        return QPixmap(self.surface.subsurface(clip_rect).copy())
    def save(self, buffer, fmt="PNG"):
        if not self.surface: return False
        try:
            if isinstance(buffer, str):
                pygame.image.save(self.surface, buffer)
            else:
                # Handle QBuffer or file-like object
                import io
                temp = io.BytesIO()
                pygame.image.save(self.surface, temp, fmt.lower())
                if hasattr(buffer, 'write'):
                    buffer.write(temp.getvalue())
                elif hasattr(buffer, 'setData'):
                    buffer.setData(temp.getvalue())
            return True
        except:
            return False

import pygame

class QUrl:
    def __init__(self, path=""): self._path = path
    def toLocalFile(self):
        # Handle file:/// URLs (file:// + /absolute/path)
        if self._path.startswith('file://'):
            return self._path[7:]  # Remove 'file://' keeping the leading /
        return self._path
    def toString(self): return self._path

class QMimeData:
    def __init__(self): self._data = {}; self._urls = []; self._image = None
    def setText(self, t): self._data['text/plain'] = t.encode('utf-8')
    def text(self): return self._data.get('text/plain', b'').decode('utf-8')
    def hasText(self): return 'text/plain' in self._data
    def setUrls(self, urls): self._urls = urls
    def urls(self): return self._urls
    def hasUrls(self): return len(self._urls) > 0
    def setData(self, mime, data): self._data[mime] = data
    def data(self, mime): return self._data.get(mime, b'')
    def setImageData(self, img): self._image = img
    def imageData(self): return self._image
    def hasImage(self): return self._image is not None or 'image/png' in self._data or 'image/jpeg' in self._data

class QClipboard:
    def __init__(self):
        self._fallback_text = ""
        self._scrap_available = False
    
    def _ensure_scrap(self):
        if not hasattr(self, '_scrap_available') or not self._scrap_available:
            try:
                if not pygame.scrap.get_init():
                    pygame.scrap.init()
                self._scrap_available = True
            except:
                self._scrap_available = False
        return self._scrap_available

    def setText(self, text):
        self._fallback_text = text
        if self._ensure_scrap():
            try:
                pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))
            except:
                pass
    
    def text(self):
        if self._ensure_scrap():
            # Try multiple text mime types as Linux flavors vary
            # scrap.get returns None or bytes
            for mime in [pygame.SCRAP_TEXT, "text/plain;charset=utf-8", "UTF8_STRING", "COMPOUND_TEXT", "STRING"]:
                try:
                    res = pygame.scrap.get(mime)
                    if res:
                        # Linux often returns null-terminated strings or bytes with nulls
                        val = res.decode('utf-8', errors='replace').split('\0')[0]
                        if val: return val
                except:
                    continue
        return self._fallback_text
    
    def setMimeData(self, mime):
        if mime.hasText(): self.setText(mime.text())
    
    def mimeData(self):
        m = QMimeData()
        t = self.text()
        if t: m.setText(t)
        return m

import pygame

class QKeySequence:
    class StandardKey: Cut = 1; Copy = 2; Paste = 3
    def __init__(self, key_str):
        self._key_str = key_str
        self._keys = []
        self._modifiers = 0
        
        parts = key_str.split('+')
        for p in parts:
            p = p.strip().upper()
            if p == 'CTRL': self._modifiers |= pygame.KMOD_CTRL
            elif p == 'ALT': self._modifiers |= pygame.KMOD_ALT
            elif p == 'SHIFT': self._modifiers |= pygame.KMOD_SHIFT
            else:
                # Try to find the key in pygame constants
                try: 
                    k_attr = f"K_{p.lower()}" if len(p) == 1 else f"K_{p}"
                    self._keys.append(getattr(pygame, k_attr))
                except AttributeError:
                    print(f"[gui.QKeySequence] Unknown key sequence part: {p}")
    
    def matches(self, key, mods):
        # Simplistic check
        if not self._keys: return False
        return key == self._keys[0] and (mods & self._modifiers) == self._modifiers

    @staticmethod
    def matches_static(k1, k2): 
        # k1 and k2 are likely QKeySequence or strings
        s1 = k1._key_str if hasattr(k1, '_key_str') else str(k1)
        s2 = k2._key_str if hasattr(k2, '_key_str') else str(k2)
        return s1.upper() == s2.upper()

import os
import pygame

class QFontDatabase:
    """
    Manages custom fonts loaded from application files.
    """
    _custom_fonts = {} # family -> path
    
    @staticmethod
    def addApplicationFont(path):
        """
        Registers a font file with the application.
        Returns the family name if successful, empty string otherwise.
        """
        if not os.path.exists(path):
            print(f"Font path does not exist: {path}")
            return ""
            
        try:
            # We use pygame to get the family name if possible, 
            # though pygame.font.Font doesn't directly expose family name easily from file
            # For now, we use the filename (without extension) as the family name
            # in a real Qt implementation it would read the TTF metadata.
            family = os.path.splitext(os.path.basename(path))[0]
            QFontDatabase._custom_fonts[family] = path
            return family
        except Exception as e:
            print(f"Failed to load font {path}: {e}")
            return ""
            
    @staticmethod
    def getFontPath(family):
        """Returns the registered path for a font family or None."""
        return QFontDatabase._custom_fonts.get(family)
        
    @staticmethod
    def families():
        """Returns a list of all available font families (system + custom)."""
        families = set(QFontDatabase._custom_fonts.keys())
        # Add system families if needed, but pygame.font.get_fonts() works for SysFont
        return sorted(list(families))

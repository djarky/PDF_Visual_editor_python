
import re

class QSSParser:
    """
    A basic parser for QSS (Qt Style Sheets) files.
    Supports selectors (class names, IDs with #, and :hover state) and property-value pairs.
    """
    @staticmethod
    def parse(qss_text):
        if not qss_text:
            return {}
            
        # Remove comments: /* ... */
        qss_text = re.sub(r'/\*.*?\*/', '', qss_text, flags=re.DOTALL)
        
        styles = {}
        # Find blocks: selectors { rules }
        # This regex matches blocks even with nested-ish content or multiple selectors.
        blocks = re.findall(r'([^{]+)\s*\{\s*([^}]+)\s*\}', qss_text)
        
        for selectors, rules in blocks:
            # Handle multiple selectors separated by comma: QWidget, QMainWindow
            for selector in selectors.split(','):
                selector = selector.strip()
                if not selector:
                    continue
                
                if selector not in styles:
                    styles[selector] = {}
                
                # Parse rules: property: value;
                # Rules are separated by semicolons.
                for rule in rules.split(';'):
                    rule = rule.strip()
                    if ':' in rule:
                        prop, val = rule.split(':', 1)
                        p_name = prop.strip().lower()
                        p_val = val.strip().lower()
                        styles[selector][p_name] = p_val
        
        return styles

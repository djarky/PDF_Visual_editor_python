
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
            
        # Detect if it's just a set of rules (no blocks)
        if '{' not in qss_text:
            return {"*": QSSParser.parse_rules(qss_text)}

        # Remove comments: /* ... */
        qss_text = re.sub(r'/\*.*?\*/', '', qss_text, flags=re.DOTALL)
        
        styles = {}
        # Find blocks: selectors { rules }
        blocks = re.findall(r'([^{]+)\s*\{\s*([^}]+)\s*\}', qss_text)
        
        for selectors, rules in blocks:
            parsed_rules = QSSParser.parse_rules(rules)
            for selector in selectors.split(','):
                selector = selector.strip()
                if not selector: continue
                if selector not in styles:
                    styles[selector] = {}
                styles[selector].update(parsed_rules)
        
        return styles

    @staticmethod
    def parse_rules(rules_text):
        """Parses a string of rules like 'color: red; margin: 5px' into a dict."""
        rules = {}
        for rule in rules_text.split(';'):
            rule = rule.strip()
            if ':' in rule:
                prop, val = rule.split(':', 1)
                p_name = prop.strip().lower()
                p_val = val.strip().lower()
                rules[p_name] = p_val
        return rules

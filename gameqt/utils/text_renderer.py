import pygame
from PIL import Image, ImageDraw, ImageFont
import os
import re

# Common emoji font paths
EMOJI_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto-emoji/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf",
]

# Common regular font paths for fallback
REGULAR_FONTS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

_emoji_font_path = None
for path in EMOJI_FONTS:
    if os.path.exists(path):
        _emoji_font_path = path
        break

_regular_font_path = None
for path in REGULAR_FONTS:
    if os.path.exists(path):
        _regular_font_path = path
        break

# Caches for performance optimization
_variant_cache = {}  # (path, bold, italic) -> resolved_path
_font_cache = {}     # (path, target_h) -> ImageFont
_render_cache = {}   # (text, font_family, font_size, color_tuple, bold, italic) -> pygame.Surface

def has_emoji(text):
    """Check if text contains high-surrogate emojis (U+10000+)."""
    return any(ord(c) > 0xFFFF for c in text)

def get_calibrated_font(path, target_h):
    """Binary search for exact pixel height (ascent + descent). Cached."""
    if not path or not os.path.exists(path): return ImageFont.load_default()
    target_h = max(1, int(target_h))
    
    key = (path, target_h)
    if key in _font_cache: return _font_cache[key]
    
    low, high = 1, 500
    best_f = None
    for _ in range(10):
        mid = (low + high) // 2
        if mid < 1: mid = 1
        try:
            f = ImageFont.truetype(path, int(mid))
            asc, desc = f.getmetrics()
            h = asc + desc
            if h < target_h: low = mid + 1; best_f = f
            elif h > target_h: high = mid - 1
            else: 
                _font_cache[key] = f
                return f
        except: 
            low = mid + 1
            if low > high: break
    
    res = best_f
    if not res:
        try: res = ImageFont.truetype(path, target_h)
        except: res = ImageFont.load_default()
    
    _font_cache[key] = res
    return res

def find_font_variant(path, bold=False, italic=False):
    """Finds the bold/italic variant for a given font path. Cached."""
    if not path or not os.path.exists(path): return path
    if not bold and not italic: return path
    
    key = (path, bold, italic)
    if key in _variant_cache: return _variant_cache[key]
    
    dir_name = os.path.dirname(path)
    base_name = os.path.basename(path)
    name, ext = os.path.splitext(base_name)
    
    # Try common suffixes
    suffixes = []
    if bold and italic: suffixes = ["-BoldItalic", "BoldItalic", "-BoldOblique", "BoldOblique", "BI", "Z"]
    elif bold: suffixes = ["-Bold", "Bold", "B"]
    elif italic: suffixes = ["-Italic", "Italic", "-Oblique", "Oblique", "I"]
    
    res = path
    # Try basic substitutions
    for s in suffixes:
        test_names = [
            f"{name}{s}{ext}",
            f"{name.replace('Regular', '')}{s}{ext}",
            f"{name.replace('-Regular', '')}{s}{ext}",
        ]
        for t in test_names:
            p = os.path.join(dir_name, t)
            if os.path.exists(p): 
                res = p
                break
        if res != path: break
            
    if res == path:
        # Fallback to scanning the directory for fuzzy match
        try:
            keywords = []
            if bold: keywords.append("bold")
            if italic: keywords.append("italic")
            for f in os.listdir(dir_name):
                f_low = f.lower()
                if all(k in f_low for k in keywords) and ext.lower() in f_low:
                    if name[:4].lower() in f_low:
                         res = os.path.join(dir_name, f)
                         break
        except: pass
    
    _variant_cache[key] = res
    return res

def get_text_metrics(text, font_family, font_size, bold=False, italic=False):
    """Returns (width, height, ascent, descent). Multiline aware."""
    from ..gui.qfontdatabase import QFontDatabase
    pil_reg_font_path = _regular_font_path
    custom_path = QFontDatabase.getFontPath(font_family)
    if custom_path: pil_reg_font_path = custom_path
    
    pil_reg_font_path = find_font_variant(pil_reg_font_path, bold, italic)
    reg_f = get_calibrated_font(pil_reg_font_path, font_size)
    r_asc, r_desc = reg_f.getmetrics()
    target_h = r_asc + r_desc
    
    emo_f = ImageFont.load_default()
    if _emoji_font_path:
        emo_f = get_calibrated_font(_emoji_font_path, target_h)
            
    dummy = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy)
    
    lines = str(text).split('\n')
    max_w = 0
    spacing = 5
    
    def measure_line(line):
        if not has_emoji(line):
            return draw.textlength(line, font=reg_f)
        else:
            total_w = 0
            emoji_pattern = r'[\ud800-\udbff][\udc00-\udfff]'
            last_idx = 0
            for match in re.finditer(emoji_pattern, line):
                if match.start() > last_idx:
                    total_w += draw.textlength(line[last_idx:match.start()], font=reg_f)
                total_w += draw.textlength(match.group(), font=emo_f)
                last_idx = match.end()
            if last_idx < len(line):
                total_w += draw.textlength(line[last_idx:], font=reg_f)
            return total_w

    for line in lines:
        max_w = max(max_w, measure_line(line))
        
    total_h = target_h * len(lines) + (spacing * (len(lines) - 1) if len(lines) > 1 else 0)
    return int(max_w), int(total_h), r_asc, r_desc

def render_text(text, font_family, font_size, color, bold=False, italic=False):
    """Renders text to a pygame surface using Pillow. Fully cached."""
    # Ensure color is hashable tuple
    color_tup = tuple(color) if hasattr(color, '__iter__') else color
    cache_key = (str(text), font_family, font_size, color_tup, bold, italic)
    if cache_key in _render_cache:
        return _render_cache[cache_key]

    try:
        w, h, asc, desc = get_text_metrics(text, font_family, font_size, bold, italic)
        from ..gui.qfontdatabase import QFontDatabase
        
        pil_reg_font_path = _regular_font_path
        custom_path = QFontDatabase.getFontPath(font_family)
        if custom_path: pil_reg_font_path = custom_path
        
        pil_reg_font_path = find_font_variant(pil_reg_font_path, bold, italic)
        reg_f = get_calibrated_font(pil_reg_font_path, font_size)
        r_asc, r_desc = reg_f.getmetrics()
        target_h = r_asc + r_desc
        emo_f = ImageFont.load_default()
        if _emoji_font_path: emo_f = get_calibrated_font(_emoji_font_path, target_h)
        
        padding = 1
        spacing = 5
        surf_img = Image.new('RGBA', (max(1, w + padding*2), max(1, h + padding*2)), (0,0,0,0))
        draw = ImageDraw.Draw(surf_img)
        
        lines = str(text).split('\n')
        curr_y = padding
        
        for line in lines:
            if not has_emoji(line):
                segments = [(line, False)]
            else:
                emoji_pattern = r'[\ud800-\udbff][\udc00-\udfff](?:[\u200d\ufe0f][\ud800-\udbff][\udc00-\udfff])*'
                segments = []
                last_idx = 0
                for match in re.finditer(emoji_pattern, line):
                    if match.start() > last_idx: segments.append((line[last_idx:match.start()], False))
                    segments.append((match.group(), True))
                    last_idx = match.end()
                if last_idx < len(line): segments.append((line[last_idx:], False))
            
            curr_x = padding
            baseline_y = curr_y + r_asc
            for content, is_emo in segments:
                f = emo_f if is_emo else reg_f
                if is_emo:
                    try: 
                        if not f.getmask(content).getbbox(): f = reg_f
                    except: pass
                
                s_asc, s_desc = f.getmetrics()
                is_real_emoji = any(ord(c) > 0xFFFF for c in content)
                draw.text((curr_x, baseline_y - s_asc), content, font=f, fill=color, embedded_color=is_real_emoji)
                curr_x += draw.textlength(content, font=f)
            
            curr_y += target_h + spacing
            
        res = pygame.image.fromstring(surf_img.tobytes("raw", "RGBA"), surf_img.size, "RGBA")
        _render_cache[cache_key] = res
        return res
    except Exception as e:
        font = pygame.font.SysFont(None, font_size)
        font.set_bold(bold)
        font.set_italic(italic)
        return font.render(str(text), True, color)

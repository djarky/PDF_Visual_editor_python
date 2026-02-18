import pygame
import os
from ..core import PyGameModalDialog

class QFileDialog:
    @staticmethod
    def getOpenFileName(parent=None, caption="Open File", dir="", filter=""):
        dlg = FileDialog(caption, mode="open", directory=dir, filter=filter)
        return dlg.exec_()

    @staticmethod
    def getSaveFileName(parent=None, caption="Save File", dir="", filter=""):
        dlg = FileDialog(caption, mode="save", directory=dir, filter=filter)
        return dlg.exec_()

    @staticmethod
    def getExistingDirectory(parent=None, caption="Select Directory", dir=""):
        dlg = FileDialog(caption, mode="dir", directory=dir)
        res = dlg.exec_()
        return res[0] if res else ""

class FileDialog(PyGameModalDialog):
    def __init__(self, title, mode="open", directory="", filter=""):
        super().__init__(title, 600, 400)
        self.mode = mode
        self.current_dir = directory if directory else os.getcwd()
        self.filter = filter
        self.items = []
        self.selected_index = -1
        self.scroll_y = 0
        self.refresh_items()
        self.filename_input = ""
        
    def refresh_items(self):
        self.items = []
        try:
            # Add ".." for parent
            self.items.append({"name": "..", "is_dir": True})
            
            for f in sorted(os.listdir(self.current_dir)):
                if f.startswith("."): continue
                path = os.path.join(self.current_dir, f)
                is_dir = os.path.isdir(path)
                
                # Filter files based on extension if needed
                if not is_dir and self.filter and self.mode in ("open", "save"):
                    # Basic filter parsing logic (e.g. "*.pdf")
                    valid_exts = []
                    if "(" in self.filter:
                        # Extract from "Description (*.ext *.ext2)"
                        parts = self.filter.split("(")[1].split(")")[0].split()
                        valid_exts = [p.replace("*", "").lower() for p in parts]
                    
                    if valid_exts:
                        _, ext = os.path.splitext(f)
                        if ext.lower() not in valid_exts:
                            continue
                
                self.items.append({"name": f, "is_dir": is_dir})
                
            # Sort: Directories first, then files
            self.items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            
        except Exception as e:
            print(f"Error accessing directory: {e}")
            self.current_dir = os.getcwd() # Fallback

    def draw(self, screen):
        super().draw(screen)
        
        font = pygame.font.SysFont("Arial", 14)
        
        # Path Bar
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.x + 10, self.rect.y + 40, self.rect.width - 20, 25))
        pygame.draw.rect(screen, (150, 150, 150), (self.rect.x + 10, self.rect.y + 40, self.rect.width - 20, 25), 1)
        path_txt = font.render(self.current_dir[-60:], True, (0, 0, 0)) # Truncate for display
        screen.blit(path_txt, (self.rect.x + 15, self.rect.y + 45))
        
        # File List Area
        list_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 75, self.rect.width - 20, self.rect.height - 120)
        pygame.draw.rect(screen, (255, 255, 255), list_rect)
        pygame.draw.rect(screen, (150, 150, 150), list_rect, 1)
        
        # Draw items
        old_clip = screen.get_clip()
        screen.set_clip(list_rect)
        
        start_y = list_rect.y + 5 - self.scroll_y
        item_height = 20
        
        for i, item in enumerate(self.items):
            y = start_y + i * item_height
            if y > list_rect.bottom: break
            if y + item_height < list_rect.top: continue
            
            # Selection highlight
            if i == self.selected_index:
                pygame.draw.rect(screen, (0, 120, 215), (list_rect.x + 2, y, list_rect.width - 4, item_height))
                text_color = (255, 255, 255)
            else:
                text_color = (0, 0, 0)
                
            icon = "[D]" if item["is_dir"] else "[F]"
            t = font.render(f"{icon} {item['name']}", True, text_color)
            screen.blit(t, (list_rect.x + 5, y + 2))
            
        screen.set_clip(old_clip)
        
        # Footer
        footer_y = self.rect.bottom - 40
        if self.mode == "save":
            # Filename input box
            pygame.draw.rect(screen, (255, 255, 255), (self.rect.x + 80, footer_y, 200, 25))
            pygame.draw.rect(screen, (150, 150, 150), (self.rect.x + 80, footer_y, 200, 25), 1)
            fname_txt = font.render(self.filename_input, True, (0, 0, 0))
            screen.blit(fname_txt, (self.rect.x + 85, footer_y + 5))
            
            lbl = font.render("Filename:", True, (0,0,0))
            screen.blit(lbl, (self.rect.x + 10, footer_y + 5))

        # Buttons
        btn_width = 80
        ok_rect = pygame.Rect(self.rect.right - 180, footer_y, btn_width, 25)
        cancel_rect = pygame.Rect(self.rect.right - 90, footer_y, btn_width, 25)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # OK Button
        color = (0, 100, 200) if ok_rect.collidepoint(mouse_pos) else (0, 120, 215)
        pygame.draw.rect(screen, color, ok_rect, border_radius=3)
        ok_txt = font.render("Open" if self.mode == "open" else "Save", True, (255, 255, 255))
        screen.blit(ok_txt, (ok_rect.centerx - ok_txt.get_width()//2, ok_rect.centery - ok_txt.get_height()//2))
        
        # Cancel Button
        color = (200, 200, 200) if cancel_rect.collidepoint(mouse_pos) else (220, 220, 220)
        pygame.draw.rect(screen, color, cancel_rect, border_radius=3)
        cancel_txt = font.render("Cancel", True, (0, 0, 0))
        screen.blit(cancel_txt, (cancel_rect.centerx - cancel_txt.get_width()//2, cancel_rect.centery - cancel_txt.get_height()//2))

    def handle_key(self, event):
        super().handle_key(event)
        if self.mode == "save":
            if event.key == pygame.K_BACKSPACE:
                self.filename_input = self.filename_input[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.filename_input += event.unicode
        
        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            self.ensure_visible(self.selected_index)
        elif event.key == pygame.K_DOWN:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            self.ensure_visible(self.selected_index)
        elif event.key == pygame.K_RETURN:
            self.go_or_select()

    def ensure_visible(self, index):
        # Adjust scroll_y so index is visible
        list_height = self.rect.height - 120
        item_height = 20
        
        top_y = index * item_height
        bottom_y = top_y + item_height
        
        if top_y < self.scroll_y:
            self.scroll_y = top_y
        elif bottom_y > self.scroll_y + list_height:
            self.scroll_y = bottom_y - list_height

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                x, y = event.pos
                
                # Check file list click
                list_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 75, self.rect.width - 20, self.rect.height - 120)
                if list_rect.collidepoint(x, y):
                    idx = int((y - list_rect.y + self.scroll_y) // 20)
                    if 0 <= idx < len(self.items):
                        self.selected_index = idx
                        self.filename_input = self.items[idx]["name"] if not self.items[idx]["is_dir"] else self.filename_input
                        
                        # Double click detection (simplified - relying on swift consecutive clicks or just button)
                        # For now, just require clicking Open button or Enter key to confirm file
                        pass
                
                # Check Buttons
                footer_y = self.rect.bottom - 40
                ok_rect = pygame.Rect(self.rect.right - 180, footer_y, 80, 25)
                cancel_rect = pygame.Rect(self.rect.right - 90, footer_y, 80, 25)
                
                if ok_rect.collidepoint(x, y):
                    self.go_or_select()
                elif cancel_rect.collidepoint(x, y):
                    self.running = False
                    self.result = ("", "")
                    
            elif event.button == 4: # Scroll Up
                self.scroll_y = max(0, self.scroll_y - 20)
            elif event.button == 5: # Scroll Down
                max_scroll = max(0, len(self.items) * 20 - (self.rect.height - 120))
                self.scroll_y = min(max_scroll, self.scroll_y + 20)

    def go_or_select(self):
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if item["is_dir"]:
                # Enter directory
                path = os.path.abspath(os.path.join(self.current_dir, item["name"]))
                if os.path.exists(path):
                    self.current_dir = path
                    self.refresh_items()
                    self.selected_index = -1
                    self.scroll_y = 0
            else:
                # Select file
                path = os.path.abspath(os.path.join(self.current_dir, item["name"]))
                self.result = (path, self.filter)
                self.running = False
        elif self.mode == "save" and self.filename_input:
             # Save logic
             path = os.path.abspath(os.path.join(self.current_dir, self.filename_input))
             self.result = (path, self.filter)
             self.running = False

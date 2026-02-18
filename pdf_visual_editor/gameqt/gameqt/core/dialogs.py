import pygame

class PyGameModalDialog:
    def __init__(self, title="Dialog", width=400, height=300):
        self.title = title
        self.rect = pygame.Rect(0, 0, width, height)
        self.result = None
        self.running = False
        
    def exec_(self):
        screen = pygame.display.get_surface()
        if not screen: return
        
        # Capture background
        bg = screen.copy()
        
        # Center dialog
        sw, sh = screen.get_size()
        self.rect.center = (sw // 2, sh // 2)
        
        clock = pygame.time.Clock()
        self.running = True
        
        try:
            while self.running:
                # Event Loop
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.result = None
                    elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                        # Handle mouse interaction with dialog elements
                        try:
                            self.handle_event(event) # Custom handler
                        except Exception as e:
                            print(f"Error handling dialog event: {e}")
                    elif event.type == pygame.KEYDOWN:
                        self.handle_key(event)
                    elif event.type == pygame.VIDEORESIZE:
                        # Update background capture if resized
                        from ..application import QApplication
                        if QApplication._instance:
                            for win in QApplication._instance._windows:
                                from ..widgets import QMainWindow
                                if isinstance(win, QMainWindow):
                                    win.resize(event.w, event.h)
                                    win._screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                            # Re-capture background so it doesn't look stretched/empty
                            bg = pygame.display.get_surface().copy()
                            sw, sh = event.w, event.h
                            self.rect.center = (sw // 2, sh // 2)
                
                # Draw
                screen.blit(bg, (0, 0))
                
                # Dim background
                overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, (0, 0))
                
                # Draw Dialog
                try:
                    self.draw(screen)
                except Exception as e:
                    print(f"Error drawing dialog: {e}")
                    # If drawing fails, we might want to stop to avoid log spam/freeze
                    # self.running = False 
                
                pygame.display.flip()
                clock.tick(60)
        except Exception as e:
            print(f"Critical error in dialog execution: {e}")
        finally:
            self.running = False
            
        return self.result

    def draw(self, screen):
        # Base window
        pygame.draw.rect(screen, (240, 240, 245), self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 110), self.rect, 1, border_radius=8)
        
        # Title bar
        title_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 30)
        pygame.draw.rect(screen, (220, 220, 230), title_rect, border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, (180, 180, 190), title_rect.bottomleft, title_rect.bottomright)
        
        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render(self.title, True, (50, 50, 60))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 5))
        
        # Close button (macOS-style circle)
        circle_radius = 9
        circle_center = (self.rect.right - 18, self.rect.y + 15)
        self.close_btn_rect = pygame.Rect(0, 0, 30, 30)
        self.close_btn_rect.center = circle_center
        
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.close_btn_rect.collidepoint(mouse_pos)
        
        # Colors: Normal (pinkish/opaque), Hover (deep red/tinto)
        circle_bg = (170, 0, 0) if is_hover else (255, 180, 180)
        pygame.draw.circle(screen, circle_bg, circle_center, circle_radius)
        if is_hover:
            pygame.draw.circle(screen, (120, 0, 0), circle_center, circle_radius, 1)

        # Draw symmetrical X inside circle (always visible, white)
        s = 4 # half-size of the cross
        cross_color = (255, 255, 255)
        pygame.draw.line(screen, cross_color, 
                         (circle_center[0] - s, circle_center[1] - s),
                         (circle_center[0] + s, circle_center[1] + s), 2)
        pygame.draw.line(screen, cross_color, 
                         (circle_center[0] + s, circle_center[1] - s),
                         (circle_center[0] - s, circle_center[1] + s), 2)

    def handle_event(self, event): 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, 'close_btn_rect') and self.close_btn_rect.collidepoint(event.pos):
                self.running = False
                self.result = None
        self.event_processed = True
    def handle_key(self, event): 
        if event.key == pygame.K_ESCAPE: self.running = False

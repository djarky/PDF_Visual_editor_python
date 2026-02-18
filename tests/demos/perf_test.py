
import pygame
import time

def test_font_performance():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    iters = 100
    
    # Test 1: Cached Font
    start = time.time()
    font = pygame.font.SysFont(None, 18)
    for i in range(iters):
        txt = font.render("Test", True, (255, 255, 255))
        screen.blit(txt, (0, 0))
    end = time.time()
    print(f"Cached Font: {end - start:.4f}s for {iters} iterations")
    
    # Test 2: Uncached Font (Simulating current QWidget._draw)
    start = time.time()
    for i in range(iters):
        font = pygame.font.SysFont(None, 18) # Re-creation!
        txt = font.render("Test", True, (255, 255, 255))
        screen.blit(txt, (0, 0))
    end = time.time()
    print(f"Uncached Font: {end - start:.4f}s for {iters} iterations")
    
    pygame.quit()

if __name__ == "__main__":
    test_font_performance()

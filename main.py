import pygame
import sys
import os
import math

# ==========================================
# НАСТРОЙКИ
# ==========================================
pygame.init()
pygame.mixer.init()

WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ErrorTale")
pygame.mouse.set_visible(False)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

cx = WIDTH // 2
cy = HEIGHT // 2

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ==========================================
# ЗАГРУЗКА РЕСУРСОВ
# ==========================================
def load_img(name, size=None):
    try:
        img = pygame.image.load(resource_path(name)).convert_alpha()
        if size: img = pygame.transform.scale(img, size)
        return img
    except:
        s = pygame.Surface(size if size else (100, 100))
        s.fill(RED)
        return s

# Загружаем логотип (сохраняя пропорции)
logo_raw = load_img('logo.png')
if logo_raw.get_width() > 0 and logo_raw.get_width() != 100:
    w, h = logo_raw.get_size()
    new_w = 400
    new_h = int(h * (new_w / w))
    logo = pygame.transform.scale(logo_raw, (new_w, new_h))
else:
    logo = logo_raw

# Загружаем шрифт
try:
    font = pygame.font.Font(resource_path('DeterminationMono.ttf'), 36)
    small_font = pygame.font.Font(resource_path('DeterminationMono.ttf'), 24)
except:
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 28)

# Загружаем звуки
def load_snd(name):
    try: return pygame.mixer.Sound(resource_path(name))
    except: return None

snd_logo1 = load_snd('undertale-logo1.mp3')
snd_logo2 = load_snd('undertale-logo2.mp3')

def play_snd(s):
    if s: s.play()

# ==========================================
# ПЕРЕМЕННЫЕ СЦЕНЫ ЛОГОТИПА
# ==========================================
STATE_LOGO_APPEAR = 0  # Появление логотипа
STATE_ERRMOD_APPEAR = 1 # Появление Error Mod
STATE_PRESS_Z = 2      # Ожидание нажатия Z

state = STATE_LOGO_APPEAR
start_time = pygame.time.get_ticks()

clock = pygame.time.Clock()
running = True

# ==========================================
# ГЛАВНЫЙ ЦИКЛ
# ==========================================
while running:
    now = pygame.time.get_ticks()
    elapsed = now - start_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if state == STATE_PRESS_Z:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    # Тут будет переход в меню (пока просто закрываем)
                    print("Нажата Z! Переход дальше...")
                    running = False

    screen.fill(BLACK)
    
    # --- ЛОГИКА СЦЕНЫ ---
    
    # 1. Появление логотипа
    if state == STATE_LOGO_APPEAR:
        if elapsed == 0 or elapsed < 50: # Запускаем звук один раз
            if not pygame.mixer.get_busy():
                play_snd(snd_logo1)
                
        # Плавное появление (Fade in)
        alpha = min(255, int((elapsed / 1000.0) * 255))
        logo_copy = logo.copy()
        logo_copy.set_alpha(alpha)
        
        # Рисуем лого
        logo_rect = logo_copy.get_rect(center=(cx, cy - 40))
        screen.blit(logo_copy, logo_rect)
        
        # Через 2 секунды переходим к Error Mod
        if elapsed > 2000:
            state = STATE_ERRMOD_APPEAR
            start_time = now
            play_snd(snd_logo2)
            
    # 2. Появление надписи Error Mod
    elif state == STATE_ERRMOD_APPEAR:
        screen.blit(logo, logo.get_rect(center=(cx, cy - 40)))
        
        # Плавное появление текста
        alpha = min(255, int((elapsed / 500.0) * 255))
        errmod_text = font.render("Error Mod", True, RED)
        errmod_copy = errmod_text.copy()
        errmod_copy.set_alpha(alpha)
        
        screen.blit(errmod_copy, errmod_copy.get_rect(center=(cx, cy + 80)))
        
        # Через 1.5 секунды переходим к ожиданию Z
        if elapsed > 1500:
            state = STATE_PRESS_Z
            start_time = now
            
    # 3. Ожидание нажатия Z
    elif state == STATE_PRESS_Z:
        screen.blit(logo, logo.get_rect(center=(cx, cy - 40)))
        
        errmod_text = font.render("Error Mod", True, RED)
        screen.blit(errmod_text, errmod_text.get_rect(center=(cx, cy + 80)))
        
        # Пульсирующая прозрачность для текста "Нажмите Z"
        # Используем синус для плавного изменения прозрачности от 50 до 255
        pulse_alpha = int(127 + 127 * math.sin(now / 300.0))
        
        press_text = small_font.render("Нажмите Z или ENTER", True, WHITE)
        press_copy = press_text.copy()
        press_copy.set_alpha(pulse_alpha)
        
        screen.blit(press_copy, press_copy.get_rect(center=(cx, HEIGHT - 60)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

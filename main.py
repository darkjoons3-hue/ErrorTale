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
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

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

# Логотип
logo_raw = load_img('logo.png')
if logo_raw.get_width() > 0 and logo_raw.get_width() != 100:
    w, h = logo_raw.get_size()
    new_w = 400
    new_h = int(h * (new_w / w))
    logo = pygame.transform.scale(logo_raw, (new_w, new_h))
else:
    logo = logo_raw

# Фоны меню
bg_up = load_img('background-up.png')
bg_down = load_img('background-down.png')

# Шрифты
try:
    font = pygame.font.Font(resource_path('DeterminationMono.ttf'), 36)
    small_font = pygame.font.Font(resource_path('DeterminationMono.ttf'), 20)
    menu_font = pygame.font.Font(resource_path('DeterminationMono.ttf'), 26)
    stat_font = pygame.font.Font(resource_path('DeterminationMono.ttf'), 28)
except:
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 24)
    menu_font = pygame.font.Font(None, 30)
    stat_font = pygame.font.Font(None, 32)

def load_snd(name):
    try: return pygame.mixer.Sound(resource_path(name))
    except: return None

snd_logo1 = load_snd('undertale-logo1.mp3')
snd_logo2 = load_snd('undertale-logo2.mp3')
snd_select = load_snd('select.mp3')

def play_snd(s):
    if s: s.play()

def play_music(path, loops=-1):
    try:
        pygame.mixer.music.load(resource_path(path))
        pygame.mixer.music.play(loops)
    except: pass

# ==========================================
# ФУНКЦИЯ РИСОВАНИЯ СЕРДЕЧКА
# ==========================================
def draw_heart(x, y, size=26, color=RED):
    r = size // 4
    pygame.draw.circle(screen, color, (int(x - r), int(y - r)), r)
    pygame.draw.circle(screen, color, (int(x + r), int(y - r)), r)
    pygame.draw.polygon(screen, color, [(x - 2*r, y - r), (x + 2*r, y - r), (x, y + r*2)])

# ==========================================
# ПЕРЕМЕННЫЕ ИГРЫ
# ==========================================
STATE_LOGO_APPEAR = 0
STATE_ERRMOD_APPEAR = 1
STATE_PRESS_Z = 2
STATE_MENU = 3

state = STATE_LOGO_APPEAR
start_time = pygame.time.get_ticks()

menu_selected = 0 
last_top = 0 
last_bottom = 2 

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
            # --- ЛОГОТИП ---
            if state == STATE_PRESS_Z:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    state = STATE_MENU
                    start_time = now
                    play_music('MainTheme.mp3')

            # --- МЕНЮ (Добавлены WASD) ---
            elif state == STATE_MENU:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if menu_selected == 1: menu_selected = 0; play_snd(snd_select)
                    elif menu_selected == 3: menu_selected = 2; play_snd(snd_select)
                        
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    if menu_selected == 0: menu_selected = 1; play_snd(snd_select)
                    elif menu_selected == 2: menu_selected = 3; play_snd(snd_select)
                        
                if event.key in (pygame.K_UP, pygame.K_w):
                    if menu_selected == 2: menu_selected = last_top; play_snd(snd_select)
                    elif menu_selected == 3: menu_selected = last_top; play_snd(snd_select)
                        
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    if menu_selected == 0: menu_selected = last_bottom; play_snd(snd_select)
                    elif menu_selected == 1: menu_selected = last_bottom; play_snd(snd_select)
                        
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    if menu_selected == 0: print("Нажато: Продолжить")
                    elif menu_selected == 1: print("Нажато: Сброс")
                    elif menu_selected == 2: print("Нажато: Настройки")
                    elif menu_selected == 3: print("Нажато: Титры")

                if menu_selected in (0, 1): last_top = menu_selected
                if menu_selected in (2, 3): last_bottom = menu_selected

    screen.fill(BLACK)
    
    # ==========================================
    # ОТРИСОВКА СЦЕН
    # ==========================================
    
    if state == STATE_LOGO_APPEAR:
        if elapsed < 50 and not pygame.mixer.get_busy(): play_snd(snd_logo1)
        alpha = min(255, int((elapsed / 1000.0) * 255))
        logo_copy = logo.copy(); logo_copy.set_alpha(alpha)
        screen.blit(logo_copy, logo_copy.get_rect(center=(cx, cy - 40)))
        if elapsed > 2000:
            state = STATE_ERRMOD_APPEAR; start_time = now; play_snd(snd_logo2)
            
    elif state == STATE_ERRMOD_APPEAR:
        screen.blit(logo, logo.get_rect(center=(cx, cy - 40)))
        alpha = min(255, int((elapsed / 500.0) * 255))
        errmod_text = font.render("Error Mod", True, RED)
        errmod_copy = errmod_text.copy(); errmod_copy.set_alpha(alpha)
        screen.blit(errmod_copy, errmod_copy.get_rect(center=(cx, cy + 80)))
        if elapsed > 1500:
            state = STATE_PRESS_Z; start_time = now
            
    elif state == STATE_PRESS_Z:
        screen.blit(logo, logo.get_rect(center=(cx, cy - 40)))
        errmod_text = font.render("Error Mod", True, RED)
        screen.blit(errmod_text, errmod_text.get_rect(center=(cx, cy + 80)))
        pulse_alpha = int(127 + 127 * math.sin(now / 300.0))
        press_text = small_font.render("Нажмите Z или ENTER", True, WHITE)
        press_copy = press_text.copy(); press_copy.set_alpha(pulse_alpha)
        screen.blit(press_copy, press_copy.get_rect(center=(cx, HEIGHT - 60)))

    # ==========================================
    # МЕНЮ
    # ==========================================
    elif state == STATE_MENU:
        # Фоны
        screen.blit(bg_up, bg_up.get_rect(center=(cx, 60)))
        screen.blit(bg_down, bg_down.get_rect(center=(cx, 380)))

        # Кнопка выхода
        screen.blit(menu_font.render("X", True, WHITE), (20, 20))

        # Статистика
        screen.blit(stat_font.render("CHARA", True, WHITE), (130, 140))
        screen.blit(stat_font.render("LV 19", True, WHITE), (290, 140))
        screen.blit(stat_font.render("666:66", True, WHITE), (450, 140))
        screen.blit(stat_font.render("КОНЕЦ", True, WHITE), (130, 180))

        # --- Верхний ряд кнопок (y=240) ---
        c1 = GOLD if menu_selected == 0 else WHITE
        t1 = menu_font.render("ПРОДОЛЖИТЬ", True, c1)
        screen.blit(t1, (130, 240))
        if menu_selected == 0: draw_heart(100, 252, 24)

        c2 = GOLD if menu_selected == 1 else WHITE
        t2 = menu_font.render("СБРОС", True, c2)
        screen.blit(t2, (410, 240))
        if menu_selected == 1: draw_heart(380, 252, 24)

        # --- Нижний ряд кнопок (Подняли с 300 на 280) ---
        c3 = GOLD if menu_selected == 2 else WHITE
        t3 = menu_font.render("НАСТРОЙКИ", True, c3)
        screen.blit(t3, (130, 280))
        if menu_selected == 2: draw_heart(100, 292, 24)

        c4 = GOLD if menu_selected == 3 else WHITE
        t4 = menu_font.render("ТИТРЫ", True, c4)
        screen.blit(t4, (410, 280))
        if menu_selected == 3: draw_heart(380, 292, 24)

        # Футер
        footer_text = small_font.render("ErrorTale by: Darkjoons, smile103 year 2026", True, WHITE)
        footer_copy = footer_text.copy()
        footer_copy.set_alpha(120) 
        screen.blit(footer_copy, footer_copy.get_rect(center=(cx, HEIGHT - 20)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

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

# Глобальные настройки
is_fullscreen = False
sound_on = True
music_on = True
show_fps = False

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

# Картинки
logo_raw = load_img('logo.png')
if logo_raw.get_width() > 0 and logo_raw.get_width() != 100:
    w, h = logo_raw.get_size()
    new_w = 400
    new_h = int(h * (new_w / w))
    logo = pygame.transform.scale(logo_raw, (new_w, new_h))
else:
    logo = logo_raw

bg_up = load_img('background-up.png', (280, 90))
bg_down = load_img('background-down.png', (320, 120))
heart_img = load_img('soul-red.png', (24, 24))
history_img = load_img('history.png', (500, 370))

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
snd_bells = load_snd('bells.mp3')

def play_snd(s):
    if s and sound_on: s.play()

def play_music(path, loops=-1):
    if not music_on: return
    try:
        pygame.mixer.music.load(resource_path(path))
        pygame.mixer.music.play(loops)
    except: pass

def stop_music():
    pygame.mixer.music.stop()

# ==========================================
# ПЕРЕМЕННЫЕ ИГРЫ
# ==========================================
STATE_LOGO = 0
STATE_MENU = 1
STATE_OPTIONS = 2
STATE_CREDITS = 3
STATE_CONFIRM_RESET = 4
STATE_HISTORY = 5
STATE_BELLS = 6

state = STATE_LOGO
start_time = pygame.time.get_ticks()

# Таймеры и переходы
fade_alpha = 0        # Для плавного затухания (0-255)
fade_dir = 0          # 1 = затемнение, -1 = просветление, 0 = стоп
next_state = None     # Куда перейдем после затухания

# Логотип
logo_phase = 0        # 0 - лого, 1 - ошибка, 2 - нажмите Z
logo_timer = 0
logo_alpha = 0
errmod_alpha = 0

# Меню
menu_selected = 0 
last_top = 0 
last_bottom = 2 
confirm_choice = 0    # 0 - Да, 1 - Нет

# Настройки
opt_selected = 0
opt_items = ["Полный экран", "Звуки", "Музыка", "Показать FPS", "Назад"]

# История и колокола
history_time = 0
bells_played = False
bells_time = 0

clock = pygame.time.Clock()
running = True

def draw_heart(x, y):
    screen.blit(heart_img, heart_img.get_rect(center=(x, y)))

def start_fade(target_state):
    global state, fade_alpha, fade_dir, next_state
    if fade_dir == 0:
        fade_dir = 1
        fade_alpha = 0
        next_state = target_state

# ==========================================
# ГЛАВНЫЙ ЦИКЛ
# ==========================================
while running:
    now = pygame.time.get_ticks()
    dt = clock.get_time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            # --- ЛОГОТИП ---
            if state == STATE_LOGO and logo_phase == 2:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    start_fade(STATE_MENU)

            # --- ГЛАВНОЕ МЕНЮ ---
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
                    if menu_selected == 0: 
                        # Продолжить -> История
                        stop_music()
                        start_fade(STATE_HISTORY)
                    elif menu_selected == 1: 
                        # Сброс -> Подтверждение
                        state = STATE_CONFIRM_RESET
                        confirm_choice = 0
                    elif menu_selected == 2: 
                        state = STATE_OPTIONS
                        opt_selected = 0
                    elif menu_selected == 3: 
                        state = STATE_CREDITS

                if menu_selected in (0, 1): last_top = menu_selected
                if menu_selected in (2, 3): last_bottom = menu_selected

            # --- ПОДТВЕРЖДЕНИЕ СБРОСА ---
            elif state == STATE_CONFIRM_RESET:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                    confirm_choice = 1 - confirm_choice # Переключение между 0 и 1
                    play_snd(snd_select)
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    if confirm_choice == 0: # Да
                        running = False
                    else: # Нет
                        state = STATE_MENU
                if event.key in (pygame.K_x, pygame.K_ESCAPE):
                    play_snd(snd_select)
                    state = STATE_MENU

            # --- НАСТРОЙКИ ---
            elif state == STATE_OPTIONS:
                if event.key in (pygame.K_UP, pygame.K_w):
                    opt_selected -= 1
                    if opt_selected < 0: opt_selected = len(opt_items) - 1
                    play_snd(snd_select)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    opt_selected += 1
                    if opt_selected >= len(opt_items): opt_selected = 0
                    play_snd(snd_select)
                
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    if opt_selected == 0: 
                        is_fullscreen = not is_fullscreen
                        if is_fullscreen: screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        else: screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    elif opt_selected == 1: sound_on = not sound_on
                    elif opt_selected == 2: 
                        music_on = not music_on
                        if not music_on: stop_music()
                        else: play_music('MainTheme.mp3')
                    elif opt_selected == 3: show_fps = not show_fps
                    elif opt_selected == 4: state = STATE_MENU
                        
                if event.key in (pygame.K_x, pygame.K_ESCAPE):
                    play_snd(snd_select)
                    state = STATE_MENU

            # --- ТИТРЫ ---
            elif state == STATE_CREDITS:
                if event.key in (pygame.K_x, pygame.K_ESCAPE, pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    state = STATE_MENU

            # --- ПРОПУСК ИСТОРИИ ---
            elif state == STATE_HISTORY:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    play_snd(snd_select)
                    stop_music()
                    start_fade(STATE_BELLS)

    # ==========================================
    # ЛОГИКА СОСТОЯНИЙ (Таймеры и анимации)
    # ==========================================
    
    # Логика Логотипа
    if state == STATE_LOGO:
        logo_timer += dt
        if logo_phase == 0:
            logo_alpha = min(255, logo_alpha + 3)
            if logo_timer == dt and sound_on: # Играем звук 1 раз при старте
                play_snd(snd_logo1)
            if logo_timer > 2000:
                logo_phase = 1
                logo_timer = 0
                play_snd(snd_logo2)
        elif logo_phase == 1:
            errmod_alpha = min(255, errmod_alpha + 5)
            if logo_timer > 1500:
                logo_phase = 2
                logo_timer = 0

    # Логика Фейда (Затухания)
    if fade_dir != 0:
        fade_alpha += 5 * fade_dir
        if fade_dir == 1 and fade_alpha >= 255:
            fade_alpha = 255
            state = next_state # Меняем состояние в пике затемнения
            if state == STATE_MENU: play_music('MainTheme.mp3')
            if state == STATE_HISTORY: 
                play_music('history.mp3', loops=0)
                history_time = 0
            if state == STATE_BELLS:
                play_snd(snd_bells)
                bells_time = 0
            fade_dir = -1 # Начинаем просветление
        elif fade_dir == -1 and fade_alpha <= 0:
            fade_alpha = 0
            fade_dir = 0

    # Логика Истории
    if state == STATE_HISTORY:
        history_time += dt

    # Логика Колоколов
    if state == STATE_BELLS:
        bells_time += dt
        # Ждем 7 секунд, пока играют колокола, и закрываем
        if bells_time > 7000:
            running = False

    # ==========================================
    # ОТРИСОВКА
    # ==========================================
    screen.fill(BLACK)
    
    # --- ЭКРАН ЛОГОТИПА ---
    if state == STATE_LOGO:
        logo_copy = logo.copy()
        logo_copy.set_alpha(logo_alpha)
        screen.blit(logo_copy, logo_copy.get_rect(center=(cx, cy - 40)))
        
        if logo_phase >= 1:
            errmod_text = font.render("Error Mod", True, RED)
            errmod_copy = errmod_text.copy()
            errmod_copy.set_alpha(errmod_alpha)
            screen.blit(errmod_copy, errmod_copy.get_rect(center=(cx, cy + 80)))
            
        if logo_phase == 2:
            pulse_alpha = int(127 + 127 * math.sin(now / 300.0))
            press_text = small_font.render("Нажмите Z или ENTER", True, WHITE)
            press_copy = press_text.copy()
            press_copy.set_alpha(pulse_alpha)
            screen.blit(press_copy, press_copy.get_rect(center=(cx, HEIGHT - 60)))

    # --- МЕНЮ ---
    elif state == STATE_MENU:
        screen.blit(bg_up, bg_up.get_rect(center=(cx, 50)))
        screen.blit(bg_down, bg_down.get_rect(center=(cx, 390)))
        screen.blit(menu_font.render("X", True, WHITE), (20, 5))

        screen.blit(stat_font.render("CHARA", True, WHITE), (130, 140))
        screen.blit(stat_font.render("LV 19", True, WHITE), (290, 140))
        screen.blit(stat_font.render("666:66", True, WHITE), (450, 140))
        screen.blit(stat_font.render("КОНЕЦ", True, WHITE), (130, 180))

        c1 = GOLD if menu_selected == 0 else WHITE
        screen.blit(menu_font.render("ПРОДОЛЖИТЬ", True, c1), (130, 240))
        if menu_selected == 0: draw_heart(100, 252)

        c2 = GOLD if menu_selected == 1 else WHITE
        screen.blit(menu_font.render("СБРОС", True, c2), (410, 240))
        if menu_selected == 1: draw_heart(380, 252)

        c3 = GOLD if menu_selected == 2 else WHITE
        screen.blit(menu_font.render("НАСТРОЙКИ", True, c3), (130, 280))
        if menu_selected == 2: draw_heart(100, 292)

        c4 = GOLD if menu_selected == 3 else WHITE
        screen.blit(menu_font.render("ТИТРЫ", True, c4), (410, 280))
        if menu_selected == 3: draw_heart(380, 292)

        footer_text = small_font.render("ErrorTale by: Darkjoons, smile103 year 2026", True, WHITE)
        footer_copy = footer_text.copy(); footer_copy.set_alpha(120) 
        screen.blit(footer_copy, footer_copy.get_rect(center=(cx, HEIGHT - 15)))

    # --- ПОДТВЕРЖДЕНИЕ СБРОСА ---
    elif state == STATE_CONFIRM_RESET:
        # Отрисовываем меню на фоне (чтобы не было черного экрана)
        screen.blit(bg_up, bg_up.get_rect(center=(cx, 50)))
        screen.blit(bg_down, bg_down.get_rect(center=(cx, 390)))
        
        # Затемняем экран
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Диалоговое окно
        box = pygame.Surface((460, 160))
        box.fill(BLACK)
        pygame.draw.rect(box, WHITE, (0, 0, 460, 160), 3)
        screen.blit(box, box.get_rect(center=(cx, cy)))

        # Текст
        title = menu_font.render("Вы уверены, что хотите", True, WHITE)
        title2 = menu_font.render("сбросить игру?", True, WHITE)
        screen.blit(title, title.get_rect(center=(cx, cy - 40)))
        screen.blit(title2, title2.get_rect(center=(cx, cy - 10)))

        # Кнопки Да / Нет
        c_yes = GOLD if confirm_choice == 0 else WHITE
        c_no = GOLD if confirm_choice == 1 else WHITE
        
        t_yes = menu_font.render("Да", True, c_yes)
        t_no = menu_font.render("Нет", True, c_no)
        
        rect_yes = t_yes.get_rect(center=(cx - 70, cy + 45))
        rect_no = t_no.get_rect(center=(cx + 70, cy + 45))
        
        screen.blit(t_yes, rect_yes)
        screen.blit(t_no, rect_no)
        
        if confirm_choice == 0: draw_heart(rect_yes.left - 25, rect_yes.centery)
        if confirm_choice == 1: draw_heart(rect_no.left - 25, rect_no.centery)

    # --- НАСТРОЙКИ ---
    elif state == STATE_OPTIONS:
        title = menu_font.render("НАСТРОЙКИ", True, WHITE)
        screen.blit(title, title.get_rect(center=(cx, 60)))

        start_y = 130
        spacing = 40
        
        for i, item in enumerate(opt_items):
            if i == 0: text = f"{item}: {'ВКЛ' if is_fullscreen else 'ВЫКЛ'}"
            elif i == 1: text = f"{item}: {'ВКЛ' if sound_on else 'ВЫКЛ'}"
            elif i == 2: text = f"{item}: {'ВКЛ' if music_on else 'ВЫКЛ'}"
            elif i == 3: text = f"{item}: {'ВКЛ' if show_fps else 'ВЫКЛ'}"
            else: text = item

            color = GOLD if i == opt_selected else WHITE
            t = menu_font.render(text, True, color)
            t_rect = t.get_rect(center=(cx, start_y + i * spacing))
            screen.blit(t, t_rect)

            if i == opt_selected: draw_heart(t_rect.left - 30, t_rect.centery)

        hint = small_font.render("Z/ENTER - изменить, X/ESC - назад", True, WHITE)
        hint.set_alpha(150)
        screen.blit(hint, hint.get_rect(center=(cx, HEIGHT - 30)))

    # --- ТИТРЫ ---
    elif state == STATE_CREDITS:
        title = font.render("ТИТРЫ", True, WHITE)
        screen.blit(title, title.get_rect(center=(cx, 100)))
        
        screen.blit(menu_font.render("Игру делали:", True, GOLD), menu_font.render("Игру делали:", True, GOLD).get_rect(center=(cx, 200)))
        screen.blit(stat_font.render("Darkjoons", True, WHITE), stat_font.render("Darkjoons", True, WHITE).get_rect(center=(cx, 260)))
        screen.blit(stat_font.render("smile103", True, WHITE), stat_font.render("smile103", True, WHITE).get_rect(center=(cx, 300)))
        
        hint = small_font.render("Нажмите X или Z чтобы вернуться", True, WHITE)
        hint.set_alpha(150)
        screen.blit(hint, hint.get_rect(center=(cx, HEIGHT - 50)))

    # --- ИСТОРИЯ ---
    elif state == STATE_HISTORY:
        # Мигание: 3 сек черный, 3 сек картинка, 3 сек черный...
        if (history_time // 3000) % 2 == 1:
            screen.blit(history_img, history_img.get_rect(center=(cx, cy)))
            
        # Подсказка "Пропустить"
        skip_text = small_font.render("Чтобы пропустить нажмите Z или ENTER", True, WHITE)
        skip_text.set_alpha(120)
        screen.blit(skip_text, skip_text.get_rect(center=(cx, HEIGHT - 20)))

    # --- КОЛОКОЛА ---
    elif state == STATE_BELLS:
        # Просто черный экран, звук уже играет
        pass

    # --- FPS ---
    if show_fps:
        fps_text = small_font.render(f"FPS: {int(clock.get_fps())}", True, GOLD)
        screen.blit(fps_text, (WIDTH - 90, 10))

    # ==========================================
    # СЛОЙ ЗАТУХАНИЯ (Fade)
    # ==========================================
    if fade_alpha > 0:
        fade_surf = pygame.Surface((WIDTH, HEIGHT))
        fade_surf.fill(BLACK)
        fade_surf.set_alpha(fade_alpha)
        screen.blit(fade_surf, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

import pygame
import sys

# --- CONFIG & COLORS ---
WIDTH, HEIGHT = 1200, 800
PANEL_WIDTH = 360
GAME_WIDTH = WIDTH - PANEL_WIDTH

BG_COLOR = (2, 3, 5)
PANEL_COLOR = (11, 15, 23)
ACCENT = (0, 255, 157)
ACCENT2 = (0, 209, 255)
TEXT_COLOR = (238, 241, 245)
MUTED_COLOR = (100, 116, 139)
CARD_COLOR = (15, 20, 31)

# --- DATA ---
PLANETS = [
    {"id": "Earth", "mult": 1, "xp": 1, "cost": 0},
    {"id": "Moon", "mult": 10, "xp": 2, "cost": 1000},
    {"id": "Mars", "mult": 50, "xp": 5, "cost": 5000}
]

TURTLES_DATA = [
    {"id": "Baby", "cps": 1, "cost": 10},
    {"id": "Farmer", "cps": 5, "cost": 100},
    {"id": "Ninja", "cps": 25, "cost": 1000}
]

# --- STATE ---
class GameState:
    def __init__(self):
        self.turtles = 0
        self.cps = 0
        self.lvl = 1
        self.xp = 0
        self.need = 100
        self.planet = "Earth"
        self.owned_planets = ["Earth"]
        self.owned_turtles = {t["id"]: 0 for t in TURTLES_DATA}
        self.tab = "planets"
        self.floats = [] 

state = GameState()

# --- INITIALIZE PYGAME ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turtle Clicker")
clock = pygame.time.Clock()

# Fonts
font_main = pygame.font.SysFont("Arial", 48, bold=True)
font_stats = pygame.font.SysFont("Courier", 18)
font_card = pygame.font.SysFont("Arial", 16, bold=True)

def format_num(n):
    if n < 1000: return str(int(n))
    for unit in ['K', 'M', 'B', 'T']:
        n /= 1000.0
        if n < 1000:
            return f"{n:.1f}{unit}"
    return f"{n:.1f}P"

def spawn_float(x, y, text):
    state.floats.append({"x": x, "y": y, "text": text, "life": 1.0})

def calculate_cps():
    total = 0
    for t in TURTLES_DATA:
        total += state.owned_turtles[t["id"]] * t["cps"]
    state.cps = total

def draw_button(surface, rect, text, color, active=True):
    pygame.draw.rect(surface, color, rect, border_radius=8)
    txt_surf = font_card.render(text, True, (0, 0, 0))
    txt_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, txt_rect)

def run_game():
    running = True
    while running:
        dt = clock.tick(60) / 1000.0 
        
        # 1. Passive Income
        state.turtles += state.cps * dt

        # 2. Event Handling
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Click Game Area
                if mx < GAME_WIDTH:
                    p_data = next(p for p in PLANETS if p["id"] == state.planet)
                    gain = 1 * p_data["mult"]
                    state.turtles += gain
                    state.xp += 10 * p_data["xp"]
                    spawn_float(mx, my, f"+{format_num(gain)}")
                    
                    if state.xp >= state.need:
                        state.xp = 0
                        state.need *= 1.4
                        state.lvl += 1

                # Click Tabs
                if GAME_WIDTH + 15 <= mx <= WIDTH - 15:
                    if 15 <= my <= 55:
                        if mx < GAME_WIDTH + PANEL_WIDTH//2: state.tab = "planets"
                        else: state.tab = "turtles"
                
                # Click Shop Items
                if mx > GAME_WIDTH + 15:
                    y_offset = 70
                    items = PLANETS if state.tab == "planets" else TURTLES_DATA
                    for item in items:
                        btn_rect = pygame.Rect(GAME_WIDTH + 20, y_offset + 50, PANEL_WIDTH - 40, 30)
                        if btn_rect.collidepoint(mx, my):
                            if state.tab == "planets":
                                if item["id"] not in state.owned_planets:
                                    if state.turtles >= item["cost"]:
                                        state.turtles -= item["cost"]
                                        state.owned_planets.append(item["id"])
                                        state.planet = item["id"]
                                else:
                                    state.planet = item["id"]
                            else: # Turtles
                                if state.turtles >= item["cost"]:
                                    state.turtles -= item["cost"]
                                    state.owned_turtles[item["id"]] += 1
                                    item["cost"] = int(item["cost"] * 1.15) 
                                    calculate_cps()
                        y_offset += 100

        # --- RENDERING ---
        screen.fill(BG_COLOR)

        # Draw HUD
        val_surf = font_main.render(format_num(state.turtles), True, ACCENT)
        screen.blit(val_surf, (30, 30))
        
        stats_txt = f"CPS: {format_num(state.cps)} | LVL: {state.lvl} | WORLD: {state.planet}"
        stats_surf = font_stats.render(stats_txt, True, MUTED_COLOR)
        screen.blit(stats_surf, (30, 90))

        # XP Bar
        pygame.draw.rect(screen, (17, 17, 17), (30, 120, 250, 8), border_radius=4)
        xp_width = min((state.xp / state.need) * 250, 250)
        pygame.draw.rect(screen, ACCENT2, (30, 120, xp_width, 8), border_radius=4)

        # Draw Right Panel
        pygame.draw.rect(screen, PANEL_COLOR, (GAME_WIDTH, 0, PANEL_WIDTH, HEIGHT))
        
        # Tabs
        p_tab_col = (40, 50, 60) if state.tab == "planets" else (20, 20, 20)
        t_tab_col = (40, 50, 60) if state.tab == "turtles" else (20, 20, 20)
        pygame.draw.rect(screen, p_tab_col, (GAME_WIDTH + 10, 15, (PANEL_WIDTH//2)-15, 40), border_radius=8)
        pygame.draw.rect(screen, t_tab_col, (GAME_WIDTH + PANEL_WIDTH//2 + 5, 15, (PANEL_WIDTH//2)-15, 40), border_radius=8)
        
        screen.blit(font_card.render("Worlds", True, TEXT_COLOR), (GAME_WIDTH + 50, 25))
        screen.blit(font_card.render("Turtles", True, TEXT_COLOR), (GAME_WIDTH + PANEL_WIDTH//2 + 40, 25))

        # Shop List
        y_offset = 70
        items = PLANETS if state.tab == "planets" else TURTLES_DATA
        for item in items:
            card_rect = pygame.Rect(GAME_WIDTH + 15, y_offset, PANEL_WIDTH - 30, 90)
            pygame.draw.rect(screen, CARD_COLOR, card_rect, border_radius=12)
            
            name_surf = font_card.render(item["id"], True, TEXT_COLOR)
            screen.blit(name_surf, (GAME_WIDTH + 25, y_offset + 10))
            
            sub_txt = f"Mult: {item['mult']}x" if state.tab == "planets" else f"CPS: {item['cps']} ({state.owned_turtles[item['id']]})"
            sub_surf = font_stats.render(sub_txt, True, MUTED_COLOR)
            screen.blit(sub_surf, (GAME_WIDTH + 25, y_offset + 28))

            btn_rect = pygame.Rect(GAME_WIDTH + 20, y_offset + 50, PANEL_WIDTH - 40, 30)
            if state.tab == "planets":
                btn_text = "USE" if item["id"] in state.owned_planets else f"BUY {format_num(item['cost'])}"
                can_buy = item["id"] in state.owned_planets or state.turtles >= item["cost"]
            else:
                btn_text = f"BUY {format_num(item['cost'])}"
                can_buy = state.turtles >= item["cost"]
            
            draw_button(screen, btn_rect, btn_text, ACCENT if can_buy else MUTED_COLOR, can_buy)
            y_offset += 100

        # Floating Particles
        for f in state.floats[:]:
            f["y"] -= 2
            f["life"] -= 0.02
            if f["life"] <= 0:
                state.floats.remove(f)
            else:
                txt = font_stats.render(f["text"], True, ACCENT2)
                # Note: set_alpha works on Surface, we'll just draw it
                screen.blit(txt, (f["x"], f["y"]))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
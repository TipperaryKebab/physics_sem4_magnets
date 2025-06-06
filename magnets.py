import pygame
import sys
import math
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

pygame.init()

WIDTH, HEIGHT = 300, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Постоянный магнит")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAGNET_COLOR = (200, 200, 200)
POLE_N_COLOR = (0, 0, 255)
POLE_S_COLOR = (255, 0, 0)
current_pole_color = POLE_N_COLOR

drawing = False
shape_mode = "free"
current_shape = []
magnets = []  # список {'points': []} для каждой фигуры
pole_seeds = []  # список {'pos':(x,y), 'type':'N'/'S', 'magnet_idx':int}

current_rect_start = None
current_circle_start = None
current_triangle = []

SPACING = 3

color_button_rect = pygame.Rect(10, 10, 50, 50)
start_button_rect = pygame.Rect(WIDTH - 110, 10, 100, 40)
mode_buttons = {
    "free": pygame.Rect(10, 70, 80, 30),
    "rect": pygame.Rect(10, 110, 80, 30),
    "triangle": pygame.Rect(10, 150, 80, 30),
    "circle": pygame.Rect(10, 190, 80, 30),
    "pole": pygame.Rect(10, 230, 80, 30),
}


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside


running = True
processing = False
while running:
    mx, my = pygame.mouse.get_pos()
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if color_button_rect.collidepoint(ev.pos):
                current_pole_color = (
                    POLE_S_COLOR if current_pole_color == POLE_N_COLOR else POLE_N_COLOR
                )
            elif start_button_rect.collidepoint(ev.pos):
                processing = True
                running = False
                break
            else:
                for mode, rect in mode_buttons.items():
                    if rect.collidepoint(ev.pos):
                        shape_mode = mode
                        if mode == "triangle":
                            current_triangle = []
                        break
                else:
                    if shape_mode == "free":
                        drawing = True
                        current_shape = [(mx, my)]
                    elif shape_mode == "rect":
                        current_rect_start = (mx, my)
                    elif shape_mode == "circle":
                        current_circle_start = (mx, my)
                    elif shape_mode == "triangle":
                        current_triangle.append((mx, my))
                        if len(current_triangle) == 3:
                            magnets.append({"points": current_triangle.copy()})
                            current_triangle = []
                    elif shape_mode == "pole":
                        for idx, m in enumerate(magnets):
                            if point_in_poly((mx, my), m["points"]):
                                typ = "N" if current_pole_color == POLE_N_COLOR else "S"
                                pole_seeds.append(
                                    {"pos": (mx, my), "type": typ, "magnet_idx": idx}
                                )
                                break
        elif ev.type == pygame.MOUSEMOTION and drawing:
            current_shape.append(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            if drawing:
                magnets.append({"points": current_shape.copy()})
                drawing = False
            elif current_rect_start:
                x1, y1 = current_rect_start
                x2, y2 = ev.pos
                magnets.append({"points": [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]})
                current_rect_start = None
            elif current_circle_start:
                cx, cy = current_circle_start
                r = math.hypot(ev.pos[0] - cx, ev.pos[1] - cy)
                pts = [
                    (
                        cx + r * math.cos(2 * math.pi * i / 20),
                        cy + r * math.sin(2 * math.pi * i / 20),
                    )
                    for i in range(20)
                ]
                magnets.append({"points": pts})
                current_circle_start = None
    screen.fill(WHITE)
    pygame.draw.rect(screen, current_pole_color, color_button_rect)
    pygame.draw.rect(screen, (0, 200, 0), start_button_rect)
    screen.blit(
        pygame.font.SysFont(None, 24).render("Start", True, WHITE), (WIDTH - 90, 15)
    )
    for mode, rect in mode_buttons.items():
        col = (180, 180, 180) if shape_mode == mode else (120, 120, 120)
        pygame.draw.rect(screen, col, rect)
        screen.blit(
            pygame.font.SysFont(None, 20).render(mode.capitalize(), True, BLACK),
            (rect.x + 5, rect.y + 5),
        )
    for m in magnets:
        pygame.draw.polygon(screen, MAGNET_COLOR, m["points"])
        pygame.draw.polygon(screen, BLACK, m["points"], 2)
    if drawing and len(current_shape) >= 2:
        pygame.draw.lines(screen, BLACK, False, current_shape, 3)

    if shape_mode == "rect" and current_rect_start:
        x1, y1 = current_rect_start
        pygame.draw.rect(screen, BLACK, (x1, y1, mx - x1, my - y1), 1)
    if shape_mode == "circle" and current_circle_start:
        cx, cy = current_circle_start
        pygame.draw.circle(
            screen, BLACK, (cx, cy), int(math.hypot(mx - cx, my - cy)), 1
        )
    if shape_mode == "triangle" and len(current_triangle) > 0:
        pts = current_triangle + [(mx, my)]
        pygame.draw.lines(screen, BLACK, False, pts, 1)
    for seed in pole_seeds:
        col = POLE_N_COLOR if seed["type"] == "N" else POLE_S_COLOR
        pygame.draw.circle(screen, col, seed["pos"], 5)
    pygame.display.flip()
    pygame.time.Clock().tick(60)

if processing:
    pygame.quit()


    def sample_interior(points, spacing=SPACING):
        pts = []
        minx, miny = int(min(p[0] for p in points)), int(min(p[1] for p in points))
        maxx, maxy = int(max(p[0] for p in points)), int(max(p[1] for p in points))
        for x in range(minx, maxx, spacing):
            for y in range(miny, maxy, spacing):
                if point_in_poly((x, y), points):
                    pts.append((x, y))
        return pts

    poles = []
    for idx, m in enumerate(magnets):
        interior = sample_interior(m["points"])
        seeds = [s for s in pole_seeds if s["magnet_idx"] == idx]
        if not seeds:
            continue
        for pt in interior:
            dists = [
                (math.hypot(pt[0] - s["pos"][0], pt[1] - s["pos"][1]), s) for s in seeds
            ]
            _, s = min(dists, key=lambda x: x[0])
            poles.append({"pos": pt, "type": s["type"]})

    H, W = HEIGHT, WIDTH
    Y, X = np.mgrid[0:H, 0:W]
    Bx, By = np.zeros((H, W)), np.zeros((H, W))
    eps = 1e-3
    for p in poles:
        x0, y0 = p["pos"]
        dx, dy = X - x0, Y - y0
        r3 = (dx * dx + dy * dy + eps) ** 1.5
        cx, cy = dx / r3, dy / r3
        if p["type"] == "S":
            cx, cy = -cx, -cy
        Bx += cx
        By += cy
    M = np.hypot(Bx, By)
    Bx /= M.max()
    By /= M.max()
    plt.figure(figsize=(6, 6))
    speed = np.hypot(Bx, By)
    plt.streamplot(X, Y, Bx, By, density=1.2, color=speed, linewidth=1, cmap="inferno")
    north = [p["pos"] for p in poles if p["type"] == "N"]
    south = [p["pos"] for p in poles if p["type"] == "S"]
    if north:
        xs, ys = zip(*north)
        plt.scatter(xs, ys, c="blue", s=5, label="Север")
    if south:
        xs, ys = zip(*south)
        plt.scatter(xs, ys, c="red", s=5, label="Юг")
    plt.legend(loc="upper right")
    plt.title("Силовые линии магнитного поля постоянного магнита")
    plt.xlim(0, W)
    plt.ylim(0, H)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
else:
    pygame.quit()
    sys.exit()
import pygame
import random
import math
import json
import os

pygame.init()

WIDTH = 800
HEIGHT = 600

CELL_SIZE = 20

BASE_INTERVAL = 110
MIN_INTERVAL = 55
SPEED_STEP = 4

ENEMIES_START = 1
MAX_ENEMIES = 6
LEVEL_EVERY = 5
ENEMY_INTERVAL = 170
ENEMY_RANDOMNESS = 0.18
ENEMY_MIN_SPAWN_DIST = 160
ENEMY_EAT_BONUS = 3
POWER_DURATION = 6000
POWER_EVERY = 5
POWER_MIN_ENEMIES = 2
ENEMY_COLORS = [
    (255, 80, 80),
    (255, 150, 40),
    (255, 90, 200),
    (120, 200, 255),
    (150, 255, 120),
    (200, 130, 255),
]
SCARED_COLOR = (40, 70, 230)
SCARED_END_COLOR = (235, 235, 255) 

MAX_SCORES = 5
HIGHSCORE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "highscores.json"
)

TUNNELS = [
    {"a": (0, 200), "b": (WIDTH - CELL_SIZE, 380), "color": (60, 200, 90)},
    {"a": (300, 0), "b": (480, HEIGHT - CELL_SIZE), "color": (230, 150, 50)},
    {"a": (140, 100), "b": (640, 460), "color": (80, 180, 255)},
    {"a": (60, 480), "b": (720, 140), "color": (200, 90, 230)},
    {"a": (220, 540), "b": (540, 60), "color": (60, 210, 210)},
]

tunnel_exit = {}
tunnel_cells = []
tunnel_positions = set()


def apply_tunnels(pairs):
    # Reconstruye los tres "indices" de tuneles a partir de una lista de
    # pares {"a", "b", "color"}.
    global tunnel_exit, tunnel_cells, tunnel_positions

    tunnel_exit = {}
    tunnel_cells = []
    for pair in pairs:
        a, b = pair["a"], pair["b"]
        tunnel_exit[a] = b
        tunnel_exit[b] = a
        tunnel_cells.append((a, pair["color"]))
        tunnel_cells.append((b, pair["color"]))
    tunnel_positions = {cell for cell, _ in tunnel_cells}


apply_tunnels(TUNNELS)


def current_interval():
    return max(MIN_INTERVAL, BASE_INTERVAL - score * SPEED_STEP)


def current_level():
    return apples // LEVEL_EVERY + 1


def desired_enemy_count():
    return min(MAX_ENEMIES, ENEMIES_START + apples // LEVEL_EVERY)


def load_high_scores():
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        scores = [int(s) for s in data]
        return sorted(scores, reverse=True)[:MAX_SCORES]
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return []


def save_high_scores(scores):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f)
    except OSError:
        pass


def register_score(value):
    global high_scores, new_record

    if value <= 0:
        new_record = False
        return

    prev_best = high_scores[0] if high_scores else 0
    high_scores.append(value)
    high_scores = sorted(high_scores, reverse=True)[:MAX_SCORES]
    new_record = value > prev_best
    save_high_scores(high_scores)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)
list_font = pygame.font.SysFont(None, 28)
button_font = pygame.font.SysFont(None, 22)

restart_button = pygame.Rect(WIDTH - 95, 10, 85, 28)
pause_button = pygame.Rect(WIDTH - 188, 10, 85, 28)
score_area = pygame.Rect(0, 0, 200, 92)


def draw_button(rect, label):
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    fill = (100, 100, 100) if hovered else (70, 70, 70)

    pygame.draw.rect(screen, fill, rect, border_radius=6)
    pygame.draw.rect(screen, (160, 160, 160), rect, 2, border_radius=6)

    text = button_font.render(label, True, (255, 255, 255))
    screen.blit(
        text,
        (
            rect.centerx - text.get_width() // 2,
            rect.centery - text.get_height() // 2
        )
    )


def draw_head_features(hx, hy):
    cx = hx + CELL_SIZE / 2
    cy = hy + CELL_SIZE / 2

    fx, fy = direction_x, direction_y
    px, py = -fy, fx

    forward = CELL_SIZE * 0.18
    side = CELL_SIZE * 0.22

    blink = (anim_time % 3200) < 130

    for s in (-1, 1):
        ex = cx + fx * forward + px * s * side
        ey = cy + fy * forward + py * s * side

        if game_over:
            pygame.draw.line(screen, (20, 20, 20),
                             (int(ex - 3), int(ey - 3)), (int(ex + 3), int(ey + 3)), 2)
            pygame.draw.line(screen, (20, 20, 20),
                             (int(ex - 3), int(ey + 3)), (int(ex + 3), int(ey - 3)), 2)
        elif blink:
            pygame.draw.line(screen, (15, 50, 15),
                             (int(ex - 3), int(ey)), (int(ex + 3), int(ey)), 2)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (int(ex), int(ey)), 3)
            pygame.draw.circle(screen, (10, 10, 10),
                               (int(ex + fx * 1.5), int(ey + fy * 1.5)), 2)

    if not game_over and not blink:
        phase = anim_time % 1800
        if phase < 260:
            ext = math.sin(phase / 260 * math.pi) * 7
            bx = cx + fx * (CELL_SIZE * 0.5)
            by = cy + fy * (CELL_SIZE * 0.5)
            tx = bx + fx * ext
            ty = by + fy * ext
            pygame.draw.line(screen, (230, 40, 70),
                             (int(bx), int(by)), (int(tx), int(ty)), 2)
            pygame.draw.line(screen, (230, 40, 70), (int(tx), int(ty)),
                             (int(tx + fx * 3 + px * 3), int(ty + fy * 3 + py * 3)), 2)
            pygame.draw.line(screen, (230, 40, 70), (int(tx), int(ty)),
                             (int(tx + fx * 3 - px * 3), int(ty + fy * 3 - py * 3)), 2)


def draw_segment(draw_x, draw_y, color, is_head):
    pygame.draw.rect(
        screen,
        color,
        (draw_x, draw_y, CELL_SIZE, CELL_SIZE),
        border_radius=6
    )
    if is_head:
        draw_head_features(draw_x, draw_y)


def draw_tunnels():
    glow = (math.sin(anim_time / 220.0) + 1) / 2
    for (cx, cy), color in tunnel_cells:
        rect = pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)
        base = (
            int(color[0] * 0.35),
            int(color[1] * 0.35),
            int(color[2] * 0.35),
        )
        rim = (
            min(255, int(color[0] * (0.7 + 0.3 * glow))),
            min(255, int(color[1] * (0.7 + 0.3 * glow))),
            min(255, int(color[2] * (0.7 + 0.3 * glow))),
        )
        pygame.draw.rect(screen, base, rect, border_radius=8)
        pygame.draw.rect(screen, rim, rect, 3, border_radius=8)
        inner = rect.inflate(-int(CELL_SIZE * 0.45), -int(CELL_SIZE * 0.45))
        pygame.draw.ellipse(screen, (12, 12, 18), inner)


def draw_power_food():
    if power_food is None:
        return

    pcx = power_food[0] + CELL_SIZE / 2
    pcy = power_food[1] + CELL_SIZE / 2
    glow = (math.sin(anim_time / 120.0) + 1) / 2

    halo = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
    pygame.draw.circle(
        halo, (120, 180, 255, 90),
        (CELL_SIZE, CELL_SIZE),
        int(CELL_SIZE * 0.7 * (0.7 + 0.3 * glow))
    )
    screen.blit(halo, (int(pcx - CELL_SIZE), int(pcy - CELL_SIZE)))

    r = int(CELL_SIZE * (0.3 + 0.12 * glow))
    pygame.draw.circle(screen, (120, 200, 255), (int(pcx), int(pcy)), r)
    pygame.draw.circle(
        screen, (235, 250, 255),
        (int(pcx), int(pcy)), max(1, int(r * 0.4))
    )


def draw_ghost(e):
    scared = power_timer > 0

    t_e = 1.0 if game_over else min(enemy_time / ENEMY_INTERVAL, 1.0)
    dxp = e["x"] - e["px"]
    dyp = e["y"] - e["py"]
    if abs(dxp) > CELL_SIZE or abs(dyp) > CELL_SIZE:
        gx, gy = e["x"], e["y"]
    else:
        gx = e["px"] + dxp * t_e
        gy = e["py"] + dyp * t_e

    if scared:
        ending = power_timer < 1500 and (anim_time // 200) % 2 == 0
        body = SCARED_END_COLOR if ending else SCARED_COLOR
    else:
        body = e["color"]

    cx = gx + CELL_SIZE / 2
    top = gy + CELL_SIZE * 0.30
    radius = CELL_SIZE * 0.40

    pygame.draw.circle(screen, body, (int(cx), int(top)), int(radius))
    pygame.draw.rect(
        screen, body,
        (int(cx - radius), int(top), int(radius * 2), int(CELL_SIZE * 0.32))
    )

    base_y = top + CELL_SIZE * 0.32
    seg = (radius * 2) / 3
    for k in range(3):
        x0 = cx - radius + k * seg
        pygame.draw.polygon(screen, body, [
            (x0, base_y),
            (x0 + seg / 2, base_y + CELL_SIZE * 0.16),
            (x0 + seg, base_y),
        ])

    # Mira hacia la cabeza de la serpiente.
    head_x, head_y = snake[0]
    look_x = (head_x > gx) - (head_x < gx)
    look_y = (head_y > gy) - (head_y < gy)

    for s in (-1, 1):
        ex = cx + s * radius * 0.42
        ey = top - radius * 0.05
        pygame.draw.circle(screen, (255, 255, 255), (int(ex), int(ey)),
                           int(radius * 0.30))
        pygame.draw.circle(
            screen, (20, 20, 60),
            (int(ex + look_x * 2), int(ey + look_y * 2)),
            max(1, int(radius * 0.16))
        )


def queue_direction(dx, dy):
    if direction_queue:
        ref_x, ref_y = direction_queue[-1]
    else:
        ref_x, ref_y = direction_x, direction_y

    if (dx, dy) == (ref_x, ref_y):
        return
    if (dx, dy) == (-ref_x, -ref_y):
        return
    if len(direction_queue) >= 2:
        return

    direction_queue.append((dx, dy))


def occupied_cells(include_food=True):
    cells = set()
    if include_food:
        cells.add((food_x, food_y))
    if power_food is not None:
        cells.add((power_food[0], power_food[1]))
    for e in enemies:
        cells.add((e["x"], e["y"]))
    return cells


def random_free_cell(min_head_dist=0, avoid=()):
    blocked = [
        restart_button.inflate(CELL_SIZE, CELL_SIZE),
        pause_button.inflate(CELL_SIZE, CELL_SIZE),
        score_area,
    ]
    head_x, head_y = snake[0]
    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)

        if [x, y] in snake:
            continue

        if (x, y) in tunnel_positions:
            continue

        if (x, y) in avoid:
            continue

        cell = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        if any(cell.colliderect(b) for b in blocked):
            continue

        if min_head_dist and abs(x - head_x) + abs(y - head_y) < min_head_dist:
            continue

        return x, y


def place_food():
    return random_free_cell(avoid=occupied_cells(include_food=False))


def spawn_enemy():
    x, y = random_free_cell(
        min_head_dist=ENEMY_MIN_SPAWN_DIST,
        avoid=occupied_cells(),
    )
    enemies.append({
        "x": x, "y": y,
        "px": x, "py": y,
        "dx": 0, "dy": 0,
        "color": ENEMY_COLORS[len(enemies) % len(ENEMY_COLORS)],
    })


def relocate_tunnels():
    global tunnel_exit, tunnel_cells, tunnel_positions

    tunnel_exit = {}
    tunnel_cells = []
    tunnel_positions = set()

    occupied = occupied_cells()
    chosen = set()
    new_pairs = []
    for pair in TUNNELS:
        a = random_free_cell(avoid=occupied | chosen)
        chosen.add(a)
        b = random_free_cell(avoid=occupied | chosen)
        chosen.add(b)
        new_pairs.append({"a": a, "b": b, "color": pair["color"]})

    apply_tunnels(new_pairs)


def resolve_enemy_contact():
    global game_over, score, time_since_move

    head = snake[0]
    eaten = []
    for e in enemies:
        if [e["x"], e["y"]] == head:
            if power_timer > 0:
                pops.append(
                    [e["x"] + CELL_SIZE / 2, e["y"] + CELL_SIZE / 2, 0]
                )
                score += ENEMY_EAT_BONUS
                eaten.append(e)
            else:
                game_over = True
                time_since_move = 0
                return
            
    for e in eaten:
        enemies.remove(e)


def step_enemies():
    scared = power_timer > 0
    head_x, head_y = snake[0]
    moves = [
        (CELL_SIZE, 0),
        (-CELL_SIZE, 0),
        (0, CELL_SIZE),
        (0, -CELL_SIZE),
    ]

    for e in enemies:
        valid = [
            (dx, dy) for dx, dy in moves
            if 0 <= e["x"] + dx < WIDTH and 0 <= e["y"] + dy < HEIGHT
        ]
        if not valid:
            continue

        # Evita dar media vuelta salvo que sea la unica salida.
        non_reverse = [m for m in valid if m != (-e["dx"], -e["dy"])]
        pool = non_reverse or valid

        if random.random() < ENEMY_RANDOMNESS:
            choice = random.choice(pool)
        else:
            def dist_after(m):
                return (
                    abs(e["x"] + m[0] - head_x)
                    + abs(e["y"] + m[1] - head_y)
                )

            choice = (max if scared else min)(pool, key=dist_after)

        e["px"], e["py"] = e["x"], e["y"]
        e["dx"], e["dy"] = choice
        e["x"] += choice[0]
        e["y"] += choice[1]

    resolve_enemy_contact()


def reset_game():
    global snake, prev_snake, direction_x, direction_y, direction_queue
    global food_x, food_y, game_over, time_since_move, score, paused
    global pops, game_over_time, score_recorded, new_record
    global enemies, power_food, power_timer, enemy_time, apples

    snake = [
        [400, 300],
        [380, 300],
        [360, 300]
    ]

    prev_snake = [segment[:] for segment in snake]

    direction_x = 1
    direction_y = 0

    direction_queue = []

    enemies = []
    power_food = None
    power_timer = 0
    enemy_time = 0

    apples = 0

    apply_tunnels(TUNNELS)

    food_x, food_y = place_food()

    for _ in range(ENEMIES_START):
        spawn_enemy()

    game_over = False

    time_since_move = 0

    score = 0

    paused = False

    pops = []

    game_over_time = 0

    score_recorded = False

    new_record = False


running = True
anim_time = 0
high_scores = load_high_scores()
new_record = False
reset_game()


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))


while running:

    dt = clock.tick(60)

    anim_time += dt

    if game_over:
        game_over_time += dt

    for pop in pops:
        pop[2] += dt
    pops[:] = [p for p in pops if p[2] <= 350]

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if restart_button.collidepoint(event.pos):
                reset_game()

            elif pause_button.collidepoint(event.pos) and not game_over:
                paused = not paused

        if event.type == pygame.KEYDOWN:

            if game_over and event.key == pygame.K_SPACE:
                reset_game()
                continue

            if event.key == pygame.K_p and not game_over:
                paused = not paused
                continue

            if event.key in (pygame.K_LEFT, pygame.K_a):
                queue_direction(-1, 0)

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                queue_direction(1, 0)

            elif event.key in (pygame.K_UP, pygame.K_w):
                queue_direction(0, -1)

            elif event.key in (pygame.K_DOWN, pygame.K_s):
                queue_direction(0, 1)

    if not game_over and not paused:

        time_since_move += dt

        max_acc = current_interval() * 3
        if time_since_move > max_acc:
            time_since_move = max_acc

        while time_since_move >= current_interval():
            time_since_move -= current_interval()

            prev_snake = [segment[:] for segment in snake]

            if direction_queue:
                direction_x, direction_y = direction_queue.pop(0)

            head_x = snake[0][0]
            head_y = snake[0][1]

            new_head = [
                head_x + direction_x * CELL_SIZE,
                head_y + direction_y * CELL_SIZE
            ]

            if (
                new_head[0] < 0
                or new_head[0] >= WIDTH
                or new_head[1] < 0
                or new_head[1] >= HEIGHT
            ):
                game_over = True
                time_since_move = 0
                break

            exit_cell = tunnel_exit.get((new_head[0], new_head[1]))
            if exit_cell is not None:
                new_head = [exit_cell[0], exit_cell[1]]

            snake.insert(0, new_head)

            ate_food = new_head[0] == food_x and new_head[1] == food_y
            ate_power = (
                power_food is not None
                and new_head[0] == power_food[0]
                and new_head[1] == power_food[1]
            )

            if ate_food:
                pops.append([food_x + CELL_SIZE / 2, food_y + CELL_SIZE / 2, 0])
                food_x, food_y = place_food()
                score += 1
                apples += 1

                # Cada LEVEL_EVERY manzanas se sube de nivel: los tuneles
                # cambian de lugar y reaparecen fantasmas hasta completar el
                # cupo del nivel (aunque te los hayas comido todos).
                if apples % LEVEL_EVERY == 0:
                    relocate_tunnels()
                    while len(enemies) < desired_enemy_count():
                        spawn_enemy()

                # El poder solo aparece cuando ya hay varios fantasmas.
                if (
                    power_food is None
                    and apples % POWER_EVERY == 0
                    and len(enemies) >= POWER_MIN_ENEMIES
                ):
                    px, py = random_free_cell(avoid=occupied_cells())
                    power_food = [px, py]

            else:
                snake.pop()

            if ate_power:
                pops.append([
                    power_food[0] + CELL_SIZE / 2,
                    power_food[1] + CELL_SIZE / 2,
                    0
                ])
                power_food = None
                power_timer = POWER_DURATION
                score += 1

            if new_head in snake[1:]:
                game_over = True

            if not game_over:
                resolve_enemy_contact()

            if game_over:
                time_since_move = 0
                break

        if power_timer > 0:
            power_timer = max(0, power_timer - dt)

        if not game_over:
            enemy_time += dt
            while enemy_time >= ENEMY_INTERVAL:
                enemy_time -= ENEMY_INTERVAL
                step_enemies()
                if game_over:
                    break

    if game_over and not score_recorded:
        register_score(score)
        score_recorded = True

    screen.fill((25, 25, 25))

    draw_grid()

    draw_tunnels()

    draw_power_food()

    pulse = (math.sin(anim_time / 180.0) + 1) / 2
    food_radius = int(CELL_SIZE * (0.38 + 0.06 * pulse))
    fcx = int(food_x + CELL_SIZE / 2)
    fcy = int(food_y + CELL_SIZE / 2)

    pygame.draw.line(
        screen, (90, 60, 30),
        (fcx, fcy - food_radius), (fcx + 2, fcy - food_radius - 4), 2
    )
    pygame.draw.circle(
        screen, (60, 180, 60),
        (fcx + 5, fcy - food_radius - 3), 3
    )
    pygame.draw.circle(screen, (210, 40, 40), (fcx, fcy), food_radius)
    pygame.draw.circle(
        screen, (255, 130, 130),
        (int(fcx - food_radius * 0.3), int(fcy - food_radius * 0.3)),
        max(1, int(food_radius * 0.3))
    )

    t = 1.0 if game_over else min(time_since_move / current_interval(), 1.0)

    head_cx, head_cy = snake[0][0] + CELL_SIZE / 2, snake[0][1] + CELL_SIZE / 2

    for i, segment in enumerate(snake):

        if i < len(prev_snake):
            start_x, start_y = prev_snake[i]
        else:
            start_x, start_y = segment

        dx = segment[0] - start_x
        dy = segment[1] - start_y

        if abs(dx) > CELL_SIZE or abs(dy) > CELL_SIZE:
            draw_x = segment[0]
            draw_y = segment[1]
        else:
            draw_x = start_x + dx * t
            draw_y = start_y + dy * t

        if i == 0:
            head_cx = draw_x + CELL_SIZE / 2
            head_cy = draw_y + CELL_SIZE / 2

        flash = (
            game_over
            and game_over_time < 600
            and (game_over_time // 120) % 2 == 0
        )

        if flash:
            color = (220, 50, 50)
        else:
            shade = max(110, 255 - i * 7)
            color = (0, shade, 0)

        draw_segment(draw_x, draw_y, color, i == 0)

    if power_timer > 0 and not game_over:
        pulse_a = (math.sin(anim_time / 90.0) + 1) / 2
        aura_r = int(CELL_SIZE * (0.7 + 0.25 * pulse_a))
        aura = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            aura, (120, 200, 255, 90),
            (aura_r + 2, aura_r + 2), aura_r, 3
        )
        screen.blit(aura, (int(head_cx - aura_r - 2), int(head_cy - aura_r - 2)))

    for e in enemies:
        draw_ghost(e)

    for pop in pops:
        prog = pop[2] / 350
        radius = int(CELL_SIZE * (0.4 + 1.4 * prog))
        alpha = max(0, int(200 * (1 - prog)))
        ring = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            ring, (255, 240, 120, alpha),
            (radius + 2, radius + 2), radius, 3
        )
        screen.blit(ring, (int(pop[0] - radius - 2), int(pop[1] - radius - 2)))

    score_text = small_font.render(
        "Puntaje: " + str(score),
        True,
        (255, 255, 255)
    )
    screen.blit(score_text, (10, 10))

    best = max(high_scores[0] if high_scores else 0, score)
    record_text = list_font.render(
        "Récord: " + str(best),
        True,
        (230, 200, 90)
    )
    screen.blit(record_text, (10, 40))

    level_text = list_font.render(
        "Nivel: " + str(current_level()),
        True,
        (140, 220, 255)
    )
    screen.blit(level_text, (10, 66))

    if power_timer > 0 and not game_over:
        frac = power_timer / POWER_DURATION
        bar_w = 200
        bx = WIDTH // 2 - bar_w // 2
        by = 18
        pygame.draw.rect(screen, (50, 55, 80), (bx, by, bar_w, 10),
                         border_radius=5)
        pygame.draw.rect(screen, (120, 200, 255),
                         (bx, by, int(bar_w * frac), 10), border_radius=5)
        label = button_font.render("¡PODER!", True, (180, 220, 255))
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, by + 12))

    draw_button(pause_button, "Reanudar" if paused else "Pausar")
    draw_button(restart_button, "Reiniciar")

    if paused and not game_over:

        pause_text = font.render(
            "PAUSA",
            True,
            (255, 255, 255)
        )

        screen.blit(
            pause_text,
            (
                WIDTH // 2 - pause_text.get_width() // 2,
                HEIGHT // 2 - pause_text.get_height() // 2
            )
        )

    if game_over:

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade = min(180, int(game_over_time / 600 * 180))
        overlay.fill((0, 0, 0, fade))
        screen.blit(overlay, (0, 0))

        y0 = 150

        text = font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y0))

        if new_record:
            rec = small_font.render("¡Nuevo récord!", True, (255, 215, 0))
            screen.blit(rec, (WIDTH // 2 - rec.get_width() // 2, y0 + 55))

        title = small_font.render("Mejores puntajes", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y0 + 110))

        list_y = y0 + 150
        if high_scores:
            highlighted = False
            for idx, s in enumerate(high_scores):
                is_current = (not highlighted) and new_record and s == score
                if is_current:
                    highlighted = True
                    color = (255, 215, 0)
                else:
                    color = (210, 210, 210)
                line = list_font.render(
                    str(idx + 1) + ".   " + str(s),
                    True,
                    color
                )
                screen.blit(
                    line,
                    (WIDTH // 2 - line.get_width() // 2, list_y + idx * 30)
                )
        else:
            none_line = list_font.render(
                "Sin puntajes aún", True, (170, 170, 170)
            )
            screen.blit(
                none_line,
                (WIDTH // 2 - none_line.get_width() // 2, list_y)
            )

        restart_text = small_font.render(
            "Presiona ESPACIO para reiniciar",
            True,
            (200, 200, 200)
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                HEIGHT - 60
            )
        )

    pygame.display.flip()

pygame.quit()

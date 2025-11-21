import pygame
from maze.maze_generator import MazeGenerator
from maze.algorithms import dijkstra, astar

# --- Cấu hình hiển thị ---
CELL_SIZE = 20
PADDING = 20
GAP = 40
FPS = 60

WALL_COLOR = (0, 0, 200)
PATH_COLOR = (0, 0, 0)
START_COLOR = (255, 255, 0)
GOAL_COLOR = (0, 255, 0)
DIVIDER_COLOR = (25, 25, 40)
BG_COLOR = (10, 10, 20)

MOVE_DELAY = 0.08    # tốc độ robot
SCAN_DELAY = 0.06    # tốc độ radar
PAUSED = False


# -------------------------------------------------------------
# VẼ MÊ CUNG
# -------------------------------------------------------------
def draw_one_maze(surface, maze, start, goal, ox, oy):
    rows, cols = maze.shape
    for r in range(rows):
        for c in range(cols):
            x = ox + c * CELL_SIZE
            y = oy + r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if maze[r, c] == 1:
                pygame.draw.rect(surface, WALL_COLOR, rect)
            else:
                pygame.draw.rect(surface, PATH_COLOR, rect)
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)

    sr, sc = start
    gr, gc = goal
    pygame.draw.rect(surface, START_COLOR,
                     (ox + sc * CELL_SIZE, oy + sr * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(surface, GOAL_COLOR,
                     (ox + gc * CELL_SIZE, oy + gr * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# -------------------------------------------------------------
# VẼ ROBOT
# -------------------------------------------------------------
def draw_robot(surface, path, index, ox, oy, color):
    if not path or index >= len(path):
        return

    r, c = path[index]
    x = ox + c * CELL_SIZE
    y = oy + r * CELL_SIZE
    pygame.draw.circle(surface, color, (x + CELL_SIZE // 2, y + CELL_SIZE // 2),
                       CELL_SIZE // 3)


# -------------------------------------------------------------
# RADAR SCAN
# -------------------------------------------------------------
def draw_radar(surface, explored, ox, oy, color, upto):
    for i in range(min(upto, len(explored))):
        r, c = explored[i]
        x = ox + c * CELL_SIZE + CELL_SIZE // 2
        y = oy + r * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(surface, color, (x, y), 4)


# -------------------------------------------------------------
# VẼ PATH = các chấm trắng
# -------------------------------------------------------------
def draw_path(surface, path, ox, oy):
    for r, c in path:
        x = ox + c * CELL_SIZE + CELL_SIZE // 2
        y = oy + r * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 4)


# -------------------------------------------------------------
# TẠO MÊ CUNG MỚI
# -------------------------------------------------------------
def generate_valid_maze(mg):
    while True:
        maze, start, goal = mg.generate_maze()
        dij_path, dij_cost, dij_scan = dijkstra(mg)
        ast_path, ast_cost, ast_scan = astar(mg)

        if dij_path and ast_path:
            return maze, start, goal, dij_path, dij_cost, ast_path, ast_cost, dij_scan, ast_scan


# -------------------------------------------------------------
# HUD
# -------------------------------------------------------------
def draw_hud(surface, speed, paused):
    font = pygame.font.SysFont(None, 24)
    t1 = font.render("SPACE: Replay | P: Pause | R: Reload | +/- Speed", True, (255, 255, 255))
    t2 = font.render(f"Toc do robot: {speed:.2f}  -  Trang thai: {'PAUSED' if paused else 'RUNNING'}", True, (200, 200, 200))
    surface.blit(t1, (20, 5))
    surface.blit(t2, (20, 30))


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
def main():
    global MOVE_DELAY, PAUSED

    pygame.init()
    pygame.display.set_caption("Radar Dijkstra vs A* Demo")
    clock = pygame.time.Clock()

    mg = MazeGenerator(width=31, height=21)

    (maze, start, goal,
     dij_path, dij_cost,
     ast_path, ast_cost,
     dij_scan, ast_scan) = generate_valid_maze(mg)

    rows, cols = maze.shape
    maze_w = cols * CELL_SIZE
    maze_h = rows * CELL_SIZE

    screen_w = PADDING + maze_w + GAP + maze_w + PADDING
    screen_h = PADDING + maze_h + PADDING + 40
    screen = pygame.display.set_mode((screen_w, screen_h))

    left_ox, left_oy = PADDING, PADDING + 40
    right_ox, right_oy = PADDING + maze_w + GAP, PADDING + 40

    # Radar index
    dij_scan_index = 0
    ast_scan_index = 0
    dij_scan_timer = 0
    ast_scan_timer = 0

    # Robot index
    dij_index = 0
    ast_index = 0

    scan_done = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        dij_scan_timer += dt
        ast_scan_timer += dt

        # ------------------------------
        # Event
        # ------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    (maze, start, goal,
                     dij_path, dij_cost,
                     ast_path, ast_cost,
                     dij_scan, ast_scan) = generate_valid_maze(mg)
                    dij_index = ast_index = 0
                    dij_scan_index = ast_scan_index = 0
                    dij_scan_timer = ast_scan_timer = 0
                    scan_done = False

                elif event.key == pygame.K_SPACE:
                    dij_index = ast_index = 0
                    dij_scan_index = ast_scan_index = len(dij_scan)
                    scan_done = True

                elif event.key == pygame.K_p:
                    PAUSED = not PAUSED

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    MOVE_DELAY = max(0.01, MOVE_DELAY - 0.01)

                elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE, pygame.K_KP_MINUS):
                    MOVE_DELAY = min(0.5, MOVE_DELAY + 0.01)

        # ------------------------------
        # Radar animation (quét trước)
        # ------------------------------
        if not PAUSED and not scan_done:
            if dij_scan_timer >= SCAN_DELAY:
                dij_scan_index += 1
                dij_scan_timer = 0

            if ast_scan_timer >= SCAN_DELAY:
                ast_scan_index += 1
                ast_scan_timer = 0

            # Khi radar quét xong
            if dij_scan_index >= len(dij_scan) and ast_scan_index >= len(ast_scan):
                scan_done = True

        # ------------------------------
        # Robot chạy sau radar
        # ------------------------------
        if scan_done and not PAUSED:
            if dij_index < len(dij_path) - 1:
                dij_index += 1

            if ast_index < len(ast_path) - 1:
                ast_index += 1

        # ------------------------------
        # DRAW
        # ------------------------------
        screen.fill(BG_COLOR)
        draw_hud(screen, MOVE_DELAY, PAUSED)

        pygame.draw.rect(screen, DIVIDER_COLOR,
                         (PADDING + maze_w, PADDING + 40, GAP, maze_h))

        draw_one_maze(screen, maze, start, goal, left_ox, left_oy)
        draw_one_maze(screen, maze, start, goal, right_ox, right_oy)

        # Radar (quét đường)
        draw_radar(screen, dij_scan, left_ox, left_oy, (80, 180, 255), dij_scan_index)
        draw_radar(screen, ast_scan, right_ox, right_oy, (200, 120, 255), ast_scan_index)

        # Path
        if scan_done:
            draw_path(screen, dij_path, left_ox, left_oy)
            draw_path(screen, ast_path, right_ox, right_oy)

        # Robot
        if scan_done:
            draw_robot(screen, dij_path, dij_index, left_ox, left_oy, (255, 50, 50))
            draw_robot(screen, ast_path, ast_index, right_ox, right_oy, (255, 0, 255))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

import pygame
from maze.maze_generator import MazeGenerator

# --- Cấu hình hiển thị ---
CELL_SIZE   = 20
PADDING     = 20          # lề xung quanh
GAP         = 40          # khoảng ngăn cách giữa 2 mê cung
FPS         = 60

WALL_COLOR  = (0, 0, 200)       # Xanh dương
PATH_COLOR  = (0, 0, 0)         # Đen
DOT_COLOR   = (255, 255, 255)   # Trắng
START_COLOR = (255, 255, 0)     # Vàng
GOAL_COLOR  = (0, 255, 0)       # Xanh lá
DIVIDER_COLOR = (25, 25, 40)    # màu vạch ngăn ở giữa
BG_COLOR    = (10, 10, 20)

def draw_one_maze(surface, maze, start, goal, ox, oy):
    """Vẽ 1 mê cung tại offset (ox, oy)"""
    rows, cols = maze.shape
    for r in range(rows):
        for c in range(cols):
            x = ox + c * CELL_SIZE
            y = oy + r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            if maze[r, c] == 1:  # tường
                pygame.draw.rect(surface, WALL_COLOR, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)  # viền đen mỏng
            else:                # đường
                pygame.draw.rect(surface, PATH_COLOR, rect)
                # chấm nhỏ cho đẹp kiểu Pac-Man
                pygame.draw.circle(surface, DOT_COLOR,
                                   (x + CELL_SIZE//2, y + CELL_SIZE//2), 3)
                pygame.draw.rect(surface, (40, 40, 40), rect, 1)  # viền xám nhạt

    # vẽ start/goal
    sr, sc = start
    gr, gc = goal
    pygame.draw.rect(surface, START_COLOR,
                     (ox + sc*CELL_SIZE, oy + sr*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(surface, GOAL_COLOR,
                     (ox + gc*CELL_SIZE, oy + gr*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    pygame.init()
    pygame.display.set_caption("Demo")
    clock = pygame.time.Clock()

    # Sinh 1 mê cung — dùng lại cùng dữ liệu để vẽ 2 lần -> hai bên giống hệt
    mg = MazeGenerator(width=31, height=21)
    maze, start, goal = mg.generate_maze()

    rows, cols = maze.shape
    maze_w = cols * CELL_SIZE
    maze_h = rows * CELL_SIZE

    # Kích thước cửa sổ: lề + mê cung trái + GAP + mê cung phải + lề
    screen_w = PADDING + maze_w + GAP + maze_w + PADDING
    screen_h = PADDING + maze_h + PADDING
    screen = pygame.display.set_mode((screen_w, screen_h))

    # Offset vẽ
    left_ox,  left_oy  = PADDING, PADDING
    right_ox, right_oy = PADDING + maze_w + GAP, PADDING

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # (dt không dùng ở bước này, để sẵn cho animation sau)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Tạo lại mê cung mới (cả hai bên vẫn y hệt nhau vì dùng cùng mảng)
                    maze, start, goal = mg.generate_maze()

        # Vẽ nền
        screen.fill(BG_COLOR)

        # Vạch ngăn giữa
        pygame.draw.rect(screen, DIVIDER_COLOR,
                         (PADDING + maze_w, PADDING, GAP, maze_h))

        # Vẽ mê cung trái & phải (dùng cùng dữ liệu)
        draw_one_maze(screen, maze, start, goal, left_ox, left_oy)
        draw_one_maze(screen, maze, start, goal, right_ox, right_oy)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

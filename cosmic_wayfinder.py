import pygame
import heapq
import time
import random
import math


COLOR_BG = (10, 10, 25) 
COLOR_GRID = (30, 30, 50)
COLOR_TEXT = (200, 200, 255)
COLOR_ACCENT = (0, 255, 200)
TILE_SIZE = 30
GRID_WIDTH = 25
GRID_HEIGHT = 20
PANEL_WIDTH = 320  
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE + 100  
FPS = 60
COST_EMPTY = 1
COST_NEBULA = 5
COST_ASTEROID = 10
COST_WORMHOLE = 2

def draw_star(surface, x, y, size, color):
    points = []
    for i in range(10):
        angle = math.pi * i / 5
        radius = size if i % 2 == 0 else size / 2
        points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 1)

def draw_ship(surface, rect):
    cx, cy = rect.center
    points = [
        (cx, rect.top + 4),        
        (rect.right - 4, rect.bottom - 4), 
        (cx, rect.bottom - 8),        
        (rect.left + 4, rect.bottom - 4)   
    ]
    pygame.draw.polygon(surface, (0, 255, 100), points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 1)

def draw_animated_ship(surface, x, y, size):
    rect = pygame.Rect(x, y, size, size)
    draw_ship(surface, rect)
    cx, cy = rect.center
    pygame.draw.circle(surface, (0, 255, 255), (cx, rect.bottom - 2), 4)

def draw_planet(surface, rect):
    cx, cy = rect.center
    r = rect.width // 2 - 2
    pygame.draw.circle(surface, (0, 100, 255), (cx, cy), r)
    pygame.draw.circle(surface, (50, 200, 50), (cx - 4, cy - 4), r // 2)
    pygame.draw.circle(surface, (50, 200, 50), (cx + 5, cy + 3), r // 3)
    pygame.draw.circle(surface, (100, 200, 255), (cx, cy), r, 1)

def draw_wormhole(surface, rect, time_offset):
    cx, cy = rect.center
    radius = (math.sin(time_offset * 5) * 2 + rect.width // 2 - 4)
    colors = [(0, 255, 255), (0, 100, 255), (255, 255, 255)]
    for i, color in enumerate(colors):
        pygame.draw.circle(surface, color, (cx, cy), max(2, int(radius - i*3)), 2)
    pygame.draw.circle(surface, (0, 50, 100), (cx, cy), 5)

def draw_blackhole(surface, rect, time_offset):
    cx, cy = rect.center
    for i in range(4):
        angle = time_offset * 2 + (i * math.pi / 2)
        end_x = cx + math.cos(angle) * 10
        end_y = cy + math.sin(angle) * 10
        pygame.draw.line(surface, (100, 0, 100), (cx, cy), (end_x, end_y), 2)
    pygame.draw.circle(surface, (0, 0, 0), (cx, cy), 6)
    pygame.draw.circle(surface, (150, 0, 150), (cx, cy), 7, 1)

def draw_asteroid(surface, rect):
    points = [
        (rect.left + 5, rect.top + 10),
        (rect.centerx, rect.top + 2),
        (rect.right - 5, rect.top + 8),
        (rect.right - 2, rect.bottom - 8),
        (rect.centerx, rect.bottom - 2),
        (rect.left + 4, rect.bottom - 6)
    ]
    pygame.draw.polygon(surface, (100, 80, 60), points)
    pygame.draw.polygon(surface, (60, 40, 30), points, 1)

def draw_rival_ship(surface, rect):
    cx, cy = rect.center
    pygame.draw.circle(surface, (255, 100, 100), (cx, cy - 2), 6)
    pygame.draw.ellipse(surface, (200, 50, 50), (rect.left, cy, rect.width, 10))
    pygame.draw.circle(surface, (255, 255, 0), (rect.left + 5, cy + 5), 2)
    pygame.draw.circle(surface, (255, 255, 0), (rect.right - 5, cy + 5), 2)
    pygame.draw.circle(surface, (255, 255, 0), (cx, cy + 6), 2)

class CosmicWayfinder:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cosmic Wayfinder: AI Search Agent")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 12) 
        self.title_font = pygame.font.SysFont("Verdana", 18, bold=True)
        
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.start = (2, GRID_HEIGHT // 2)
        self.goal = (GRID_WIDTH - 3, GRID_HEIGHT // 2)
        self.wormholes = {}
    
        self.path = []
        self.visited = set()
        self.frontier = []  
        self.running_algo = None
        self.algo_generator = None
        
        self.animating_ship = False
        self.ship_pos = None 
        self.ship_path_index = 0
        
        self.racing = False
        self.race_winner = None
        self.rival_pos = None
        self.rival_path = []
        self.rival_path_index = 0
        self.player_race_path = []
        
        self.bg_ships = []
        for _ in range(5):
            self.bg_ships.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(10, 20)
            })

        self.stats = {
            "UCS": {"nodes": 0, "cost": 0, "time": 0.0},
            "A*":  {"nodes": 0, "cost": 0, "time": 0.0},
            "Greedy": {"nodes": 0, "cost": 0, "time": 0.0} 
        }
        self.last_run = None 

        self.stars = [(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), random.random()) for _ in range(50)]

        self.generate_random_map()

    def generate_random_map(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.wormholes.clear()
        self.path = []
        self.visited = set()
        self.frontier = []
        self.last_run = None
        self.animating_ship = False 
   
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if random.random() < 0.35: self.grid[y][x] = 2 

        new_grid = [row[:] for row in self.grid]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == 2:
                    count = 0
                    for dy in [-1,0,1]:
                        for dx in [-1,0,1]:
                            if 0 <= x+dx < GRID_WIDTH and 0 <= y+dy < GRID_HEIGHT:
                                if self.grid[y+dy][x+dx] == 2: count += 1
                    if count < 4: new_grid[y][x] = 0 
        self.grid = new_grid

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if (x, y) == self.start or (x, y) == self.goal:
                    self.grid[y][x] = 0 
                    continue
                
                if self.grid[y][x] == 0:
                    r = random.random()
                    if r < 0.06: self.grid[y][x] = 1  
                    elif r < 0.15: self.grid[y][x] = 3 

        for _ in range(3):
            x1, y1 = random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)
            x2, y2 = random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)
            if (x1, y1) in [self.start, self.goal] or (x2, y2) in [self.start, self.goal]: continue
            
            if self.grid[y1][x1] == 0 and self.grid[y2][x2] == 0 and (x1,y1) != (x2,y2):
                self.grid[y1][x1] = 4
                self.grid[y2][x2] = 4
                self.wormholes[(x1, y1)] = (x2, y2)
                self.wormholes[(x2, y2)] = (x1, y1)
 

    def get_cost(self, pos):
        x, y = pos
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT): return float('inf')
        val = self.grid[y][x]
        if val == 1: return float('inf') 
        if val == 2: return COST_NEBULA
        if val == 3: return COST_ASTEROID
        return COST_EMPTY

    def get_neighbors(self, pos):
        x, y = pos
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neighbors = []
        if pos in self.wormholes:
            neighbors.append((self.wormholes[pos], COST_WORMHOLE))

        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                cost = self.get_cost((nx, ny))
                if cost != float('inf'):
                    neighbors.append(((nx, ny), cost))
        return neighbors
    
    def check_ship_collision(self, ship_pos):
     ship_rect = pygame.Rect(ship_pos[0], ship_pos[1], TILE_SIZE, TILE_SIZE)
     for bg in self.bg_ships:
        bg_rect = pygame.Rect(bg['x'], bg['y'], bg['size'], bg['size']//2)
        if ship_rect.colliderect(bg_rect):
            return True
     return False
 

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def solve_greedy(self):
        start_time = time.time()
        pq = [(self.heuristic(self.start, self.goal), self.start, [])] 
        visited = {self.start}
        nodes_expanded = 0

        while pq:
            _, current_node, current_path = heapq.heappop(pq)
            nodes_expanded += 1
            
            if nodes_expanded % 2 == 0:
                self.frontier = [node for _, node, _ in pq]
                yield

            if current_node == self.goal:
                self.path = current_path + [current_node]
                total_cost = 0
                for i in range(len(self.path)-1):
                    dist = abs(self.path[i][0] - self.path[i+1][0]) + abs(self.path[i][1] - self.path[i+1][1])
                    if dist > 1: total_cost += COST_WORMHOLE
                    else: total_cost += self.get_cost(self.path[i+1])

                self.stats["Greedy"] = {
                    "nodes": nodes_expanded,
                    "cost": total_cost,
                    "time": time.time() - start_time
                }
                self.last_run = "Greedy"
                return

            for neighbor, _ in self.get_neighbors(current_node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    self.visited.add(neighbor)
                    h = self.heuristic(neighbor, self.goal)
                    heapq.heappush(pq, (h, neighbor, current_path + [current_node]))
        
        self.last_run = "Greedy"

    def solve_ucs(self):
        start_time = time.time()
        pq = [(0, self.start, [])]
        visited_costs = {self.start: 0}
        nodes_expanded = 0

        while pq:
            current_cost, current_node, current_path = heapq.heappop(pq)
            nodes_expanded += 1
            
            if nodes_expanded % 2 == 0: 
                self.frontier = [node for _, node, _ in pq]
                yield

            if current_node == self.goal:
                self.path = current_path + [current_node]
                self.stats["UCS"] = {
                    "nodes": nodes_expanded,
                    "cost": current_cost,
                    "time": time.time() - start_time
                }
                self.last_run = "UCS"
                return

            for neighbor, step_cost in self.get_neighbors(current_node):
                new_cost = current_cost + step_cost
                if neighbor not in visited_costs or new_cost < visited_costs[neighbor]:
                    visited_costs[neighbor] = new_cost
                    self.visited.add(neighbor)
                    heapq.heappush(pq, (new_cost, neighbor, current_path + [current_node]))
        
        self.last_run = "UCS"

    def solve_astar(self):
        start_time = time.time()
        pq = [(0, self.start, [])] 
        g_scores = {self.start: 0}
        nodes_expanded = 0

        while pq:
            _, current_node, current_path = heapq.heappop(pq)
            nodes_expanded += 1
            
            if nodes_expanded % 2 == 0:
                self.frontier = [node for _, node, _ in pq]
                yield

            if current_node == self.goal:
                self.path = current_path + [current_node]
                self.stats["A*"] = {
                    "nodes": nodes_expanded,
                    "cost": g_scores[current_node],
                    "time": time.time() - start_time
                }
                self.last_run = "A*"
                return

            for neighbor, step_cost in self.get_neighbors(current_node):
                new_g = g_scores[current_node] + step_cost
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    f_score = new_g + self.heuristic(neighbor, self.goal)
                    self.visited.add(neighbor)
                    heapq.heappush(pq, (f_score, neighbor, current_path + [current_node]))

        self.last_run = "A*"

    def get_path_astar(self):
        pq = [(0, self.start, [])]
        g_scores = {self.start: 0}
        
        while pq:
            _, current, path = heapq.heappop(pq)
            if current == self.goal: return path + [current]
            
            for neighbor, cost in self.get_neighbors(current):
                new_g = g_scores[current] + cost
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    f = new_g + self.heuristic(neighbor, self.goal)
                    heapq.heappush(pq, (f, neighbor, path + [current]))
        return []

    def get_path_greedy(self):
        pq = [(self.heuristic(self.start, self.goal), self.start, [])]
        visited = {self.start}
        
        while pq:
            _, current, path = heapq.heappop(pq)
            if current == self.goal: return path + [current]
            
            for neighbor, _ in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    h = self.heuristic(neighbor, self.goal)
                    heapq.heappush(pq, (h, neighbor, path + [current]))
        return []

    def start_race(self):
        self.player_race_path = self.get_path_astar()
        self.rival_path = self.get_path_greedy()
        
        if not self.player_race_path or not self.rival_path: return
        
        self.racing = True
        self.race_winner = None
        self.animating_ship = False 
        self.running_algo = False
        
        sx, sy = self.start
        self.ship_pos = [sx * TILE_SIZE, sy * TILE_SIZE]
        self.rival_pos = [sx * TILE_SIZE, sy * TILE_SIZE]
        self.ship_path_index = 0
        self.rival_path_index = 0

    def update_race(self):
        if not self.racing: return
        collision = self.check_ship_collision(self.ship_pos)
        if collision:
            speed = 2  
        else:
            speed = 5  

        def move_entity(pos, path, idx, is_player):
            if idx >= len(path) - 1: return pos, idx, True 
            
            target_grid = path[idx + 1]
            tx, ty = target_grid[0] * TILE_SIZE, target_grid[1] * TILE_SIZE
            
            dx = tx - pos[0]
            dy = ty - pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > TILE_SIZE * 1.5:
                return [tx, ty], idx + 1, False

            current_grid = path[idx]
            cost = self.get_cost(current_grid)
            if cost == float('inf'): cost = 1 
            
            speed = 4.0 / max(1, cost * 0.5) 
            
            if dist <= speed:
                return [tx, ty], idx + 1, False
            else:
                return [pos[0] + (dx/dist)*speed, pos[1] + (dy/dist)*speed], idx, False

        self.ship_pos, self.ship_path_index, p_finished = move_entity(
            self.ship_pos, self.player_race_path, self.ship_path_index, True)
            
        self.rival_pos, self.rival_path_index, r_finished = move_entity(
            self.rival_pos, self.rival_path, self.rival_path_index, False)
            
        if p_finished and not self.race_winner:
            self.race_winner = "YOU WON!"
            self.racing = False
        elif r_finished and not self.race_winner:
            self.race_winner = "RIVAL WON!"
            self.racing = False

    def update_animation(self):
     if not self.animating_ship or not self.path or not self.ship_pos:
        return

     ship_rect = pygame.Rect(self.ship_pos[0], self.ship_pos[1], TILE_SIZE, TILE_SIZE)
     for bg in self.bg_ships:
        bg_rect = pygame.Rect(bg['x'], bg['y'], bg['size'], bg['size']//2)
        if ship_rect.colliderect(bg_rect):
            self.animating_ship = False
            self.path = []
            self.visited = set()
            self.last_run = None
            self.ship_pos = None
            self.race_winner = "YOU LOSE!"
            return 
        
     target_grid_pos = self.path[self.ship_path_index]
     target_x = target_grid_pos[0] * TILE_SIZE
     target_y = target_grid_pos[1] * TILE_SIZE

     dx = target_x - self.ship_pos[0]
     dy = target_y - self.ship_pos[1]
     dist = math.sqrt(dx*dx + dy*dy)
    
     speed = 5

     if dist > TILE_SIZE * 1.5: 
        self.ship_pos = [target_x, target_y]   
        dist = 0

     if dist <= speed:
        self.ship_pos = [target_x, target_y]
        self.ship_path_index += 1
        if self.ship_path_index >= len(self.path):
            self.animating_ship = False  
     else:
        self.ship_pos[0] += (dx / dist) * speed
        self.ship_pos[1] += (dy / dist) * speed

     for ship in self.bg_ships:
        ship['x'] += ship['speed']
        if ship['x'] > WINDOW_WIDTH:
            ship['x'] = -20
            ship['y'] = random.randint(0, WINDOW_HEIGHT)

    def draw_dashboard(self):
        panel_rect = pygame.Rect(WINDOW_WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (20, 20, 35), panel_rect)
        pygame.draw.line(self.screen, COLOR_ACCENT, (panel_rect.left, 0), (panel_rect.left, WINDOW_HEIGHT), 2)

        padding = 15
        
        title = self.title_font.render("MISSION CONTROL", True, COLOR_ACCENT)
        self.screen.blit(title, (panel_rect.left + padding, 20))

        y_off = 50 
        instr = [
            "CONTROLS:",
            "[1] Run UCS (Optimal)",
            "[2] Run A* (Fast, Optimal)",
            "[3] Run Greedy (Fastest, Subopt)", 
            "[4] RACE MODE!", 
            "[SPACE] Fly Ship (after a path is found)",
            "[M] New Map",
            "[R] Reset Search",
            "[L-Click] Place Black Hole",
            "[R-Click] Place Nebula"
        ]
        for line in instr:
            color = (180, 180, 200)
            txt = self.font.render(line, True, color)
            self.screen.blit(txt, (panel_rect.left + padding, y_off))
            y_off += 18 
        
        y_off += 15
        legend_items = [
            ("Start", (0, 255, 100)), ("Goal", (0, 100, 255)),
            ("Nebula (Cost 5)", (100, 0, 100)), ("Asteroid (Cost 10)", (100, 80, 60)),
            ("Wormhole (Teleport)", (0, 255, 255)),
            ("Rival (Greedy)", (255, 100, 100)) 
        ]
        for label, color in legend_items:
            pygame.draw.circle(self.screen, color, (panel_rect.left + padding + 5, y_off + 7), 5)
            txt = self.font.render(label, True, (200, 200, 200))
            self.screen.blit(txt, (panel_rect.left + padding + 20, y_off))
            y_off += 18

        y_off += 25
        
        if self.racing or self.race_winner:
            header = self.title_font.render("RACE STATUS", True, (255, 100, 100))
            self.screen.blit(header, (panel_rect.left + padding, y_off))
            y_off += 25
            
            status = "RACING..." if self.racing else self.race_winner
            col = (255, 255, 255) if self.racing else ((0, 255, 0) if "YOU" in status else (255, 0, 0))
            
            s_txt = self.font.render(status, True, col)
            self.screen.blit(s_txt, (panel_rect.left + padding, y_off))
            y_off += 40

        if self.last_run and not self.racing:
            header = self.title_font.render(f"LAST RUN: {self.last_run}", True, (255, 255, 0))
            self.screen.blit(header, (panel_rect.left + padding, y_off))
            y_off += 25
            
            s = self.stats[self.last_run]
            
            stats_txt = [
                f"Nodes Expanded: {s['nodes']}",
                f"Total Path Cost: {s['cost']}",
                f"Compute Time: {s['time']:.4f}s"
            ]
            for line in stats_txt:
                t = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(t, (panel_rect.left + padding, y_off))
                y_off += 18

            y_off += 15
            graph_h = 100 
            graph_w = PANEL_WIDTH - (padding * 2)
            base_y = y_off + graph_h
            
            pygame.draw.rect(self.screen, (30, 30, 45), (panel_rect.left + padding, y_off, graph_w, graph_h))
            
            pygame.draw.line(self.screen, (100, 100, 100), (panel_rect.left + padding, base_y), (panel_rect.left + padding + graph_w, base_y))
            pygame.draw.line(self.screen, (100, 100, 100), (panel_rect.left + padding, y_off), (panel_rect.left + padding, base_y))
            
            max_nodes = max(self.stats["UCS"]["nodes"], self.stats["A*"]["nodes"], self.stats["Greedy"]["nodes"])
            if max_nodes == 0: max_nodes = 1
            
            bar_width = 30 
            spacing = 15
            
            def draw_bar(key, color, x_offset):
                val = self.stats[key]["nodes"]
                if val > 0:
                    h = (val / max_nodes) * (graph_h - 20)
                    pygame.draw.rect(self.screen, color, 
                                   (panel_rect.left + padding + x_offset, base_y - h, bar_width, h))
                    val_txt = self.font.render(str(val), True, (200, 200, 200))
                    self.screen.blit(val_txt, (panel_rect.left + padding + x_offset, base_y - h - 15))
                
                lbl = self.font.render(key, True, color)
                self.screen.blit(lbl, (panel_rect.left + padding + x_offset, base_y + 5))

            draw_bar("UCS", (255, 80, 80), 10)
            draw_bar("A*", (80, 255, 80), 10 + bar_width + spacing)
            draw_bar("Greedy", (80, 80, 255), 10 + (bar_width + spacing)*2) # Added Greedy Bar

    def draw(self):
        self.screen.fill(COLOR_BG)
        time_offset = time.time()
        
        for sx, sy, sb in self.stars:
            b = int(255 * (math.sin(time_offset * sb) + 1) / 2)
            self.screen.set_at((sx, sy), (b, b, b))
            
        for ship in self.bg_ships:
            pygame.draw.rect(self.screen, (50, 50, 70), (ship['x'], ship['y'], ship['size'], ship['size']//2))
            pygame.draw.circle(self.screen, (100, 100, 150), (ship['x'] + ship['size']//2, ship['y']), 2)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                cell_type = self.grid[y][x]
                
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

                if cell_type == 1: 
                    draw_blackhole(self.screen, rect, time_offset)
                elif cell_type == 2: 
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((100, 0, 100, 100)) 
                    self.screen.blit(s, rect)
                elif cell_type == 3: 
                    draw_asteroid(self.screen, rect)
                elif cell_type == 4: 
                    draw_wormhole(self.screen, rect, time_offset)
                    if (x,y) in self.wormholes:
                        target = self.wormholes[(x,y)]
                        if (x < target[0]) or (x == target[0] and y < target[1]):
                            start_pos = rect.center
                            end_pos = (target[0] * TILE_SIZE + TILE_SIZE//2, target[1] * TILE_SIZE + TILE_SIZE//2)
                            pygame.draw.line(self.screen, (0, 100, 100), start_pos, end_pos, 1)

        for vx, vy in self.visited:
            if (vx, vy) != self.start and (vx, vy) != self.goal:
                center = (vx * TILE_SIZE + TILE_SIZE//2, vy * TILE_SIZE + TILE_SIZE//2)
                pygame.draw.circle(self.screen, (50, 50, 100), center, 2)

        if len(self.path) > 1:
            for i in range(len(self.path) - 1):
                p1 = self.path[i]
                p2 = self.path[i+1]
                
                pos1 = (p1[0] * TILE_SIZE + TILE_SIZE//2, p1[1] * TILE_SIZE + TILE_SIZE//2)
                pos2 = (p2[0] * TILE_SIZE + TILE_SIZE//2, p2[1] * TILE_SIZE + TILE_SIZE//2)
                
                dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                
                if dist > 1: 
                    pygame.draw.line(self.screen, (0, 255, 255), pos1, pos2, 2) 
                else:
                    pygame.draw.line(self.screen, (200, 200, 50), pos1, pos2, 4) 

        if self.racing or self.race_winner:
            if self.rival_pos:
                rect = pygame.Rect(self.rival_pos[0], self.rival_pos[1], TILE_SIZE, TILE_SIZE)
                draw_rival_ship(self.screen, rect)

        sx, sy = self.start
        gx, gy = self.goal
        
        if not self.animating_ship and not self.racing and not self.race_winner:
            draw_ship(self.screen, pygame.Rect(sx * TILE_SIZE, sy * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        else:
            if self.ship_pos:
                draw_animated_ship(self.screen, self.ship_pos[0], self.ship_pos[1], TILE_SIZE)

        draw_planet(self.screen, pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        self.draw_dashboard()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                    
                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        if (gx, gy) != self.start and (gx, gy) != self.goal:
                            if event.button == 1: 
                                self.grid[gy][gx] = 1 if self.grid[gy][gx] != 1 else 0
                            elif event.button == 3: 
                                self.grid[gy][gx] = 2 if self.grid[gy][gx] != 2 else 0
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.path = []
                        self.visited = set()
                        self.algo_generator = self.solve_ucs()
                        self.running_algo = True
                        self.animating_ship = False
                        self.racing = False # 
                        self.race_winner = None
                    elif event.key == pygame.K_2:
                        self.path = []
                        self.visited = set()
                        self.algo_generator = self.solve_astar()
                        self.running_algo = True
                        self.animating_ship = False
                        self.racing = False # 
                        self.race_winner = None
                    elif event.key == pygame.K_3: 
                        self.visited = set()
                        self.algo_generator = self.solve_greedy()
                        self.running_algo = True
                        self.animating_ship = False
                        self.racing = False 
                        self.race_winner = None
                    elif event.key == pygame.K_4: 
                        self.start_race()
                    elif event.key == pygame.K_SPACE:
                        if self.path:
                            self.animating_ship = True
                            self.ship_path_index = 0
                            self.ship_pos = [self.path[0][0] * TILE_SIZE, self.path[0][1] * TILE_SIZE]
                    elif event.key == pygame.K_m:
                        self.generate_random_map()
                        self.racing = False # 
                        self.race_winner = None
                    elif event.key == pygame.K_r:
                        self.path = []
                        self.visited = set()
                        self.last_run = None
                        self.animating_ship = False
                        self.racing = False # 
                        self.race_winner = None

            if self.running_algo:
                try:
                    next(self.algo_generator)
                except StopIteration:
                    self.running_algo = False
            
            if self.animating_ship:
                self.update_animation()
            
            if self.racing:
                self.update_race()
            
            if not self.animating_ship:
                for ship in self.bg_ships:
                    ship['x'] += ship['speed']
                    if ship['x'] > WINDOW_WIDTH:
                        ship['x'] = -20
                        ship['y'] = random.randint(0, WINDOW_HEIGHT)

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = CosmicWayfinder()
    game.run()

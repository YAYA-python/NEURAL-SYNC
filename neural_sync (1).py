                      
"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   N E U R A L - S Y N C   :   O B S I D I A N   S E C T O R    ║
║                                                                  ║
║   Cyberpunk grid-management action game                         ║
║   Prevent thermal cascade. Control the meltdown.                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pygame, math, random, sys

                                                                 
            
                                                                 
pygame.init()
SW, SH = 900, 700
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("NEURAL-SYNC: OBSIDIAN SECTOR")
pygame.mouse.set_visible(False)
clock  = pygame.time.Clock()

                                                                 
                     
                                                                 
VOID      = (  8,   8,  10)                          
STABLE    = ( 22,  33,  62)                                 
WARM      = ( 15,  52,  96)                                  
CRITICAL  = (233,  69,  96)                                  
GLITCH    = (255, 211, 105)                                
COOLANT   = (  0, 210, 255)                           
WHITE     = (255, 255, 255)

                                                                 
                
                                                                 
NW  = NH = 64                                      
NRAD     = 6                       
GAP      = 12                             
ROWS = COLS = 8
GW = COLS*NW + (COLS-1)*GAP                               
GH = ROWS*NH + (ROWS-1)*GAP                               
GX0 = 450 - GW//2                                
GY0 = 350 - GH//2                                

                                                                 
                     
                                                                 
HEAT_RISE    = 1.0                                        
DIFF_THR     = 75.0                                  
DIFF_K       = 0.05                                         
HEAT_MAX     = 100.0
MELT_LIMIT   = 4                                              
WORM_ITV     = 12.0                               
SHAKE_MAX    = 20                            
SHAKE_AMP    = 8                             
COOL_MAX     = 100.0
COOL_REFILL  = 8.0                
COOL_COST    = 15.0                
COOL_AMOUNT  = 25.0                                 

                                                                 
              
                                                                 
def _fnt(size, bold=True):
    for name in ("Courier New", "Courier", "Lucida Console",
                 "DejaVu Sans Mono", "monospace"):
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

F8  = _fnt(8);  F10 = _fnt(10); F12 = _fnt(12)
F14 = _fnt(14); F26 = _fnt(26); F46 = _fnt(46)

                                                                 
                                                              
                                                                 
LAYER = pygame.Surface((SW, SH), pygame.SRCALPHA)

                                                                 
                                              
                                                                 
def _build_scanlines():
    s = pygame.Surface((SW, SH), pygame.SRCALPHA)
    for y in range(0, SH, 3):
        pygame.draw.line(s, (0, 0, 0, 18), (0, y), (SW, y))
    return s

def _build_vignette():
    s = pygame.Surface((SW, SH), pygame.SRCALPHA)
    cx, cy = SW//2, SH//2
    mr = math.hypot(cx, cy)
    for i in range(1, 70):
        r = int(mr * i / 70)
        a = int(75 * (1 - i/70)**2.2)
        pygame.draw.ellipse(s, (0, 0, 0, a), (cx-r, cy-r, r*2, r*2), 1)
    return s

def _build_grid_bg():
    """Faint hex-grid texture behind the node matrix."""
    s = pygame.Surface((SW, SH), pygame.SRCALPHA)
                                                        
    for c in range(COLS + 1):
        x = GX0 + c*(NW+GAP) - GAP//2
        pygame.draw.line(s, (*STABLE, 30), (x, GY0-10), (x, GY0+GH+10))
    for r in range(ROWS + 1):
        y = GY0 + r*(NH+GAP) - GAP//2
        pygame.draw.line(s, (*STABLE, 30), (GX0-10, y), (GX0+GW+10, y))
    return s

SCANLINES = _build_scanlines()
VIGNETTE  = _build_vignette()
GRID_BG   = _build_grid_bg()

                                                                 
          
                                                                 
def lc(a, b, t):
    """Lerp two RGB tuples by scalar t ∈ [0,1]."""
    t = max(0.0, min(1.0, t))
    return (int(a[0]+(b[0]-a[0])*t),
            int(a[1]+(b[1]-a[1])*t),
            int(a[2]+(b[2]-a[2])*t))

def heat_color(h):
    """3-way gradient: STABLE → WARM → CRITICAL."""
    f = min(h, 100.0) / 100.0
    if f <= 0.40:
        return lc(STABLE, WARM,     f / 0.40)
    return         lc(WARM,   CRITICAL, (f - 0.40) / 0.60)

                                                                 
                            
                                                                 
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life')

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        a = random.uniform(0.0, 6.2832)
                                              
        spd = random.uniform(80.0, 140.0)
        self.vx, self.vy = math.cos(a)*spd, math.sin(a)*spd
        self.life = 30.0                                       

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= 60.0 * dt                               
        return self.life > 0.0

    def draw(self, layer, ox: int, oy: int):
        px, py = int(self.x + ox), int(self.y + oy)
        if 0 <= px < SW and 0 <= py < SH:
            a = max(0, int(255 * self.life / 30.0))
            layer.set_at((px, py), (*GLITCH, a))

                                                                 
       
                                                                 
class Node:
    def __init__(self, row: int, col: int):
        self.row, self.col = row, col
        self.heat  = random.uniform(5.0, 20.0)
        self._ever_melted = False                               
                                         
        self.bx = GX0 + col * (NW + GAP)
        self.by = GY0 + row * (NH + GAP)

                                                                
    @property
    def sag(self)  -> float:        return self.heat / 20.0
    @property
    def ry(self)   -> int:          return int(self.by + self.sag)
    @property
    def rect(self) -> pygame.Rect:  return pygame.Rect(self.bx, self.ry, NW, NH)
    @property
    def cx(self)   -> int:          return self.bx + NW // 2
    @property
    def cy(self)   -> int:          return self.ry  + NH // 2

                                                                
    def update(self, dt: float):
        self.heat = min(HEAT_MAX, self.heat + HEAT_RISE * dt)

    def cool(self, amount: float):
        self.heat = max(0.0, self.heat - amount)

    def melt_trigger(self) -> bool:
        """Returns True exactly once when node first hits 100."""
        if self.heat >= HEAT_MAX and not self._ever_melted:
            self._ever_melted = True
            return True
        if self.heat < 99.0:
            self._ever_melted = False
        return False

                                                                
    def draw(self, surf, layer, ox: int, oy: int):
        dr  = pygame.Rect(self.bx + ox, self.ry + oy, NW, NH)
        col = heat_color(self.heat)
        t   = pygame.time.get_ticks()
        h   = self.heat

                                                                
        if h > 50:
            gfrac = (h - 50) / 50.0
            ga    = int(55 * gfrac)
            gc    = CRITICAL if h > 72 else WARM
            gs    = NW + 22
            pygame.draw.rect(layer, (*gc, ga),
                             (dr.x - 11, dr.y - 11, gs, gs),
                             border_radius=NRAD + 9)

                                                                
        pygame.draw.rect(surf, col, dr, border_radius=NRAD)

                                                                
        tha = int(48 * (1.0 - h / 100.0))
        if tha > 5:
            pygame.draw.rect(layer, (*WHITE, tha),
                             (dr.x + 3, dr.y + 3, NW - 6, 3))

                                                                
        bc = lc(lc(COOLANT, GLITCH, h / 100.0), CRITICAL, max(0.0, (h-70)/30.0))
        pygame.draw.rect(surf, bc, dr, 1, border_radius=NRAD)

                                                                
                                             
                                                  
        hb_scale = abs(math.sin(t * 0.005))
        hb_size  = max(1, int(4 * hb_scale))
        hb_alpha = int(200 * ((t % 2000) / 2000.0))
        hbx = dr.centerx - hb_size // 2
        hby = dr.centery - hb_size // 2 - 8
        pygame.draw.rect(layer, (*COOLANT, hb_alpha),
                         (hbx, hby, hb_size, hb_size))

                                                               
        jx = jy = 0
        if h > 92:
            jx = random.randint(-2, 2)
            jy = random.randint(-2, 2)
        tc = CRITICAL if h > 75 else WHITE
        label = F10.render(f"{int(h)}%", True, tc)
        surf.blit(label, (dr.centerx - label.get_width()//2 + jx,
                          dr.bottom  - 14 + jy))

                                                                
        if h >= HEAT_MAX:
            mp = int(100 + 80 * abs(math.sin(t * 0.012)))
            pygame.draw.rect(layer, (*CRITICAL, mp), dr, 2, border_radius=NRAD)


                                                                 
              
                                                                 
class GlitchWorm:
    SPEED  = 105.0           
    LEAD_R = 10                                          
    TAIL_R = 6                                             
    N_SEGS = 6                              
    HIST   = 80                      

    def __init__(self):
        margin = 25
        edge   = random.randint(0, 3)
        if   edge == 0: x, y = random.randint(margin, SW-margin), -margin
        elif edge == 1: x, y = random.randint(margin, SW-margin),  SH+margin
        elif edge == 2: x, y = -margin,    random.randint(margin, SH-margin)
        else:           x, y =  SW+margin, random.randint(margin, SH-margin)
        self.x, self.y = float(x), float(y)
        self.history   = [(self.x, self.y)] * (self.N_SEGS * 10)
        self.dead      = False
        self.pulse     = 0.0                       

    def update(self, dt: float, grid):
                                                                
        target = max((n for row in grid for n in row), key=lambda n: n.heat)
        dx = target.cx - self.x
        dy = target.cy - self.y
        dist = math.hypot(dx, dy)
        if dist < 0.5: return

        self.x += (dx / dist) * self.SPEED * dt
        self.y += (dy / dist) * self.SPEED * dt
        self.history.insert(0, (self.x, self.y))
        if len(self.history) > self.HIST:
            self.history.pop()

        self.pulse += dt * 6.0

                                                               
        if dist <= 20.0:
            target.heat = min(HEAT_MAX, target.heat + 25.0)
            self.dead   = True

    def draw(self, layer, ox: int, oy: int):
        step = max(1, len(self.history) // self.N_SEGS)
        glow_alpha = int(30 + 20 * abs(math.sin(self.pulse)))
        for i in range(self.N_SEGS):
            sx, sy = self.history[min(i * step, len(self.history) - 1)]
            r = self.LEAD_R if i == 0 else self.TAIL_R
                                     
            seg_alpha = max(30, 180 - i * 22)
            px_, py_ = int(sx + ox), int(sy + oy)

                        
            g = r + 5
            pygame.draw.circle(layer, (*GLITCH, glow_alpha), (px_, py_), g)

                          
            pygame.draw.circle(layer, (*GLITCH, seg_alpha), (px_, py_), r)

                                         
            if i == 0:
                pygame.draw.circle(layer, (255, 255, 255, 220), (px_, py_), 3)
                            
                arc_a = int(60 + 40 * abs(math.sin(self.pulse * 1.5)))
                pygame.draw.circle(layer, (*CRITICAL, arc_a), (px_, py_), r + 3, 1)


                                                                 
                          
                                                                 
class Needle:
    SIZE = 24

    def __init__(self):
        self.angle  = 0.0
                                                           
        self.pulses = []

    def update(self, dt: float):
                                                                 
        self.angle = (self.angle + 90.0 * dt) % 360.0
        self.pulses = [(s, e, l - 60.0*dt, m)
                       for s, e, l, m in self.pulses
                       if l - 60.0*dt > 0]

    def hit_node(self, mx: int, my: int, grid) -> "Node | None":
        for row in grid:
            for n in row:
                if n.rect.collidepoint(mx, my):
                    return n
        return None

    def fire_pulse(self, src, dst):
        self.pulses.append((src, dst, 20.0, 20.0))

    def draw(self, surf, layer, mx: int, my: int, ox: int, oy: int):
        px, py = mx + ox, my + oy
        half   = self.SIZE // 2
        gap    = 6
        cr     = math.radians(self.angle)
        ca, sa = math.cos(cr), math.sin(cr)

        def rot(lx, ly):
            return (int(px + lx*ca - ly*sa),
                    int(py + lx*sa + ly*ca))

                                                                
        for (sx, sy), (ex, ey), life, maxl in self.pulses:
            a = int(230 * life / maxl)
                          
            pygame.draw.line(layer, (*COOLANT, a),
                             (sx+ox, sy+oy), (ex+ox, ey+oy), 1)
                            
            pygame.draw.line(layer, (*COOLANT, a // 5),
                             (sx+ox, sy+oy), (ex+ox, ey+oy), 4)

                                                                
        pygame.draw.circle(layer, (*COOLANT, 100), (px, py), half,     1)
        pygame.draw.circle(layer, (*COOLANT,  35), (px, py), half + 4, 1)

                                                                
        arms = [
            (-half, 0, -gap, 0), (gap, 0, half, 0),
            (0, -half, 0, -gap), (0, gap, 0, half),
        ]
        for ax, ay, bx, by in arms:
            pygame.draw.line(surf, COOLANT, rot(ax, ay), rot(bx, by), 1)

                                                                
        for ta in (45, 135, 225, 315):
            ar = math.radians(self.angle + ta)
            x1 = int(px + (half - 5) * math.cos(ar))
            y1 = int(py + (half - 5) * math.sin(ar))
            x2 = int(px + half * math.cos(ar))
            y2 = int(py + half * math.sin(ar))
            pygame.draw.line(surf, COOLANT, (x1, y1), (x2, y2), 1)

                                                                
        pygame.draw.circle(surf, COOLANT, (px, py), 2)


                                                                 
                       
                                                                 
class NeuralSync:
    def __init__(self):
        self.grid      = [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.particles = []
        self.worms     = []
        self.needle    = Needle()
        self.coolant   = COOL_MAX
        self.worm_t    = 0.0
        self.shake     = 0
        self.over      = False
        self.tick      = 0                                     

                                                                
    def click(self, mx: int, my: int):
        if self.over or self.coolant < 1.0:
            return
        node = self.needle.hit_node(mx, my, self.grid)
        if node:
                                       
            self.needle.fire_pulse((mx, my), (node.cx, node.cy))
                                              
            for _ in range(12):
                self.particles.append(Particle(float(node.cx), float(node.cy)))
                                  
            node.cool(COOL_AMOUNT)
            self.coolant = max(0.0, self.coolant - COOL_COST)

                                                                
    def update(self, dt: float):
        if self.over:
            return
        dt = min(dt, 0.05)               
        self.tick += 1

                                
        self.coolant = min(COOL_MAX, self.coolant + COOL_REFILL * dt)

                                                                
        for row in self.grid:
            for n in row:
                n.update(dt)
                if n.melt_trigger():
                    self.shake = SHAKE_MAX

                                                     
                                                                
        delta = [[0.0] * COLS for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                h = self.grid[r][c].heat
                if h > DIFF_THR:
                                                                    
                    spread = h * DIFF_K * dt
                    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS:
                            delta[nr][nc] += spread
        for r in range(ROWS):
            for c in range(COLS):
                self.grid[r][c].heat = min(HEAT_MAX,
                                           self.grid[r][c].heat + delta[r][c])

                                                                
        melted = sum(1 for row in self.grid for n in row
                     if n.heat >= HEAT_MAX)
        if melted >= MELT_LIMIT:
            self.over = True

                                                                
        if self.shake > 0:
            self.shake -= 1

                                                                
        self.worm_t += dt
        if self.worm_t >= WORM_ITV:
            self.worm_t = 0.0
            self.worms.append(GlitchWorm())

        for w in self.worms:
            w.update(dt, self.grid)
        self.worms = [w for w in self.worms if not w.dead]

                                                                
        self.particles = [p for p in self.particles if p.update(dt)]
        self.needle.update(dt)

                                                                
    def draw(self):
                                            
        if self.shake > 0:
            fr  = self.shake
            amp = SHAKE_AMP * (fr / SHAKE_MAX)
            ox  = int(math.sin(fr * 1.5) * amp)
            oy  = int(math.cos(fr * 2.1) * amp * 0.55)
        else:
            ox = oy = 0

                                                                
        screen.fill(VOID)
        LAYER.fill((0, 0, 0, 0))

                                                                
        screen.blit(GRID_BG, (ox, oy))

                                                                
        for r in range(ROWS):
            for c in range(COLS):
                n = self.grid[r][c]
                for dr, dc in ((0, 1), (1, 0)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        nb = self.grid[nr][nc]
                        avg_h = (n.heat + nb.heat) * 0.5
                        a = int(14 + 22 * (avg_h / 100.0))
                        wire_col = lc(STABLE, CRITICAL, avg_h / 100.0)
                        pygame.draw.line(LAYER, (*wire_col, a),
                                         (n.cx+ox, n.cy+oy),
                                         (nb.cx+ox, nb.cy+oy), 1)

                                                                
        for row in self.grid:
            for n in row:
                n.draw(screen, LAYER, ox, oy)

                                                                
        for w in self.worms:
            w.draw(LAYER, ox, oy)

                                                                
        for p in self.particles:
            p.draw(LAYER, ox, oy)

                                                                
        mx, my = pygame.mouse.get_pos()
        self.needle.draw(screen, LAYER, mx, my, ox, oy)

                                                                
        screen.blit(LAYER, (0, 0))

                                                                
        screen.blit(SCANLINES, (0, 0))
        screen.blit(VIGNETTE,  (0, 0))

                                                                
        self._draw_hud()

                                                                
        if self.over:
            self._draw_gameover()

                                                                
    def _draw_hud(self):
        t = pygame.time.get_ticks()

                                                                
        title = F14.render("NEURAL-SYNC : OBSIDIAN SECTOR", True, COOLANT)
        screen.blit(title, (10, 8))
        pygame.draw.line(screen, COOLANT, (10, 28), (title.get_width()+10, 28), 1)

                                                                
        melted = sum(1 for row in self.grid for n in row if n.heat >= HEAT_MAX)
        avg_h  = sum(n.heat for row in self.grid for n in row) / 64.0
        nxw    = max(0.0, WORM_ITV - self.worm_t)

        stats = [
            (f"MELTDOWN  {melted}/4",           CRITICAL if melted > 0 else COOLANT),
            (f"AVG HEAT  {avg_h:5.1f}%",         GLITCH   if avg_h > 50  else COOLANT),
            (f"WORMS     {len(self.worms)}",     GLITCH),
            (f"NEXT WORM {nxw:5.1f}s",           GLITCH   if nxw < 3     else COOLANT),
            (f"COOLANT   {self.coolant:5.1f}%",  COOLANT),
        ]
        for i, (txt, col) in enumerate(stats):
            screen.blit(F12.render(txt, True, col), (10, 33 + i * 16))

                                                                
        TW, TH = 30, 400
        TX = SW - 64
        TY = (SH - TH) // 2

                           
        pygame.draw.rect(screen, STABLE, (TX, TY, TW, TH), border_radius=4)

                    
        fill_h = max(0, int((self.coolant / COOL_MAX) * (TH - 4)))
        if fill_h > 0:
            fy = TY + TH - 2 - fill_h
                                   
            if self.coolant < 25:
                pulse_a = int(60 + 50 * abs(math.sin(t * 0.007)))
                ds = pygame.Surface((TW, TH), pygame.SRCALPHA)
                pygame.draw.rect(ds, (*CRITICAL, pulse_a),
                                 (0, 0, TW, TH), border_radius=4)
                screen.blit(ds, (TX, TY))

            fill_col = lc(COOLANT, CRITICAL, 1.0 - self.coolant/COOL_MAX)
            pygame.draw.rect(screen, fill_col,
                             (TX+2, fy, TW-4, fill_h), border_radius=2)

                                                                      
            slosh = pygame.Surface((TW-4, 5), pygame.SRCALPHA)
            slosh.fill((255, 255, 255, 100))
            screen.blit(slosh, (TX+2, fy))

                     
        border_col = CRITICAL if self.coolant < 25 else COOLANT
        pygame.draw.rect(screen, border_col, (TX, TY, TW, TH), 1, border_radius=4)

                                              
        label_col = CRITICAL if self.coolant < 25 else COOLANT
        for i, ch in enumerate("COOLANT"):
            cs = F8.render(ch, True, label_col)
            screen.blit(cs, (TX + 11, TY + 8 + i * 15))

                               
        pct = F10.render(f"{int(self.coolant)}%", True, border_col)
        screen.blit(pct, (TX + 2, TY + TH + 6))

                                                                
        hint = F10.render(
            "[ LMB ] SYNAPSE PULSE    [ ESC ] QUIT    [ R ] RESTART",
            True, COOLANT)
                                        
        hbg = pygame.Surface((hint.get_width()+20, 18), pygame.SRCALPHA)
        hbg.fill((*VOID, 160))
        hx = SW//2 - hint.get_width()//2
        screen.blit(hbg, (hx - 10, SH - 20))
        screen.blit(hint, (hx, SH - 17))

                                                                
        if self.coolant < 1.0:
            wa = int(120 * abs(math.sin(t * 0.015)))
            ws = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ws.fill((*CRITICAL, wa // 8))
            screen.blit(ws, (0, 0))
            warn = F14.render("COOLANT DEPLETED", True, CRITICAL)
            screen.blit(warn, (SW//2 - warn.get_width()//2, SH//2 + 320))

                                                                
    def _draw_gameover(self):
        t = pygame.time.get_ticks()

                                            
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((*CRITICAL, 120))
        screen.blit(ov, (0, 0))

                              
        for _ in range(12):
            fy = random.randint(0, SH)
            fa = random.randint(8, 35)
            pygame.draw.line(screen, (*GLITCH, fa), (0, fy), (SW, fy))

                                                                
        y_mid = SH//2 - 40

                     
        shd = F46.render("SYSTEM_COLLAPSE", True, (0, 0, 0))
        screen.blit(shd, (SW//2 - shd.get_width()//2 + 3,
                          y_mid + 3))
                   
        main = F46.render("SYSTEM_COLLAPSE", True, WHITE)
        screen.blit(main, (SW//2 - main.get_width()//2, y_mid))

                  
        sub = F26.render("THERMAL RUNAWAY  ·  NETWORK OFFLINE", True, GLITCH)
        screen.blit(sub, (SW//2 - sub.get_width()//2, y_mid + 58))

                                
        rp_a = int(180 + 75 * abs(math.sin(t * 0.004)))
        rp_s = pygame.Surface((260, 22), pygame.SRCALPHA)
        rp_s.fill((*VOID, 180))
        screen.blit(rp_s, (SW//2 - 130, y_mid + 108))
        rst = F14.render("[ R ]  REINITIALIZE SYSTEM", True, WHITE)
        screen.blit(rst, (SW//2 - rst.get_width()//2, y_mid + 110))


                                                                 
              
                                                                 
def main():
    print("═" * 62)
    print("  NEURAL-SYNC: OBSIDIAN SECTOR")
    print("  Controls: Left Click = Synapse Pulse  |  ESC = Quit")
    print("            R = Restart (after game over)")
    print("═" * 62)

    game = NeuralSync()

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_r and game.over:
                    game = NeuralSync()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.click(*event.pos)

        game.update(dt)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()

import pygame, random, sys

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(0, 999999)
W, H = 1280, 720
T = 32          # tile size
RW, RH = 30, 18 # room size in tiles

def rng(*salts):
    r = random.Random(SEED)
    for s in salts: r.seed(r.random() + hash(s))
    return r

def make_room(gx, gy, doors):
    r = rng(gx, gy)
    grid = [[1]*RW for _ in range(RH)]
    for row in range(2, RH-2):
        for col in range(2, RW-2):
            grid[row][col] = 0
    # platforms
    for _ in range(r.randint(2, 5)):
        pr, pc, pl = r.randint(6, RH-5), r.randint(2, RW//2), r.randint(3, 8)
        for c in range(pc, min(pc+pl, RW-2)):
            if not grid[pr][c]: grid[pr][c] = 2
    # solid floor
    for c in range(RW): grid[RH-2][c] = 0; grid[RH-1][c] = 1
    # doors
    m = RH//2
    if 'L' in doors: grid[m-1][0]=grid[m][0]=grid[m+1][0] = 3
    if 'R' in doors: grid[m-1][RW-1]=grid[m][RW-1]=grid[m+1][RW-1] = 3
    if 'U' in doors: grid[0][RW//2-1]=grid[0][RW//2]=grid[0][RW//2+1] = 3
    if 'D' in doors: grid[RH-1][RW//2-1]=grid[RH-1][RW//2]=grid[RH-1][RW//2+1] = 3
    return grid

def build_floor():
    r = rng("floor")
    positions = [(0,0)]
    pos = (0,0)
    for _ in range(12):
        d = r.choice([(1,0),(1,0),(0,1),(0,-1),(-1,0)])
        pos = (pos[0]+d[0], pos[1]+d[1])
        if pos not in positions: positions.append(pos)
    rooms = {}
    for gp in positions:
        doors = set()
        for dname,(dx,dy) in zip('RLUD',[(1,0),(-1,0),(0,-1),(0,1)]):
            if (gp[0]+dx, gp[1]+dy) in positions: doors.add(dname)
        rooms[gp] = make_room(*gp, doors)
    return rooms, positions[0]

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(f"Seed: {SEED}  |  R=new  WASD=move  SPACE=jump")
clock = pygame.time.Clock()

COLORS = {0:(18,20,38), 1:(40,45,80), 2:(60,110,200), 3:(255,200,50)}

rooms, cur = build_floor()

px, py, vx, vy = W//2, H//2, 0, 0
on_ground = False
cooldown = 0

def draw():
    screen.fill((10,10,20))
    room = rooms[cur]
    cam_x = max(0, min(int(px)-W//2, RW*T-W))
    cam_y = max(0, min(int(py)-H//2, RH*T-H))
    for r,row in enumerate(room):
        for c,tile in enumerate(row):
            if tile==0: continue
            rx,ry = c*T-cam_x, r*T-cam_y
            if tile==2: pygame.draw.rect(screen,COLORS[2],(rx,ry+T-6,T,6))
            elif tile==3: pygame.draw.rect(screen,COLORS[3],(rx,ry,T,T))
            else: pygame.draw.rect(screen,COLORS[1],(rx,ry,T,T))
    pygame.draw.rect(screen,(80,220,255),(int(px)-cam_x,int(py)-cam_y,20,28))
    # minimap
    for (gx,gy) in rooms:
        mx,my = W-150+(gx-cur[0])*12, 20+(gy-cur[1])*12
        col = (180,80,80) if (gx,gy)==cur else (60,60,90)
        pygame.draw.rect(screen,col,(mx,my,10,10))
    f=pygame.font.SysFont("consolas",14)
    screen.blit(f.render(f"SEED {SEED}  room {cur}",True,(180,180,220)),(10,10))

running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN and e.key==pygame.K_r:
            SEED=random.randint(0,999999)
            rooms,cur=build_floor()
            px,py=W//2,H//2
            pygame.display.set_caption(f"Seed: {SEED}  |  R=new  WASD=move  SPACE=jump")

    vx = (-4 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 4 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0)
    if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and on_ground:
        vy = -13; on_ground = False
    vy = min(vy+0.6, 15)

    room = rooms[cur]
    for axis in ((vx,0),(0,vy)):
        px+=axis[0]; py+=axis[1]
        pr=pygame.Rect(int(px),int(py),20,28)
        for ri,row in enumerate(room):
            for ci,tile in enumerate(row):
                if tile not in (1,2,3): continue
                tr=pygame.Rect(ci*T,ri*T,T,T)
                if not pr.colliderect(tr): continue
                if tile==2:
                    if axis[1]>0 and pr.bottom-axis[1]<=tr.top+2:
                        py=tr.top-28; vy=0; on_ground=True
                    continue
                if axis[0]>0: px=tr.left-20
                elif axis[0]<0: px=tr.right
                elif axis[1]>0: py=tr.top-28; vy=0; on_ground=True
                elif axis[1]<0: py=tr.bottom; vy=0
                pr=pygame.Rect(int(px),int(py),20,28)
        if axis[1]<0: on_ground=False

    # room transitions
    if cooldown>0: cooldown-=1
    else:
        m=RH//2; nx=None
        doors_here = set()
        for dname,(dx,dy) in zip('RLUD',[(1,0),(-1,0),(0,-1),(0,1)]):
            if (cur[0]+dx,cur[1]+dy) in rooms: doors_here.add(dname)
        if px<T*1.5 and 'L' in doors_here:
            cur=(cur[0]-1,cur[1]); px=RW*T-T*3; cooldown=20
        elif px>RW*T-T*1.5-20 and 'R' in doors_here:
            cur=(cur[0]+1,cur[1]); px=T*2; cooldown=20
        elif py<T*1.5 and 'U' in doors_here:
            cur=(cur[0],cur[1]-1); py=RH*T-T*3; cooldown=20
        elif py>RH*T-T*1.5-28 and 'D' in doors_here:
            cur=(cur[0],cur[1]+1); py=T*2; cooldown=20

    draw()
    pygame.display.flip()

pygame.quit()
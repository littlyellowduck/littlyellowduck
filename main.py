
# main.py
import pygame
import sys
import random
from tile import Tile
from menu import Menu

pygame.init()

# 定义常量
# FPS = 60
WIDTH, HEIGHT = 475, 700  # 屏幕的宽度和高度
BG_COLOR = (249, 230, 190) # 背景颜色
TILE_SIZE = 60 #卡牌大小
# OFFSET = 20  # 平移的像素值
COLLECT_BOX_HEIGHT = 100  # 底部收集框的高度
COLLECT_BOX_LIMIT = 8  # 收集框容量上限
COLLECTION_TILE_SIZE = 60  # 收集框中的图片大小
COLLECTION_BOX_HEIGHT = 100  # 收集框高度
COLLECTION_COLOR = (236, 126, 97) # 收集框颜色
DELAY_DURATION = 100  # 消除的延迟时间（以毫秒为单位）
COUNTDOWN_TIME = 100  # 倒计时总时间
LEVEL = 1 # 游戏关卡
namelist = ['糖果', '小熊', '树', '杯子', '帽子', '铃铛']

# 定义一些全局变量
remove_delay = False  # 是否需要延迟移除
remove_time = 0  # 延迟移除的起始时间

game_over = False  # 判断游戏是否结束
game_result = ""   # 存储游戏结果（"win" or "lose"）
paused = False  # 是否暂停

level_selected = False # 关卡是否选择完毕
next_selected = False

rows , cols = 0,0 # 卡牌行列
margin = 0 #卡牌边距
grid_width = 0 #网格宽高
grid_height = 0
start_x = 0 #起始坐标量
start_y = 0
offset = 0 #偏移量
# 定义收集框的位置
collect_box_start_y = HEIGHT - COLLECT_BOX_HEIGHT  # 底部收集框的起始Y坐标
collect_box = []
# 创建用于存储矩形的二维数组
rects_layer1 = []
rects_layer2 = []
# 初始化倒计时相关变量
countdown_start_time = pygame.time.get_ticks()  # 记录游戏开始时间
# 字体设置
font_score = pygame.font.Font(None, 50)
font_pause = pygame.font.Font(None, 25)
# 初始化分数
score = 0
show_score = True  # 初始化为显示分数
show_time = True # 初始化为显示时间
# 绘制游戏主窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('MerryChristmas')
screen.fill(BG_COLOR)
font = pygame.font.Font(None, 50)  # 字体
button_font = pygame.font.Font(None, 40)  # 按钮字体

# 渲染分数的函数
def render_score():
    score_text = font_score.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (WIDTH - 186, 10))

# 模拟成功消除函数
def successful_match():
    global score
    score += 3  # 每次成功消除加3分

# 倒计时显示
def render_countdown():
    global remaining_time
    if not paused:
        elapsed_time = pygame.time.get_ticks() - countdown_start_time  # 计算已过去的时间
        remaining_time = max(0, COUNTDOWN_TIME * 1000 - elapsed_time)  # 更新剩余时间，确保不为负数

    minutes = remaining_time // 60000
    seconds = (remaining_time % 60000) // 1000
    countdown_text = font_score.render(f"Time: {minutes}:{seconds:02}", True, (0, 0, 0))
    screen.blit(countdown_text, (10, 10))

# 不同关卡变量初始化
def level_initial():
    global COLLECT_BOX_LIMIT,TILE_SIZE
    global margin,rows,cols , offset_x,offset_y
    if LEVEL == 1:
        margin =  40
        rows, cols = 3, 3  # 行列数
        offset_x, offset_y = 8, 15
    if LEVEL== 2:
        TILE_SIZE = 55
        margin = 15
        rows, cols = 5,5
        offset_x, offset_y = 20, 15
    if LEVEL == 3:
        TILE_SIZE = 50
        margin = 10
        rows, cols = 6,7
        offset_x, offset_y = 15, 15
        COLLECT_BOX_LIMIT = 7
#创建图层
def create_layers(rows, cols, margin, offset_x, offset_y):
    global rects_layer1, rects_layer2, grid_width, grid_height, start_x, start_y

    rects_layer1 = []
    rects_layer2 = []

    # 计算网格的总宽度和总高度
    grid_width = cols * TILE_SIZE + (cols - 1) * margin
    grid_height = rows * TILE_SIZE + (rows - 1) * margin

    # 计算网格的起始位置，使矩阵居中显示
    start_x = (WIDTH - grid_width) // 2
    start_y = (HEIGHT - grid_height) // 2 - 60

    # 计算总的网格单元数，两层的总数量
    total_tiles = rows * cols * 2

    # 确保每种图片的数量为3的倍数，且总数不超过网格单元数
    num_types = len(namelist)

    # 为每种图片生成随机数量，确保数量接近并为3的倍数
    image_counts = []
    remaining_slots = total_tiles
    min_images_per_type = max(1, remaining_slots // (num_types * 3)) * 3  # 每种图片至少生成的数量为3的倍数

    for i in range(num_types):
        if remaining_slots < 3:
            break
        # 随机生成图片数量，确保每种图片的数量为3的倍数，且不超过剩余槽位
        count = min(min_images_per_type, remaining_slots)
        count = (count // 3) * 3  # 确保为3的倍数
        image_counts.append(count)
        remaining_slots -= count

    # 如果有剩余槽位，使用空槽填充
    empty_slots = remaining_slots

    # 创建图片列表
    image_list = []
    for i, count in enumerate(image_counts):
        image_list.extend([namelist[i]] * count)

    # 添加空槽
    image_list.extend([None] * empty_slots)

    # 随机打乱图片列表
    random.shuffle(image_list)

    # 填充到两层中，带有固定的置空位置
    for row in range(rows):
        rects_row1 = []
        rects_row2 = []
        for col in range(cols):
            # 第一图层
            rect1 = pygame.Rect(
                start_x + col * (TILE_SIZE + margin),
                start_y + row * (TILE_SIZE + margin),
                TILE_SIZE, TILE_SIZE
            )
            # 第二图层，向右平移offset_x，向下平移offset_y
            rect2 = rect1.move(offset_x, offset_y)

            # 获取图片名称
            if image_list:
                image_name1 = image_list.pop()
            else:
                image_name1 = None

            if image_list:
                image_name2 = image_list.pop()
            else:
                image_name2 = None

            # 创建第一图层和第二图层的图片对象
            tile1 = Tile(f"./images/{image_name1}_gray.png", rect1.topleft, 1, 1) if image_name1 else None
            tile2 = Tile(f"./images/{image_name2}.png", rect2.topleft, 2, 0) if image_name2 else None

            # 把卡牌加到单元格数组里
            rects_row1.append(tile1)
            rects_row2.append(tile2)

        # 把单元格加到图层里
        rects_layer1.append(rects_row1)
        rects_layer2.append(rects_row2)
# 检查覆盖
def check_uncovered(tile, rects_layer2):
    for row in rects_layer2:
        for tile2 in row:
            if tile2 and tile.rect.colliderect(tile2.rect):  # 如果还有其他图片覆盖
                return False
    return True  # 没有被覆盖
# 更新图片的状态
def update_tile_status():
    for row in rects_layer1:
        for tile in row:
            if tile:
                # 检查该图片是否被遮盖
                if check_uncovered(tile, rects_layer2):
                    # 图片未被遮盖，设置为亮色
                    tile.image = pygame.image.load(tile.name.replace('_gray', '')).convert_alpha()
                    tile.state = 0
                    tile.name = tile.name.replace('_gray', '')
                else:
                    # 图片被遮盖，设置为灰色
                    tile.image = pygame.image.load(tile.name).convert_alpha()
                tile.image = pygame.transform.scale(tile.image, (TILE_SIZE, TILE_SIZE))
# 绘制圆角矩形带有厚度
def draw_rounded_rect_with_thickness(surface, rect, color, radius, thickness=3, shadow_color=(100, 100, 100)):
    # 创建阴影
    shadow_rect = rect.move(thickness, thickness)
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=radius)
    # 创建圆角矩形
    pygame.draw.rect(surface, color, rect, border_radius=radius)
# 更新Tile类中的绘制逻辑
def draw_tile_with_rounded_rect(tile, surface):
    # 创建卡牌的圆角背景矩形
    rect = pygame.Rect(tile.position[0], tile.position[1], TILE_SIZE , TILE_SIZE )
    # 创建卡牌的阴影
    draw_rounded_rect_with_thickness(surface, rect, (255, 255, 255), 5)  # 白色圆角卡牌

    # 计算图片居中的位置
    image_width, image_height = tile.image.get_size()
    rect_width, rect_height = rect.size

    # 将图片在圆角矩形内部居中
    tile.image = pygame.transform.scale(tile.image, (TILE_SIZE - 5, TILE_SIZE - 5))
    image_x = rect.x + (rect_width - image_width) // 2
    image_y = rect.y + (rect_height - image_height) // 2

    # 将图片绘制在计算好的居中位置

    surface.blit(tile.image, (image_x, image_y))
# 绘制图层
def draw_rects(rects):
    for row in rects:
        for tile in row:
            if tile:
                draw_tile_with_rounded_rect(tile, screen)
# 绘制收集框
def draw_collection_box():
    # 先绘制收集框的背景
    pygame.draw.rect(screen, COLLECTION_COLOR, (0, HEIGHT - COLLECTION_BOX_HEIGHT, WIDTH, COLLECTION_BOX_HEIGHT))
    pygame.draw.rect(screen, (140, 54, 28),
                     (0, HEIGHT - COLLECTION_BOX_HEIGHT, WIDTH, (COLLECTION_BOX_HEIGHT - 65) // 2))
# 绘制收集框中的图片
def draw_collect_box(margin):
    for index, tile in enumerate(collect_box):
        if tile:  # 如果卡片存在
            x_pos = index * (COLLECTION_TILE_SIZE + 7) + 4
            y_pos = collect_box_start_y + TILE_SIZE // 2 - 5 # 在收集框中稍微向下移一点

            # 创建卡片的圆角背景矩形
            rect = pygame.Rect(x_pos, y_pos, COLLECTION_TILE_SIZE + 5, COLLECTION_TILE_SIZE + 5)
            draw_rounded_rect_with_thickness(screen, rect, (255, 255, 255), 5)  # 白色圆角卡牌

            # 计算图片居中的位置
            image_width, image_height = tile.image.get_size()
            rect_width, rect_height = rect.size

            # 将图片在圆角矩形内部居中
            image_x = rect.x + (rect_width - image_width) // 2
            image_y = rect.y + (rect_height - image_height) // 2

            # 将图片绘制在计算好的居中位置
            screen.blit(tile.image, (image_x, image_y))

# 绘制暂停键
def draw_pause(mouse_pos, is_paused):
    pause_button_rect = pygame.Rect(2, HEIGHT - 131, 70, 30)
    # 根据游戏是否暂停改变按钮颜色
    color = (46, 139, 87) if not is_paused else (0, 100, 0)
    pygame.draw.rect(screen, color, pause_button_rect)

    if not is_paused:
        text_surface = font_pause.render('PAUSE', True, (255, 255, 255))
    else:
        text_surface = font_pause.render('PLAY', True, (255, 255, 255))

    text_rect = text_surface.get_rect(center=pause_button_rect.center)
    screen.blit(text_surface, text_rect)

    return pause_button_rect
# 三消逻辑
def remove_tiles(tile_name):
    global collect_box
    #从收集框中移除指定名称的三个图片，并补位
    removed_count = 0
    new_collect_box = []

    # 仅保留不被消除的图片
    for tile in collect_box:
        if tile.name == tile_name and removed_count < 3:
            removed_count += 1
        else:
            new_collect_box.append(tile)


    # 更新收集框
    collect_box = new_collect_box

def check_three_match():
    global remove_delay, remove_time

    if len(collect_box) < 3:
        return None  # 如果不足三个，直接返回

    tile_count = {}
    for tile in collect_box:
        if tile.name in tile_count:
            tile_count[tile.name] += 1
        else:
            tile_count[tile.name] = 1

    # 查找三消的图片
    for tile_name, count in tile_count.items():
        if count >= 3:

            # 设置延迟清除标志
            remove_delay = True
            remove_time = pygame.time.get_ticks()  # 记录当前时间
            return tile_name  # 返回找到的图案名

    return None
# 处理点击事件
def handle_click(mouse_pos):
    # 优先处理第二图层的点击
    for row in rects_layer2:
        for tile in row:
            if tile and tile.rect.collidepoint(mouse_pos):

                if tile.state == 0:  # 如果是顶层图片
                    print(tile.name)
                    if len(collect_box) < COLLECT_BOX_LIMIT:  # 收集框未满
                        # print(tile.name)
                        row[row.index(tile)] = None  # 将图片从游戏网格移除
                        collect_box.append(tile)  # 将图片放入收集框
                        check_three_match()  # 检查三消逻辑
                        # 更新第一图层对应图片的状态
                        update_first_layer_state(tile.rect)
                    return  # 点击事件处理完毕，退出

    # 检查第一图层的点击
    for row in rects_layer1:
        for tile in row:

            if tile and tile.rect.collidepoint(mouse_pos):
                print(tile.name)
                if tile.state == 0:  # 如果图片状态为顶层（未遮盖）

                    if len(collect_box) < COLLECT_BOX_LIMIT:  # 收集框未满
                        # print(tile.name)
                        row[row.index(tile)] = None  # 将图片从游戏网格移除
                        collect_box.append(tile)  # 将图片放入收集框
                        check_three_match()  # 检查三消逻辑
                    return  # 点击事件处理完毕，退出

# 更新第一图层的状态
def update_first_layer_state(removed_tile_rect):
    """当第二图层的图片被移除时，检查第一图层对应位置的图片，并更新其状态"""
    for row in rects_layer1:
        for tile in row:
            if tile and tile.rect.colliderect(removed_tile_rect):
                if check_uncovered(tile, rects_layer2):  # 检查底层图片是否被覆盖
                    tile.state = 0  # 更新为顶层状态（可点击）
                    # 更新图片名称去除灰色标记
                    if "_gray" in tile.name:
                        tile.name = tile.name.replace('_gray', '')
                    # 更新图片显示
                    tile.image = pygame.image.load(tile.name).convert_alpha()
                    tile.image = pygame.transform.scale(tile.image, (TILE_SIZE, TILE_SIZE))

def check_game_over():
    global game_over, game_result

    # 检查收集框是否已满
    if len(collect_box) >= COLLECT_BOX_LIMIT:  # 如果收集框已满
        # 检查是否仍有剩余的卡牌
        remaining_tiles_layer1 = any(tile for row in rects_layer1 for tile in row if tile is not None)
        remaining_tiles_layer2 = any(tile for row in rects_layer2 for tile in row if tile is not None)

        if remaining_tiles_layer1 or remaining_tiles_layer2:
            game_over = True
            game_result = "lose"  # 游戏失败
        else:
            game_over = True
            game_result = "win"  # 游戏胜利

    # 如果卡牌被全部清除，且收集框没有达到上限，判定为游戏胜利
    else:
        remaining_tiles_layer1 = any(tile for row in rects_layer1 for tile in row if tile is not None)
        remaining_tiles_layer2 = any(tile for row in rects_layer2 for tile in row if tile is not None)

        if not remaining_tiles_layer1 and not remaining_tiles_layer2:
            game_over = True
            game_result = "win"  # 游戏胜利
# 绘制结算界面
def draw_end_screen(result):
    global show_score,show_time  # 声明全局变量
    show_score = False  # 在结算界面时不显示分数
    show_time  = False
    screen.fill(BG_COLOR)
    font = pygame.font.SysFont(None, 70)
    if result == "win":
        text1 = font.render("Merry Christmas!",True,    (243, 129, 129))
        text2 = font.render("——I'll be with You.",True, (243, 129, 129))
    else:
        text1 = font.render("GAME OVER!", True, (0,0,0))
        text2 = font.render("Cheer up up up!", True, (0,0,0))

    text_rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 100))
    text_rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(text1, text_rect1)
    screen.blit(text2, text_rect2)
    mouse_pos = pygame.mouse.get_pos()
    # 创建按钮
    if result == "win":
        next_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2, 220, 60)
        draw_button("NEXT LEVEL", next_button, mouse_pos)
        select_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 100, 220, 50)
        draw_button("SELECT", select_button, mouse_pos)
        leave_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 190, 220, 50)
        draw_button("LEAVE", leave_button, mouse_pos)

    else:
        continue_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        draw_button("CONTINUE", continue_button, mouse_pos)
        select_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
        draw_button("SELECT", select_button, mouse_pos)
        quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)
        draw_button("QUIT", quit_button, mouse_pos)

    # render_countdown()
    # render_score()
    pygame.display.flip()

    # 处理按钮点击事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if result == "win":
                if next_button.collidepoint(mouse_pos):
                    next_level()
                if select_button.collidepoint(mouse_pos):
                    select_level()
                if leave_button.collidepoint(mouse_pos):
                    leave_game()
            else:
                if continue_button.collidepoint(mouse_pos):
                    restart_level()
                if select_button.collidepoint(mouse_pos):
                    select_level()
                if quit_button.collidepoint(mouse_pos):
                    quit_game()

# 绘制选择界面
def draw_select_screen():
    global LEVEL, level_selected,font
    screen.fill(BG_COLOR)
    font = pygame.font.SysFont(None, 70)

    text1 = font.render("Which LEVEL??", True, (46, 139, 87))
    text2 = font.render("Please Select...", True, (46, 139, 87))

    text_rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 100))
    text_rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 3))

    screen.blit(text1, text_rect1)
    screen.blit(text2, text_rect2)

    mouse_pos = pygame.mouse.get_pos()

    # 创建按钮
    level1_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    draw_button("Easy", level1_button, mouse_pos)
    level2_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
    draw_button("Normal", level2_button, mouse_pos)
    level3_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)
    draw_button("Hard", level3_button, mouse_pos)

    # 刷新界面
    pygame.display.flip()

    # 处理按钮点击事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if level1_button.collidepoint(mouse_pos):
                LEVEL = 1
                level_selected = True  # 标志关卡已选择
                # print(level_selected)
            elif level2_button.collidepoint(mouse_pos):
                LEVEL = 2
                level_selected = True
            elif level3_button.collidepoint(mouse_pos):
                LEVEL = 3
                level_selected = True


#绘制按钮
def draw_button(text,rect,mouse_pos):
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (46, 139, 87), rect)
        pygame.draw.rect(screen, (0, 100, 0), rect.inflate(15, 15), 5)

    else:
        pygame.draw.rect(screen, (170, 72, 46), rect)
        pygame.draw.rect(screen, (140, 54, 28), rect.inflate(15, 15), 5)
    text_surface = button_font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# 按钮功能实现
def next_level():
    global LEVEL, game_over, game_result, score, next_selected
    next_selected = True  # 标记选择了下一关
    game_over = False      # 重置游戏状态
    game_result = ""       # 清空结果状态
    # 切换关卡逻辑
    LEVEL += 1
    if LEVEL > 3:  # 假设最多 3 关
        LEVEL = 1  # 如果超过 3 关，重新回到第 1 关
    game_loop()

def select_level():
    global game_over, game_result, collect_box, rects_layer1, rects_layer2, score
    score = 0
    game_over = False
    game_result = ''
    rects_layer1 = []
    rects_layer2 = []
    collect_box.clear()
    game_loop()

def leave_game():
    pygame.quit()
    sys.exit()

def restart_level():
    global game_over, game_result, score, next_selected,rects_layer1, rects_layer2
    next_selected = True
    game_over = False  # 重置游戏状态
    game_result = ""  # 清空结果状态
    rects_layer1 = []
    rects_layer2 = []
    collect_box.clear()
    score = 0
    game_loop()

def quit_game():
    pygame.quit()
    sys.exit()

def game_loop():
    global remove_delay, remove_time, game_over, game_result,paused, countdown_start_time,level_selected,next_selected,show_score,show_time
    show_score = True
    show_time = True
    # 如果是从下一关开始，则直接跳过选择界面
    if not next_selected:
        level_selected = False  # 初始化为未选择状态

        # 进入关卡选择
        while not level_selected:
            draw_select_screen()


    level_initial()
    create_layers(rows, cols, margin, offset_x, offset_y)
    tile_name_to_remove = None  # 初始化要移除的图案
    clock = pygame.time.Clock()
    # 初始化倒计时相关变量
    countdown_start_time = pygame.time.get_ticks()  # 记录游戏开始时间
    # 计时器和游戏状态更新
    if not game_over:
        render_countdown()
        update_tile_status()
        check_three_match()
        check_game_over()
    while True:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        if not game_over:

            # 刷新图片状态
            update_tile_status()

            # 绘制图层
            draw_rects(rects_layer1)
            draw_rects(rects_layer2)
            # 绘制收集框
            draw_collection_box()
            # 绘制暂停键
            pause_button_rect = draw_pause(mouse_pos, paused)
            # 绘制收集框图片
            draw_collect_box(margin)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_button_rect.collidepoint(mouse_pos):
                        paused = not paused
                        if not paused:
                            countdown_start_time = pygame.time.get_ticks() - (COUNTDOWN_TIME * 1000 - remaining_time)
                    else:
                        handle_click(mouse_pos)

            # 检查三消逻辑
            if not remove_delay:
                match_name = check_three_match()  # 检查是否有三消
                if match_name:
                    tile_name_to_remove = match_name  # 准备移除的图案

            # 如果有三消并且延迟标志已设置，则检查是否达到延迟时间
            if remove_delay and pygame.time.get_ticks() - remove_time >= DELAY_DURATION:
                if tile_name_to_remove:
                    remove_tiles(tile_name_to_remove)  # 执行消除
                    successful_match()
                    tile_name_to_remove = None  # 清空待移除的图案
                remove_delay = False  # 重置延迟标志

            check_game_over()  # 每次循环都检查游戏是否结束
        else:
            draw_end_screen(game_result)  # 游戏结束时绘制结束界面
            next_selected = False

        if show_time:
            render_countdown()
        if show_score:
            render_score()  # 只在游戏过程中渲染分数

        pygame.display.flip()

# 定义开始菜单函数
def start_menu():
    # 运行游戏主循环
    menu = Menu(screen, WIDTH, HEIGHT)
    menu.run_menu(game_loop)

# 主程序入口
if __name__ == "__main__":
    start_menu()



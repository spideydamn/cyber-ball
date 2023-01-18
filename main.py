import pygame
import random
import os
import sys
import sqlite3


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


FPS = 60

pygame.init()
pygame.display.set_caption("CyberBall")
size = WIDTH, HEIGHT = 780, 780
screen = pygame.display.set_mode(size)


con = sqlite3.connect(resource_path(os.path.join('data', 'DB.db')))
cur = con.cursor()

GLOBAL_SCORE = cur.execute("""SELECT score FROM score""").fetchall()[0][0]
local_score = 0

left_flag = False
right_flag = False

bricks_list = []

brick_number_of_changes = 0
brick_number_of_changes_inline = 0

panel = 0
panel_number = 0
panel_images = list()

pygame.mixer.pre_init(44100, 16, 2, 4096)

sound_effects = dict(
    brick_hit=pygame.mixer.Sound(resource_path(os.path.join('sound_effects', 'brick_hit.wav'))),
    effect_done=pygame.mixer.Sound(resource_path(os.path.join('sound_effects', 'effect_done.wav'))),
    paddle_hit=pygame.mixer.Sound(resource_path(os.path.join('sound_effects', 'paddle_hit.wav'))),
    win=pygame.mixer.Sound(resource_path(os.path.join('sound_effects', 'win.wav'))),
    game_over=pygame.mixer.Sound(resource_path(os.path.join('sound_effects', 'game_over.wav'))),
    live=pygame.mixer.Sound(resource_path(os.path.join('sound_effects', 'live.wav'))),
)

music = pygame.mixer.music.load(resource_path(os.path.join('sound_effects', 'music.mp3')))
pygame.mixer.music.play(-1, 0.0)

def load_image(name, colorkey=None):
    fullname = resource_path(os.path.join('data', name))
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    with open(resource_path(os.path.join('data', filename)), 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    global GLOBAL_SCORE, sound_effect

    count_stars = 0

    while True:
        local_score = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 388 <= event.pos[
                0] <= 746 and 197 <= event.pos[1] <= 270:
                sound_effects['effect_done'].play()
                local_score = play()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 388 <= event.pos[
                0] <= 746 and 281 <= event.pos[1] <= 354:
                sound_effects['effect_done'].play()
                change_level()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 388 <= event.pos[
                0] <= 746 and 365 <= event.pos[1] <= 438:
                sound_effects['effect_done'].play()
                change_ball()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 388 <= event.pos[
                0] <= 746 and 449 <= event.pos[1] <= 522:
                sound_effects['effect_done'].play()
                terminate()
            if event.type == pygame.MOUSEMOTION:
                cursor.rect.topleft = event.pos
            if event.type == pygame.MOUSEMOTION and 388 <= event.pos[0] <= 746 and 197 <= event.pos[1] <= 270:
                cursor.image = click_image
                play_sprite.image = mini_play_image
                play_sprite.rect.topleft = (button_pos_x + (button_size[0] - mini_button_size[0]) // 2,
                                            button_pos_y + (button_size[1] - mini_button_size[1]) // 2)
            elif event.type == pygame.MOUSEMOTION and 388 <= event.pos[0] <= 746 and 281 <= event.pos[1] <= 354:
                cursor.image = click_image
                level_sprite.image = mini_level_image
                level_sprite.rect.topleft = (button_pos_x + (button_size[0] - mini_button_size[0]) // 2,
                                            button_pos_y + gap_button + (button_size[1] - mini_button_size[1]) // 2)
            elif event.type == pygame.MOUSEMOTION and 388 <= event.pos[0] <= 746 and 365 <= event.pos[1] <= 438:
                cursor.image = click_image
                ball_sprite.image = mini_ball_image
                ball_sprite.rect.topleft = (button_pos_x + (button_size[0] - mini_button_size[0]) // 2,
                                            button_pos_y + gap_button * 2 + (button_size[1] - mini_button_size[1]) // 2)
            elif event.type == pygame.MOUSEMOTION and 388 <= event.pos[0] <= 746 and 449 <= event.pos[1] <= 522:
                cursor.image = click_image
                quit_sprite.image = mini_quit_image
                quit_sprite.rect.topleft = (button_pos_x + (button_size[0] - mini_button_size[0]) // 2,
                                            button_pos_y + gap_button * 3 + (button_size[1] - mini_button_size[1]) // 2)
            else:
                cursor.image = cursor_image

                play_sprite.image = play_image
                play_sprite.rect.topleft = button_pos

                level_sprite.image = level_image
                level_sprite.rect.topleft = (button_pos_x, button_pos_y + gap_button)

                ball_sprite.image = ball_image
                ball_sprite.rect.topleft = (button_pos_x, button_pos_y + gap_button * 2)

                quit_sprite.image = quit_image
                quit_sprite.rect.topleft = (button_pos_x, button_pos_y + gap_button * 3)

        screen.fill(black)

        if count_stars % 6 == 0:
            stars_sprites.update()

        stars_sprites.draw(screen)
        start_sprites.draw(screen)
        all_sprites.draw(screen)
        cursor_sprites.draw(screen)

        GLOBAL_SCORE += local_score
        cur.execute("""UPDATE score SET score = ?""", (GLOBAL_SCORE,))
        con.commit()

        font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 50)
        string_rendered = font.render(str(GLOBAL_SCORE), True, pygame.Color('white'))
        screen.blit(string_rendered,
                    (WIDTH - string_rendered.get_rect()[2] - 10, HEIGHT - string_rendered.get_rect()[3]))

        score.rect.topleft = (WIDTH - string_rendered.get_rect()[2] - 167, HEIGHT - 41)

        pygame.display.flip()
        clock.tick(FPS)

        count_stars += 1


def play():
    global bricks_list, brick_number_of_changes, local_score, GLOBAL_SCORE, brick_number_of_changes_inline
    global sound_effect

    game_over_count = -1

    level_map = load_level(cur.execute("""SELECT path FROM levels WHERE choice = 1""").fetchall()[0][0])

    bricks_list = [[0 for jj in range(len(level_map[j]))] for j in range(len(level_map))]

    max_len_level = 0

    for yy in range(len(level_map)):
        if len(level_map[yy]) > max_len_level:
            max_len_level = len(level_map[yy])

    for yy in range(len(level_map)):
        for xx in range(len(level_map[yy])):
            if level_map[yy][xx] != ".":
                bricks_list[yy][xx] = Brick(xx * ((WIDTH - 146) // max_len_level),
                                            yy * int(((WIDTH - 146) / max_len_level) * (450 / 1248)),
                                            ((WIDTH - 146) // max_len_level),
                                            int(((WIDTH - 146) / max_len_level) * (450 / 1248)), level_map[yy][xx],
                                            brick_sprites)

    lives = 3

    local_score = 0

    count_stars = 0

    global left_flag, right_flag

    speed_panel = 8

    up_border = Border(0, 0, WIDTH, 0)
    right_border = Border(WIDTH - 151, 0, WIDTH - 151, HEIGHT)
    left_border = Border(0, 0, 0, HEIGHT)

    ball = Ball((WIDTH - 146) // 2 - 16, HEIGHT - 110,
                cur.execute("""SELECT id FROM balls WHERE choice = 1""").fetchall()[0][0] - 1)

    panel_number = 1
    panel.image = panel_images[panel_number]
    panel.rect = panel.image.get_rect()

    panel.rect.topleft = ((WIDTH - 146) // 2 - panel.rect[2] // 2, HEIGHT - 78)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GLOBAL_SCORE += local_score
                cur.execute("""UPDATE score SET score = ?""", (GLOBAL_SCORE,))
                con.commit()
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and WIDTH - 146 <= event.pos[0] \
                    <= WIDTH - 5 and 5 <= event.pos[1] <= 66:
                sound_effects['effect_done'].play()
                up_border.kill()
                right_border.kill()
                left_border.kill()
                ball.kill()
                for i in bricks_list:
                    for j in i:
                        j.kill()
                return local_score
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and WIDTH - 146 <= event.pos[0] \
                    <= WIDTH - 5 and 71 <= event.pos[1] <= 132:
                sound_effects['effect_done'].play()
                GLOBAL_SCORE += local_score
                cur.execute("""UPDATE score SET score = ?""", (GLOBAL_SCORE,))
                con.commit()
                terminate()
            if event.type == pygame.MOUSEMOTION and WIDTH - 146 <= event.pos[0] \
                    <= WIDTH - 5 and 5 <= event.pos[1] <= 66:
                cursor.image = click_image
                menu.image = mini_menu_image
                menu.rect.topleft = (WIDTH - 143, 7)
            elif event.type == pygame.MOUSEMOTION and WIDTH - 146 <= event.pos[0] \
                    <= WIDTH - 5 and 71 <= event.pos[1] <= 132:
                cursor.image = click_image
                mini_quit.image = mini_mini_quit_image
                mini_quit.rect.topleft = (WIDTH - 143, 73)
            else:
                cursor.image = cursor_image

                menu.image = menu_image
                menu.rect.topleft = (WIDTH - 146, 5)

                mini_quit.image = second_mini_quit_image
                mini_quit.rect.topleft = (WIDTH - 146, 71)

            if event.type == pygame.KEYDOWN and event.key == 1073741904 and panel.rect.topleft[0] > 0:
                left_flag = True
            elif event.type == pygame.KEYUP and event.key == 1073741904:
                left_flag = False

            if event.type == pygame.KEYDOWN and event.key == 1073741903 and panel.rect.topleft[0] < WIDTH - 151 - \
                    panel.rect[2]:
                right_flag = True
            elif event.type == pygame.KEYUP and event.key == 1073741903:
                right_flag = False

            if event.type == pygame.MOUSEMOTION:
                cursor.rect.topleft = event.pos

        screen.fill(black)

        if count_stars % 6 == 0:
            stars_sprites.update()

        font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 42)
        string_rendered = font.render(str(local_score), True, pygame.Color('white'))
        screen.blit(string_rendered,
                    (WIDTH - string_rendered.get_rect()[2] - 5, HEIGHT - string_rendered.get_rect()[3]))

        score_play.rect.topleft = (WIDTH - 146, HEIGHT - 41 - string_rendered.get_rect()[3])

        string_rendered = font.render(str(lives), True, pygame.Color('white'))
        screen.blit(string_rendered,
                    (WIDTH - string_rendered.get_rect()[2] - 5,
                     HEIGHT - string_rendered.get_rect()[3] * 2 - score_play_image.get_rect()[3] - 40))

        lives_play.rect.topleft = (
        WIDTH - 124, HEIGHT - 41 - string_rendered.get_rect()[3] * 2 - score_play_image.get_rect()[3] - 40)

        if left_flag and game_over_count == -1:
            panel.rect.topleft = (max(panel.rect.topleft[0] - speed_panel, 0), panel.rect.topleft[1])
        if right_flag  and game_over_count == -1:
            panel.rect.topleft = (
            min(panel.rect.topleft[0] + speed_panel, WIDTH - 151 - panel.rect[2]), panel.rect.topleft[1])

        if ball.rect.topleft[1] > HEIGHT + 100 or ball.rect.topleft[1] < -100 or ball.rect.topleft[
            0] > WIDTH + 100 or ball.rect.topleft[0] < -100:
            ball.kill()
            if lives > 0:
                sound_effects['live'].play()
            lives = max(lives - 1, 0)
            if lives > 0:
                ball = Ball(panel.rect.topleft[0] + panel.rect[2] // 2 - 16, HEIGHT - 110,
                            cur.execute("""SELECT id FROM balls WHERE choice = 1""").fetchall()[0][0] - 1)

        brick_number_of_changes = 0
        brick_number_of_changes_inline = 0
        brick_sprites.update(ball)

        tf = True
        for j in bricks_list:
            for jj in j:
                if str(jj) != "<Brick Sprite(in 0 groups)>":
                    tf = False
        if tf:
            ball.kill()
            sound_effects['win'].play()
            cur.execute("""UPDATE levels SET available = 1 WHERE id = ?""",
                        (cur.execute("""SELECT id FROM levels WHERE choice = 1""").fetchall()[0][0] + 1, ))
            cur.execute("""UPDATE levels SET choice = 1 WHERE id = ?""",
                        (cur.execute("""SELECT id FROM levels WHERE choice = 1""").fetchall()[0][0] + 1,))
            cur.execute("""UPDATE levels SET choice = 0 WHERE id = ?""",
                        (cur.execute("""SELECT id FROM levels WHERE choice = 1""").fetchall()[0][0],))
            con.commit()
            return local_score + play()

        play_sprites.update()
        stars_sprites.draw(screen)
        play_sprites.draw(screen)
        panel_sprite.draw(screen)
        brick_sprites.draw(screen)

        if lives == 0:
            game_over_sprites.draw(screen)
            game_over_count += 1
            if game_over_count == 0:
                sound_effects['game_over'].play()
            ball.kill()

        if game_over_count == 450:
            for i in bricks_list:
                for j in i:
                    j.kill()
            sound_effects['effect_done'].play()
            return local_score

        cursor_sprites.draw(screen)


        pygame.display.flip()
        clock.tick(FPS)

        count_stars += 1


def change_level():
    global GLOBAL_SCORE, sound_effect

    count_stars = 0

    cards = pygame.sprite.Group()
    cards_list = [0] * 3
    data = cur.execute("""SELECT * FROM levels""").fetchall()

    for j in range(3):
        if data[j][3] == 1:
            cards_list[j] = pygame.sprite.Sprite(cards)
            cards_list[j].image = big_choice_frame_image
            cards_list[j].rect = cards_list[j].image.get_rect()
            cards_list[j].rect.topleft = ((j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2,
                                          (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2)
            font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 24 - (j // 3) * 5)
            string_rendered = font.render(str(data[j][1]), True, pygame.Color('white'))
            cost = pygame.sprite.Sprite(cards)
            cost.image = string_rendered
            cost.rect = cost.image.get_rect()
            cost.rect.topleft = ((j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2 + (
                    cards_list[j].rect[2] - cost.rect[2]) // 2,
                                 (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 +
                                 cards_list[j].rect[3] - cost.rect[3] - 25)
        elif data[j][3] == 1:
            cards_list[j] = pygame.sprite.Sprite(cards)
            cards_list[j].image = big_green_frame_image
            cards_list[j].rect = cards_list[j].image.get_rect()
            cards_list[j].rect.topleft = ((j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2,
                                          (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2)
            font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 24 - (j // 3) * 5)
            string_rendered = font.render(str(data[j][1]), True, pygame.Color('white'))
            cost = pygame.sprite.Sprite(cards)
            cost.image = string_rendered
            cost.rect = cost.image.get_rect()
            cost.rect.topleft = ((j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2 + (
                    cards_list[j].rect[2] - cost.rect[2]) // 2,
                                 (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 +
                                 cards_list[j].rect[3] - cost.rect[3] - 25)
        elif data[j][3] == 0:
            cards_list[j] = pygame.sprite.Sprite(cards)
            cards_list[j].image = big_red_frame_image
            cards_list[j].rect = cards_list[j].image.get_rect()
            cards_list[j].rect.topleft = ((j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2,
                                          (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2)
            font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 24 - (j // 3) * 5)
            string_rendered = font.render(str(data[j][1]), True, pygame.Color('white'))
            cost = pygame.sprite.Sprite(cards)
            cost.image = string_rendered
            cost.rect = cost.image.get_rect()
            cost.rect.topleft = ((j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2 + (
                    cards_list[j].rect[2] - cost.rect[2]) // 2,
                                 (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 +
                                 cards_list[j].rect[3] - cost.rect[3] - 25)
        level_map = load_level(cur.execute("""SELECT path FROM levels WHERE id = ?""", (j + 1, )).fetchall()[0][0])
        max_len_level = 0
        for yy in range(len(level_map)):
            if len(level_map[yy]) > max_len_level:
                max_len_level = len(level_map[yy])
        for yy in range(len(level_map)):
            for xx in range(len(level_map[yy])):
                if level_map[yy][xx] != ".":
                    Brick(30 + cards_list[j].rect.topleft[0] + xx * ((cards_list[j].rect[2] - 60) // max_len_level),
                          30 + cards_list[j].rect.topleft[1] + yy * int(
                              ((cards_list[j].rect[2] - 60) / max_len_level) * (450 / 1248)),
                          ((cards_list[j].rect[2] - 60) // max_len_level),
                          int(((cards_list[j].rect[2] - 60) / max_len_level) * (450 / 1248)), level_map[yy][xx],
                          brick_level_sprites)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 5 <= event.pos[0] <= 146 and 5 <= \
                    event.pos[1] <= 66:
                sound_effects['effect_done'].play()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and WIDTH - 146 <= event.pos[0] \
                    <= WIDTH - 5 and 5 <= event.pos[1] <= 66:
                sound_effects['effect_done'].play()
                terminate()
            data = cur.execute("""SELECT * FROM levels""").fetchall()
            if event.type == pygame.MOUSEMOTION and 5 <= event.pos[0] <= 146 and 5 <= event.pos[1] <= 66:
                cursor.image = click_image
                menu.image = mini_menu_image
                menu.rect.topleft = (8, 7)
            elif event.type == pygame.MOUSEMOTION and WIDTH - 146 <= event.pos[0] <= WIDTH - 5 and 5 <= event.pos[
                1] <= 66:
                cursor.image = click_image
                mini_quit.image = mini_mini_quit_image
                mini_quit.rect.topleft = (WIDTH - 143, 7)
            else:
                tf = False
                for j in range(3):
                    if event.type == pygame.MOUSEMOTION and (j % 3) * cards_list[j].rect[2] + (
                            WIDTH - cards_list[j].rect[2] * 3) // 2 + 5 <= event.pos[0] <= (j % 3) * cards_list[j].rect[
                        2] + (WIDTH - cards_list[j].rect[2] * 3) // 2 + cards_list[j].rect[2] - 5 and (j // 3) * \
                            cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 + 5 <= event.pos[1] <= (
                            j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 + \
                            cards_list[j].rect[3] - 5 and data[j][4] == 0:
                        if data[j][3] == 1:
                            old_rect = cards_list[j].rect
                            old_rect_topleft = cards_list[j].rect.topleft
                            cards_list[j].image = big_mini_green_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                                old_rect_topleft[0] + (old_rect[2] - cards_list[j].rect[2]) // 2,
                                old_rect_topleft[1] + (old_rect[3] - cards_list[j].rect[3]) // 2)
                        else:
                            old_rect = cards_list[j].rect
                            old_rect_topleft = cards_list[j].rect.topleft
                            cards_list[j].image = big_mini_red_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                                old_rect_topleft[0] + (old_rect[2] - cards_list[j].rect[2]) // 2,
                                old_rect_topleft[1] + (old_rect[3] - cards_list[j].rect[3]) // 2)
                        cursor.image = click_image
                        tf = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (j % 3) * cards_list[j].rect[
                        2] + (
                            WIDTH - cards_list[j].rect[2] * 3) // 2 + 5 <= event.pos[0] <= (j % 3) * cards_list[j].rect[
                        2] + (WIDTH - cards_list[j].rect[2] * 3) // 2 + cards_list[j].rect[2] - 5 and (j // 3) * \
                            cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 + 5 <= event.pos[1] <= (
                            j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2 + \
                            cards_list[j].rect[3] - 5 and data[j][4] == 0:
                        sound_effects['effect_done'].play()
                        if data[j][3] == 1:
                            cur.execute("""UPDATE levels SET choice = ? WHERE id = ?""", (1, j + 1))
                            cur.execute("""UPDATE levels SET choice = ? WHERE id != ?""", (0, j + 1))
                            con.commit()
                            cards_list[j].image = big_choice_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                                (j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2,
                                (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2)
                        cursor.image = click_image
                        tf = True
                if not tf:
                    cursor.image = cursor_image
                    for j in range(3):
                        if data[j][4] == 0:
                            if data[j][3] == 1:
                                cards_list[j].image = big_green_frame_image
                                cards_list[j].rect = cards_list[j].image.get_rect()
                                cards_list[j].rect.topleft = (
                                    (j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2,
                                    (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2)
                            else:
                                cards_list[j].image = big_red_frame_image
                                cards_list[j].rect = cards_list[j].image.get_rect()
                                cards_list[j].rect.topleft = (
                                    (j % 3) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 3) // 2,
                                    (j // 3) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 1) // 2)
                menu.image = menu_image
                menu.rect.topleft = (5, 5)

                mini_quit.image = second_mini_quit_image
                mini_quit.rect.topleft = (WIDTH - 146, 5)

            if event.type == pygame.MOUSEMOTION:
                cursor.rect.topleft = event.pos

        screen.fill(black)

        if count_stars % 6 == 0:
            stars_sprites.update()

        font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 42)
        string_rendered = font.render(str(GLOBAL_SCORE), True, pygame.Color('white'))
        screen.blit(string_rendered, (
            int(WIDTH / 2 - (string_rendered.get_rect()[2] + score_change_ball.rect[2] + 10) / 2) +
            score_change_ball.rect[
                2] + 10, 20))
        score_change_level.rect.topleft = (
            int(WIDTH / 2 - (string_rendered.get_rect()[2] + score_change_ball.rect[2] + 10) / 2), 25)

        stars_sprites.draw(screen)
        cards.draw(screen)
        change_level_sprites.draw(screen)
        brick_level_sprites.draw(screen)
        cursor_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

        count_stars += 1


def change_ball():
    global GLOBAL_SCORE, sound_effect

    count_stars = 0

    cards = pygame.sprite.Group()
    cards_list = [0] * 24
    data = cur.execute("""SELECT * FROM balls""").fetchall()

    for j in range(24):
        if data[j][2] == 1:
            cards_list[j] = pygame.sprite.Sprite(cards)
            cards_list[j].image = choice_frame_image
            cards_list[j].rect = cards_list[j].image.get_rect()
            cards_list[j].rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                                          (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
            font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 34 - (j // 6) * 5)
            string_rendered = font.render(str(data[j][3]), True, pygame.Color('white'))
            cost = pygame.sprite.Sprite(cards)
            cost.image = string_rendered
            cost.rect = cost.image.get_rect()
            cost.rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + (
                        cards_list[j].rect[2] - cost.rect[2]) // 2,
                                 (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 +
                                 cards_list[j].rect[3] - cost.rect[3] - 15)
            sphere = pygame.sprite.Sprite(cards)
            sphere.image = balls_shop_images[j]
            sphere.rect = sphere.image.get_rect()
            sphere.rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + (
                        cards_list[j].rect[2] - sphere.rect[2]) // 2,
                                 (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + 30)
        elif data[j][1] == 1:
            cards_list[j] = pygame.sprite.Sprite(cards)
            cards_list[j].image = green_frame_image
            cards_list[j].rect = cards_list[j].image.get_rect()
            cards_list[j].rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                                          (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
            font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 34 - (j // 6) * 5)
            string_rendered = font.render(str(data[j][3]), True, pygame.Color('white'))
            cost = pygame.sprite.Sprite(cards)
            cost.image = string_rendered
            cost.rect = cost.image.get_rect()
            cost.rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + (
                        cards_list[j].rect[2] - cost.rect[2]) // 2,
                                 (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 +
                                 cards_list[j].rect[3] - cost.rect[3] - 15)
            sphere = pygame.sprite.Sprite(cards)
            sphere.image = balls_shop_images[j]
            sphere.rect = sphere.image.get_rect()
            sphere.rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + (
                    cards_list[j].rect[2] - sphere.rect[2]) // 2,
                                   (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + 30)

        elif data[j][1] == 0:
            cards_list[j] = pygame.sprite.Sprite(cards)
            cards_list[j].image = red_frame_image
            cards_list[j].rect = cards_list[j].image.get_rect()
            cards_list[j].rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                                          (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
            font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 34 - (j // 6) * 5)
            string_rendered = font.render(str(data[j][3]), True, pygame.Color('white'))
            cost = pygame.sprite.Sprite(cards)
            cost.image = string_rendered
            cost.rect = cost.image.get_rect()
            cost.rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + (
                        cards_list[j].rect[2] - cost.rect[2]) // 2,
                                 (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 +
                                 cards_list[j].rect[3] - cost.rect[3] - 15)
            sphere = pygame.sprite.Sprite(cards)
            sphere.image = balls_shop_images[j]
            sphere.rect = sphere.image.get_rect()
            sphere.rect.topleft = ((j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + (
                    cards_list[j].rect[2] - sphere.rect[2]) // 2,
                                   (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 5 <= event.pos[0] <= 146 and 5 <= \
                    event.pos[1] <= 66:
                sound_effects['effect_done'].play()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and WIDTH - 146 <= event.pos[0] \
                    <= WIDTH - 5 and 5 <= event.pos[1] <= 66:
                sound_effects['effect_done'].play()
                terminate()
            data = cur.execute("""SELECT * FROM balls""").fetchall()
            if event.type == pygame.MOUSEMOTION and 5 <= event.pos[0] <= 146 and 5 <= event.pos[1] <= 66:
                cursor.image = click_image
                menu.image = mini_menu_image
                menu.rect.topleft = (8, 7)
            elif event.type == pygame.MOUSEMOTION and WIDTH - 146 <= event.pos[0] <= WIDTH - 5 and 5 <= event.pos[
                1] <= 66:
                cursor.image = click_image
                mini_quit.image = mini_mini_quit_image
                mini_quit.rect.topleft = (WIDTH - 143, 7)
            else:
                tf = False
                for j in range(24):
                    if event.type == pygame.MOUSEMOTION and (j % 6) * cards_list[j].rect[2] + (
                            WIDTH - cards_list[j].rect[2] * 6) // 2 + 5 <= event.pos[0] <= (j % 6) * cards_list[j].rect[
                        2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + cards_list[j].rect[2] - 5 and (j // 6) * \
                            cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + 5 <= event.pos[1] <= (
                            j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + \
                            cards_list[j].rect[3] - 5 and data[j][2] == 0:
                        if data[j][1] == 1:
                            old_rect = cards_list[j].rect
                            old_rect_topleft = cards_list[j].rect.topleft
                            cards_list[j].image = mini_green_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                            old_rect_topleft[0] + (old_rect[2] - cards_list[j].rect[2]) // 2,
                            old_rect_topleft[1] + (old_rect[3] - cards_list[j].rect[3]) // 2)
                        else:
                            old_rect = cards_list[j].rect
                            old_rect_topleft = cards_list[j].rect.topleft
                            cards_list[j].image = mini_red_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                            old_rect_topleft[0] + (old_rect[2] - cards_list[j].rect[2]) // 2,
                            old_rect_topleft[1] + (old_rect[3] - cards_list[j].rect[3]) // 2)
                        cursor.image = click_image
                        tf = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (j % 6) * cards_list[j].rect[
                        2] + (
                            WIDTH - cards_list[j].rect[2] * 6) // 2 + 5 <= event.pos[0] <= (j % 6) * cards_list[j].rect[
                        2] + (WIDTH - cards_list[j].rect[2] * 6) // 2 + cards_list[j].rect[2] - 5 and (j // 6) * \
                            cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + 5 <= event.pos[1] <= (
                            j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2 + \
                            cards_list[j].rect[3] - 5 and data[j][2] == 0:
                        sound_effects['effect_done'].play()
                        if data[j][1] == 0 and data[j][3] <= GLOBAL_SCORE:
                            GLOBAL_SCORE -= data[j][3]
                            cur.execute("""UPDATE score SET score = ?""", (GLOBAL_SCORE,))
                            cur.execute("""UPDATE balls SET available = ? WHERE id = ?""", (1, j + 1))
                            cur.execute("""UPDATE balls SET choice = ? WHERE id = ?""", (1, j + 1))
                            cur.execute("""UPDATE balls SET choice = ? WHERE id != ?""", (0, j + 1))
                            con.commit()
                            cards_list[j].image = choice_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                            (j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                            (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
                        elif data[j][1] == 1:
                            cur.execute("""UPDATE balls SET choice = ? WHERE id = ?""", (1, j + 1))
                            cur.execute("""UPDATE balls SET choice = ? WHERE id != ?""", (0, j + 1))
                            con.commit()
                            cards_list[j].image = choice_frame_image
                            cards_list[j].rect = cards_list[j].image.get_rect()
                            cards_list[j].rect.topleft = (
                                (j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                                (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
                        cursor.image = click_image
                        tf = True
                if not tf:
                    cursor.image = cursor_image
                    for j in range(24):
                        if data[j][2] == 0:
                            if data[j][1] == 1:
                                cards_list[j].image = green_frame_image
                                cards_list[j].rect = cards_list[j].image.get_rect()
                                cards_list[j].rect.topleft = (
                                (j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                                (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
                            else:
                                cards_list[j].image = red_frame_image
                                cards_list[j].rect = cards_list[j].image.get_rect()
                                cards_list[j].rect.topleft = (
                                (j % 6) * cards_list[j].rect[2] + (WIDTH - cards_list[j].rect[2] * 6) // 2,
                                (j // 6) * cards_list[j].rect[3] + (HEIGHT - cards_list[j].rect[3] * 4) // 2)
                menu.image = menu_image
                menu.rect.topleft = (5, 5)

                mini_quit.image = second_mini_quit_image
                mini_quit.rect.topleft = (WIDTH - 146, 5)

            if event.type == pygame.MOUSEMOTION:
                cursor.rect.topleft = event.pos

        screen.fill(black)

        if count_stars % 6 == 0:
            stars_sprites.update()

        font = pygame.font.Font(resource_path(os.path.join('data', 'Pixon.ttf')), 42)
        string_rendered = font.render(str(GLOBAL_SCORE), True, pygame.Color('white'))
        screen.blit(string_rendered, (
        int(WIDTH / 2 - (string_rendered.get_rect()[2] + score_change_ball.rect[2] + 10) / 2) + score_change_ball.rect[
            2] + 10, 20))
        score_change_ball.rect.topleft = (
        int(WIDTH / 2 - (string_rendered.get_rect()[2] + score_change_ball.rect[2] + 10) / 2), 25)

        stars_sprites.draw(screen)
        cards.draw(screen)
        change_ball_sprites.draw(screen)
        cursor_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

        count_stars += 1


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, group, frame_size=(-1, -1)):
        super().__init__(group)
        self.frame_size = frame_size
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = int(random.random() * columns * rows)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                if self.frame_size != (-1, -1):
                    self.frames.append(pygame.transform.scale((sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size))), self.frame_size))
                else:
                    self.frames.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, n):
        super().__init__(play_sprites)
        self.radius = 16
        self.image = balls_images[n]
        self.rect = pygame.Rect(x, y, 2 * self.radius, 2 * self.radius)
        self.vx = random.randint(-2, 2)
        self.vy = -5
        self.centerx = self.rect.topleft[0] + self.radius
        self.centery = self.rect.topleft[1] + self.radius

    def intersect(self, obj):
        edges = dict(
            left=pygame.rect.Rect(obj.rect.topleft[0], obj.rect.topleft[1], 1, obj.rect[3]),
            right=pygame.rect.Rect(obj.rect.topleft[0] + obj.rect[2], obj.rect.topleft[1], 1, obj.rect[3]),
            top=pygame.rect.Rect(obj.rect.topleft[0], obj.rect.topleft[1], obj.rect[2], 1),
            bottom=pygame.rect.Rect(obj.rect.topleft[0], obj.rect.topleft[1] + obj.rect[3], obj.rect[2], 1))
        collisions = set(edge for edge, rect in edges.items() if
                         self.rect.colliderect(rect))
        if not collisions:
            return None

        if len(collisions) == 1:
            return list(collisions)[0]

        if 'top' in collisions:
            if self.centery >= obj.rect.topleft[1]:
                return 'top'
            if self.centerx < obj.rect.topleft[0]:
                return 'left'
            else:
                return 'right'

        if 'bottom' in collisions:
            if self.centery >= obj.rect.topleft[1] + obj.rect[3]:
                return 'bottom'
            if self.centerx < obj.rect.topleft[0]:
                return 'left'
            else:
                return 'right'

    def update(self):
        global left_flag, right_flag, bricks_list, sound_effect
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, panel_sprite) and self.intersect(panel) == "top" or \
                self.intersect(panel) == "bottom":
            sound_effects['paddle_hit'].play()
            self.vy = -self.vy
            if left_flag:
                self.vx -= 1
            if right_flag:
                self.vx += 1
        elif pygame.sprite.spritecollideany(self, panel_sprite) and self.intersect(panel) == "left" or self.intersect(
            panel) == "right":
            sound_effects['paddle_hit'].play()
            self.vx = -self.vx


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(play_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, c, group_of_sprites):
        super().__init__(group_of_sprites)
        self.w = w
        self.h = h
        self.color = c
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(tile_images[self.color], (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, ball):
        global brick_number_of_changes, local_score, panel, panel_number, panel_images, brick_number_of_changes_inline
        global sound_effect
        if ball.intersect(self) == "top" or ball.intersect(self) == "bottom":
            sound_effects['brick_hit'].play()
            if brick_number_of_changes == 0:
                ball.vy = -ball.vy
            brick_number_of_changes += 1
            if self.color == 'r':
                local_score += 64
                self.color = 'g'
                self.image = pygame.transform.scale(tile_images[self.color], (self.w, self.h))
                self.rect.topleft = (self.x, self.y)
            elif self.color == 'o':
                local_score += 32
                ball.vx = int(ball.vx * 1.5)
                ball.vy = int(ball.vy * 1.5)
                self.kill()
            elif self.color == 'y':
                local_score += 16
                ball.vx = int(ball.vx * 0.8)
                ball.vy = max(3, int(ball.vy * 0.8))
                self.kill()
            elif self.color == 'g':
                local_score += 8
                self.color = 'p'
                self.image = pygame.transform.scale(tile_images[self.color], (self.w, self.h))
                self.rect.topleft = (self.x, self.y)
            elif self.color == 't':
                local_score += 4
                old_rect = panel.rect
                old_rect_tl = panel.rect.topleft
                panel.kill()
                panel = pygame.sprite.Sprite(panel_sprite)
                panel_number = min(panel_number + 1, 2)
                panel.image = panel_images[panel_number]
                panel.rect = panel.image.get_rect()
                panel.rect.topleft = (
                min(max(old_rect_tl[0] + old_rect[2] // 2 - panel.rect[2] // 2, 0), WIDTH - panel.rect[2] - 151),
                HEIGHT - 78)
                self.kill()
            elif self.color == 'b':
                local_score += 2
                old_rect = panel.rect
                old_rect_tl = panel.rect.topleft
                panel.kill()
                panel = pygame.sprite.Sprite(panel_sprite)
                panel_number = max(panel_number - 1, 0)
                panel.image = panel_images[panel_number]
                panel.rect = panel.image.get_rect()
                panel.rect.topleft = (
                min(max(old_rect_tl[0] + old_rect[2] // 2 - panel.rect[2] // 2, 0), WIDTH - panel.rect[2] - 151),
                HEIGHT - 78)
                self.kill()
            elif self.color == 'p':
                local_score += 1
                self.kill()
        if ball.intersect(self) == "left" or ball.intersect(self) == "right":
            sound_effects['brick_hit'].play()
            if brick_number_of_changes_inline == 0:
                ball.vx = -ball.vx
            brick_number_of_changes_inline += 1
            if self.color == 'r':
                local_score += 64
                self.color = 'g'
                self.image = pygame.transform.scale(tile_images[self.color], (self.w, self.h))
                self.rect.topleft = (self.x, self.y)
            elif self.color == 'o':
                local_score += 32
                ball.vx = int(ball.vx * 1.5)
                ball.vy = int(ball.vy * 1.5)
                self.kill()
            elif self.color == 'y':
                local_score += 16
                ball.vx = int(ball.vx * 0.8)
                ball.vy = max(3, int(ball.vy * 0.8))
                self.kill()
            elif self.color == 'g':
                local_score += 8
                self.color = 'p'
                self.image = pygame.transform.scale(tile_images[self.color], (self.w, self.h))
                self.rect.topleft = (self.x, self.y)
            elif self.color == 't':
                local_score += 4
                old_rect = panel.rect
                old_rect_tl = panel.rect.topleft
                panel.kill()
                panel = pygame.sprite.Sprite(panel_sprite)
                panel_number = min(panel_number + 1, 2)
                panel.image = panel_images[panel_number]
                panel.rect = panel.image.get_rect()
                panel.rect.topleft = (
                    min(max(old_rect_tl[0] + old_rect[2] // 2 - panel.rect[2] // 2, 0), WIDTH - panel.rect[2] - 151),
                    HEIGHT - 78)
                self.kill()
            elif self.color == 'b':
                local_score += 2
                old_rect = panel.rect
                old_rect_tl = panel.rect.topleft
                panel.kill()
                panel = pygame.sprite.Sprite(panel_sprite)
                panel_number = max(panel_number - 1, 0)
                panel.image = panel_images[panel_number]
                panel.rect = panel.image.get_rect()
                panel.rect.topleft = (
                    min(max(old_rect_tl[0] + old_rect[2] // 2 - panel.rect[2] // 2, 0), WIDTH - panel.rect[2] - 151),
                    HEIGHT - 78)
                self.kill()
            elif self.color == 'p':
                local_score += 1
                self.kill()


if __name__ == '__main__':

    clock = pygame.time.Clock()

    icon = load_image('icon.png')
    pygame.display.set_icon(icon)

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    stars_sprites = pygame.sprite.Group()
    start_sprites = pygame.sprite.Group()
    cursor_sprites = pygame.sprite.Group()
    play_sprites = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    panel_sprite = pygame.sprite.Group()
    brick_sprites = pygame.sprite.Group()
    brick_level_sprites = pygame.sprite.Group()
    change_ball_sprites = pygame.sprite.Group()
    change_level_sprites = pygame.sprite.Group()
    game_over_sprites = pygame.sprite.Group()

    click_image = load_image('click.png')
    cursor_image = load_image('pointer.png')
    cursor = pygame.sprite.Sprite(cursor_sprites)
    cursor.image = cursor_image
    cursor.rect = cursor.image.get_rect()

    pygame.mouse.set_visible(False)

    planet_image = pygame.transform.scale(load_image('planet.png'), (329, 737))
    title_image = pygame.transform.scale(load_image('title.png'), (661, 82))
    score_image = pygame.transform.scale(load_image('score.png'), (145, 29))

    button_size = (358, 73)

    play_image = pygame.transform.scale(load_image('play.png'), button_size)
    level_image = pygame.transform.scale(load_image('level.png'), button_size)
    ball_image = pygame.transform.scale(load_image('ball.png'), button_size)
    quit_image = pygame.transform.scale(load_image('quit.png'), button_size)

    button_difference = 20
    mini_button_size = (358 - button_difference, 73 - int(button_difference * (73 / 358)))

    mini_play_image = pygame.transform.scale(load_image('play.png'), mini_button_size)
    mini_level_image = pygame.transform.scale(load_image('level.png'), mini_button_size)
    mini_ball_image = pygame.transform.scale(load_image('ball.png'), mini_button_size)
    mini_quit_image = pygame.transform.scale(load_image('quit.png'), mini_button_size)

    black = pygame.Color("black")

    planet = pygame.sprite.Sprite(start_sprites)
    planet.image = planet_image
    planet.rect = planet.image.get_rect()
    planet.rect.topleft = (0, 43)

    title = pygame.sprite.Sprite(start_sprites)
    title.image = title_image
    title.rect = title.image.get_rect()
    title.rect.topleft = (83, 49)

    button_pos = button_pos_x, button_pos_y = (388, 197)
    gap_button = 84

    play_sprite = pygame.sprite.Sprite(start_sprites)
    play_sprite.image = play_image
    play_sprite.rect = play_sprite.image.get_rect()
    play_sprite.rect.topleft = button_pos

    level_sprite = pygame.sprite.Sprite(start_sprites)
    level_sprite.image = level_image
    level_sprite.rect = level_sprite.image.get_rect()
    level_sprite.rect.topleft = (button_pos_x, button_pos_y + gap_button)

    ball_sprite = pygame.sprite.Sprite(start_sprites)
    ball_sprite.image = ball_image
    ball_sprite.rect = ball_sprite.image.get_rect()
    ball_sprite.rect.topleft = (button_pos_x, button_pos_y + gap_button * 2)

    quit_sprite = pygame.sprite.Sprite(start_sprites)
    quit_sprite.image = quit_image
    quit_sprite.rect = quit_sprite.image.get_rect()
    quit_sprite.rect.topleft = (button_pos_x, button_pos_y + gap_button * 3)

    score = pygame.sprite.Sprite(start_sprites)
    score.image = score_image
    score.rect = score.image.get_rect()
    score.rect.topleft = (WIDTH, HEIGHT)

    score_play_image = pygame.transform.scale(load_image('score.png'), (141, 28))

    score_play = pygame.sprite.Sprite(play_sprites)
    score_play.image = score_play_image
    score_play.rect = score_play.image.get_rect()
    score_play.rect.topleft = (WIDTH, HEIGHT)

    score_change_ball_image = pygame.transform.scale(load_image('score.png'), (141, 28))

    score_change_ball = pygame.sprite.Sprite(change_ball_sprites)
    score_change_ball.image = score_change_ball_image
    score_change_ball.rect = score_change_ball.image.get_rect()
    score_change_ball.rect.topleft = (WIDTH, HEIGHT)

    score_change_level_image = pygame.transform.scale(load_image('score.png'), (141, 28))

    score_change_level = pygame.sprite.Sprite(change_level_sprites)
    score_change_level.image = score_change_level_image
    score_change_level.rect = score_change_level.image.get_rect()
    score_change_level.rect.topleft = (WIDTH, HEIGHT)

    lives_image = pygame.transform.scale(load_image('lives.png'), (119, 29))

    lives_play = pygame.sprite.Sprite(play_sprites)
    lives_play.image = lives_image
    lives_play.rect = lives_play.image.get_rect()
    lives_play.rect.topleft = (WIDTH, HEIGHT)

    game_over_image = pygame.transform.scale(load_image('game_over.png'), (int(520 * 1), int(430 * 1)))

    game_over = pygame.sprite.Sprite(game_over_sprites)
    game_over.image = game_over_image
    game_over.rect = game_over.image.get_rect()
    game_over.rect.topleft = (WIDTH // 2 - game_over.rect[2] // 2, HEIGHT // 2.5 - game_over.rect[3] // 2)

    for i in range(300):
        AnimatedSprite(load_image("stars.png"), 17, 1, (random.random() * 780), (random.random() * 780), stars_sprites,
                       (15, 15))

    menu_image = pygame.transform.scale(load_image('menu.png'), (141, 61))
    mini_menu_image = pygame.transform.scale(load_image('menu.png'), (136, 58))

    menu = pygame.sprite.Sprite(play_sprites)
    menu.image = menu_image
    menu.rect = menu.image.get_rect()
    menu.rect.topleft = (WIDTH - 146, 5)
    change_ball_sprites.add(menu)
    change_level_sprites.add(menu)

    second_mini_quit_image = pygame.transform.scale(load_image('mini_quit.png'), (141, 61))
    mini_mini_quit_image = pygame.transform.scale(load_image('mini_quit.png'), (136, 58))
    mini_quit = pygame.sprite.Sprite(play_sprites)
    mini_quit.image = second_mini_quit_image
    mini_quit.rect = mini_quit.image.get_rect()
    mini_quit.rect.topleft = (WIDTH - 146, 71)
    change_ball_sprites.add(mini_quit)
    change_level_sprites.add(mini_quit)

    tile_images = {
        'r': load_image('red_tile.png'),
        'o': load_image('orange_tile.png'),
        'y': load_image('yellow_tile.png'),
        'g': load_image('green_tile.png'),
        't': load_image('turquoise_tile.png'),
        'b': load_image('blue_tile.png'),
        'p': load_image('purple_tile.png')
    }

    panel_images = [
        pygame.transform.scale(load_image('panel4.png'), (120, 25)),
        pygame.transform.scale(load_image('panel8.png'), (247, 25)),
        pygame.transform.scale(load_image('panel16.png'), (499, 25))
    ]
    balls_images = list()
    for i in range(1, 25):
        balls_images.append(pygame.transform.scale(load_image(f'sphere{str(i)}.png'), (32, 32)))

    balls_shop_images = list()
    for i in range(1, 25):
        balls_shop_images.append(pygame.transform.scale(load_image(f'sphere{str(i)}.png'), (48, 48)))

    panel = pygame.sprite.Sprite(panel_sprite)
    panel_number = 1
    panel.image = panel_images[panel_number]
    panel.rect = panel.image.get_rect()

    green_frame_image = pygame.transform.scale(load_image('green_frame.png'), (705 // 6, 860 // 6))
    red_frame_image = pygame.transform.scale(load_image('red_frame.png'), (705 // 6, 860 // 6))
    choice_frame_image = pygame.transform.scale(load_image('choice_frame.png'), (705 // 6, 860 // 6))

    mini_green_frame_image = pygame.transform.scale(load_image('green_frame.png'), (705 // 6 * 0.97, 860 // 6 * 0.97))
    mini_red_frame_image = pygame.transform.scale(load_image('red_frame.png'), (705 // 6 * 0.97, 860 // 6 * 0.97))

    big_green_frame_image = pygame.transform.scale(load_image('big_green_frame.png'), (344 // 1.5, 473 // 1.5))
    big_red_frame_image = pygame.transform.scale(load_image('big_red_frame.png'), (344 // 1.5, 473 // 1.5))
    big_choice_frame_image = pygame.transform.scale(load_image('big_choice_frame.png'), (344 // 1.5, 473 // 1.5))

    big_mini_green_frame_image = pygame.transform.scale(load_image('big_green_frame.png'),
                                                        (int(344 // 1.5 * 0.97), int(473 // 1.5 * 0.97)))
    big_mini_red_frame_image = pygame.transform.scale(load_image('big_red_frame.png'),
                                                      (int(344 // 1.5 * 0.97), int(473 // 1.5 * 0.97)))

    start_screen()
    terminate()

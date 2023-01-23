import sys, random
import pygame
from pygame.locals import *
from signal import pause
from time import sleep
import math

# ゲーム画面を初期化 --- (*1)
pygame.init()
screen = pygame.display.set_mode((600, 400))

white = (255,255,255)
black = (0,0,0)
# 繰り返し画面を描画 --- (*2)
font1 = pygame.font.SysFont(None, 20)
text = font1.render('test', True, (255,0,0))
image = pygame.image.load('needle.jpg')
angle = 0

while True:
    # 背景と円を描画 --- (*3)
    screen.fill(black) # 背景を黒で塗りつぶす
    pygame.draw.circle(screen, white, (300,200), 200) # 円を描画
    angle += 1
    screen.blit(pygame.transform.rotozoom(image, angle,1), (300 - 5 * math.cos(angle * 0.0174532925),200 - 5 * math.sin(angle * 0.0174532925)))
    # 画面を更新 --- (*4)
    pygame.display.update()

    # 終了イベントを確認 --- (*5)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    sleep(0.033)
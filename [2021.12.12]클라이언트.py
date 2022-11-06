# 2021-12-10 금요일 201611466 정원용 네트워크 프로그래밍 프로젝트 #
import os
import sys
import time
import pygame
import socket
import threading

# 프로그램 기본 초기화 #
pygame.init()

# 화면 크기 설정 #
screen_width = 1280 # 가로 크기
screen_height = 720 # 세로 크기
screen = pygame.display.set_mode((screen_width, screen_height))

# 게임 타이틀 설정 #
pygame.display.set_caption("클라이언트")

# 게임 텍스트 폰트 #
myFont = pygame.font.Font("./src/Typo_SsangmunDongB.ttf", 30)
game_time = 1
text_time = myFont.render(str(game_time)+"초", True, (0, 0, 0))

# FPS #
clock = pygame.time.Clock()

# 사용자 게임 초기화 (배경 화면, 게임 이미지, 좌표, 속도, 폰트 등) #
current_path = os.path.dirname(__file__) # 현재 파일의 위치 반환
image_path = os.path.join(current_path, "src") # src 폴더 위치 반환

# 배경 만들기 #
background = pygame.image.load(os.path.join(image_path, "background.png"))

# 스테이지 만들기 #
stage = pygame.image.load(os.path.join(image_path, "stage.png"))

# 공 만들기 #
ball = []
b_name = "green_ball.png"
ball.append(pygame.image.load(os.path.join(image_path, b_name)).convert_alpha())
b_name = "yellow_ball.png"
ball.append(pygame.image.load(os.path.join(image_path, b_name)).convert_alpha())

# 캐릭터 모습 리스트에 넣기 #
character_idle_list_1 = []  # 기본 IDLE 오른쪽 방향
for i in range(18):
    name = "Reaper_Man_Idle_"+str(i)+".png"
    character_idle_list_1.append(pygame.image.load(os.path.join(image_path, name)).convert_alpha())
character_idle_list_2 = []  # 기본 IDLE 왼쪽 방향
for i in range(18):
    name = "Reaper_Man_Idle_L_"+str(i)+".png"
    character_idle_list_2.append(pygame.image.load(os.path.join(image_path, name)).convert_alpha())
enemy_idle_list_1 = []
for i in range(18):
    name = "Golem_Idle_"+str(i)+".png"
    enemy_idle_list_1.append(pygame.image.load(os.path.join(image_path, name)).convert_alpha())
enemy_idle_list_2 = []
for i in range(18):
    name = "Golem_Idle_L_"+str(i)+".png"
    enemy_idle_list_2.append(pygame.image.load(os.path.join(image_path, name)).convert_alpha())

# 승리/패배 이미지 #
win = pygame.image.load(os.path.join(image_path, "win.png"))
defeat = pygame.image.load(os.path.join(image_path, "defeat.png"))

# 적과 나의 좌표 #
my_x = 1130
my_y = 530
enemy_x = 0
enemy_y = 530
ball_x = 0
ball_y = 0
ball_to_x = 0.5
ball_to_y = 0.5
left = True # 왼쪽을 보고 있는가
enemy_left = False
to_x = 0 # 이동할 좌표
to_y = 0
enemy_to_x = 0
enemy_to_y = 0
speed = 0.5 # 캐릭터 좌 우 움직임 속도

# 적 점프 처리 #
enemy_is_jump = False # 점프중이 아님

def enmy_jump():
    global enemy_y, enemy_is_jump
    enemy_is_jump = True
    for i in range(20):
        enemy_y -= 8
        time.sleep(0.01)
    for i in range(20):
        enemy_y += 8
        time.sleep(0.001)
    enemy_is_jump = False

# 공의 움직임 #
def ball_move():
    global ball_x, ball_y, ball_to_x, ball_to_y
    if ball_x<0:
        ball_x = 0
        ball_to_x *= -1
    if ball_x>1105:
        ball_x = 1105
        ball_to_x *= -1
    if ball_y<0:
        ball_y = 0
        ball_to_y *= -1
    if ball_y>480:
        ball_y = 480
        ball_to_y *= -1
        
start = "no"

# 상대방으로부터 받는 데이터 #
def consoles():
    global enemy_to_x, enemy_to_y, enemy_left, start, running
    while True:
        message = client.recv(1024) # 클라이언트로부터 1024바이트 데이터 수신
        if(message.decode()=='left'):
            enemy_to_x -= speed
            enemy_left = True
        elif(message.decode()=='right'):
            enemy_to_x += speed
            enemy_left = False
        elif(message.decode()=='jump'):
            if(enemy_is_jump==False):
                thr_jump = threading.Thread(target=enmy_jump, args=())
                thr_jump.Daemon = True
                thr_jump.start()
        elif(message.decode()=='none'):
            enemy_to_x = 0
        elif(message.decode()=='none_y'):
            enemy_to_y = 0
        elif(message.decode()=='start'):
            start = "start"
        elif(message.decode()=='hit'):
            iswin = True
            running = False

# 소켓 통신 연결 #
def accept():
    global client
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))

    thr=threading.Thread(target=consoles, args=())
    thr.Daemon = True
    thr.start()

# 점프 처리 #
is_jump = False # 점프중이 아님

def jump():
    global my_y, is_jump
    is_jump = True
    for i in range(20):
        my_y -= 8
        time.sleep(0.01)
    for i in range(20):
        my_y += 8
        time.sleep(0.001)
    is_jump = False

# 게임 실행 파트 #
accept()
running = True # 게임 실행 여부
sequence = 0 # 캐릭터 순차 표시 변수
under_y = 530 # 바닥에 맞닿을 때 캐릭터의 y좌표
timer=1
iswin = True

# 충돌처리를 위한 스프라이트 객체화 #
class SpriteInfo(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        self.image = img
        self.rect = img.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.mask = pygame.mask.from_surface(img)

# 충돌 처리 #
def collider():
    global sequence, character_idle_list_1, character_idle_list_2, my_x, my_y, ball_x, ball_y, left, running, iswin
    if sequence<18:
        if left == False:
            character = SpriteInfo(character_idle_list_1[sequence], my_x, my_y)
        else:
            character = SpriteInfo(character_idle_list_2[sequence], my_x, my_y)
        ball_char = SpriteInfo(ball[0], ball_x, ball_y)
        if(pygame.sprite.collide_mask(character, ball_char)):
            # 패배 처리 #
            iswin = False
            running = False

while True:
    if(start=='start'):
        break
ball_x = -300
ball_y = -300
while running:
    if(sequence>17):
        sequence = 0
    if(timer>60):
        timer = 1
        game_time += 1
        text_time = myFont.render(str(game_time)+"초", True, (0, 0, 0))
        message=str(game_time)+"초"
        client.sendall(message.encode())
    dt = clock.tick(60) # 프레임
    my_x += to_x * dt
    enemy_x += enemy_to_x * dt
    ball_move()
    ball_x += ball_to_x * dt
    ball_y += ball_to_y * dt
    # 이벤트 처리(종료버튼, 키 입력 처리 등) #
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if is_jump == False:
                    thr_jump = threading.Thread(target=jump, args=())
                    thr_jump.Daemon = True
                    thr_jump.start()
                    message="jump"
                    client.sendall(message.encode())
            if event.key == pygame.K_LEFT:
                to_x -= speed
                left = True
                message="left"
                client.sendall(message.encode())
            if event.key == pygame.K_RIGHT:
                to_x += speed
                left = False
                message="right"
                client.sendall(message.encode())
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                to_x = 0
                message="none"
                client.sendall(message.encode())
            if event.key == pygame.K_UP:
                to_y = 0
                message="none_y"
                client.sendall(message.encode())

    # 가로 경계 값 처리 #
    if my_x < -45:
        my_x = -45
    elif my_x > 1175:
        my_x = 1175
    if enemy_x < -45:
        enemy_x = -45
    elif enemy_x > 1175:
        enemy_x = 1175

    screen.blit(background, (0, 0))
    screen.blit(stage, (0, 0))
    if enemy_left == True:
        screen.blit(enemy_idle_list_2[sequence], (enemy_x, enemy_y))
    else:
        screen.blit(enemy_idle_list_1[sequence], (enemy_x, enemy_y))
    if left == False:
        screen.blit(character_idle_list_1[sequence], (my_x, my_y))
    else:
        screen.blit(character_idle_list_2[sequence], (my_x, my_y))
    screen.blit(ball[0], (ball_x, ball_y))
    screen.blit(text_time, (0, 0))
    collider()
    sequence += 1
    timer += 1
    pygame.display.update()

if iswin == False:
    message="hit"
    client.sendall(message.encode())
    screen.blit(defeat, (0, 0))
else:
    screen.blit(win, (0, 0))

pygame.display.update()

while event.type != pygame.QUIT:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break

pygame.quit()

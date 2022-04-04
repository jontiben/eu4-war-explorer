import pygame
pygame.init()
start_width = 1000
start_height = 600
WINDOW = pygame.display.set_mode((start_width, start_height), pygame.RESIZABLE)

QUIT = False

def disp_resize(screen_size):
	global WINDOW
	WINDOW = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
	pygame.display.update()

def event_handle():
	global QUIT
	for event in pygame.event.get():
		print(event)
		if event.type == pygame.QUIT:
			QUIT = True
		elif event.type == pygame.VIDEORESIZE:
			disp_resize(event.size)
		else:
			return event

while not QUIT:
	event_handle()
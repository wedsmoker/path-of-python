import pygame

pygame.init()

screen = pygame.display.set_mode((200, 200))
pygame.display.set_caption("Mouse Button Test")

font = pygame.font.Font(None, 36)

running = True
button_pressed = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            button_pressed = event.button
            print(f"Mouse button {event.button} pressed")

    screen.fill((255, 255, 255))  # White background

    if button_pressed:
        text = font.render(f"Button: {button_pressed}", True, (0, 0, 0))
        screen.blit(text, (50, 50))

    pygame.display.flip()

pygame.quit()
import time
import pygame
from pygame.locals import *
import ctypes
import socket

class conn():

    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def __init__(self, ip, port):
        self.clientSocket.connect((ip,port))

    def get_alt(self):
        self.clientSocket.send("alt".encode())
        msg, addr = self.clientSocket.recvfrom(1024)
        return msg.decode()

    def close(self):
        self.clientSocket.close()

class UI:

    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    def __draw_alt(self):
        x = self.width/4
        y = self.height/4

        # Draw Title
        title_surf = self.font.render("Altitude", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(x,y))
        self.screen.blit(title_surf, title_rect)

        # Draw altitude
        alt_surf= self.font.render(self.server.get_alt(), True, self.BLACK)
        alt_rect = alt_surf.get_rect(center=(x, y+20))
        self.screen.blit(alt_surf, alt_rect)

    def draw_error(self,text):
        self.screen.fill(self.WHITE)
        alt_surf= self.font.render(text, True, self.RED)
        alt_rect = alt_surf.get_rect(center=(self.width/2, self.width/2))
        screen.blit(alt_surf, alt_rect)
        pygame.display.flip()

    def update_screen(self):
        self.screen.fill(self.WHITE)
        self.__draw_alt()
        pygame.display.flip()

    def __init__(self,server=None):
        pygame.init()

        # window title 
        pygame.display.set_caption("LTA Base Station")# Font and size
        self.font = pygame.font.Font(None, 20)

        # Set the width and height of the screen [width, height]
        user32 = ctypes.windll.user32
        self.size = self.width, self.height = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        self.screen = pygame.display.set_mode(self.size)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        self.frame_rate = 8
        if not server is None:
            self.server = server
            self.update_screen()
       

if __name__ == '__main__':
    try:
        server = conn('10.148.11.245',12002)
    except:
        ui = UI(None)
        ui.draw_error("Connection error")
        pygame.quit()
    
    ui = UI(server)

    try:
        for i in range(10):
            ui.update_screen()
            time.sleep(1)
    except:
        print("Error")
        server.close()
        pygame.quit()
        raise
    
    conn.close()
    pygame.quit()


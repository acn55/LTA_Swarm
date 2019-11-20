import time
import pygame
from pygame.locals import *
import ctypes
import socket
import threading

# Globals
alt = 0
coords = "(0, 0)"
orient = 0
running = True

class conn():
    
    def __init__(self, ip, port):
        self.clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientSocket.connect((ip,port))
    
    def get_coord(self):
        self.clientSocket.send("coord".encode())
        msg, addr = self.clientSocket.recvfrom(1024)
        #return tuple(map(int,msg.decode().split(',')))
        return msg.decode()
    
    def get_alt(self):
        self.clientSocket.send("alt".encode())
        msg, addr = self.clientSocket.recvfrom(1024)
        return msg.decode()
        
    def get_orient(self):
        self.clientSocket.send("orient".encode())
        msg, addr = self.clientSocket.recvfrom(1024)
        return msg.decode()
        
    
    def exit(self):
        self.clientSocket.send("quit".encode())
        self.clientSocket.recvfrom(1024)
    
    def close(self):
        self.clientSocket.close()

class UI:

    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    def __draw_loc(self):
        # Draw position
        title_surf = self.font.render("Position", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.loc_x,self.loc_y))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(coords, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.loc_x, self.loc_y+20))
        self.screen.blit(txt_surf, txt_rect)

        # Draw altitude
        title_surf = self.font.render("Altitude", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.loc_x,self.loc_y+60))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(str(alt), True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.loc_x, self.loc_y+80))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw orientation
        title_surf = self.font.render("Heading", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.loc_x,self.loc_y+120))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(str(orient) + u"\u00b0", True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.loc_x, self.loc_y+140))
        self.screen.blit(txt_surf, txt_rect)
        
    def __draw_quit(self):
        text_surf = self.font.render("QUIT", True, self.WHITE)
        text_rect = text_surf.get_rect(center=(self.quit_x,self.quit_y))
        button_surf = pygame.Surface((40, 20))
        button_surf.fill(self.RED)
        self.screen.blit(button_surf,(self.quit_x - 20,self.quit_y - 10))
        self.screen.blit(text_surf,text_rect)
        
    def __draw_drive_sel(self):
        but_size = (80,40)
        txt_x = self.mode_x + but_size[0]/2
        txt_y = self.mode_y + but_size[1]/2
        but_space = but_size[0] + 20
        for i in range(3):
   
            # Background
            back_surf = pygame.Surface(but_size)
            back_rect = (self.mode_x + i*but_space, self.mode_y)
            if i == self.drive:
                # Currently in this mode
                back_surf.fill(self.GREEN)
            else:
                # Not in this mode
                back_surf.fill(self.RED)
            self.screen.blit(back_surf, back_rect)
            
            # Text
            if i == 0:
                txt = "Auto"
            elif i == 1:
                txt = "Waypoint"
            elif i == 2:
                txt = "Manual"
            txt_surf = self.font.render(txt, True, self.WHITE)
            txt_rect = txt_surf.get_rect(center=(txt_x + i*but_space,txt_y))
            self.screen.blit(txt_surf, txt_rect)

    def draw_error(self,text):
        self.screen.fill(self.WHITE)
        alt_surf= self.font.render(text, True, self.RED)
        alt_rect = alt_surf.get_rect(center=(self.width/2, self.width/2))
        self.screen.blit(alt_surf, alt_rect)
        pygame.display.flip()
        
    def wait_frame_rate(self):
        self.clock.tick(self.frame_rate)

    def update_screen(self):
        self.screen.fill(self.WHITE)
        self.__draw_loc()
        self.__draw_quit()
        self.__draw_drive_sel()
        pygame.display.flip()

    def __init__(self):
        pygame.init()

        # window title 
        pygame.display.set_caption("LTA Base Station")# Font and size
        self.font = pygame.font.Font(None, 20)

        # Set the width and height of the screen [width, height]
        user32 = ctypes.windll.user32
        self.size = self.width, self.height = (user32.GetSystemMetrics(0)*6/10, user32.GetSystemMetrics(1)*6/10)
        self.screen = pygame.display.set_mode(self.size)
        
        # Drive type
        # 0 - auto, 1 - waypoint, 2 - manual
        self.drive = 0
        
        # Object coordinates
        # quit button
        self.quit_x = self.width - 40
        self.quit_y = 20
        
        # camera feed
        self.cam_x = 20
        self.cam_y = 20
        
        # Localization information
        self.loc_x = self.width - 80
        self.loc_y = 80
        
        # navigation mode buttons
        self.mode_x = 20
        self.mode_y = 200

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        self.frame_rate = 1
       

def conn_thread(ip,port):
    global coords, alt, orient
    data = {"coords", "alt", "orient"}
    for d in data:
        server = conn(ip,port)
        if d == "coords":
            coords = server.get_coord()
        elif d == "alt":
            alt = server.get_alt()  
        elif d == "orient":
            orient = server.get_orient()
        server.close()
    
def terminate_server(ip,port):
    server = conn(ip,port)
    server.exit()
    server.close()

def event_handler():
    global running
    

if __name__ == '__main__':
    
    try:
        coord_thread = threading.Thread(target=conn_thread, args=('localhost',12002))
        coord_thread.start()
    except:
        ui = UI()
        ui.draw_error("Connection error")
        pygame.quit()
        raise
    
    ui = UI()

    try:
        while running:
            
            server_thread = threading.Thread(target=conn_thread, args=('localhost',12002))
            server_thread.start()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif(event.type is MOUSEBUTTONUP):
                    x,y = pygame.mouse.get_pos()
                    if x > ui.quit_x - 20 and x < ui.quit_x + 20 and y < ui.quit_y + 10 and y > ui.quit_y - 10:
                        # Quit button clicked
                        running = False
                    elif x < ui.mode_x + 40 and x > ui.mode_x - 40 and y < ui.mode_y + 20 and y > ui.mode_y - 20:
                        # Auto button clicked
                        print("Auto")
                        ui.drive = 0
                    elif x < ui.mode_x + 140 and x > ui.mode_x + 60 and y < ui.mode_y + 20 and y > ui.mode_y - 20:
                        # Waypoint button clicked
                        print("Waypoint")
                        ui.drive = 1
                    elif x < ui.mode_x + 240 and x > ui.mode_x + 160 and y < ui.mode_y + 20 and y > ui.mode_y - 20:
                        # Manual button clicked
                        print("Manual")
                        ui.drive = 2
            
            ui.update_screen()
            
            ui.wait_frame_rate()
    except:
        print("Error")
        #terminate_server('localhost',12002)
        pygame.quit()
        raise
    
    #terminate_server('localhost',12002)
    pygame.quit()


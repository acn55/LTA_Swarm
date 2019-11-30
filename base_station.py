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
        
    def get_wp(self):
        self.clientSocket.send("curr wp".encode())
        msg,addr = self.clientSocket.recvfrom(1024)
        return msg.decode()
        
    def send_acc(self, dir):
        if dir == "forward" or dir == "backward" or dir == "right" \
            or dir == "left" or dir == "up" or dir == "down" or dir == "stop":
            self.clientSocket.send(dir.encode())
        else:
            raise Exception("Acceleration direction not recognized")
            
    def send_wp(self, x, y, z, theta):
        str = "wp " + x + "," + y + "," + z + "," + theta
        self.clientSocket.send(str.encode())
    
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
    TXT_COLOR_INACTIVE = pygame.Color('lightskyblue3')
    TXT_COLOR_ACTIVE = pygame.Color('dodgerblue2')
        
    # Object coordinates
    # quit button
    quit_x = 400
    quit_y = 10
    
    # camera feed
    cam_x = 20
    cam_y = 20
    
    # Localization information
    loc_x = 370
    loc_y = 80
    
    # Navigation mode buttons
    # UL of leftmost button
    mode_x = 20
    mode_y = 200
    
    # Manual control position buttons
    # UL of up arrow key
    pos_x = mode_x + 105
    pos_y = mode_y + 70
    
    # Manual control altitude buttons
    # UL of up arrow key
    alt_x = pos_x + 200
    alt_y = pos_y
    
    # Waypoint control textbox size
    wp_tb_size = (50,20)
    
    # Waypoint control UL x input textbox
    wp_x_x = mode_x
    wp_x_y = mode_y + 70
    
    # Waypoint control UL y input textbox
    wp_y_x = mode_x + wp_tb_size[0] + 10
    wp_y_y = mode_y + 70
    
    # Waypoint control UL z input textbox
    wp_z_x = mode_x + 2*(wp_tb_size[0] + 10)
    wp_z_y = mode_y + 70
    
    # Waypoint control UL theta input textbox
    wp_theta_x = mode_x + 3*(wp_tb_size[0] + 10)
    wp_theta_y = mode_y + 70
    
    # Arrow key images
    up_arrow = pygame.image.load("up_arrow.png")
    down_arrow = pygame.image.load("down_arrow.png")
    right_arrow = pygame.image.load("right_arrow.png")
    left_arrow = pygame.image.load("left_arrow.png")

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
        text_rect = text_surf.get_rect(center=(self.quit_x+20,self.quit_y+10))
        button_surf = pygame.Surface((40, 20))
        button_surf.fill(self.RED)
        self.screen.blit(button_surf,(self.quit_x,self.quit_y))
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
            
    def __draw_man_ctrl(self):
    
        # Position arrows
        pos_surf = self.font.render("Position", True, self.BLACK)
        pos_rect = pos_surf.get_rect(center=(self.pos_x + 35, self.pos_y - 10))
        self.screen.blit(pos_surf,pos_rect)
        self.screen.blit(self.up_arrow, (self.pos_x, self.pos_y))
        self.screen.blit(self.down_arrow, (self.pos_x, self.pos_y+80))
        self.screen.blit(self.right_arrow, (self.pos_x+80, self.pos_y+80))
        self.screen.blit(self.left_arrow, (self.pos_x-80, self.pos_y+80))
        
        # Altitude arrows
        alt_surf = self.font.render("Altitude", True, self.BLACK)
        alt_rect = alt_surf.get_rect(center=(self.alt_x + 35, self.alt_y - 10))
        self.screen.blit(alt_surf,alt_rect)
        self.screen.blit(self.up_arrow, (self.alt_x, self.alt_y))
        self.screen.blit(self.down_arrow, (self.alt_x, self.alt_y+80))
        
    def __draw_wp_ctrl(self):
        
        # Waypoint entry
        if self.wp_x_active:
            x_color = self.TXT_COLOR_ACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        elif self.wp_y_active:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_ACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        elif self.wp_z_active:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_ACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        elif self.wp_theta_active:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_ACTIVE
        else:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        
        x_surf = pygame.Surface(self.wp_tb_size)
        x_surf.fill(x_color)
        x_txt_surf = self.font.render(self.wp_x_txt, True, self.BLACK)
        x_rect = pygame.Rect((self.wp_x_x,self.wp_x_y), self.wp_tb_size)
        x_label_surf = self.font.render("x", True, self.BLACK)
        x_label_rect = x_label_surf.get_rect(center=(self.wp_x_x + self.wp_tb_size[0]/2, self.wp_x_y - 15))
        y_surf = pygame.Surface(self.wp_tb_size)
        y_surf.fill(y_color)
        y_txt_surf = self.font.render(self.wp_y_txt, True, self.BLACK)
        y_rect = pygame.Rect((self.wp_y_x,self.wp_y_y), self.wp_tb_size)
        y_label_surf = self.font.render("y", True, self.BLACK)
        y_label_rect = y_label_surf.get_rect(center=(self.wp_y_x + self.wp_tb_size[0]/2, self.wp_y_y - 15))
        z_surf = pygame.Surface(self.wp_tb_size)
        z_surf.fill(z_color)
        z_txt_surf = self.font.render(self.wp_z_txt, True, self.BLACK)
        z_rect = pygame.Rect((self.wp_z_x,self.wp_z_y), self.wp_tb_size)
        z_label_surf = self.font.render("z", True, self.BLACK)
        z_label_rect = z_label_surf.get_rect(center=(self.wp_z_x + self.wp_tb_size[0]/2, self.wp_z_y - 15))
        theta_surf = pygame.Surface(self.wp_tb_size)
        theta_surf.fill(theta_color)
        theta_txt_surf = self.font.render(self.wp_theta_txt, True, self.BLACK)
        theta_rect = pygame.Rect((self.wp_theta_x,self.wp_theta_y), self.wp_tb_size)
        theta_label_surf = self.font.render(u"\u03B8", True, self.BLACK)
        theta_label_rect = theta_label_surf.get_rect(center=(self.wp_theta_x + self.wp_tb_size[0]/2, self.wp_theta_y - 15))
        
        self.screen.blit(x_surf,x_rect)
        self.screen.blit(x_txt_surf,x_rect)
        self.screen.blit(x_label_surf,x_label_rect)
        self.screen.blit(y_surf,y_rect)
        self.screen.blit(y_txt_surf,y_rect)
        self.screen.blit(y_label_surf,y_label_rect)
        self.screen.blit(z_surf,z_rect)
        self.screen.blit(z_txt_surf,z_rect)
        self.screen.blit(z_label_surf,z_label_rect)
        self.screen.blit(theta_surf,theta_rect)
        self.screen.blit(theta_txt_surf,theta_rect)
        self.screen.blit(theta_label_surf,theta_label_rect)
        
        

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
        if self.drive == 1:
            self.__draw_wp_ctrl()
        elif self.drive == 2:
            self.__draw_man_ctrl()
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
        
        # Waypoint text entry
        self.wp_x_active = False
        self.wp_x_txt = ""
        self.wp_y_active = False
        self.wp_y_txt = ""
        self.wp_z_active = False
        self.wp_z_txt = ""
        self.wp_theta_active = False
        self.wp_theta_txt = ""

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        self.frame_rate = 30
       

def get_pos_thread(ip,port):
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
        
def man_control_thread(ip,port,dir):
    server = conn(ip,port)
    server.send_acc(dir)
    server.close()
    
def wp_control_thread(ip,port,x,y,z,theta):
    if x == '':
        x = '0'
    if y == '':
        y = '0'
    if z == '':
        z = '1'
    if theta == '':
        theta = '0'
    server = conn(ip,port)
    server.send_wp(x, y, z, theta)
    server.close()    
    
def terminate_server(ip,port):
    server = conn(ip,port)
    server.exit()
    server.close()

def event_handler():
    global running
    

if __name__ == '__main__':
    
    server_ip = 'localhost'
    server_port = 12002
    
    
    try:
        coord_thread = threading.Thread(target=get_pos_thread, args=(server_ip,server_port))
        coord_thread.start()
    except:
        ui = UI()
        ui.draw_error("Connection error")
        pygame.quit()
        raise
    
    ui = UI()
    
    server_counter = 0
    
    try:
        while running:
            
            if server_counter == 30:
                server_thread = threading.Thread(target=get_pos_thread, args=(server_ip,server_port))
                server_thread.start()
                server_counter = 0
                
            server_counter += 1
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif(event.type is MOUSEBUTTONDOWN):
                    x,y = pygame.mouse.get_pos()
                    
                    if ui.drive == 1:
                        ui.wp_x_active = False
                        ui.wp_y_active = False
                        ui.wp_z_active = False
                        ui.wp_theta_active = False
                        
                    if x > ui.quit_x and x < ui.quit_x + 40 and y < ui.quit_y + 20 and y > ui.quit_y:
                        # Quit button clicked
                        running = False
                        terminate_server(server_ip,server_port)
                    elif x < ui.mode_x + 80 and x > ui.mode_x and y < ui.mode_y + 40 and y > ui.mode_y:
                        # Auto button clicked
                        print("Auto")
                        ui.drive = 0
                    elif x < ui.mode_x + 180 and x > ui.mode_x + 100 and y < ui.mode_y + 40 and y > ui.mode_y:
                        # Waypoint button clicked
                        print("Waypoint")
                        ui.drive = 1
                    elif x < ui.mode_x + 280 and x > ui.mode_x + 200 and y < ui.mode_y + 40 and y > ui.mode_y:
                        # Manual button clicked
                        print("Manual")
                        ui.drive = 2
                    elif ui.drive == 1:
                        # Waypoint drive mode
                        if x > ui.wp_x_x and x < ui.wp_x_x + ui.wp_tb_size[0] and y > ui.wp_x_y and y < ui.wp_x_y + ui.wp_tb_size[1]:
                            # Waypoint x input clicked
                            print("WP x clicked")
                            ui.wp_x_active = True
                        elif x > ui.wp_y_x and x < ui.wp_y_x + ui.wp_tb_size[0] and y > ui.wp_y_y and y < ui.wp_y_y + ui.wp_tb_size[1]:
                            # Waypoint y input clicked
                            print("WP y clicked")
                            ui.wp_y_active = True
                        elif x > ui.wp_z_x and x < ui.wp_z_x + ui.wp_tb_size[0] and y > ui.wp_z_y and y < ui.wp_z_y + ui.wp_tb_size[1]:
                            # Waypoint z input clicked
                            print("WP z clicked")
                            ui.wp_z_active = True
                        elif x > ui.wp_theta_x and x < ui.wp_theta_x + ui.wp_tb_size[0] and y > ui.wp_theta_y and y < ui.wp_theta_y + ui.wp_tb_size[1]:
                            # Waypoint theta input clicked
                            print("WP theta clicked")
                            ui.wp_theta_active = True
                    elif ui.drive == 2:
                        # Manual drive mode
                        if x > ui.pos_x and x < ui.pos_x + 70 and y > ui.pos_y and y < ui.pos_y + 70:
                            # Forward button clicked
                            print("Forward")
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"forward"))
                            move_thread.start()
                        elif x > ui.pos_x and x < ui.pos_x + 70 and y > ui.pos_y + 80 and y < ui.pos_y + 150:
                            # Back button clicked
                            print("Backward")
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"backward"))
                            move_thread.start()
                        elif x > ui.pos_x + 80 and x < ui.pos_x + 150 and y > ui.pos_y + 80 and y < ui.pos_y + 150:
                            # Right button clicked
                            print("Right")
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"right"))
                            move_thread.start()
                        elif x > ui.pos_x - 80 and x < ui.pos_x - 10 and y > ui.pos_y + 80 and y < ui.pos_y + 150:
                            # Left button clicked
                            print("Left")
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"left"))
                            move_thread.start()
                        elif x > ui.alt_x and x < ui.alt_x + 70 and y > ui.alt_y and y < ui.alt_y + 70:
                            # Up button clicked
                            print("Up")
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"up"))
                            move_thread.start()
                        elif x > ui.alt_x and x < ui.alt_x + 70 and y > ui.alt_y + 80 and y < ui.alt_y + 150:
                            # Down button clicked
                            print("Down")
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"down"))
                            move_thread.start()
                    else:
                        print(x)
                        print(y)
                elif(event.type is MOUSEBUTTONUP) and ui.drive == 2:
                    # Stop motors
                    print("Motors not running")
                    move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"stop"))
                    move_thread.start()
                elif(event.type is KEYDOWN) and ui.drive == 1:
                    if event.key == pygame.K_RETURN:
                        print("Sending wp")
                        move_thread = threading.Thread(target=wp_control_thread, \
                            args=(server_ip,server_port,ui.wp_x_txt,ui.wp_y_txt,ui.wp_z_txt,ui.wp_theta_txt))
                        move_thread.start()
                    elif ui.wp_x_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_x_txt = ui.wp_x_txt[:-1]
                        else:
                            ui.wp_x_txt += event.unicode
                    elif ui.wp_y_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_y_txt = ui.wp_y_txt[:-1]
                        else:
                            ui.wp_y_txt += event.unicode
                    elif ui.wp_z_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_z_txt = ui.wp_z_txt[:-1]
                        else:
                            ui.wp_z_txt += event.unicode
                    elif ui.wp_theta_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_theta_txt = ui.wp_theta_txt[:-1]
                        else:
                            ui.wp_theta_txt += event.unicode
                else:
                    pass
            
            ui.update_screen()
            
            time.sleep(0.02)
            
            ui.wait_frame_rate()
    except:
        print("Error")
        #terminate_server(server_ip,server_port)
        pygame.quit()
        raise
    
    #terminate_server(server_ip,server_port)
    pygame.quit()


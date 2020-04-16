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
ATs = []
running = True

class AT():
    
    def __init__(self, num, dist, ang):
        self.num = num
        self.dist = dist
        self.angle = ang

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
        
    def get_ATs(self):
        self.clientSocket.send("ats".encode())
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
        
    def send_drive(self,mode):
        str = "mode " + mode
        self.clientSocket.send(str.encode())
    
    def exit(self):
        self.clientSocket.send("quit".encode())
        self.clientSocket.recvfrom(1024)
    
    def close(self):
        self.clientSocket.close()

class UI:
    
    # Screen size
    size = width, height = (500, 500)
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    LIST_TITLE_COLOR = (16, 89, 20)
    LIST_HEADER_COLOR = (28, 128, 33)
    LIST_ENTRY_COLOR = (194, 237, 197)
    TXT_COLOR_INACTIVE = pygame.Color('lightskyblue3')
    TXT_COLOR_ACTIVE = pygame.Color('dodgerblue2')
        
    # Object coordinates
    # quit button
    quit_x = 400
    quit_y = 10
    
    # Localization information
    loc_x = 370
    loc_y = 80
    
    # Navigation mode buttons
    # UL of leftmost button
    mode_x = 20
    mode_y = 200
    
    # Navigation mode button size and spacing
    mode_but_size = (80,40)
    mode_but_space = mode_but_size[0] + 20
    
    # AprilTag list
    # UL of table
    ATList_x = 20
    ATList_y = 20
    
    # AprilTag list row size
    ATList_size = (3*mode_but_space - 20,20)
    
    # AprilTag list number of rows
    ATList_rows = 5
    
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
    wp_x_y = mode_y + 110
    
    # Waypoint control UL y input textbox
    wp_y_x = wp_x_x + wp_tb_size[0] + 10
    wp_y_y = wp_x_y
    
    # Waypoint control UL z input textbox
    wp_z_x = wp_y_x + wp_tb_size[0] + 10
    wp_z_y = wp_x_y
    
    # Waypoint control UL theta input textbox
    wp_theta_x = wp_z_x + wp_tb_size[0] + 10
    wp_theta_y = wp_x_y
    
    # Waypoint control UL send button
    wp_send_x = wp_theta_x + wp_tb_size[0] + 10
    wp_send_y = wp_x_y
    
    # Current waypoint x center
    curr_wp_x_x = wp_x_x + wp_tb_size[0]/2
    curr_wp_x_y = wp_x_y + 90
    
    # Current waypoint y center
    curr_wp_y_x = curr_wp_x_x + wp_tb_size[0] + 10
    curr_wp_y_y = curr_wp_x_y
    
    # Current waypoint z center
    curr_wp_z_x = curr_wp_y_x + wp_tb_size[0] + 10
    curr_wp_z_y = curr_wp_x_y
    
    # Current waypoint theta center
    curr_wp_theta_x = curr_wp_z_x + wp_tb_size[0] + 10
    curr_wp_theta_y = curr_wp_x_y
    
    # Center running error text
    err_x = width/2
    err_y = height - 10
    
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
        
    def __draw_ATList(self):
        
        # Title background
        back_surf = pygame.Surface(self.ATList_size)
        back_rect = (self.ATList_x, self.ATList_y)
        back_surf.fill(self.LIST_TITLE_COLOR)
        self.screen.blit(back_surf, back_rect)
        
        # Title text
        txt_surf = self.font.render("Visible AprilTags", True, self.WHITE)
        txt_rect = txt_surf.get_rect(center=(self.ATList_x + self.ATList_size[0]/2, self.ATList_y + self.ATList_size[1]/2))
        self.screen.blit(txt_surf, txt_rect)
        
        # Column headers background
        back_surf = pygame.Surface(self.ATList_size)
        back_rect = (self.ATList_x, self.ATList_y + self.ATList_size[1])
        back_surf.fill(self.LIST_HEADER_COLOR)
        self.screen.blit(back_surf, back_rect)
        
        # Header text
        txt_surf = self.font.render("Number", True, self.WHITE)
        txt_rect = txt_surf.get_rect(center=(self.ATList_x + self.ATList_size[0]/6, self.ATList_y + 1.5*self.ATList_size[1]))
        self.screen.blit(txt_surf, txt_rect)
        txt_surf = self.font.render("Distance", True, self.WHITE)
        txt_rect = txt_surf.get_rect(center=(self.ATList_x + self.ATList_size[0]/2, self.ATList_y + 1.5*self.ATList_size[1]))
        self.screen.blit(txt_surf, txt_rect)
        txt_surf = self.font.render("Orientation", True, self.WHITE)
        txt_rect = txt_surf.get_rect(center=(self.ATList_x + (5./6.)*self.ATList_size[0], self.ATList_y + 1.5*self.ATList_size[1]))
        self.screen.blit(txt_surf, txt_rect)
        
        # Blank rows
        for r in range(2,self.ATList_rows+2):
            back_surf = pygame.Surface(self.ATList_size)
            back_rect = (self.ATList_x, self.ATList_y + r*self.ATList_size[1])
            back_surf.fill(self.LIST_ENTRY_COLOR)
            self.screen.blit(back_surf, back_rect)
        
        # Table lines
        for c in range(1,3):
            pygame.draw.line(self.screen, self.BLACK, (self.ATList_x+(c/3.)*self.ATList_size[0],self.ATList_y+self.ATList_size[1]), (self.ATList_x+(c/3.)*self.ATList_size[0],self.ATList_y+(self.ATList_rows+2)*self.ATList_size[1]-1))
        for r in range(1,self.ATList_rows+2):
            pygame.draw.line(self.screen, self.BLACK, (self.ATList_x,self.ATList_y+r*self.ATList_size[1]), (self.ATList_x+self.ATList_size[0]-1,self.ATList_y+r*self.ATList_size[1]))
        
        global ATs
        
        # AprilTag info text
        for a in range(len(ATs)):
            txt_surf = self.font.render(str(ATs[a].num), True, self.BLACK)
            txt_rect = txt_surf.get_rect(center=(self.ATList_x + self.ATList_size[0]/6, self.ATList_y + (2.5+a)*self.ATList_size[1]))
            self.screen.blit(txt_surf, txt_rect)
            txt_surf = self.font.render(str(ATs[a].dist), True, self.BLACK)
            txt_rect = txt_surf.get_rect(center=(self.ATList_x + self.ATList_size[0]/2, self.ATList_y + (2.5+a)*self.ATList_size[1]))
            self.screen.blit(txt_surf, txt_rect)
            txt_surf = self.font.render(str(ATs[a].angle), True, self.BLACK)
            txt_rect = txt_surf.get_rect(center=(self.ATList_x + (5./6.)*self.ATList_size[0], self.ATList_y + (2.5+a)*self.ATList_size[1]))
            self.screen.blit(txt_surf, txt_rect)
        
    def __draw_drive_sel(self):
        txt_x = self.mode_x + self.mode_but_size[0]/2
        txt_y = self.mode_y + self.mode_but_size[1]/2
        for i in range(3):
   
            # Background
            back_surf = pygame.Surface(self.mode_but_size)
            back_rect = (self.mode_x + i*self.mode_but_space, self.mode_y)
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
            txt_rect = txt_surf.get_rect(center=(txt_x + i*self.mode_but_space,txt_y))
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
        
        # Draw title
        title_surf = self.font.render("Waypoint to Send", True, self.BLUE)
        title_rect = title_surf.get_rect(center=((self.wp_y_x + self.wp_z_x + self.wp_tb_size[0])/2,self.wp_x_y-40))
        self.screen.blit(title_surf, title_rect)
        
        # Draw x textbox
        x_surf = pygame.Surface(self.wp_tb_size)
        x_surf.fill(x_color)
        x_txt_surf = self.font.render(self.wp_x_txt, True, self.BLACK)
        x_rect = pygame.Rect((self.wp_x_x,self.wp_x_y), self.wp_tb_size)
        x_label_surf = self.font.render("x", True, self.BLACK)
        x_label_rect = x_label_surf.get_rect(center=(self.wp_x_x + self.wp_tb_size[0]/2, self.wp_x_y - 20))
        self.screen.blit(x_surf,x_rect)
        self.screen.blit(x_txt_surf,x_rect)
        self.screen.blit(x_label_surf,x_label_rect)
        
        # Draw y textbox
        y_surf = pygame.Surface(self.wp_tb_size)
        y_surf.fill(y_color)
        y_txt_surf = self.font.render(self.wp_y_txt, True, self.BLACK)
        y_rect = pygame.Rect((self.wp_y_x,self.wp_y_y), self.wp_tb_size)
        y_label_surf = self.font.render("y", True, self.BLACK)
        y_label_rect = y_label_surf.get_rect(center=(self.wp_y_x + self.wp_tb_size[0]/2, self.wp_y_y - 20))
        self.screen.blit(y_surf,y_rect)
        self.screen.blit(y_txt_surf,y_rect)
        self.screen.blit(y_label_surf,y_label_rect)
        
        # Draw z textbox
        z_surf = pygame.Surface(self.wp_tb_size)
        z_surf.fill(z_color)
        z_txt_surf = self.font.render(self.wp_z_txt, True, self.BLACK)
        z_rect = pygame.Rect((self.wp_z_x,self.wp_z_y), self.wp_tb_size)
        z_label_surf = self.font.render("z", True, self.BLACK)
        z_label_rect = z_label_surf.get_rect(center=(self.wp_z_x + self.wp_tb_size[0]/2, self.wp_z_y - 20))
        self.screen.blit(z_surf,z_rect)
        self.screen.blit(z_txt_surf,z_rect)
        self.screen.blit(z_label_surf,z_label_rect)
        
        # Draw theta textbox
        theta_surf = pygame.Surface(self.wp_tb_size)
        theta_surf.fill(theta_color)
        theta_txt_surf = self.font.render(self.wp_theta_txt, True, self.BLACK)
        theta_rect = pygame.Rect((self.wp_theta_x,self.wp_theta_y), self.wp_tb_size)
        theta_label_surf = self.font.render(u"\u03B8", True, self.BLACK)
        theta_label_rect = theta_label_surf.get_rect(center=(self.wp_theta_x + self.wp_tb_size[0]/2, self.wp_theta_y - 20))
        self.screen.blit(theta_surf,theta_rect)
        self.screen.blit(theta_txt_surf,theta_rect)
        self.screen.blit(theta_label_surf,theta_label_rect)
        
        # Draw send button
        text_surf = self.font.render("Send", True, self.WHITE)
        text_rect = text_surf.get_rect(center=(self.wp_send_x + self.wp_tb_size[0]/2,self.wp_send_y + self.wp_tb_size[1]/2))
        button_surf = pygame.Surface(self.wp_tb_size)
        button_surf.fill(self.GREEN)
        self.screen.blit(button_surf,(self.wp_send_x,self.wp_send_y))
        self.screen.blit(text_surf,text_rect)
        
    def __draw_curr_wp(self):
        
        # Draw title
        title_surf = self.font.render("Current Waypoint", True, self.BLUE)
        title_rect = title_surf.get_rect(center=((self.curr_wp_y_x + self.curr_wp_z_x)/2,self.curr_wp_x_y-40))
        self.screen.blit(title_surf, title_rect)
        
        # Draw x
        title_surf = self.font.render("x", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_x_x,self.curr_wp_x_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_x, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_x_x,self.curr_wp_x_y))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw y
        title_surf = self.font.render("y", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_y_x,self.curr_wp_y_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_y, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_y_x,self.curr_wp_y_y))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw z
        title_surf = self.font.render("z", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_z_x,self.curr_wp_z_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_z, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_z_x,self.curr_wp_z_y))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw theta
        title_surf = self.font.render(u"\u03B8", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_theta_x,self.curr_wp_theta_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_theta, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_theta_x,self.curr_wp_theta_y))
        self.screen.blit(txt_surf, txt_rect)

    def draw_error(self,text):
        self.screen.fill(self.WHITE)
        alt_surf= self.font.render(text, True, self.RED)
        alt_rect = alt_surf.get_rect(center=(self.width/2, self.width/2))
        self.screen.blit(alt_surf, alt_rect)
        pygame.display.flip()
        
    def __draw_error_running(self):
        if self.print_err:
            if time.time() - self.err_time >= 3:
                # Stop printing error after 3 sec
                self.__print_err = False
            else:
                text_surf = self.font.render(self.err_txt, True, self.RED)
                text_rect = text_surf.get_rect(center=(self.err_x,self.err_y))
                self.screen.blit(text_surf,text_rect)
        
    def wait_frame_rate(self):
        self.clock.tick(self.frame_rate)

    def update_screen(self):
        self.screen.fill(self.WHITE)
        self.__draw_loc()
        self.__draw_quit()
        self.__draw_drive_sel()
        self.__draw_ATList()
        self.__draw_error_running()
        if self.drive == 0:
            # Full auto mode
            self.__draw_curr_wp()
        elif self.drive == 1:
            # Waypoint mode
            self.__draw_wp_ctrl()
            self.__draw_curr_wp()
        elif self.drive == 2:
            # Manual mode
            self.__draw_man_ctrl()
        pygame.display.flip()

    def __init__(self):
        pygame.init()

        # window title 
        pygame.display.set_caption("LTA Base Station")# Font and size
        self.font = pygame.font.Font(None, 20)

        # Set the width and height of the screen [width, height]
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
        
        # Current waypoint
        self.curr_wp_x = '0'
        self.curr_wp_y = '0'
        self.curr_wp_z = '1'
        self.curr_wp_theta = '0'

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        self.frame_rate = 30
        
        # Error to be printed
        self.print_err = False
        self.err_txt = ''
        self.err_time = time.time()

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
        
def get_ats_thread(ip,port):
    server = conn(ip,port)
    global ATs
    ATs = []
    new_ATs = server.get_ATs().split(',')
    num_ATs = int(new_ATs[0])
    for a in range(num_ATs):
        ATs.append(AT(int(new_ATs[3*a+1]),float(new_ATs[3*a+2]),float(new_ATs[3*a+3])))
    server.close()
        
def man_control_thread(ip,port,dir):
    server = conn(ip,port)
    server.send_acc(dir)
    server.close()

def str_is_num(str):
    try:
        float(str)
        return True
    except ValueError:
        return False
    
def wp_control_thread(ip,port,ui):
    
    # Get coordinate strings
    x,y,z,theta = ui.wp_x_txt,ui.wp_y_txt,ui.wp_z_txt,ui.wp_theta_txt
    
    # Fill in default values for blank coordinates
    if x == '':
        x = '0'
    if y == '':
        y = '0'
    if z == '':
        z = '1'
    if theta == '':
        theta = '0'
        
    # Clear textbox selections
    ui.wp_x_active = False
    ui.wp_y_active = False
    ui.wp_z_active = False
    ui.wp_theta_active = False
    
    # Check that all entries are floats before sending
    if str_is_num(x):
        if str_is_num(y):
            if str_is_num(z):
                if str_is_num(theta):
                    print("Sending wp")
                    server = conn(ip,port)
                    server.send_wp(x, y, z, theta)
                    server.close()
                else:
                    ui.print_err = True
                    ui.err_txt = u"\u03B8" + " value is not a number"
                    ui.err_time = time.time()
                    ui.wp_theta_active = True
            else:
                ui.print_err = True
                ui.err_txt = "z value is not a number"
                ui.err_time = time.time()
                ui.wp_z_active = True
        else:
            ui.print_err = True
            ui.err_txt = "y value is not a number"
            ui.err_time = time.time()
            ui.wp_y_active = True
    else:
        ui.print_err = True
        ui.err_txt = "x value is not a number"
        ui.err_time = time.time()
        ui.wp_x_active = True
        
def get_wp_thread(ip,port,ui):
    server = conn(ip,port)
    ui.curr_wp_x, ui.curr_wp_y, ui.curr_wp_z, ui.curr_wp_theta = server.get_wp().split(',')
    server.close()
        
def send_drive_thread(ip,port,mode):
    server = conn(ip,port)
    server.send_drive(str(mode))
    server.close()
    
def terminate_server(ip,port):
    server = conn(ip,port)
    server.exit()
    server.close()
    

if __name__ == '__main__':
    
    server_ip = '127.0.0.1'

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
            
            # Only query drone for position, current waypoint, and AprilTags every 30 frames
            if server_counter == 30:
                server_thread = threading.Thread(target=get_pos_thread, args=(server_ip,server_port))
                server_thread.start()
                server_counter = 0
            elif ui.drive == 0 and server_counter == 20:
                # Waypoint only changes in auto mode
                wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                wp_thread.start()
            elif server_counter == 10:
                at_thread = threading.Thread(target=get_ats_thread, args=(server_ip,server_port))
                at_thread.start()
                
            server_counter += 1
            
            # Handle PyGame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # X button
                    running = False
                    break
                elif(event.type is MOUSEBUTTONDOWN):
                    # Mouse click
                    x,y = pygame.mouse.get_pos()
                    
                    # If in waypoint mode and click somewhere else, clear textbox selection
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
                        wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                        wp_thread.start()
                        time.sleep(0.02)
                        drive_thread = threading.Thread(target=send_drive_thread, args=(server_ip,server_port,ui.drive))
                        drive_thread.start()    
                    elif x < ui.mode_x + 180 and x > ui.mode_x + 100 and y < ui.mode_y + 40 and y > ui.mode_y:
                        # Waypoint button clicked
                        print("Waypoint")
                        ui.drive = 1
                        wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                        wp_thread.start()
                        time.sleep(0.02)
                        drive_thread = threading.Thread(target=send_drive_thread, args=(server_ip,server_port,ui.drive))
                        drive_thread.start()                     
                    elif x < ui.mode_x + 280 and x > ui.mode_x + 200 and y < ui.mode_y + 40 and y > ui.mode_y:
                        # Manual button clicked
                        print("Manual")
                        ui.drive = 2
                        time.sleep(0.02)
                        drive_thread = threading.Thread(target=send_drive_thread, args=(server_ip,server_port,ui.drive))
                        drive_thread.start()    
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
                        elif x > ui.wp_send_x and x < ui.wp_send_x + ui.wp_tb_size[0] and y > ui.wp_send_y and y < ui.wp_send_y + ui.wp_tb_size[1]:
                            # Send waypoint clicked
                            move_thread = threading.Thread(target=wp_control_thread, args=(server_ip,server_port,ui))
                            move_thread.start()
                            time.sleep(0.02)
                            wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                            wp_thread.start()                            
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
                        move_thread = threading.Thread(target=wp_control_thread, args=(server_ip,server_port,ui))
                        move_thread.start()
                        time.sleep(0.02)
                        wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                        wp_thread.start()
                    elif ui.wp_x_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_x_txt = ui.wp_x_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_x_active = False
                            ui.wp_y_active = True
                        else:
                            ui.wp_x_txt += event.unicode
                    elif ui.wp_y_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_y_txt = ui.wp_y_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_y_active = False
                            ui.wp_z_active = True
                        else:
                            ui.wp_y_txt += event.unicode
                    elif ui.wp_z_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_z_txt = ui.wp_z_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_z_active = False
                            ui.wp_theta_active = True
                        else:
                            ui.wp_z_txt += event.unicode
                    elif ui.wp_theta_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_theta_txt = ui.wp_theta_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_theta_active = False
                            ui.wp_x_active = True
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


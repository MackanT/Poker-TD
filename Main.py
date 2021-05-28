
from tkinter import *
import PIL
import threading
import numpy as np
from assets.UI import *
from assets.Tiles import Tile
from assets.Enemies import Enemy, Projectile
import simpleaudio as sa
import csv
import os

# Game Design Dimensions

dimension_screen_attempt = 1000 # Dimension game will try to achieve
dimension_screen_border = 20 # Width around playing field
dimension_info_width = 296 # Width of information bar 256px + 2pcs dimension_screen_border


# Hard coded game parameters
game_tile_number = 15 
game_tile_width = int((dimension_screen_attempt - 2*dimension_screen_border)
                       /game_tile_number)

dimension_screen = game_tile_number * game_tile_width
dimension_info_cards_y = dimension_screen - 128 - 2*dimension_screen_border
dimension_window_width = (dimension_screen + 2*dimension_screen_border 
                          + dimension_info_width)
dimension_window_height = dimension_screen + 2*dimension_screen_border

button_fraction = 1/3


# Eventually move over to file that is read ?
color = ['#EBE8E0','#A8BBB0','#0A0A00','#A2252A'] # Color Pallette
card_suite = ['heart', 'spade', 'diamond', 'club']

class Main():

    def __init__(self):

        # Screen Settings
        self.root = Tk()
        self.root.winfo_toplevel().geometry("{}x{}".format(dimension_screen 
                                + dimension_screen_border, dimension_screen 
                                + 2*dimension_screen_border))
        self.root.configure(bg=color[3])
        self.root.resizable(False, False)
        self.root.title('Poker TD - The Play')
        self.cwd = os.getcwd()

        self.canvas_info = Canvas(self.root, width = dimension_info_width, 
                                  height = dimension_screen, bg=color[0], 
                                  bd=0, highlightthickness=0)
        self.canvas_game = Canvas(self.root, width = dimension_screen, 
                                  height = dimension_screen, bg=color[0], 
                                  bd=0, highlightthickness=0)

        self.canvas_game.place(x=dimension_screen_border, 
                               y=dimension_screen_border, anchor=NW)
        self.canvas_info.place(x=dimension_screen + dimension_screen_border, 
                               y=dimension_screen_border, anchor=NW)
        
        # -1 pre, 0 start screen, 1 in-game
        self.state_game = -1 

        self.tile_previous_selected = [-5, -5]
        self.tile_current_selected = [-2,-2]
        self.tile_previous_marked = [-5, -5]
        self.tile_current_marked = [-2,-2]
        self.tile_counter = -1

        self.odds_base = 10
        self.odds_current = 0

        self.draws_base = 1
        self.draws_current = self.draws_base

        self.turn_time_base = 10
        self.turn_time_current = self.turn_time_base

        self.current_wave = 1
        self.current_wave_built = False
        self.wave_in_progress = False

        self.mobs_base = 10
        self.mobs_current = 0

        self.current_hand = []
        self.current_towers = []
        
        self.current_enemies = np.empty(self.mobs_base, dtype=Enemy)
        for i in range(self.mobs_base):
            self.current_enemies[i] = Enemy(canvas=self.canvas_game, id=i)

        self.current_projectiles = []
        self.tile_path_x = []
        self.tile_path_y = []

        # Sound
        self.sound_home_button = self.load_sound('home_screen')
        self.sound_place_tile = self.load_sound('place')
        self.sound_place_fail = self.load_sound('place_fail')
        self.sound_all_cards = self.load_sound('full_cards')
        self.sound_coin_use = self.load_sound('coin_use')

        self.def_proj = self.load_image('standard', folder='projectile')

        # Game Files
        file_name = self.cwd + '\\assets\\towers.csv'
        self.tower_stats = np.genfromtxt(file_name, delimiter=';', dtype=("|U10", int, int, float, float, "|U15", "|U28"), skip_header=1)

        # Event Binders canvas_game
        self.canvas_game.bind('<Motion>', self.moved_mouse)
        self.canvas_game.bind('<Double-Button-1>', self.place_tower)
        self.canvas_game.bind('<Button-1>', self.left_click)
        # self.canvas_game.bind('<Button-2>', self.middle_click)
        self.canvas_game.bind('<Button-3>', self.right_click)
        self.root.bind('<KeyPress>', self.key_pressed)
        self.root.bind('<KeyRelease>', self.key_released)

        # Event Binders canvas_info
        self.canvas_info.bind('<Motion>', self.deselect_tiles)


        self.time_counter = 0

        self.start_timer()

        ## Startup Screen
        self.create_startup()

        self.mainloop()


    ## Load Images + Sound

    def load_image(self, file_name, dim=None, dims=None, folder='tower\\tile'):

        f = self.cwd + '\\art\\' + folder + '\\' + file_name + '.png'
        image = PIL.Image.open(f)
        if dim:
            if dims != None:
                image = image.resize((dims[0], dims[1]), PIL.Image.NEAREST)
            else:
                image = image.resize((dim, dim), PIL.Image.NEAREST)
        return PIL.ImageTk.PhotoImage(image)

    def load_sound(self, file_name):
        """ loads specified sound file as wave object """
        return sa.WaveObject.from_wave_file(self.cwd 
                        + '\\sound\\' + file_name + '.wav')

    def play_sound(self, file_name):
        """ Plays specified sound file """ 
        if file_name == 'home_button':
            self.sound_home_button.play()
        elif file_name == 'place_tower':
            self.sound_place_tile.play()
        elif file_name == 'place_fail':
            self.sound_place_fail.play()
        elif file_name == 'all_cards':
            self.sound_all_cards.play()
        elif file_name == 'coin_use':
            self.sound_coin_use.play()

    ## Background Items - Timers

    def start_timer(self):
        threading.Timer(0.05, self.start_timer).start()
        if self.state_game == 1:

            self.time_counter += 1

            if self.wave_in_progress:
                if self.time_counter%2 == 0:
                    self.update_enemies()
                self.shoot_enemies()
                self.update_projectiles()
            
            ## Every Second
            if self.time_counter%20 == 0:
                if self.turn_time_current == 0:
                    if not self.wave_in_progress: self.new_wave()
                    else:
                        self.spawn_mobs()
                else:   
                    self.turn_time_current -= 1
                    self.canvas_game.itemconfigure(self.timer_visual, text=str(self.turn_time_current))

    def reset_timer(self):
        self.turn_time_current = self.turn_time_base


    ## Home Screen Functions

    def home_button_sound(self, event):
        if (event.x > dimension_screen*button_fraction):
            for i in self.startup_screen:
                if i.check_pos(event.x, event.y):
                    self.play_sound('home_button')

    def home_button_functions(self):
        for i in self.startup_screen:
            if i.get_state():
                if (i.get_y() == 0):
                    print('Starting!')
                    self.gen_board()
                elif (i.get_y() == 200):
                    print('About')
                else:
                    print('Quit')

    def create_startup(self):

        self.startup_screen = []

        b_names = ['play', 'about', 'quit']
        b_num = len(b_names)

        b_height = int(dimension_screen / b_num)
        b_width = int(dimension_screen*button_fraction)

        ## Imagery
        image_filename = self.cwd + "\\art\\startup\\main_img_border.png"
        self.startup_img = PhotoImage(file=image_filename)

        for i, name in enumerate(b_names):
            self.startup_screen.append(Home_Button(self.canvas_game, x=dimension_screen-b_width, y=i*b_height, w=b_width, h=b_height, col=color, image=name))

        self.canvas_game.create_image(5, 50, anchor=NW, image = self.startup_img)
        self.state_game = 0


    ## User Input

    def key_pressed(self, event):
        if self.state_game == 0: return
        if event.keycode == 17:
            # When Ctrl pressed, attempts to highligt  tile[x, y]
            mouse_x = self.root.winfo_pointerx() - self.root.winfo_rootx() - dimension_screen_border
            mouse_y = self.root.winfo_pointery() - self.root.winfo_rooty() - dimension_screen_border
            x = int(mouse_x/game_tile_width)
            y = int(mouse_y/game_tile_width)

            if not self.check_tile(x, y): return

            self.highlight_tower_range(x, y)
        
    def key_released(self, event):
        if self.state_game == 0: return
        if event.keycode == 17:
            self.unhighlight_tower_range(event)

    def highlight_tower_range(self, x, y):

        self.tile_current_marked = [x, y]

        if self.tile_current_marked != self.tile_previous_marked:      

            tile = self.get_tile(x, y)
            if tile.get_path() or tile.get_buildable(): return

            radius = tile.get_range()
            tile_w = tile.get_w()
            tile_x = int((tile.get_x()+1/2)*tile_w)
            tile_y = int((tile.get_y()+1/2)*tile_w)

            x0, x1, y0, y1 = self.__draw_circle_radius(tile_x, tile_y, radius*tile_w)
            self.canvas_game.itemconfigure(self.tower_radius_marker, state='normal')
            self.canvas_game.coords(self.tower_radius_marker, x0, y0, x1, y1)
            self.update_tile_information(x,y)
            self.tile_previous_marked = [x, y]
        else:
            self.get_tile(x, y).highlight_tile(False)

    def unhighlight_tower_range(self, event):
        """ Hides radius marker when ctrl is released """
        self.canvas_game.itemconfigure(self.tower_radius_marker, state='hidden')
        self.tile_previous_marked = [-5, -5]
        self.tile_current_marked = [-2,-2]

    def moved_mouse(self, event):
        """ Fired by mouse movement, calls appropriate function depending on game state """
        if (self.state_game == 0): self.home_button_sound(event)
        elif self.state_game == 1: self.select_tile(event)

    def left_click(self, event):

        # print('---')
        # print(event.x, event.y)
        if self.state_game == 0: self.home_button_functions()
        elif self.state_game == 1:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                tile = self.current_board[x][y]
                # print(tile.get_x()*game_tile_width, tile.get_y()*game_tile_width)
                    
    def right_click(self, event):
        # Break out if not in game
        if self.state_game != 1: return
    
        x, y = self.find_tile(event)
        if self.check_tile(x, y):
            tile = self.get_tile(x,y)
            if not tile.get_path() and not tile.get_buildable():
                tile.switch_selected()



    ## Tower Functions

    def select_tile(self, event):
        """ Checks if current position is ok and sets its state accordingly"""
        
        x, y = self.find_tile(event)
        if not self.check_tile(x, y): return

        self.tile_current_selected = [x, y]
        if self.tile_current_selected == self.tile_previous_selected: return

        self.get_tile(x,y).highlight_tile(True)
        tile = self.current_board[self.tile_previous_selected[0]][self.tile_previous_selected[1]]
        tile.highlight_tile(False)
        self.update_tile_information(x,y)
        self.tile_previous_selected = [x, y]

    def deselect_tiles(self, event):
        """ Deselects current tile """
        # Break out if not in game
        if self.state_game != 1: return
        tile = self.current_board[self.tile_current_selected[0]][self.tile_current_selected[1]]
        tile.highlight_tile(False)
        self.tile_previous_selected = [-1, -1]

    def find_tile(self, event):
        """ Finds x,y position of currently hoovered over tile """
        x = int(event.x/game_tile_width)
        y = int(event.y/game_tile_width)
        return x, y

    def get_tile(self, x, y):
        """ Returns reference to requested tile x,y """
        return self.current_board[x][y]

    def check_tile(self, x, y):
        ### Unneccessary?
        """ Returns true if marked area is a viable tile """
        if (x < 0 or x > game_tile_number - 1): return False
        if (y < 0 or y > game_tile_number - 1): return False
        return True

    def get_card_name(self, suite, number):
        """ Returns expected name of single tower """
        return str(self.tower_stats[number][6])+' of '+suite.capitalize()+'s'

    def place_tower(self, event):
        """ Attempts to create tower at mouse clicked tile """

        if self.wave_in_progress: return

        if self.state_game == 1 and self.tile_counter < 4:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                tile = self.get_tile(x,y)

                if not tile.get_buildable():
                    self.play_sound('place_fail')
                    return

                stats = self.find_tower(self.gen_card())

                tile.set_tower( 
                               number=stats[0],
                               name=stats[6],   
                               attack_min=stats[1], 
                               attack_max=stats[2],
                               range=stats[3], 
                               speed=stats[4], 
                               ability=stats[5]
                                )

                self.tile_counter += 1
                self.current_hand.append(tile)
                self.play_sound('place_tower')
                self.update_tile_information(x, y)
                self.update_tile_hand()
                self.determine_best_hand()

        elif self.tile_counter == 4: self.play_sound('place_fail')

    def redraw_tower(self):
        """ Rerandomizes selected towers"""

        if self.wave_in_progress: return

        # Avoid redraw if not all cards are played or if no more draws
        if self.tile_counter != 4: return
        if self.draws_current == 0: return

        iter = []
        for i, tile in enumerate(self.current_hand):
            if tile.get_selected(): iter.append(i)
        
        for i in iter:
            tile = self.current_hand[i]

            stats = self.find_tower(self.gen_card())

            tile.set_tower( 
                number=stats[0],
                name=stats[6],   
                attack_min=stats[1], 
                attack_max=stats[2],
                range=stats[3], 
                speed=stats[4], 
                ability=stats[5]
            )
            
            # self.play_sound('place_tower') # Tower redraw sound....
            self.update_tile_information(0, 0, tile=tile)
            self.update_tile_hand(pos=i)
        self.determine_best_hand()
        self.draws_current -= 1
        self.__update_draw_counter()

    def find_tower(self, card_type):
        for i in self.tower_stats:
            if i[0] == card_type:
                return i
                break

    def build_tower(self, override=False):
        """ Converts single towers to actual tower """
        if self.tile_counter != 4 and not override: return
        if self.current_wave_built: return

        if override and len(self.current_hand) == 0: return
        card_type = self.determine_best_hand(type=True)

        x = self.current_hand[0].get_x()
        y = self.current_hand[0].get_y()
        
        for tile in self.current_hand:
            tile.remove_tower()
            tile.deselect()
        
        stats = self.find_tower(card_type)
        
        self.current_board[x][y].set_tower(                                         
                                           number=stats[0],
                                           name=stats[6],   
                                           attack_min=stats[1], 
                                           attack_max=stats[2],
                                           range=stats[3], 
                                           speed=stats[4], 
                                           ability=stats[5]
                                           )

        self.tile_counter = -1
        self.odds_current = 0
        self.current_hand.clear()

        self.__reset_best_hand_position(new_turn=True)
        self.__update_gold_counter()
        self.current_wave_built = True

        self.current_towers.append(self.current_board[x][y])

        if self.turn_time_current > 0:
            self.turn_time_current = 0
            self.canvas_game.itemconfigure(self.timer_visual, text=str(self.turn_time_current))
            self.new_wave()

    ## Game Board Functions

    def gen_board(self):
        
        self.canvas_game.delete('all')
        self.root.winfo_toplevel().geometry("{}x{}".format(
                                dimension_screen + dimension_info_width 
                                + 2*dimension_screen_border, dimension_screen 
                                + 2*dimension_screen_border))

        self.current_board = [[Tile(self.canvas_game, x=i, y=j, 
                                    w=game_tile_width) 
                                    for j in range(game_tile_number)] 
                                    for i in range(game_tile_number)]
            
        self.load_map(1)

        self.tower_radius_marker = self.canvas_game.create_oval(0,0,100,100, width=4, fill=None, state='hidden')

        self.wave_counter_visual = self.canvas_game.create_text(dimension_screen_border, dimension_screen_border, fill='White', anchor=NW, text='Wave: {}'.format(self.current_wave), font=('Dutch801 XBd BT', 28))

        self.timer_visual = self.canvas_game.create_text(dimension_screen_border, 3*dimension_screen_border, fill='White', anchor=NW, text=str(self.turn_time_base), font=('Dutch801 XBd BT', 28))

        self.state_game = 1
        self.__create_tile_information()

    def load_map(self, map_num):
        """ Map to load - Begin with 1 and call at beginning of every game """
        counter = 0
        with open(self.cwd + '\\assets\\maps.csv') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                if counter == map_num: 
                    break
                else: counter += 1

        for tile in row:
            tile = int(tile)
            x = tile%game_tile_number - 1
            y = int(tile/game_tile_number)
            self.tile_path_x.append(y)
            self.tile_path_y.append(x)
            self.get_tile(x,y).set_path()
        
        self.tile_path_x = np.array(self.tile_path_x)*game_tile_width + int(game_tile_width*0.5)
        self.tile_path_y = np.array(self.tile_path_y)*game_tile_width + int(game_tile_width*0.5)

        # for i, x in enumerate(self.tile_path_x):
        #     self.canvas_game.create_text(x, self.tile_path_y[i], text=i)

    def new_wave(self):
        
        self.wave_in_progress = True
        if not self.current_wave_built: self.build_tower(override=True)
        self.current_wave += 1
        self.draws_current = self.draws_base
        self.__update_draw_counter()

    def end_wave(self):

        self.wave_in_progress = False
        self.current_wave_built = False
        self.turn_time_current = self.turn_time_base
        self.mobs_current = 0
        self.canvas_game.itemconfigure(self.wave_counter_visual, text='Wave: {}'.format(self.current_wave))

    def spawn_mobs(self):
        
        if self.mobs_current < self.mobs_base:

            slime_img = self.load_image('slime', folder='enemies')

            goal = [self.tile_path_x[0], self.tile_path_y[0]]
            self.current_enemies[self.mobs_current].reset_mob(x=self.tile_path_x[0]-game_tile_width, y=self.tile_path_y[0], 
                                    hp=150, speed=8, goal=goal,image=slime_img)
            self.mobs_current += 1

    def update_projectiles(self):
        for i, e in enumerate(self.current_projectiles):
            hit, kill = e.move()
            if kill:
                self.__change_gold(1)
                self.remove_enemy(e.get_target())
            if hit: 
                self.current_projectiles.pop(i)
                e.remove()

    def update_enemies(self):

        if self.wave_over(): return

        for e in self.current_enemies:
            
            if e.get_alive():
                new_goal = e.move()
                
                if new_goal:
                    index = e.get_goal() + 1
                    if index == 75:
                        self.__change_gold(-2)
                        self.remove_enemy(e)
                    else:
                        e.set_goal([self.tile_path_x[index], self.tile_path_y[index]])

    def shoot_enemies(self):

        # Returns if no enemies have yet been spawned
        if self.wave_over(): return

        mobs = self.get_enemy_locations()
        for tower in self.current_towers:
            if tower.fire_count_down():

                tower_pos = np.array([tower.get_x() + 0.5, tower.get_y() + 0.5])
                tower_pos *= game_tile_width
                tower_range = tower.get_range()*game_tile_width

                dist = np.linalg.norm(mobs - tower_pos, axis=1)

                for i, distance in enumerate(dist):
                    if distance <= tower_range and self.current_enemies[i].get_alive():
                        self.fire(tower, self.current_enemies[i])
                        break

    def remove_enemy(self, enemy):
        enemy.remove()
        if self.wave_over():
            for e in self.current_projectiles:
                e.remove()
            self.end_wave()

    def wave_over(self):
        """ Returns true if all enemies are not beaten/fled """
        
        if self.mobs_current > self.mobs_base: return False

        for e in self.current_enemies:
            if e.get_alive(): return False
        return True

    def get_enemy_locations(self):

        num_mobs = len(self.current_enemies)
        pos_mobs = np.zeros((num_mobs, 2))

        for i, e in enumerate(self.current_enemies):
            pos_mobs[i, 0] = e.get_x()
            pos_mobs[i, 1] = e.get_y()
        
        return pos_mobs

    def fire(self, tower, enemy):
        self.current_projectiles.append(Projectile(canvas=self.canvas_game, x=int((tower.get_x()+0.5)*game_tile_width), y=int((tower.get_y()+0.5)*game_tile_width), damage=tower.get_damage(), speed=16, target=enemy, image=self.def_proj))
        tower.fire_reset()

    ## Tile Information Functions

    def update_tile_information(self, x, y, tile=None):
        if tile == None:
            tile = self.get_tile(x,y)

        img = tile.get_image()
        self.info_tile_image_file = self.load_image(img, dim=256)
        self.canvas_info.itemconfig(self.info_tile_image, 
                                    image=self.info_tile_image_file)
        self.canvas_info.itemconfig(self.info_tile_name, text=tile.get_name())

        stats = tile.get_stats()
        for i, stat in enumerate(stats):
            self.canvas_info.itemconfig(int(self.info_tile_stat_values[i]), 
                                        text=stat)

    def update_tile_hand(self, pos=None):
        if pos == None:
            pos = self.tile_counter

        short_name = self.get_short_name(self.current_hand[pos])
        suite = self.current_hand[pos].get_suite_number()

        self.canvas_info.itemconfigure(self.tile_info_hand_cards_values[pos], text=short_name)
        self.canvas_info.itemconfigure(self.tile_info_hand_cards_suites[pos], image=self.tile_info_hand_symbol[suite], state='normal')
        
    def __create_tile_information(self):

        self.info_tile_image_file = self.load_image('blank')
        self.info_tile_image = self.canvas_info.create_image(
                            dimension_screen_border, dimension_screen_border, 
                            anchor=NW, image=self.info_tile_image_file)

        self.info_tile_name = self.canvas_info.create_text(
                            dimension_screen_border, 300, anchor=NW, 
                            text='', font=('Dutch801 XBd BT', 22))

        stats = ['Attack', 'Speed', 'Range', 'Ability']
        self.info_tile_stat_name = []

        for i, stat in enumerate(stats):
            self.info_tile_stat_name.append(self.canvas_info.create_text(
                            dimension_screen_border, 320 + 40*(i+1), 
                            anchor=NW, text=stat+': ', font=('Dutch801 XBd BT', 15)))
        
        stats = ['', '', '', '']
        self.info_tile_stat_values = []
        for i, stat in enumerate(stats):
            self.info_tile_stat_values.append(self.canvas_info.create_text(
                            dimension_screen_border + 80, 320 + 40*(i+1), 
                            anchor=NW, text=stat, font=('Dutch801 XBd BT', 15)))

        self.__create_tile_information_current_hand()
        self.__create_tile_information_buttons()

        self.__reset_best_hand_position()

        self.current_gold = 100 # Temporarily very high!
        self.info_tile_image_gold = self.load_image('coin', folder='misc')
        self.info_tile_gold_image = self.canvas_info.create_image(
                            dimension_screen_border, 600, 
                            anchor=W, image=self.info_tile_image_gold)
        self.info_tile_gold_number = self.canvas_info.create_text(
                            2*dimension_screen_border, 600, anchor=W, 
                            text=self.current_gold, font=('Dutch801 XBd BT', 22))
        
        self.info_tile_image_draw = self.load_image('draw', folder='misc')
        self.info_tile_draw_image = self.canvas_info.create_image(
                            dimension_screen_border, 660, 
                            anchor=W, image=self.info_tile_image_draw)
        self.info_tile_draw_number = self.canvas_info.create_text(
                            2*dimension_screen_border, 660, anchor=W, 
                            text=self.draws_current, font=('Dutch801 XBd BT', 22))

        

        # Temporary debugging!
        self.canvas_info.create_text(
                            dimension_screen_border, 700, anchor=W, 
                            text='Current Odds:', font=('Dutch801 XBd BT', 16))
        self.info_tile_odds_number = self.canvas_info.create_text(
                            9*dimension_screen_border, 700, anchor=W, 
                            text=self.odds_current, font=('Dutch801 XBd BT', 16))

    def __create_tile_information_current_hand(self):

        self.tile_info_hand_title = self.canvas_info.create_text(
                            dimension_info_width/2, dimension_info_cards_y-80, 
                            text=' - Current Hand - ', anchor=N, 
                            font=('Dutch801 XBd BT', 20))

        # Loads blank card backgrounds
        self.tile_info_hand_cards = []
        self.tile_info_hand_image = self.load_image('card', folder='misc')
        for i in range(5):
            self.tile_info_hand_cards.append(
                                self.canvas_info.create_image(0, 0, anchor=NW, 
                                image=self.tile_info_hand_image))

        # Prints card number on card
        self.tile_info_hand_cards_values = []
        for i in range(5):
            self.tile_info_hand_cards_values.append(
                                self.canvas_info.create_text(0, 0, text='',
                                anchor=CENTER, font=('Dutch801 XBd BT', 28)))
        
        # Loads 4 suite symbols
        self.tile_info_hand_symbol = []
        for name in card_suite:
            self.tile_info_hand_symbol.append(
                                self.load_image(name + '_marker', 
                                folder='misc'))
        
        # Prints 4 suite symbols
        self.tile_info_hand_cards_suites = []
        for i in range(5):
            self.tile_info_hand_cards_suites.append(
                                self.canvas_info.create_image(0, 0, 
                                anchor=CENTER, image=None))

        # Placeholder for 'All Cards!" text when all cards can be used to build tower
        self.tile_info_hand_all_cards = self.canvas_info.create_text(
                                dimension_info_width/2, dimension_info_cards_y 
                                + 128 - 50, text='', anchor=N, 
                                font=('Dutch801 XBd BT', 20))

    def __create_tile_information_buttons(self):
        
        self.tile_info_button_redraw = Button(self.canvas_info, text='Draw', command=self.redraw_tower, font=('Dutch801 XBd BT', 15))
        self.tile_info_button_redraw.place(x=dimension_info_width - dimension_screen_border/2, y=dimension_screen-dimension_screen_border, height=35, width=128, anchor=SE)

        self.tile_info_button_build = Button(self.canvas_info, text='Play', command=self.build_tower, font=('Dutch801 XBd BT', 15))
        self.tile_info_button_build.place(x=dimension_screen_border/2, y=dimension_screen-dimension_screen_border, height=35, width=128, anchor=SW)

        self.tile_info_button_tip = Button(self.canvas_info, text='Tip', command=self.increase_odds, font=('Dutch801 XBd BT', 15))
        self.tile_info_button_tip.place(x=dimension_info_width - dimension_screen_border/2, y=600, height=35, width=128, anchor=E)

        self.tile_info_button_draw = Button(self.canvas_info, text='Draw', command=self.increase_draws, font=('Dutch801 XBd BT', 15))
        self.tile_info_button_draw.place(x=dimension_info_width - dimension_screen_border/2, y=660, height=35, width=128, anchor=E)

    def gen_card(self):

        # Attempts to increase likelyhood that all further cards are of the same suite
        weights = np.ones(4)*self.odds_base
        if self.tile_counter >= 0:
            current_suite = self.current_hand[0].get_suite_number()
            weights[current_suite] += self.odds_current
        weights *= 1 / np.sum(weights)
        suite_num = np.random.choice([0, 1, 2, 3], p=weights)

        # Increases likelyhood of getting same card number as previous with odds and likelyhood of getting +-1 with half odds
        weights = np.ones(13)*self.odds_base
        if self.tile_counter >= 0:
            for tile in self.current_hand:
                i = tile.get_card_number()
                weights[i] += self.odds_current
                weights[(i+1)%13] += self.odds_current/2
                weights[(i-1)%13] += self.odds_current/2
        weights *= 1 / np.sum(weights)
        number = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], p=weights)

        return str(suite_num) + '_11_' + str(number)

    def __reset_best_hand_position(self, new_turn=False):

        for i in range(5):
            self.canvas_info.coords(self.tile_info_hand_cards[i], 59*i, dimension_info_cards_y + 30 - 50)
            self.canvas_info.coords(self.tile_info_hand_cards_values[i], 59*(i+1/2), dimension_info_cards_y + 70 - 50)
            self.canvas_info.coords(self.tile_info_hand_cards_suites[i], 59*(i+1/2), dimension_info_cards_y + 128 - 50)
        self.canvas_info.itemconfigure(self.tile_info_hand_all_cards, text='')

        if not new_turn: return
        for i in range(5):
            self.canvas_info.itemconfigure(self.tile_info_hand_cards_values[i], text='')
            self.canvas_info.itemconfigure(self.tile_info_hand_cards_suites[i], image=None, state='hidden')

    def __update_best_hand_indicator(self):
        self.canvas_info.itemconfigure(self.tile_info_hand_all_cards, text='All Cards!')

    def __update_best_hand_position(self, index):

        self.__reset_best_hand_position()

        for i in index:
            self.canvas_info.move(self.tile_info_hand_cards[i], 0, -30)
            self.canvas_info.move(self.tile_info_hand_cards_values[i], 0, -30)
            self.canvas_info.move(self.tile_info_hand_cards_suites[i], 0, -30)

    def __update_gold_counter(self):
        self.canvas_info.itemconfigure(self.info_tile_gold_number, text=str(self.current_gold))
        self.canvas_info.itemconfigure(self.info_tile_odds_number, text=str(self.odds_current))

    def __update_draw_counter(self):
        self.canvas_info.itemconfigure(self.info_tile_draw_number, text=str(self.draws_current))
        self.__update_gold_counter()

    def __change_gold(self, amount):
        self.current_gold += amount
        self.play_sound('coin_use')
        if self.current_gold <= 0:
            print('Game Over!')
        self.__update_gold_counter()

    def increase_odds(self):
        if not self.wave_in_progress: return

        if self.current_gold <= 10:
            print('Inusfficient Gold!')
            return
        
        self.odds_current += 2
        self.__change_gold(-10)

    def increase_draws(self):
        if not self.wave_in_progress: return

        if self.current_gold <= 30:
            print('Inusfficient Gold!')
            return

        self.draws_current += 1
        self.__change_gold(-30)
        self.__update_draw_counter()

    ## Determine Current Hand

    def determine_best_hand(self, type=False):
        cards = []
        for tile in self.current_hand: cards.append(tile.get_card_number())
        seen, dupes = self.__best_card_multiple(cards)

        playable_hand = [0 for i in range(12)]
        playable_hand[1] = self.__n_of_a_kind(seen, 5)
        if playable_hand[1]: 
            playable_hand[0] = self.__is_flush()
        playable_hand[7] = self.__is_straigt(cards)
        if playable_hand[7]: 
            playable_hand[3] = self.__is_flush()
        if playable_hand[3]: 
            playable_hand[2] = self.__is_royal(cards)
        playable_hand[4] = self.__n_of_a_kind(seen, 4)
        playable_hand[5] = self.__full_house(seen)
        playable_hand[6] = self.__is_flush()
        playable_hand[8] = self.__n_of_a_kind(seen, 3)
        playable_hand[9] = self.__two_pairs(seen)
        playable_hand[10] = self.__n_of_a_kind(seen, 2)
        playable_hand[11] = 1

        for i, state in enumerate(playable_hand):
            
            if type and state == 1: 
                if i in [0, 2, 6]: number = self.current_hand[0].get_suite_number()
                elif i == 1: number = cards[0]
                elif i in [3, 5]: number = max(cards) # Full house doesnt print 3 type
                elif i in [4, 8, 10]: number = dupes[0]
                elif i in [5, 9]: number = max(dupes) # Doesnt set ace as high... [9]
                else: 
                    number = self.__best_card_single(cards)
                    return str(self.current_hand[number].get_suite_number()) + '_' + str(i) + '_' + str(cards[number])
                
                return str(i) + '_' + str(number)

            if state == 1:
                if i in [0, 1, 2, 3, 5, 6, 7]:
                    self.__update_best_hand_position([0,1,2,3,4])
                    self.__update_best_hand_indicator()
                    self.play_sound('all_cards')
                    return
                else:
                    self.__update_best_hand_position(self.__index_of_dupes(cards, dupes))
                    return
        self.__update_best_hand_position([self.__best_card_single(cards)])

    def __best_card_single(self, cards):
        """ Returns index of highest card, Ace, King, Queen.... """
        if 0 in cards: return cards.index(0)
        else: return cards.index(max(cards))
            
    def __best_card_multiple(self, cards):

        seen = {}
        dupes = []

        for x in cards:
            if x not in seen:
                seen[x] = 1
            else:
                if seen[x] == 1:
                    dupes.append(x)
                seen[x] += 1   

        return seen, dupes

    def __index_of_dupes(self, cards, dupes):
        dupe_list = []
        for dupe in dupes:
            index_pos_list = [ i for i in range(len(cards)) if cards[i] == dupe]
            for i in index_pos_list:
                dupe_list.append(i)
        return dupe_list

    def __n_of_a_kind(self, cards, n):
        for x in cards:
            if cards[x] == n: return 1
        return 0
    
    def __full_house(self, cards):
         
        three_pair = self.__n_of_a_kind(cards, 3)
        if three_pair == False: return 0

        for x in cards:
            if cards[x] == 2: return 1
        return 0

    def __two_pairs(self, cards):
        pair_counter = 0
        for x in cards:
            if cards[x] == 2:
                pair_counter += 1
        if pair_counter == 2: return 1
        else: return 0

    def __is_flush(self):
        """ Checks if flush returns T/F """
        if self.tile_counter < 4: return 0

        suite = self.current_hand[0].get_suite_number()
        for i in range(1, len(self.current_hand)):
            if suite != self.current_hand[i].get_suite_number(): return 0
        return 1
    
    def get_short_name(self, tile):
        """ converts from tile number '0, 1, ..., 11, 12' to 'A, 2, ... , Q, K' """
        number = tile.get_card_number()
        if number in [0, 10, 11, 12]:
            for i in self.tower_stats:
                if i[0] == '0_11_' + str(number):
                    return i[6][0]
        else:
            return str(number + 1)

    def __is_straigt(self, cards):
        """ Checks if straight returns T/F """
        if self.tile_counter < 4: return 0

        new_cards = cards.copy()
        new_cards.sort(reverse=True)
        if new_cards[0] == 12 and new_cards[-1] == 0:
            new_cards.insert(0, 13)

        for i in range(1, 5):
            if new_cards[i-1] - new_cards[i] != 1: return 0
        return 1

    def __is_royal(self, cards):
        """ Checks ace high returns T/F """
        if self.tile_counter < 4: return 0

        if 0 in cards: return 1
        else: return 0



    # Help Functions

    def __draw_circle_radius(self, x, y, r):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return x0, x1, y0, y1


    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()

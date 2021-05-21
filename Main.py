from tkinter import *
import threading
import numpy as np
from assets.UI import *
from assets.Tiles import *
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

        self.tile_previous = [0, 0]
        self.tile_current = [-2,-2]
        self.tile_counter = -1

        self.current_hand = []

        # Sound
        self.sound_home_button = self.load_sound('home_screen')
        self.sound_place_tile = self.load_sound('place')
        self.sound_place_fail = self.load_sound('place_fail')
        self.sound_all_cards = self.load_sound('full_cards')

        # Game Files
        file_name = self.cwd + '\\assets\\towers.csv'
        self.tower_stats = np.genfromtxt(file_name, delimiter=';', dtype=(int, int, int, float, "|U10", "|U10", "|U10"), skip_header=1)


        # Event Binders canvas_game
        self.canvas_game.bind('<Motion>', self.moved_mouse)
        self.canvas_game.bind('<Double-Button-1>', self.build_tile)
        self.canvas_game.bind('<Button-1>', self.left_click)
        # self.canvas_game.bind('<Button-2>', self.middle_click)
        self.canvas_game.bind('<Button-3>', self.right_click)

        # Event Binders canvas_info
        self.canvas_info.bind('<Motion>', self.deselect_tiles)


        #self.startTimer()

        ## Startup Screen
        self.create_startup()

        self.mainloop()

    def load_image(self, file_name, tile=True, folder=None):

        if folder:
            f = self.cwd + '\\art\\' + folder + '\\' + file_name + '.png'
        elif tile:
            f = self.cwd + '\\art\\tower\\tile\\' + file_name + '.png'
        else:
            f = self.cwd + '\\art\\tower\\thumbnail\\' + file_name + '.png'
        return PhotoImage(file=f)    

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

    def start_timer(self):
        threading.Timer(1.0, self.startTimer).start()
        if self.booleanGameActive == True:
            self.currentTime += 1
            #self.canvas_game.itemconfig(self.timeMarker, text=str(self.currentTime))

    def reset_timer(self):
        self.currentTime = 0

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

    def moved_mouse(self, event):
        """ Fired by mouse movement, calls appropriate function depending on game state """
        if (self.state_game == 0): self.home_button_sound(event)
        elif self.state_game == 1: self.select_tile(event)

    def select_tile(self, event):
        """ Checks if current position is ok and sets its state accordingly"""
        x, y = self.find_tile(event)
        if not self.check_tile(x, y): return

        self.tile_current = [x, y]
        if self.tile_current != self.tile_previous:
            self.get_tile(x,y).highlight_tile(True)
            self.current_board[self.tile_previous[0]][self.tile_previous[1]].highlight_tile(False)
            self.update_tile_information(x,y)
            self.tile_previous = [x, y]

    def deselect_tiles(self, event):
        """ Deselects current tile """
        # Break out if not in game
        if self.state_game != 1: return
        self.current_board[self.tile_current[0]][self.tile_current[1]].highlight_tile(False)
        self.tile_previous = [-1, -1]

    def left_click(self, event):
        if self.state_game == 0: self.home_button_functions()
        elif self.state_game == 1:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                1
                    
    def right_click(self, event):
        # Break out if not in game
        if self.state_game != 1: return
    
        x, y = self.find_tile(event)
        if self.check_tile(x, y):
            # print(x,y)
            # self.get_tile(x,y).set_border()
            #self.redraw_tower(self.get_tile(x,y))
            1

    def build_tile(self, event):
        if self.state_game == 1 and self.tile_counter < 4:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                tile = self.get_tile(x,y)
                if tile.get_buildable():

                    suite, number = self.gen_card()
                    # if self.tile_counter < 2:
                    # suite = 0
                    # number = 10
                    # else:
                    #     suite = 1
                    #     number = 11
                    suite_num = suite
                    suite = card_suite[suite]
                    img_name = suite + '_' + str(number)

                    tile.set_tower(image=img_name, name=self.get_card_name(suite, number), 
                                   suite=suite, suite_num=suite_num, value=card_value[number], attack=3, range=2, 
                                   speed=1, ability=None, number=number)
                    self.tile_counter += 1
                    self.current_hand.append(tile)
                    self.play_sound('place_tower')
                    self.update_tile_information(x, y)
                    self.update_tile_hand()
                    self.determine_best_hand()
                else:
                    self.play_sound('place_fail')
        elif self.tile_counter == 4: self.play_sound('place_fail')

    def redraw_tower(self):
        
        # Avoid redraw if not all cards are played
        if self.tile_counter != 4: return

        iter = []
        for i, tile in enumerate(self.current_hand):
            if tile.get_selected(): iter.append(i)
        
        for i in iter:
            tile = self.current_hand[i]

            suite_num, number = self.gen_card()
            suite = card_suite[suite_num]

            tile.set_tower(image=str(suite_num) + '_' + str(number), 
                                   name=self.get_card_name(suite, number), 
                                   suite=suite, 
                                   attack=3, 
                                   range=2, 
                                   speed=1, 
                                   ability=None, 
                                   number=number
                                )
            
            # self.play_sound('place_tower') # Tower redraw sound....
            self.update_tile_information(0, 0, tile=tile)
            self.update_tile_hand(pos=i)
            self.determine_best_hand()

    def build_tower(self):
        
        new_card = self.determine_best_hand(type=True)
        print(new_card)

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
            self.get_tile(x,y).set_path()

    def find_tile(self, event):
        """ Finds x,y position of currently hoovered over tile """
        x = int(event.x/game_tile_width)
        y = int(event.y/game_tile_width)
        return x, y

    def get_tile(self, x, y):
        """ Returns reference to requested tile """
        return self.current_board[x][y]

    def check_tile(self, x, y):
        """ Returns true if marked area is a viable tile """
        if (x < 0 or x > game_tile_number - 1): return False
        if (y < 0 or y > game_tile_number - 1): return False
        return True

    def update_tile_information(self, x, y, tile=None):
        if tile == None:
            tile = self.get_tile(x,y)

        img = tile.get_image()
        self.info_tile_image_file = self.load_image(img, tile=False)
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
        suite =  self.get_suite_number(self.current_hand[pos])

        self.canvas_info.itemconfigure(self.tile_info_hand_cards_values[pos], text=short_name)
        self.canvas_info.itemconfigure(self.tile_info_hand_cards_suites[pos], image=self.tile_info_hand_symbol[suite])
        
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

    def __create_tile_information_current_hand(self):

        self.tile_info_hand_title = self.canvas_info.create_text(
                            dimension_info_width/2, dimension_info_cards_y-50, 
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
                                + 128, text='', anchor=N, 
                                font=('Dutch801 XBd BT', 20))

    def redraw_tower_temp(self):
        print(1)

    def __create_tile_information_buttons(self):
        
        self.tile_info_button_redraw = Button(self.canvas_info, text='Draw', command=self.redraw_tower_temp, font=('Dutch801 XBd BT', 15))
        self.tile_info_button_redraw.place(x=dimension_info_width - 2*dimension_screen_border, y=400, height=30, width=100, anchor=E)

    def get_card_name(self, suite, number):
        return card_value_name[number] + ' of ' + suite.capitalize() + 's'

    def gen_card(self, odds=None):

        # Add odds eventually
        suite_num = np.random.randint(4)
        number = np.random.randint(13)

        return suite_num, number


    def determine_best_hand(self):
        # 5 of a kind, Straight flush, 4 of a kind, full house, flush, straight, 3 of a kind, two pair, one pair, high card

        cards = []
        for tile in self.current_hand: cards.append(tile.get_number())
        seen, dupes = self.__best_card_multiple(cards)

        playable_hand = [0 for i in range(11)]
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

        full_hand = [0, 1, 2, 3, 5, 6, 7]

        for i, state in enumerate(playable_hand):
            if state != 0:
                if i in full_hand:
                    self.__update_best_hand_position([0,1,2,3,4])
                    self.__update_best_hand_indicator()
                    self.play_sound('all_cards')
                    return
                else:
                    self.__update_best_hand_position(self.__index_of_dupes(cards, dupes))
                    return
        self.__update_best_hand_position([self.__best_card_single(cards)])

    def __reset_best_hand_position(self):

        for i in range(5):
            self.canvas_info.coords(self.tile_info_hand_cards[i], 59*i, dimension_info_cards_y + 30)
            self.canvas_info.coords(self.tile_info_hand_cards_values[i], 59*(i+1/2), dimension_info_cards_y + 70)
            self.canvas_info.coords(self.tile_info_hand_cards_suites[i], 59*(i+1/2), dimension_info_cards_y + 128)
        self.canvas_info.itemconfigure(self.tile_info_hand_all_cards, text='')

    def __update_best_hand_indicator(self):
        self.canvas_info.itemconfigure(self.tile_info_hand_all_cards, text='All Cards!')

    def __update_best_hand_position(self, index):

        self.__reset_best_hand_position()

        for i in index:
            self.canvas_info.move(self.tile_info_hand_cards[i], 0, -30)
            self.canvas_info.move(self.tile_info_hand_cards_values[i], 0, -30)
            self.canvas_info.move(self.tile_info_hand_cards_suites[i], 0, -30)
            
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

        suite = self.get_suite_number(self.current_hand[0])
        for i in range(1, len(self.current_hand)):
            if suite != self.get_suite_number(self.current_hand[i]): return 0
        return 1
    
    def get_suite_number(self, tile):
        """ converts from tile suite 'heart, spade...' to '0, 1...' """
        tile_suite = tile.get_suite()
        for i, suite in enumerate(card_suite):
            if suite == tile_suite: return i
    
    def get_short_name(self, tile):
        """ converts from tile number '0, 1, ..., 11, 12' to 'A, 1, ... , Q, K' """
        return self.tower_stats[tile.get_number()][6]

    def __is_straigt(self, cards):
        """ Checks if straight returns T/F """
        if self.tile_counter < 4: return 0

        new_cards = cards.copy()
        new_cards.sort(reverse=True)
        if new_cards[0] == 12 and new_cards[-1] == 0:
            new_cards.insert(0, 13)

        for i in range(1, len(new_cards)-1):
            if new_cards[i-1] - new_cards[i] != 1: return 0
        return 1

    def __is_royal(self, cards):
        """ Checks ace high returns T/F """
        if self.tile_counter < 4: return 0

        if 0 in cards: return 1
        else: return 0

    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()

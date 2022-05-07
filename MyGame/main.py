from kivy.app import App
from kivy.graphics import Rectangle, RoundedRectangle
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.animation import Animation
from random import randint, random, choices, sample, choice
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import math

# Window.size = 540, 860
# Window.left = 700
# Window.top = 60

p_new_resource = 0.1

p_cell_die = 0.4

p_cell_evil = 0.01

p_new_cell_3 = 0.1
p_new_cell_4 = 0.3


def distance(pos1, pos2):
    return [math.fabs(pos1[0] - pos2[0]), math.fabs(pos1[1] - pos2[1])]


class Resource:
    def __init__(self):
        self.tiles = []
        self.value = 20
        self.max_cell = 9
        self.max_cell_interval = 2
        self.color = [random(), random(), random(), 0.8]

    def value_to_alpha(self):
        self.color[3] = 0.8
        if self.value < 15:
            self.color[3] = 0.5
        if self.value < 10:
            self.color[3] = 0.3
        if self.value < 5:
            self.color[3] = 0.1
        if self.value == 0:
            self.color = [1, 1, 1, 1]

    def update_tile(self):
        for i in self.tiles:
            if i.rgba[3] != self.color[3]:
                i.rgba = self.color
                anim = Animation(opacity=self.color[3],
                                 duration=0.3)
                anim.start(i)

    def expansion_p(self):
        if len(self.tiles) < 3:
            return 1
        elif len(self.tiles) < 10:
            return 1.0 / len(self.tiles) + 0.8
        elif len(self.tiles) < 20:
            return 1.0 / len(self.tiles) + 0.5
        elif len(self.tiles) < 30:
            return 1.0 / len(self.tiles) + 0.2
        return 1.0 / len(self.tiles)

    def update_resource(self):
        cells = 0
        evils = 0
        for i in self.tiles:
            if i.state == i.states[1] or i.state == i.states[2]:
                cells += 1
            elif i.state == i.states[3]:
                evils += 1
        if cells + evils > self.max_cell:
            self.value -= int(2 ** (int((cells + evils - self.max_cell) / self.max_cell_interval) - 1))
            # print("resource decrease: %d"%int(2 ** (int((cells + evils - self.max_cell) / self.max_cell_interval) - 1)))
        self.value_to_alpha()
        if self.value > 0:
            return cells - evils
        return 0

    def is_over_developed(self):
        cells = 0
        evils = 0
        for i in self.tiles:
            if i.state == i.states[1] or i.state == i.states[2]:
                cells += 1
            elif i.state == i.states[3]:
                evils += 1
        if cells + evils > self.max_cell:
            return True
        return False


class Tile(Widget):
    def __init__(self, x=0, y=0, source="", **kwargs):
        super(Tile, self).__init__(**kwargs)
        self.map_pos = [x, y]
        self.absolute_center = [0, 0]
        self.size = (Window.size[1] / 15, Window.size[1] / 15)
        with self.canvas:
            self.bg = Rectangle(source=source, pos=(0, 0), size=(Window.size[1] / 15, Window.size[1] / 15))
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
        self.state = "none"
        self.states = ["none", "cell", "ill_cell", "evil"]
        self.rgba = (1, 1, 1, 1)
        self.cell = None

    def update_color(self, color):
        self.rgba = color

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def new_cell(self):
        if self.state == self.states[0]:
            self.state = self.states[1]
            self.cell = Image(source="resources/cell.png")
            self.cell.size = (self.size[0] * .9, self.size[1] * .9)
            self.cell.pos = (self.pos[0] + self.size[0] * .05, self.pos[1] + self.size[1] * .05)
            # with self.canvas:
            #     self.cell = Rectangle(source="resources/cell.png", pos=(0, 0), size=(80, 80))
            self.bind(pos=self.update_cell)
            self.add_widget(self.cell)
            self.cell.opacity = 0
            anim = Animation(opacity=1,
                             duration=0.3)
            anim.start(self.cell)
        elif self.state == self.states[3]:
            self.cell = Image(source="resources/cell_evil.png")
            self.cell.size = (self.size[0] * .9, self.size[1] * .9)
            self.cell.pos = (self.pos[0] + self.size[0] * .05, self.pos[1] + self.size[1] * .05)
            # with self.canvas:
            #     self.cell = Rectangle(source="resources/cell.png", pos=(0, 0), size=(80, 80))
            self.bind(pos=self.update_cell)
            self.add_widget(self.cell)
            self.cell.opacity = 0
            anim = Animation(opacity=1,
                             duration=0.3)
            anim.start(self.cell)

    def ill_cell(self):
        if self.state == self.states[1]:
            self.state = self.states[2]
            anim = Animation(opacity=0,
                             duration=0.3)
            anim.start(self.cell)

            self.cell = Image(source="resources/cell_ill.png")
            self.cell.size = (self.size[0] * .9, self.size[1] * .9)
            self.cell.pos = (self.pos[0] + self.size[0] * .05, self.pos[1] + self.size[1] * .05)
            # with self.canvas:
            #     self.cell = Rectangle(source="resources/cell.png", pos=(0, 0), size=(80, 80))
            self.bind(pos=self.update_cell)
            self.add_widget(self.cell)
            self.cell.opacity = 0
            anim = Animation(opacity=1,
                             duration=0.3)
            anim.start(self.cell)

    def remove_cell(self):
        if self.state == self.states[1] or self.state == self.states[2]:
            self.state = self.states[0]
            anim = Animation(opacity=0,
                             duration=0.3)
            anim.start(self.cell)

    def update_cell(self, *args):
        self.cell.size = (self.size[0] * .9, self.size[1] * .9)
        self.cell.pos = (self.pos[0] + self.size[0] * .05, self.pos[1] + self.size[1] * .05)


class ChooseWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (Window.size[1] / 15, Window.size[1] / 15)
        with self.canvas:
            self.bg = Rectangle(source="resources/select.png", pos=(0, 0),
                                size=(Window.size[1] / 15, Window.size[1] / 15))
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class Background(RelativeLayout):
    def __init__(self, **kwargs):
        super(Background, self).__init__(**kwargs)
        self.clear_restart()

    def clear_restart(self):
        self.clear_widgets(self.children)

        self.initialized = False
        self.init_center = (self.size[0] / 2, self.size[1] / 2)
        print("init center ", self.init_center)
        self.zero = (0, 0)
        self.touch_pos = None

        self.tiles = []
        self.tiles_map = [[None for _ in range(1024)] for _ in range(1024)]
        self.resources = []

        self.game_on = True
        self.turn = 1
        self.movements = ["none", "increase", "rest", "decrease"]
        self.movement = self.movements[0]

        self.population = 0
        self.money = 1500
        self.cell_money = 50
        self.increase_cell_money = 50
        self.generate_cell_money = 7
        self.decrease_cell_money = 25
        self.cell_salary = 10
        self.resource_money = 35

        self.choose = None
        self.select_tile = None

        self.max_money = 0
        self.max_cell = 0

        self.resource_cells = Label()
        self.resource_cells.bold = True
        self.resource_cells.italic = True
        self.resource_cells.font_size = '25dp'
        self.add_widget(self.resource_cells)

        self.resource_value = Label()
        self.resource_value.bold = True
        self.resource_value.italic = True
        self.resource_value.font_size = '25dp'
        self.add_widget(self.resource_value)

        self.illegal_move = Label()
        self.illegal_move.color = (.9, .2, .2, 1)
        self.illegal_move.bold = True
        self.illegal_move.font_size = '15dp'
        self.add_widget(self.illegal_move)

        self.turn_label = Label(text="+ 1")
        self.turn_label.color = (.2, .2, .2, 1)
        self.turn_label.font_size = '15dp'
        # self.turn_label.bold = True
        self.turn_label.center = [Window.size[0] * .2, Window.size[1] * .85]
        self.add_widget(self.turn_label)

        self.money_message_labels = [Label() for _ in range(10)]
        for i in range(10):
            self.add_widget(self.money_message_labels[i])

        self.over_develop_labels = [Label() for _ in range(10)]
        for i in self.over_develop_labels:
            i.font_size = '20dp'
            i.underline = True
            i.bold = True
            i.color = (.45, .45, .15, 1)
            i.opacity = 0
            self.add_widget(i)
        self.involution_labels = [Label() for _ in range(10)]
        for i in self.involution_labels:
            i.font_size = '20dp'
            i.underline = True
            i.italic = True
            i.opacity = 0
            i.color = (.85, .85, .85, 1)
            i.text = "INVOLUTION !!"
            self.add_widget(i)

    def initial(self):
        self.resources.append(Resource())

        self.init_center = (self.size[0] / 2, self.size[1] / 2)
        print("init center ", self.init_center)

        self.initialized = True
        for i in range(25):
            temp_tile = Tile(source="resources/grid1.png", x=i % 5 + 512, y=int(i / 5) + 512)
            if i == 0:
                temp_tile.absolute_center = (self.init_center[0] - 2.5 * temp_tile.size[0],
                                             self.init_center[1] - 2.5 * temp_tile.size[1])
            else:
                center0 = self.tiles[0].center
                temp_tile.absolute_center = (center0[0] + temp_tile.size[0] * int(i % 5),
                                             center0[1] + temp_tile.size[1] * int(i / 5))

            if i == 12:
                self.resources[0].tiles.append(temp_tile)
            temp_tile.center = (temp_tile.absolute_center[0], temp_tile.absolute_center[1])
            self.tiles.append(temp_tile)
            self.tiles_map[i % 5 + 512][int(i / 5) + 512] = temp_tile
        for i in self.tiles:
            self.add_widget(i)
            print(i.pos)

        self.new_tile_src(self.tiles)
        self.new_evil(self.tiles)

        self.choose = ChooseWidget()
        # with self.choose.canvas:
        #     self.choose.bg_rect = Rectangle(pos=self.pos, size=self.choose.size)
        self.add_widget(self.choose)

    def update_positions(self):
        for i in self.tiles:
            to_center = (i.absolute_center[0] + self.zero[0], i.absolute_center[1] + self.zero[1])
            if (to_center[0] < self.width + 150 and to_center[0] > -150 and to_center[1] < self.height + 150 and
                to_center[1] > -150) \
                    or (i.center[0] < self.width + 150 and i.center[0] > -150 and i.center[1] < self.height + 150 and
                        i.center[1] > -150):
                anim = Animation(
                    opacity=1,
                    center=(to_center[0],
                            to_center[1]),
                    duration=0.3)
                anim.start(i)
        # print("init center", self.init_center)
        self.remove_widget(self.choose)
        self.add_widget(self.choose)
        anim = Animation(center=(self.init_center[0], self.init_center[1]),
                         size=(Window.size[1] / 15, Window.size[1] / 15),
                         duration=0.3)
        anim.start(self.choose)

        for i in self.resources:
            i.update_tile()

        return

    def touch_tile(self, touch):
        self.init_center = (self.size[0] / 2, self.size[1] / 2)
        # print("init center ", self.init_center)
        touch_x = touch.x
        touch_y = touch.y
        for i in self.tiles:
            if i.absolute_center[0] - i.size[1] / 2 + self.zero[0] < touch_x and i.absolute_center[0] + self.zero[0] + \
                    i.size[
                        0] / 2 > touch_x and \
                    i.absolute_center[1] - i.size[1] / 2 + self.zero[1] < touch_y and i.absolute_center[1] + self.zero[
                1] + i.size[
                1] / 2 > touch_y:
                print("map pos ", i.map_pos)
                self.zero = (self.init_center[0] - i.absolute_center[0],
                             self.init_center[1] - i.absolute_center[1])
                self.choose.center = i.center
                for j in range(len(self.resources)):
                    if i in self.resources[j].tiles:
                        print("selected in ", j)

                self.select_tile = i

                return i
        return None

    def on_touch_down(self, touch):
        if not self.initialized:
            self.initial()
        else:
            self.touch_pos = None
            self.touch_tile(touch)
            self.message_select()
            self.update_positions()

    def on_touch_up(self, touch):
        self.message_select(show=False)

    def new_cell(self):
        if self.select_tile != None \
                and self.select_tile.state == self.select_tile.states[0] \
                and self.money >= self.cell_money:
            self.investigation()
            self.message_money(-self.cell_money, color=(0.2, 0.2, 0.2, 1))
            self.money -= self.cell_money
            self.cell_money += self.increase_cell_money
            self.select_tile.new_cell()
            # self.select_tile.update_cell()
            self.update_game()
        elif self.money < self.cell_money:
            self.message_illegal("Not Enough Welfare !")
        elif self.select_tile.state != self.select_tile.states[0]:
            self.message_illegal("Not Empty")
        else:
            self.message_illegal()

    def remove_cell(self):
        if self.select_tile != None and (self.select_tile.state == self.select_tile.states[1] or
                                         self.select_tile.state == self.select_tile.states[2]):
            self.select_tile.remove_cell()
            if self.cell_money > self.decrease_cell_money:
                self.cell_money -= self.decrease_cell_money
            else:
                self.cell_money = 0
            self.movement = self.movements[3]
            self.update_game()
            # self.select_tile.update_cell()
        elif self.select_tile.state == self.select_tile.states[0]:
            self.message_illegal("Nothing to be Removed !")
        elif self.select_tile.state == self.select_tile.states[3]:
            self.message_illegal("I AM EVIL !!!")
        else:
            self.message_illegal()

    def get_neighbours(self, temp_tile):
        temp_pos = temp_tile.map_pos
        neighbours = []
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    pass
                else:
                    if self.tiles_map[temp_pos[0] + i - 1][temp_pos[1] + j - 1] is not None:
                        neighbours.append(self.tiles_map[temp_pos[0] + i - 1][temp_pos[1] + j - 1])
        return neighbours

    def update_game(self):
        if self.game_on:
            self.turn += 1
            self.message_turn()
            self.update_cells()
            self.update_income()
            if self.money > self.max_money:
                self.max_money = self.money
            population = 0
            for i in self.tiles:
                if i.state != i.states[0]:
                    population += 1
            if population > self.max_cell:
                self.max_cell = population
            self.population = population

            self.movement = self.movements[0]

            if self.turn >= 100 or self.money < 0:
                print("GAME OVER")
                self.game_on = False

                game_over_label = Label()
                temp_str = ""
                if self.turn >= 100:
                    temp_str = "Time is UP"
                elif self.money < 0:
                    temp_str = "Run out of Capital"
                game_over_label.text = \
                    '''
%s !!!\n
Welfare now: %d
MAX welfare: %d
Population now: %d
MAX population: %d
Land Size: %d\n 
Thanks for playing !!
by darkbloodevil
2573283827@qq.com
                ''' % \
                    (temp_str, self.money, self.max_money, self.population, self.max_cell,
                     len(self.tiles))
                self.add_widget(game_over_label)
                game_over_label.font_size = '25dp'
                game_over_label.color = (0, 0, 0, 1)
                game_over_label.center = [0, 0]
                game_over_label.size = [self.width / 2, self.height / 2]

                rr_size = [self.width / 1.2, self.height / 2]
                rr_center = [self.width / 2, self.height / 2]
                with game_over_label.canvas.before:
                    rr = RoundedRectangle()
                    rr.size = rr_size
                    rr.pos = [rr_center[0] - rr_size[0] / 2, rr_center[1] - rr_size[1] / 2]

                anim = Animation(center=[self.width / 2, self.height / 2], size=[self.width / 2, self.height / 4],
                                 duration=0.7)

                anim.start(game_over_label)

    def update_cells(self):
        new_cells = []
        die_cells = []
        ill_cells = []
        for i in self.tiles:
            if i.state == i.states[0] and (
                    self.movement != self.movements[3] or (i != self.select_tile and i not in self.get_neighbours(
                self.select_tile))):
                count_neigh_cell = 0
                has_ill = False
                for j in self.get_neighbours(i):
                    if j.state == j.states[1] or j.state == j.states[3]:
                        count_neigh_cell += 1
                    if j.state == j.states[2]:
                        has_ill = True
                        break
                if count_neigh_cell == 3 and random() < p_new_cell_3 and not has_ill:
                    new_cells.append(i)
                if count_neigh_cell == 4 and random() < p_new_cell_4 and not has_ill:
                    new_cells.append(i)
            if i.state == i.states[1]:
                count_neigh_cell = 0
                for j in self.get_neighbours(i):
                    if j.state != j.states[0]:
                        count_neigh_cell += 1
                if count_neigh_cell > 5:
                    self.message_involution(i)
                    ill_cells.append(i)
                if self.turn > 3:
                    if count_neigh_cell < 1:
                        ill_cells.append(i)
            if i.state == i.states[2]:
                if random() < p_cell_die:
                    die_cells.append(i)
        for i in new_cells:
            self.cell_money += self.generate_cell_money
            i.new_cell()
        for i in ill_cells:
            i.ill_cell()
        for i in die_cells:
            i.remove_cell()

    def update_income(self):
        cell_num = 0
        for i in self.tiles:
            if i.state != i.states[0]:
                cell_num += 1

        distinct_resources = []
        for i in self.resources:
            resource_money = self.resource_money * i.update_resource()
            resource_cell = 0
            for j in i.tiles:
                if j.state != j.states[0]:
                    resource_cell += 1
            resource_money -= resource_cell * self.cell_salary
            cell_num -= resource_cell
            self.money += resource_money
            if resource_money != 0:
                self.message_money(resource_money, i.color)
            if i.value <= 0:
                distinct_resources.append(i)
            elif i.is_over_developed():
                self.message_over_develop(i)
        for i in distinct_resources:
            for j in i.tiles:
                j.rgba = [1, 1, 1, 1]
            self.resources.remove(i)

        if cell_num > 0:
            self.message_money(-cell_num * self.cell_salary, (1, 0, 0, 1))
        self.money -= cell_num * self.cell_salary

    def message_select(self, show=True):
        self.remove_widget(self.resource_cells)
        self.add_widget(self.resource_cells)
        self.remove_widget(self.resource_value)
        self.add_widget(self.resource_value)
        if self.select_tile==None:return

        if show:
            bias = [random() * Window.size[0] * 0.15, random() * Window.size[1] * 0.15]
            temp_color = (0, 0, 0, 1)
            temp_num = 0
            is_resource = False
            for i in self.resources:
                if self.select_tile in i.tiles:
                    for j in i.tiles:
                        if j.state != j.states[0]:
                            temp_num += 1
                    if i.color[3] > .6:
                        temp_color = (1 - i.color[0] if math.fabs(0.5 - i.color[0]) > 0.15 else (i.color[0] + .5) % 1,
                                      1 - i.color[1] if math.fabs(0.5 - i.color[1]) > 0.15 else (i.color[1] + .5) % 1,
                                      1 - i.color[2] if math.fabs(0.5 - i.color[2]) > 0.15 else (i.color[2] + .5) % 1,
                                      1)
                    is_resource = True

                    self.resource_value.text = "VALUE: %d" % i.value
                    self.resource_value.color = temp_color

                    temp_center = [self.select_tile.center[0] - bias[0],
                                   self.select_tile.center[1] + bias[1] - Window.size[1] / 10]
                    self.resource_value.center = temp_center
                    self.resource_value.opacity = 1
                    anim = Animation(opacity=1,
                                     center=[temp_center[0],
                                             temp_center[1]],
                                     duration=.8)
                    anim.start(self.resource_value)
                    break
            if not is_resource:
                for i in self.resources:
                    for j in i.tiles:
                        if j.state != j.states[0]:
                            temp_num += 1
                temp_num = self.population - temp_num
                self.resource_value.opacity = 0

            self.resource_cells.text = "COMPETITORs: %d" % temp_num
            self.resource_cells.color = temp_color
            temp_center = [self.select_tile.center[0] - bias[0], self.select_tile.center[1] + bias[1]]
            self.resource_cells.center = temp_center
            self.resource_cells.opacity = 1

            anim = Animation(opacity=1,
                             center=[temp_center[0],
                                     temp_center[1]],
                             duration=.8)
            anim.start(self.resource_cells)


        else:
            self.resource_cells.opacity = 1
            anim = Animation(opacity=0,
                             center=[self.resource_cells.center[0],
                                     self.resource_cells.center[1]],
                             duration=.8)
            anim.start(self.resource_cells)

            anim = Animation(opacity=0,
                             center=[self.resource_value.center[0],
                                     self.resource_value.center[1]],
                             duration=.8)
            anim.start(self.resource_value)

    def message_illegal(self, message="illegal !"):
        self.remove_widget(self.illegal_move)
        self.add_widget(self.illegal_move)
        self.illegal_move.opacity = 1
        self.illegal_move.text = message
        self.illegal_move.center = [Window.size[0] / 2, Window.size[1] * .45]
        anim = Animation(opacity=0,
                         center=[self.illegal_move.center[0], Window.size[1] * .65],
                         duration=.8, transition="in_cubic")
        anim.start(self.illegal_move)

    def message_turn(self):
        self.remove_widget(self.turn_label)
        self.add_widget(self.turn_label)
        self.turn_label.opacity = 1
        self.turn_label.center = [Window.size[0] * .2, Window.size[1] * .85]
        anim = Animation(opacity=0,
                         center=[self.turn_label.center[0], Window.size[1] * .95],
                         duration=.5, transition="in_cubic")
        anim.start(self.turn_label)

    def message_money(self, money, color=(0, 0, 0, 1)):
        temp_label = self.money_message_labels[0]
        self.remove_widget(temp_label)
        self.add_widget(temp_label)
        self.money_message_labels.remove(temp_label)
        self.money_message_labels.append(temp_label)
        if money >= 0:
            temp_text = "+ %d" % money
        else:
            temp_text = "- %d" % math.fabs(money)
        temp_label.text = temp_text
        temp_label.color = color
        temp_label.font_size = '15dp'
        temp_label.bold = True
        bias = [random() * Window.size[0] * 0.15, random() * Window.size[1] * 0.05]
        money_x = 0
        if money >= 0:
            money_x = Window.size[0] * .65 - bias[0]
        if money < 0:
            money_x = Window.size[0] * .5 + bias[0]
        temp_label.center = [money_x, Window.size[1] * .8 + bias[1]]

        temp_label.opacity = 0
        anim = Animation(d=random() * 0.5) + \
               Animation(d=random() * .05, opacity=1) + \
               Animation(opacity=0,
                         center=[money_x,
                                 Window.size[
                                     1] * .95 +
                                 bias[1]],
                         duration=1,
                         transition="in_cubic")
        anim.start(temp_label)

    def message_over_develop(self, resource):
        temp_message = self.over_develop_labels[0]
        self.over_develop_labels.remove(temp_message)
        self.over_develop_labels.append(temp_message)
        self.remove_widget(temp_message)
        self.add_widget(temp_message)
        temp_tile = choice(resource.tiles)
        temp_center = self.normalize_in_window(temp_tile.center)
        temp_message.center = temp_center
        temp_message.text = "OVER DEVELOPED !!"

        temp_message.opacity = 1
        anim = Animation(opacity=0, center=temp_tile.center,
                         duration=2, transition="in_out_bounce")
        anim.start(temp_message)

    def message_involution(self, tile):
        temp_message = self.involution_labels[0]
        self.involution_labels.remove(temp_message)
        self.involution_labels.append(temp_message)
        self.remove_widget(temp_message)
        self.add_widget(temp_message)
        temp_tile = tile
        temp_center = self.normalize_in_window(temp_tile.center)
        temp_message.center = temp_center

        temp_message.opacity = 1
        anim = Animation(opacity=0, center=temp_tile.center,
                         duration=2, transition="in_out_bounce")
        anim.start(temp_message)

    def normalize_in_window(self, pos):
        temp_pos = [pos[0], pos[1]]
        if pos[0] > Window.size[0]:
            temp_pos[0] = Window.size[0] * 0.95
        elif pos[0] < 0:
            temp_pos[0] = Window.size[0] * 0.05
        if pos[1] > Window.size[1]:
            temp_pos[1] = Window.size[1] * 0.8
        elif pos[1] < 0:
            temp_pos[1] = Window.size[1] * 0.2
        return temp_pos

    def new_tile_src(self, new_tiles):
        times = int(len(new_tiles) / 5)
        if times < 1:
            times = 1
        for u in range(times):
            resource_list = []
            resource_dict = {}
            contend_list = []
            for i in range(len(self.resources)):
                resource_dict[i] = []
                for j in self.resources[i].tiles:
                    if j in new_tiles:
                        contend_list.append(j)
                    for k in self.get_neighbours(j):
                        if k in new_tiles:
                            if k in resource_list:
                                if k not in resource_dict[i]:
                                    resource_list.remove(k)
                                    contend_list.append(k)
                            elif k not in contend_list:
                                resource_list.append(k)
                                resource_dict[i].append(k)
            rest_list = [i for i in new_tiles if i not in resource_list and i not in contend_list]
            for i in rest_list:
                if random() < p_new_resource:
                    new_resource = Resource()
                    new_resource.tiles.append(i)
                    contend_list.append(i)
                    resource_dict[len(self.resources)] = [i]
                    self.resources.append(new_resource)
                    break
            resource_list = []
            for i in range(len(self.resources)):
                resource_dict[i] = []
                for j in self.resources[i].tiles:
                    for k in self.get_neighbours(j):
                        if k in new_tiles:
                            if k in resource_list:
                                if k not in resource_dict[i]:
                                    resource_list.remove(k)
                                    contend_list.append(k)
                            elif k not in contend_list:
                                resource_list.append(k)
                                resource_dict[i].append(k)
            for i in range(len(self.resources)):
                for j in resource_dict[i]:
                    if j not in contend_list:
                        if random() < self.resources[i].expansion_p():
                            self.resources[i].tiles.append(j)

    def new_evil(self, new_tiles):
        for i in new_tiles:
            if random() < p_cell_evil:
                i.state = i.states[3]
                i.new_cell()

    def investigation(self):
        tiles_new = []
        for i in range(5):
            for j in range(5):
                temp_pos = [self.select_tile.map_pos[0] + i - 2, self.select_tile.map_pos[1] + j - 2]
                if self.tiles_map[temp_pos[0]][temp_pos[1]] is None:
                    temp_tile = Tile(source="resources/grid1.png", x=temp_pos[0], y=temp_pos[1])
                    tiles_new.append(temp_tile)
                    temp_tile.absolute_center = (self.select_tile.absolute_center[0] + (i - 2) * temp_tile.size[0],
                                                 self.select_tile.absolute_center[1] + (j - 2) * temp_tile.size[1])
                    temp_tile.center = [temp_tile.absolute_center[0] + self.zero[0],
                                        temp_tile.absolute_center[1] + self.zero[1]]
        for temp_tile in tiles_new:
            temp_tile.opacity = 0
            self.add_widget(temp_tile)
            self.tiles.append(temp_tile)
            self.tiles_map[temp_tile.map_pos[0]][temp_tile.map_pos[1]] = temp_tile
        if len(tiles_new) > 0:
            self.new_tile_src(tiles_new)
            self.new_evil(tiles_new)
        self.update_positions()


class GameItems(RelativeLayout):
    def __init__(self, background, **kwargs):
        super().__init__(**kwargs)
        self.background = background
        self.ids.turn.text = "turn: \n%d" % self.background.turn

    def touch_start(self):
        self.background.clear_restart()
        self.background.initial()

    def touch_increase(self):
        # self.background.investigation()
        self.background.new_cell()
        self.update_labels()
        print("increase!")

    def touch_decrease(self):
        self.background.remove_cell()
        self.update_labels()
        # print("increase!")

    def touch_rest(self):
        self.background.update_game()
        self.update_labels()

    def update_labels(self):
        self.ids.turn.text = "turn: \n%d" % self.background.turn
        self.ids.money.text = "Welfare:\n %d" % self.background.money
        self.ids.cell_money.text = "Cost:\n %d" % self.background.cell_money


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = Background()
        self.add_widget(self.background)
        self.add_widget(GameItems(self.background))


class MenuScreen(Screen):
    def __init__(self, screens, sm, **kw):
        super().__init__(**kw)
        self.screens = screens
        self.sm = sm

    def to_game(self):
        self.sm.switch_to(self.screens[0], direction='right')


class HelpScreen(Screen):
    pass


class TestApp(App):
    def build(self):
        sm = ScreenManager()
        self.screens = []
        self.screens.append(GameScreen(name="game"))
        self.screens.append(HelpScreen(name='help'))
        self.screens.append(MenuScreen(name="menu", screens=self.screens, sm=sm))

        sm.add_widget(self.screens[0])
        sm.add_widget(self.screens[1])
        sm.add_widget(self.screens[2])
        sm.switch_to(self.screens[0])
        return sm


Window.clearcolor = get_color_from_hex('faf8ef')
TestApp().run()

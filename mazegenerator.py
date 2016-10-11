# File name: mazegenerator.py
__author__ = 'MazeFX'

import random
from math import cos , sin, degrees, fmod, frexp
from math import pi as PI

from kivy.config import Config
Config.set('graphics', 'width', '1100')
Config.set('graphics', 'height', '1100')

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen


BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)

CORRIDOR = 60
WALL = 5
CORNER = 10
CORNERSIZE = 4
DIAMDOT = 10

ANIMSPEED = 0.1
current_wedge = 1

CenterX = 550
CenterY = 550


class MazeGeneratorApp(App):

    def build(self):
        Larch = Shell()
        return Larch


class Shell(ScreenManager):
    pass


class MazeSettings(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        Clock.schedule_once(self.callback)
        self.corridor_set = CORRIDOR
        self.wall_set = WALL
        self.corner_set = CORNER
        self.corner_size_set = CORNERSIZE
        self.dot_set = DIAMDOT
        self.animation_set = ANIMSPEED

    def callback(self, dt):
        self.setconfig()

    def my_callback(self, dt):
        self.generator.createmaze()

    def setconfig(self):
        self.corridor.header.text = "Corridor"
        self.corridor.footer.text = '60'
        self.corridor.w_slider.min = 20
        self.corridor.w_slider.max = 200
        self.corridor.w_slider.value = 60
        self.wall.header.text = "Wall"
        self.wall.footer.text = '5'
        self.wall.w_slider.min = 1
        self.wall.w_slider.max = 30
        self.wall.w_slider.value = 5
        self.corner.header.text = "Corner"
        self.corner.footer.text = '10'
        self.corner.w_slider.min = 1
        self.corner.w_slider.max = 60
        self.corner.w_slider.value = 10
        self.corner_size.header.text = "Corner\nsize"
        self.corner_size.footer.text = '1/4'
        self.corner_size.w_slider.min = 1
        self.corner_size.w_slider.max = 15
        self.corner_size.w_slider.value = 4
        self.dot.header.text = "Dot\ndiameter"
        self.dot.footer.text = '10'
        self.dot.w_slider.min = 2
        self.dot.w_slider.max = 60
        self.dot.w_slider.value = 10
        self.animation.header.text = "Animation\nspeed"
        self.animation.footer.text = '10'
        self.animation.w_slider.min = 1
        self.animation.w_slider.max = 30
        self.animation.w_slider.value = 10

    def reset(self):
        global CORRIDOR, WALL, CORNER,CORNERSIZE, DIAMDOT, ANIMSPEED, current_wedge
        CORRIDOR = self.corridor_set
        WALL = self.wall_set
        CORNER = self.corner_set
        CORNERSIZE = self.corner_size_set
        DIAMDOT = self.dot_set
        ANIMSPEED = self.animation_set
        current_wedge = 1
        self.generator.deletemaze()
        Clock.schedule_once(self.my_callback)

    def applylayout(self):
        global WALL, CORNER, CORNERSIZE, DIAMDOT
        WALL = self.wall_set
        CORNER = self.corner_set
        CORNERSIZE = self.corner_size_set
        DIAMDOT = self.dot_set
        self.generator.applylayout()


class CustomSlider(BoxLayout):

    def slide_to(self, value, name):
        if name == 'corner size':
            self.footer.text = '1 / ' + str(int(value))
        else:
            self.footer.text = str(int(value))
        if name == 'corridor':
            self.parent.corridor_set = value
        if name == 'wall':
            self.parent.wall_set = value
        if name == 'corner':
            self.parent.corner_set = value
        if name == 'corner size':
            self.parent.corner_size_set = value
        if name == 'dot':
            self.parent.dot_set = value
        if name == 'animation':
            self.parent.animation_set = 1 / value


class MazeGenerator(Screen):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.root = None
        self.started = False
        self.createmaze()

    def deletemaze(self):
        self.root.canvas.clear()
        self.root.canvas.ask_update()
        self.remove_widget(self.root)

    def applylayout(self):
        self.root.canvas.clear()
        self.root.setvalues()
        self.root.draw()
        self.root.canvas.ask_update()

    def createmaze(self):
        self.root = Maze()
        self.add_widget(self.root)

    def start(self, button):
        if button == 'back':
            self.started = True
        if not self.started:
            self.started = True
            Clock.schedule_interval(self.my_callback, ANIMSPEED)
            self.running.text = 'Stop'
        else:
            Clock.unschedule(self.my_callback)
            self.started = False
            self.running.text = 'Start'

    def my_callback(self, dt):
        self.root.update()


class Maze(RelativeLayout):

    def __init__(self, **kwargs):
        global current_wedge
        super(RelativeLayout, self).__init__(**kwargs)
        self.wedge_list = []
        self.color_list = [BLACK, BLACK, BLACK]
        self.ring_count = int(500 / CORRIDOR)
        self.inner_ring = 500 - (self.ring_count * CORRIDOR)

        if self.inner_ring < CORRIDOR:
            self.inner_ring = self.inner_ring + CORRIDOR
            self.ring_count -= 1

        wedge_density = int(((2 * PI) * self.inner_ring) // CORRIDOR)
        for rnum in range(self.ring_count):

            wedge_count = Counter(rnum, wedge_density, self.inner_ring)
            wedge_size = (2 * PI) / wedge_count

            first = len(self.wedge_list)
            for wnum in range(wedge_count):
                a_left = wedge_size * wnum
                a_right = wedge_size * (wnum + 1)
                w = Wedge(a_left, a_right, (rnum, first), (wedge_count, self.ring_count, wedge_density), len(self.wedge_list), self.inner_ring)
                self.wedge_list.append(w)

            if rnum == self.ring_count - 1:
                self.outer_line = InstructionGroup()
                self.outer_size = wedge_size
                self.outer_count = wedge_count

        for wnum in range(len(self.wedge_list)):
            self.wedge_list[wnum].neighborize(self.wedge_list)

        self.wedge_list[current_wedge].makeactive(None)
        self.draw()

    def update(self):
        global current_wedge
        self.wedge_list[current_wedge].makecheck()
        self.canvas.clear()
        self.draw()
        self.canvas.ask_update()

    def setvalues(self):
        for wnum in range(len(self.wedge_list)):
            self.wedge_list[wnum].setcorners()

    def draw(self):
        with self.canvas:
            Color(*BLACK)
            self.drawouterring(self.outer_count, self.outer_size)
        for wnum in range(len(self.wedge_list)):
            with self.canvas:
                    Color(*BLACK)
                    self.wedge_list[wnum].draw(self.canvas)
                    Color(*GREEN)
                    self.wedge_list[wnum].draw_dot(self.canvas)


    def drawouterring(self, wedge_count, wedge_size):
        self.line = Line(circle=(CenterX, CenterY, self.inner_ring + (self.ring_count * CORRIDOR), 0, 360), width=WALL)
        self.outer_line.clear()
        for w_num in range(wedge_count):
            angle = w_num * wedge_size
            outer_corner = wedge_size / CORNERSIZE
            self.outer_line.add(Line(circle=(CenterX, CenterY,
                                    self.inner_ring + (self.ring_count * CORRIDOR),
                                    degrees(angle - outer_corner), degrees(angle + outer_corner)),
                                    width=CORNER, cap='round'))
        self.canvas.add(self.outer_line)


class Wedge(RelativeLayout):

    def __init__(self, angle_left, angle_right, ring_num, ring_spec, list_pos, in_ring):
        self.flag_open = True
        self.flag_routed = False
        self.flag_inner_blocked = True
        self.flag_left_blocked = True
        self.dot = None

        self.in_ring = in_ring
        self.r_num = ring_num[0]
        self.first = ring_num[1]
        self.w_in = None
        self.w_prior = None

        self.ring_spec = ring_spec
        self.a_left = angle_left
        self.a_right = angle_right
        self.diameter_inner_arc = (ring_num[0] + 1) * CORRIDOR

        self.radius_inner = in_ring + (ring_num[0] * CORRIDOR)
        self.left_in = (CenterX + int(sin(self.a_left) * self.radius_inner), CenterY + int(cos(self.a_left) * self.radius_inner))
        self.radius_outer = in_ring + ((ring_num[0] + 1) * CORRIDOR)
        self.left_out = (CenterX + int(sin(self.a_left) * self.radius_outer), CenterY + int(cos(self.a_left) * self.radius_outer))

        self.a_corner = (self.a_right - self.a_left) / CORNERSIZE
        self.radius_corner = int(CORRIDOR / CORNERSIZE)
        self.pos_corner_up = (CenterX + int(sin(self.a_left) * (self.radius_outer - self.radius_corner)),
                              CenterY + int(cos(self.a_left) * (self.radius_outer - self.radius_corner)))
        self.pos_corner_down = (CenterX + int(sin(self.a_left) * (self.radius_inner + self.radius_corner)),
                                CenterY + int(cos(self.a_left) * (self.radius_inner + self.radius_corner)))

        self.radius_dot = int((self.radius_outer + self.radius_inner) / 2)
        self.a_dot = (self.a_right + self.a_left) / 2
        self.center_dot = (CenterX + int(sin(self.a_dot) * self.radius_dot), CenterY + int(cos(self.a_dot) * self.radius_dot))
        self.pos_dot = (self.center_dot[0] - DIAMDOT / 2, self.center_dot[1] - DIAMDOT / 2)
        self.l_pos = list_pos

    def neighborize(self, wedge_list):
        self.last = self.first + self.ring_spec[0] - 1
        self.left = self.l_pos - 1
        if self.left < self.first:
            self.left = self.last

        self.right = self.l_pos + 1
        if self.right > self.last:
            self.right = self.first

        self.w_left = wedge_list[self.left]
        self.w_right = wedge_list[self.right]

        if Counter(self.r_num + 1, self.ring_spec[2], self.in_ring) != self.ring_spec[0]:
            wnum = self.l_pos - self.first
            self.out1 = self.l_pos + self.ring_spec[0] + wnum
            self.out2 = self.out1 + 1
        else:
            self.out1 = self.l_pos + self.ring_spec[0]
            self.out2 = None

        if self.out1 < len(wedge_list):
            self.w_out1 = wedge_list[self.out1]
            self.w_out1.w_in = self
            self.w_out1.In = self.l_pos
        else:
            self.w_out1 = None

        if self.out2 < len(wedge_list):
            if self.out2 is not None:
                self.w_out2 = wedge_list[self.out2]
                self.w_out2.w_in = self
                self.w_out2.In = self.l_pos
            else:
                self.w_out2 = None
        else:
            self.w_out2 = None

        if self.r_num > 0:
            self.w_in = wedge_list[self.In]
        else:
            self.In = 0
            self.w_in = None

    def makeactive(self, w):
        global current_wedge
        self.flag_open = False
        self.flag_routed = True
        current_wedge = self.l_pos
        if w is not None:
            self.w_prior = w

    def makecheck(self):
        global current_wedge
        if self.l_pos == current_wedge:
            b_available = self.w_right.flag_open | self.w_left.flag_open
            if self.w_out1 is not None:
                b_available |= self.w_out1.flag_open
            if self.w_out2 is not None:
                b_available |= self.w_out2.flag_open
            if self.w_in is not None:
                b_available |= self.w_in.flag_open

            if b_available:
                b_picked = False
                while not b_picked:
                    v = int(random.randrange(5))
                    for case in switch(v):
                        if case(0):
                            if self.w_right.flag_open:
                                self.w_right.makeactive(self)
                                self.w_right.flag_left_blocked = False
                                b_picked = True
                                break
                        if case(1):
                            if self.w_left.flag_open:
                                self.w_left.makeactive(self)
                                self.flag_left_blocked = False
                                b_picked = True
                                break
                        if case(2):
                            if self.w_out1 is not None:
                                if self.w_out1.flag_open:
                                    self.w_out1.makeactive(self)
                                    self.w_out1.flag_inner_blocked = False
                                    b_picked = True
                                    break
                        if case(3):
                            if self.w_out2 is not None:
                                if self.w_out2.flag_open:
                                    self.w_out2.makeactive(self)
                                    self.w_out2.flag_inner_blocked = False
                                    b_picked = True
                                    break
                        if case(4):
                            if self.w_in is not None:
                                if self.w_in.flag_open:
                                    self.w_in.makeactive(self)
                                    self.flag_inner_blocked = False
                                    b_picked = True
                                    break
            else:
                self.flag_routed = False
                if self.w_prior is not None:
                    self.w_prior.makeactive(None)
                else:
                    print('Finished')

    def setcorners(self):
        self.pos_corner_up = (CenterX + int(sin(self.a_left) * (self.radius_outer - self.radius_corner)),
                              CenterY + int(cos(self.a_left) * (self.radius_outer - self.radius_corner)))
        self.pos_corner_down = (CenterX + int(sin(self.a_left) * (self.radius_inner + self.radius_corner)),
                                CenterY + int(cos(self.a_left) * (self.radius_inner + self.radius_corner)))
        self.a_corner = (self.a_right - self.a_left) / CORNERSIZE
        self.radius_corner = int(CORRIDOR / CORNERSIZE)

    def draw(self, Canvas):
        if self.flag_inner_blocked:
            with Canvas:
                self.arc = Line(circle=(CenterX, CenterY,
                                            self.radius_inner,
                                            degrees(self.a_left), degrees(self.a_right)),
                                            width=WALL, cap='round')
                self.corner_left = Line(circle=(CenterX, CenterY,
                                            self.radius_inner,
                                            degrees(self.a_left), degrees(self.a_left + self.a_corner)),
                                            width=CORNER, cap='round')
                self.corner_right = Line(circle=(CenterX, CenterY,
                                            self.radius_inner,
                                            degrees(self.a_right - self.a_corner), degrees(self.a_right)),
                                            width=CORNER, cap='round')
        else:
            if self.arc is not None:
                self.arc = None
            if self.corner_left is not None:
                self.corner_left = None
            if self.corner_right is not None:
                self.corner_right = None

        if self.flag_left_blocked:
            with Canvas:
                self.wall = Line(points=[self.left_in[0], self.left_in[1],
                                         self.left_out[0], self.left_out[1]], width=WALL, cap='round')
                self.corner_down = Line(points=[self.left_in[0], self.left_in[1],
                                              self.pos_corner_down[0], self.pos_corner_down[1]], width=CORNER, cap='round')
                self.corner_up = Line(points=[self.pos_corner_up[0], self.pos_corner_up[1],
                                              self.left_out[0], self.left_out[1]], width=CORNER, cap='round')
        else:
            if self.wall is not None:
                self.wall = None
            if self.corner_down is not None:
                self.corner_down = None
            if self.corner_up is not None:
                self.corner_up = None
#       with Canvas:
#           self.g_number = Label(pos= self.pos_dot,
#                               size=(DIAMDOT, DIAMDOT),
#                               text=str(self.l_pos),
#                               color=(0, 0, 0, 1),
#                               markup=True,
#                               halign='center',
#                               valign='middle')
#
#           self.g_in = Label(pos= (self.pos_dot[0] - DIAMDOT, self.pos_dot[1] - DIAMDOT),
#                               size=(DIAMDOT, DIAMDOT),
#                               text=str(self.In),
#                               color=(1, 0, 0, 1),
#                               markup=True,
#                               halign='left',
#                               valign='bottom')
#           self.g_out1 = Label(pos= (self.pos_dot[0] - DIAMDOT, self.pos_dot[1] + DIAMDOT),
#                               size=(DIAMDOT, DIAMDOT),
#                               text=str(self.out1),
#                               color=(0, 0, 1, 1),
#                               markup=True,
#                               halign='left',
#                               valign='bottom')
#           if self.out2 is not None:
#               self.g_out2 = Label(pos= (self.pos_dot[0] + DIAMDOT, self.pos_dot[1] + DIAMDOT),
#                                   size=(DIAMDOT, DIAMDOT),
#                                   text=str(self.out2),
#                                   color=(0, 0, 1, 1),
#                                   markup=True,
#                                   halign='left',
#                                    valign='bottom')

    def draw_dot(self, Canvas):
        if self.flag_routed:
            with Canvas:
                self.dot = Ellipse(pos=self.pos_dot, size=(DIAMDOT, DIAMDOT))
        else:
            if self.dot is not None:
                self.dot = None


def Counter(rnum, wedge_density, inner_ring):
        wedge_count = int((2 * PI) * (inner_ring + (rnum * CORRIDOR)) // CORRIDOR)
        wedge_cap = int(fmod(wedge_count, wedge_density))

        wedge_count -= wedge_cap
        wedge_level = (wedge_count / wedge_density)
        wedge_level2 = frexp(wedge_level)
        if wedge_level2[0] <> 0.5:
            wedge_count = wedge_density * (2 ** (wedge_level2[1] - 1))
        return wedge_count


class switch(object):

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


if __name__ == '__main__':
    MazeGeneratorApp().run()


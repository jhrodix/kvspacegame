from kivy.app import App
from kivy.lang import builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.utils import QueryDict
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color
import random

from kivy.config import Config
Config.set('graphics', 'width', '200')
Config.set('graphics', 'height', '200')

class Square(Widget):
    red= NumericProperty(0)
    green=NumericProperty(1)
    blue=NumericProperty(0)
    alpha=NumericProperty(1)
    def receive_attack(self,bullet):
        if self.collide_widget(bullet): 
            self.green=0
            self.blue=0 
            return True
        return False

class Enemy(Widget):
    direction_x=1
    def move(self):
        x,y = self.pos
        x,y = (x+1*self.direction_x,y-0.1)
        if x>800 or x<0:
            self.direction_x*=-1
        self.pos=(x,y)

class Bullet(Widget):
    age=50
    state=1

    def move(self):
        if self.state==1:
            x,y = self.pos
            x,y = (x,y+10)
            self.pos = (x,y)
            self.age-=1

    def setState(self,state):
        self.state=state

class Ship(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    bullets = []
    def move(self):
        self.pos = Vector(*self.velocity)+self.pos

class SpaceGame(Widget):
    myship= ObjectProperty(None)
    mybullets = []
    myenemies = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def destroy_bullet(self,bullet):
        self.remove_widget(bullet)
        self.mybullets.remove(bullet) 

    def try_kill_enemy(self,bullet):
        for e in self.myenemies:
            tmp = [x for x in e.ids.keys()]
            for s in tmp:
                if e.ids[s] and e.ids[s].receive_attack(bullet):
                    #self.destroy_bullet(bullet)
                    bullet.setState(0)
                    e.ids[s]=None

    def move_or_destroy_bullet(self,bullet):
        if bullet.age>0 and bullet.state: 
            bullet.move()
        else:
            self.destroy_bullet(bullet)

    def update_bullets(self):
        for x in self.mybullets:
            self.try_kill_enemy(x)
            self.move_or_destroy_bullet(x)

    def move_enemy(self):
        for e in self.myenemies:
            e.move()

    def shut(self):
        tmp = Bullet()
        x,y = self.myship.pos
        tmp.pos=(x+10,y+10)
        self.add_widget(tmp)
        self.mybullets+=[tmp]

    def update(self,dt):
        self.myship.move()
        self.update_bullets()
        for e in self.myenemies:
            e.move()

    def on_touch_move(self, touch):
        self.myship.center_x = touch.x

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def create_enemy(self,dt):
        e=Enemy(pos=(300,500))
        e.direction_x = random.choice([1,-1])
        self.myenemies+=[e]  
        self.add_widget(e)

    def _on_keyboard_down(self,keyboard,keycode,text,modifiers):
        if keycode[1]=='f':
            self.myship.center_x += 10
        if keycode[1]=='a':
            self.myship.center_x -= 10
        if keycode[1]=='j':
            self.shut()     
        return True

class SpaceGameApp(App):
    def build(self):
        game = SpaceGame()
        Clock.schedule_interval(game.update, 1.0/60.0)
        Clock.schedule_interval(game.create_enemy, 5.0)
        return game

SpaceGameApp().run()

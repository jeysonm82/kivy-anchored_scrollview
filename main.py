# -*- coding: utf-8 -*-
""" Script de arranque que inicializa la interfaz gráfica
de la App"""
import os
from kivy.config import Config
Config.set('graphics', 'width', '640')
Config.set('graphics', 'height', '980')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.lang import Factory
from kivy import properties as props
import sys
import traceback
from kivy.uix.behaviors import FocusBehavior
from kivy.clock import Clock
from kivy.lang import Builder
import time
from functools import partial


class InnerScroll(ScrollView):

    def simulate_touch_down(self, touch):
        return super(InnerScroll, self).simulate_touch_down(touch)

    def on_scroll_move(self, touch):
        if self.handle_touch:
            return super(InnerScroll, self).on_scroll_move(touch)

    def on_scroll_start(self, touch, check_children=True):
        print "START", self.handle_touch
        if self.handle_touch:
            return super(InnerScroll, self).on_scroll_start(touch, check_children)
        else:
            #self.simulate_touch_down(touch)
            pass

    def on_scroll_stop(self, touch, check_children=True):
       if self.handle_touch:
           return super(InnerScroll, self).on_scroll_stop(touch, check_children)
       else:
            Clock.schedule_once(partial(self._do_touch_up, touch), .2)

class AnchoredScrollView(ScrollView):
   anchor = props.ObjectProperty(None)
   content = props.ObjectProperty(None)
   viewport = props.ObjectProperty(None)
   inner_scroll = props.ObjectProperty(None)
   _sv_item = props.ObjectProperty(None)
   anchor_mode = props.StringProperty('top')
   _can_dispatch = True

   def _change_touch_mode(self, *largs):
       return
       """
       # Disable change_touch_mode logic when anchored or scroll_y = 1.0,
       # this makes internal scrollview behaves correctly.
       if self.scroll_y == 0 or self.scroll_y == 1.0:
           return
       return super(AnchoredScrollView, self)._change_touch_mode(largs)
       """

   def on_anchor(self, obj, value):
       self.anchor.bind(size=self.calc_viewport_height)
       self.anchor.bind(pos=self.calc_viewport_height)

   def calc_viewport_height(self, *args):
       ah = [c.height for c in self._viewport.children if c != self.anchor and c != self.inner_scroll]
       self.viewport.height = self.height + sum(ah)
       self._trigger_update_from_scroll()

  
   def on_scroll_start(self, touch, check_children=True):
       if self.scroll_y > 0:
           check_children =  False
       return super(AnchoredScrollView, self).on_scroll_start(touch, check_children)

   def on_scroll_stop(self, touch, check_children=True):
       if self.scroll_y > 0:
           check_children =  False
       return super(AnchoredScrollView, self).on_scroll_stop(touch, check_children)

   def on_scroll_move(self, touch):
        height = self.height
        dy = touch.dy / float(height - height * self.vbar[1])
        touch.push()
        touch.apply_transform_2d(self.to_local)

        if dy > 0:
            if self.scroll_y == 0:
                # Scrolling down from 1 to 0
                self.inner_scroll.handle_touch = True
                if self.dispatch_children('on_scroll_move', touch):
                        return True
                return True
            else:
                self.inner_scroll.handle_touch = False
        else: #dy<0

            # Scrolling up. from 0 to 1
            if self.scroll_y == 1:
                self.inner_scroll.handle_touch = True
                if self.dispatch_children('on_scroll_move', touch):
                    return True
                pass
            elif self.scroll_y > 0:
                self.inner_scroll.handle_touch = False


        touch.pop()
        self._can_dispatch = False
        s = super(AnchoredScrollView, self).on_scroll_move(touch)
        self._can_dispatch = True
        return s

   def dispatch_children(self, ev, *args):
       if self._can_dispatch:
           return super(AnchoredScrollView, self).dispatch_children(ev, *args)

   def add_widget(self, widget, index=0):
       if isinstance(widget, SvItem):
           self._sv_item = widget
           self._sv_item.bind(content=self._process_svitem)
       else:
           return super(AnchoredScrollView, self).add_widget(widget, index)


   def _process_svitem(self, *args):
       """Adds widgets from svitem to self"""
       if self._sv_item is None or self.inner_scroll is None:
           return

       svitem = self._sv_item

       for c in list(svitem.children):
           c.parent.remove_widget(c)
           if c == svitem.content:
               self.inner_scroll.add_widget(c)
           else:
               self._viewport.add_widget(c, len(self._viewport.children))
               if c == svitem.anchor:
                   self.anchor = c



class SvItem(Widget):
    anchor = props.ObjectProperty(None)
    content = props.ObjectProperty(None)

kv="""
#:import effects kivy.effects

<AnchoredScrollView>:
    bar_width: 6
    viewport: _viewport
    inner_scroll: _isv
    effect_cls: effects.scroll.ScrollEffect

    BoxLayout:
        id: _viewport
        orientation: 'vertical'
        size_hint_y: None
        height: 100

        InnerScroll:
            id: _isv
            effect_cls: effects.scroll.ScrollEffect
            handle_touch: True
"""
Builder.load_string(kv)

if __name__ in ('__main__', '__android__'):
    kv = """
TabbedPanel:
    do_default_tab: False
    TabbedPanelItem:
        text: "1"
        AnchoredScrollView:

            SvItem:
                anchor: _lbl
                content: _bl
                AsyncImage:
                    source: "http://lorempixel.com/700/400/"
                    size_hint_y: None
                    height: 400

                Label:
                    id: _lbl
                    size_hint_y: None
                    height: 100
                    text: "Header"

                BoxLayout:
                    id: _bl
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 2000
                    padding: 4
                    canvas:
                        Color:
                            rgba: 0.8, 0.3, 0.2, 0.8
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    Button:
                        text: "Hello "+str(self.uid)
                        on_press: print self
                    Button:
                        text: "Hello "+str(self.uid)
                        on_press: print self
                    Button:
                        text: "Hello "+str(self.uid)
                        on_press: print self
                    Button:
                        text: "Hello "+str(self.uid)
                        on_press: print self
                    Button:
                        text: "Hello "+str(self.uid)
                        on_press: print self
                    Button:
                        text: "Hello "+str(self.uid)
                        on_press: print self

    """

    class TestApp(App):
        def build(self):
            return Builder.load_string(kv)


    app = TestApp()
    app.run()

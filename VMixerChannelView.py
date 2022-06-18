import socket
import sys
import time
import random
from scene import *
from ui import Path, ScrollView

DEBUG = True

class MyFader(ShapeNode):
    def __init__(self, *args, **kwargs):
        self.length = 240
        super().__init__(Path.rounded_rect(0, 0, 20, self.length, 10), '#444', *args, **kwargs)
        self.knob = ShapeNode(Path.oval(0, 0, 25, 25), '#fefefe', parent=self)
        # value ranges from 0 to 1, at least for now
        self.knob_size = 25
        self.set_raw_value(0.0)
        self.dragging = False
        
    def handle_touch_begin(self, pos, panel_pos):
        kx, ky = self.knob.point_from_scene(pos)
        if abs(kx) > 10:
            return
        if abs(ky) > 25:
            return
        self.dragging = True

    def handle_touch_drag(self, pos, panel_pos):
        sx, sy = self.point_from_scene(pos)
        if self.dragging:
            self.update_value(sy)
        return self.dragging
    
    def handle_touch_ended(self, pos, panel_pos):
        sx, sy = self.point_from_scene(pos)
        if self.dragging:
            self.dragging = False
            self.update_value(sy)
            return True
        return False
        
    def update_value(self, y):
        y_adjusted = min(max(0, y + self.length / 2 - self.knob_size), self.length - self.knob_size)
        y_adjusted /= self.length - self.knob_size
        self.set_raw_value(y_adjusted)

    def update_knob_pos(self):
        y = (self.value - 0.5) * (self.length - self.knob_size)
        self.knob.position = (0, y)

    def get_raw_value(self):
        return self.value
        
    def set_raw_value(self, val):
        self.value = val
        self.update_knob_pos()

class ScrollBar(ShapeNode):
    def __init__(self, knob_shape, knob_color, *args, initial_value=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.knob = ShapeNode(knob_shape, knob_color, parent=self)
        self.knob.anchor_point = (0, 1)
        self.value = initial_value
    
    def get_value(self):
        return self.value
    
    def set_value(self, val):
        self.value = val

class HorizontalScrollBar(ScrollBar):
    def __init__(self, width, height, color, knob_color, *args, initial_value=1.0, **kwargs):
        super().__init__(
            Path.oval(0, 0, height, height),
            knob_color,
            Path.rounded_rect(0, 0, width, height, height/2),
            color,
            *args,
            **kwargs
        )
        self.knob
        self.knob_size = height
        self.length = width
        self.anchor_point = (0, 1)
        self.dragging = False
        
    def update_value(self, x):
        x_adjusted = min(max(0, x - self.knob_size/2), self.length - self.knob_size)
        self.knob.position = (x_adjusted, 0)
        x_adjusted /= self.length - self.knob_size
        self.set_value(x_adjusted)

    def handle_touch_begin_safe(self, pos):
        cx, cy = self.knob.position
        x, y = pos
        if abs(x - cx - self.knob_size/2) < 50:
            self.dragging = True
            #update_value(x)

    def handle_touch_drag_safe(self, pos):
        if self.dragging:
            self.update_value(pos[0])
        return self.dragging
    
    def handle_touch_ended_safe(self, pos):
        if self.dragging:
            self.update_value(pos[0])
            self.dragging = False
            return True
        return False
        

class RFader(MyFader):
    def __init__(self, *args, init_value='0.0', **kwargs):
        super().__init__(*args, **kwargs)
        self.set_value(init_value)
    
    def get_value(self):
        value = self.get_raw_value()
        if value < 0.02:
            return 'INF'
        temp_val = value - 0.02
        temp_val /= 98
        temp_val *= 90
        temp_val -= 80
        return '{:.1f}'.format(temp_val)
        
    def set_value(self, val):
        if val.lower() == 'inf':
            self.set_raw_value(0.0)
        f = float(val)
        f += 80
        f /= 90
        f * 98
        self.set_raw_value(f + 0.02)

class MyButton(ShapeNode):
    def __init__(self, label, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button_text = LabelNode(label, font=('Monospace', 18), parent=self)
        self.button_held = False
        self.action = action
    
    # called for EVERY touch, not just ones in the area of the button
    def handle_touch_begin(self, pos, panel_pos):
        if self.frame.contains_point(pos):
            self.action(self.command)
            self._reverseHeldAnimation()
    
    def handle_touch_move(self, pos, panel_pos):
        self.handle_selection(pos)

    def handle_touch_ended(self, pos, panel_pos):
        self.handle_selection(pos)

    def _setHeldTrue(self):
        self.button_held = True

    def _setHeldFalse(self):
        self.button_held = False
        
    def _runHeldAnimation(self):        
        self.run_action(
            Action.sequence(
                Action.scale_to(1.125, 0.05),
                Action.call(self._setHeldTrue)
            )
        )
    
    def _reverseHeldAnimation(self):
        self.run_action(
                Action.sequence(
                    Action.scale_to(1, 0.05),
                    Action.call(self._setHeldFalse)
                )
        )
    
    # like above comment
    def handle_selection(self, pos):
        if not self.is_visible:
            return
        if self.frame.contains_point(pos):
            if not self.button_held:
                self._runHeldAnimation()
        elif self.button_held:
            self._reverseHeldAnimation()

class UnmuteButton(MyButton):
    def __init__(self, path, action, label, id, *args, **kwargs):
        super().__init__(label, action, path, '#3f3', '#040', *args, **kwargs)
        self.command = 'MUC:' + str(id) + ',0'

class MuteButton(MyButton):
    def __init__(self, path, action, label, id, *args, **kwargs):
        super().__init__(label, action, path, '#f33', '#400', *args, **kwargs)
        self.command = 'MUC:' + str(id) + ',1'


class Main(Scene):    
    def setup(self):
        self.CHANNEL_COUNT = 25 # 16 out, 8 mtx, main
        self.CHANNEL_SCREEN_WIDTH = 68
        self.SCROLLBAR_HEIGHT = 30
        self.panel_height = self.bounds.height - self.SCROLLBAR_HEIGHT
        self.panel_width = max(self.bounds.width, self.CHANNEL_SCREEN_WIDTH * self.CHANNEL_COUNT)
        self.root_node = Node(parent=self, position=(0, self.SCROLLBAR_HEIGHT))
        self.scroll = HorizontalScrollBar(
            self.bounds.width,
            self.SCROLLBAR_HEIGHT,
            '#AAA',
            '#FFF',
            parent=self,
            position=(0, self.SCROLLBAR_HEIGHT)
        )
        self.panel = ShapeNode(
            Path(0, 0, self.panel_height, self.panel_width),
            parent=self.root_node
        )
        self.all_ui_elements = []
        for r in range(self.CHANNEL_COUNT):
            self.all_ui_elements.append(
                RFader(parent=self.panel, position=(self.CHANNEL_SCREEN_WIDTH * (r + 0.5), self.panel_height / 2))
            )
        
    
    def update_scroll_pos(self):
        self.root_node.position = (
            min(0, -self.scroll.get_value() * (self.panel_width - self.bounds.width)),
            self.SCROLLBAR_HEIGHT
        )
    
    def touch_ended(self, touch):
        pos = touch.location
        if self.scroll.handle_touch_ended_safe(pos):
            self.update_scroll_pos()
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            elem.handle_touch_ended(pos, pos_panel)
    
    def touch_moved(self, touch):
        pos = touch.location
        #if pos[1] >= self.bounds.height - SCROLLBAR_HEIGHT:
        if self.scroll.handle_touch_drag_safe(pos):
            self.update_scroll_pos()
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            elem.handle_touch_drag(pos, pos_panel)
    
    def touch_began(self, touch):
        pos = touch.location
        if pos[1] <= self.SCROLLBAR_HEIGHT:
            self.scroll.handle_touch_begin_safe(pos)
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            elem.handle_touch_begin(pos, pos_panel)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def send_command_stub(command):
    print(command)

def create_socket_and_send(command):
    #def sendAssertReply(command, expectedReply):
    #    reply = sendGetReply(command)
    #    assert reply == chr(2) + expectedReply + ";"
    
    
    def sendGetReply(command):
        reply = ''
        try:
            message = chr(2) + command + ';'
            sock.sendall(message)
            while len(reply) == 0 or reply[-1] != ';':
                reply += sock.recv(64)
    
        except socket.timeout:
            reply = None
    
        if reply:
            reply = reply.replace(chr(6), "<ack>")
            reply = reply.replace(chr(2), "<stx>")
    
        return reply
    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print('connecting to %s port %s' % server_address, file=sys.stderr)
    sock.connect(server_address)
    sock.settimeout(3)
    
    reply = sendGetReply(command)
    
    print(reply)
    
    print('closing socket', file=sys.stderr)
    sock.close()

'''
reply_dict = {}
for loop in range(100, 0, -1):

    for i in range(32):
        inputID = "I" + str(i + 1)
        command = ""
        command += "CNq:" + inputID + "&"
        command += "PIq:" + inputID + "&"
        command += "MUq:" + inputID + "&"
        command += "FDq:" + inputID

        reply = sendGetReply(command)
        expectedReply = reply_dict.get(inputID, "")
        if expectedReply:
            assert reply == expectedReply
            sys.stdout.write('.')
            sys.stdout.flush()
        else:
            reply_dict[inputID] = reply
            print(bcolors.OKBLUE + command + bcolors.ENDC)
            print(bcolors.OKGREEN + reply + bcolors.ENDC)

    command = ""
    for i in range(8):
        inputID = "AX" + str(i + 1)
        command += "CNq:" + inputID + "&"
    command += "SCq"
    reply = sendGetReply(command)
    expectedReply = reply_dict.get(inputID, "")
    if expectedReply:
        assert reply == expectedReply
        sys.stdout.write('.')
        sys.stdout.flush()
    else:
        reply_dict[inputID] = reply
        print(bcolors.OKBLUE + command + bcolors.ENDC)
        print(bcolors.OKGREEN + reply + bcolors.ENDC)

    delay = 5 + random.random()
    print("  %gs [%d]" % (delay, loop))
    time.sleep(delay)
'''

if __name__ == '__main__':
    run(Main())

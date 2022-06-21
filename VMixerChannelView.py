import socket
import sys
import time
import random
from scene import *
from ui import Path
from dialogs import form_dialog

DEBUG = False

class ChannelName(ShapeNode):
    def __init__(self, x_size, color, name, *args, **kwargs):
        # super is the label box
        super().__init__(Path.rect(0, 0, x_size, 50), *args, **kwargs)
        self.label_text = LabelNode(name, ('Monospace', 20), parent=self)
        self.update_label(color, name)
    
    def update_label(self, color, name):
        self.fill_color = {0:'#444'}[0]
        self.stroke_color = {0:'#222'}[0]
        self.name = name
        self.label_text.text = name
        
class DynamicLabel(ShapeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Path.rect(0, 0, 60, 20),
            '#444',
            '#222',
             *args,
             **kwargs
        )
        self.label_text = LabelNode('0.0 db', ('Monospace', 10), parent=self)
    
    def set_text(self, text_value):
        self.label_text.text = text_value + ' db'

class MyFader(ShapeNode):
    def __init__(self, *args, length=240, **kwargs):
        self.length = length
        super().__init__(Path.rounded_rect(0, 0, 20, self.length, 10), '#444', *args, **kwargs)
        self.knob = ShapeNode(Path.oval(0, 0, 25, 25), '#fefefe', parent=self)
        # value ranges from 0 to 1, at least for now
        self.knob_size = 25
        self.set_raw_value(0.0)
        self.dragging = False
        
    def handle_touch_begin(self, pos, panel_pos):
        kx, ky = self.knob.point_from_scene(pos)
        if abs(kx) > 25:
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
            self.send_command()
            return True
        return False
    
    def update_display(self):
        pass # intended to be implemented in a subclass
    
    def update_value(self, y):
        y_adjusted = min(max(0, y + self.length / 2 - self.knob_size), self.length - self.knob_size)
        y_adjusted /= self.length - self.knob_size
        self.set_raw_value(y_adjusted)
        self.update_display()

    def update_knob_pos(self):
        y = (self.value - 0.5) * (self.length - self.knob_size)
        self.knob.position = (0, y)

    def get_raw_value(self):
        return self.value
        
    def set_raw_value(self, val):
        self.value = val
        self.update_knob_pos()

class RFader(MyFader):
    def __init__(self, id, action, *args, init_value='0.0', length=240, **kwargs):
        super().__init__(*args, length=length, **kwargs)
        self.label = DynamicLabel(parent=self)
        self.label.position = (0, - self.path.bounds.height / 2 - 40)
        self.id = id
        self.command = 'FDC:' + str(id)
        self.action = action
        self.set_value(init_value)
        
    def send_command(self):
        self.action(self.command + ',' + self.get_value() + ',C')
    
    def get_value(self):
        value = self.get_raw_value()
        if value < 0.02:
            return 'INF'
        temp_val = value - 0.02
        temp_val /= 0.98
        temp_val *= 90
        temp_val -= 80
        return '{:.1f}'.format(temp_val)
        
    def update_display(self):
        value = self.get_value()
        self.label.set_text(value)
        
    def set_value(self, val):
        self.label.set_text(val)
        if val.lower() == 'inf':
            self.set_raw_value(0.0)
            return
        f = float(val)
        f += 80
        f /= 90
        f * 0.98
        self.set_raw_value(f + 0.02)

class RSendFader(RFader):
    def __init__(self, alt_command, send_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = alt_command + str(self.id) + ',' + send_id

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
        x_adjusted /= self.length - self.knob_size
        self.set_value(x_adjusted)
        
    def set_value(self, val):
        super().set_value(val)
        x_adjusted = val * (self.length - self.knob_size)
        self.knob.position = (x_adjusted, 0)
    
    def handle_touch_begin_safe(self, pos):
        cx, cy = self.knob.position
        x, y = pos
        if abs(x - cx - self.knob_size/2) < 50:
            self.dragging = True
        return True

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

class MyButton(ShapeNode):
    def __init__(self, label, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button_text = LabelNode(label, font=('Monospace', 18), parent=self)
        self.button_held = False
        self.action = action
    
    # called for EVERY touch, not just ones in the area of the button
    def handle_touch_ended(self, pos, panel_pos):
        if not self.button_held:
            return False
        self.button_held = False
        if not self.frame.contains_point(panel_pos):
            return False        
        self.action(self.command)
        self._reverseHeldAnimation()
        return True

    # like above
    def handle_touch_drag(self, pos, panel_pos):
        if not self.button_held:
            return False
        if not self.frame.contains_point(panel_pos):
            self._reverseHeldAnimation()
        else:
            self._runHeldAnimation()
        return True

    # like above
    def handle_touch_begin(self, pos, panel_pos):
        if not self.frame.contains_point(panel_pos):
            return False
        self.button_held = True
        self._runHeldAnimation()
        return True

    def _setHeldTrue(self):
        self.button_held = True

    def _setHeldFalse(self):
        self.button_held = False
        
    def _runHeldAnimation(self):        
        self.run_action(
            Action.scale_to(1.125, 0.05)
        )
    
    def _reverseHeldAnimation(self):
        self.run_action(
            Action.scale_to(1, 0.05)
        )

class UnmuteButton(MyButton):
    def __init__(self, path, action, label, id, *args, **kwargs):
        super().__init__(label, action, path, '#3f3', '#040', *args, **kwargs)
        self.command = 'MUC:' + str(id) + ',0'

class MuteButton(MyButton):
    def __init__(self, path, action, label, id, *args, **kwargs):
        super().__init__(label, action, path, '#f33', '#400', *args, **kwargs)
        self.command = 'MUC:' + str(id) + ',1'
        
class SendsButton(MyButton):
    def __init__(self, action, path, id, *args, **kwargs):
        super().__init__('SENDS', action, path, '#f83', '#420', *args, **kwargs)
        self.command = id

class Main(Scene):
    def __init__(self, *args, **kwargs):
        try:
            with open('.vmxproxypyipport', 'r') as f:
                self.ip = f.readline().strip()
                self.port = int(f.readline().strip())
        except Exception:
            data = form_dialog(
                'Configure Proxy', 
                [
                    {'title': 'IP', 'type': 'text'},
                    {'title': 'PORT', 'type': 'number'},
                    {'title': 'remember', 'type': 'check'}
                ]
            )
            self.ip = data['IP']
            self.port = int(data['PORT'])
            if data['remember']:
                with open('.vmxproxypyipport', 'w') as f:
                    f.write(self.ip + '\n' + str(self.port))
        super().__init__(*args, **kwargs)
    
    def setup(self):
        self.ch_ids = (
            ['AX'+str(v) for v in range(1, 9)]
            + ['MX'+str(v) for v in range(1, 5)]
            + ['MAL']
        )
        self.CHANNEL_COUNT = len(self.ch_ids) # 8 out, 4 mtx, main
        self.cmd = self.send_command_stub if DEBUG else self.create_socket_and_send
        self.CHANNEL_SCREEN_WIDTH = 128
        self.SCROLLBAR_HEIGHT = 30
        if orientation == DEFAULT_ORIENTATION:
            self.panel_height = min(self.bounds.width, self.bounds.height) - self.SCROLLBAR_HEIGHT
        else:
            self.panel_height = self.bounds.height - self.SCROLLBAR_HEIGHT
        self.panel_width = self.CHANNEL_SCREEN_WIDTH * self.CHANNEL_COUNT
        self.background_color = '#111'
        self.all_noninteractive_elems = []
        self.all_ui_elements = []
        self.get_channel_properties()
        self.create_ui_elements()
        self.dragging = False

    def get_channel_properties(self):
        # names
        self.channel_names = self.get_channel_names(self.ch_ids[:-1])
        if self.channel_names is None:
            self.channel_names = [None]*(self.CHANNEL_COUNT - 1)
        else:
            self.channel_names = [
                v.split('"')[1] if v.count('"') == 2
                else None
                for v in self.channel_names
            ]
        self.channel_names.append(None)
        # volumes
        self.init_volumes = self.get_channel_volumes(self.ch_ids)
        if self.init_volumes is None:
            self.init_volumes = ['0.0']*self.CHANNEL_COUNT
        else:
            self.init_volumes = [
                v.split(',')[1] if v.count(',') == 1
                else '0.0'
                for v in self.init_volumes
            ]
        
    def create_ui_elements(self):
        # main panel
        self.panel = ShapeNode(
            Path.rect(0, 0, self.panel_width, self.panel_height),
            self.background_color,
            parent=self,
            position=(
                0,
                self.SCROLLBAR_HEIGHT
            ),
            anchor_point=(0, 0)
        )
        # main scroll bar
        self.scroll = HorizontalScrollBar(
            self.bounds.width,
            self.SCROLLBAR_HEIGHT,
            '#AAA',
            '#FFF',
            parent=self,
            position=(0, self.SCROLLBAR_HEIGHT)
        )
        # channel elements
        for r, channel_id in enumerate(self.ch_ids):
            # name tag
            channel_name = self.channel_names[r]
            if channel_name is None:
                channel_name = (
                    'OUT ' + str(r+1) if r < 8
                    else 'MTX ' + str(r - 7) if r < 12
                    else 'MAIN'
                )
            self.all_noninteractive_elems.append(
                ChannelName(
                    self.CHANNEL_SCREEN_WIDTH * 7 / 8,
                    0,
                    channel_name,
                    parent=self.panel,
                    position=(
                        self.CHANNEL_SCREEN_WIDTH * (r + 0.5),
                        self.panel_height - 35
                    )
                )
            )
            self.all_ui_elements.append(
                RFader(
                    channel_id,
                    self.cmd,
                    init_value=self.init_volumes[r],
                    length=240 if self.bounds.height >= 600 else 120,
                    parent=self.panel,
                    position=(
                        self.CHANNEL_SCREEN_WIDTH * (r + 0.5),
                        self.panel_height / 2
                    )
                )
            )
            self.all_ui_elements.append(
                MuteButton(
                    Path.rect(0, 0, 60, 60),
                    self.cmd,
                    'M',
                    channel_id,
                    parent=self.panel,
                    position=((r+0.5) * self.CHANNEL_SCREEN_WIDTH, self.panel_height - 110)
                )
            )
            self.all_ui_elements.append(
                UnmuteButton(
                    Path.rect(0, 0, 60, 60),
                    self.cmd,
                    'U',
                    channel_id,
                    parent=self.panel,
                    position=((r+0.5) * self.CHANNEL_SCREEN_WIDTH, self.panel_height - 190)
                )
            )
            self.all_ui_elements.append(
                SendsButton(
                    self.show_sends,
                    Path.rect(0, 0, 80, 60),
                    channel_id,
                    parent=self.panel,
                    position=((r+0.5) * self.CHANNEL_SCREEN_WIDTH, 80)
                )
            )
            
    def show_sends(self, ch_id):
        sends_scene = SendsScene(self, ch_id)
        self.present_modal_scene(sends_scene)
            
    def mirror_scroll_pos(self):
        norm_pos = min(1,
            max(0,
                -self.panel.position.x / (self.panel_width - self.bounds.width)
            )
        )
        self.scroll.set_value(norm_pos)
    
    def update_scroll_pos(self):
        self.panel.position = (
            min(0, -self.scroll.get_value() * (self.panel_width - self.bounds.width)),
            self.SCROLLBAR_HEIGHT
        )
    
    def touch_ended(self, touch):
        pos = touch.location
        has_interacted = False
        if self.scroll.handle_touch_ended_safe(pos):
            self.update_scroll_pos()
            has_interacted = True
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            has_interacted = (has_interacted or
                elem.handle_touch_ended(pos, pos_panel)
            )
        if has_interacted:
            return True
        if self.dragging:
            self.dragging = False
            bounded_pos = max(
                -(self.panel_width - self.bounds.width), 
                min(0, self.panel.position.x)
            )
            self.panel.run_action(
                Action.sequence(
                    Action.move_to(
                        bounded_pos,
                        self.SCROLLBAR_HEIGHT,
                        0.5,
                        TIMING_SINODIAL
                    ),
                    Action.call(self.mirror_scroll_pos)
                )
            )
    
    def touch_moved(self, touch):
        pos = touch.location
        has_interacted = False
        #if pos[1] >= self.bounds.height - SCROLLBAR_HEIGHT:
        if self.scroll.handle_touch_drag_safe(pos):
            self.update_scroll_pos()
            has_interacted = True
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            has_interacted = (has_interacted or
                elem.handle_touch_drag(pos, pos_panel)
            )
        if has_interacted:
            return
        if self.dragging:
            dx = touch.location[0] - touch.prev_location[0]
            self.panel.run_action(Action.move_by(dx, 0, 0))
            self.mirror_scroll_pos()
    
    def touch_began(self, touch):
        pos = touch.location
        has_interacted = False
        if pos[1] <= self.SCROLLBAR_HEIGHT:
            self.scroll.handle_touch_begin_safe(pos)
            has_interacted = True
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            has_interacted = (has_interacted or
                elem.handle_touch_begin(pos, pos_panel)
            )
        if has_interacted:
           return
        self.dragging = True
        
    def get_channel_volumes(self, chids):
        return self.get_multiple_results(chids, self.get_channel_volume_query)
        
    def get_channel_names(self, chids):
        return self.get_multiple_results(chids, self.get_channel_name_query)
        
    def get_multiple_results(self, chids, query):
        results = query(chids)
        if not isinstance(results, str):
            return None
        return results.split(';')[:-1]
    
    
    def get_channel_volume_query(self, chid):
        if isinstance(chid, list):
            chid = '&FDQ:'.join(chid)
        return self.cmd('FDQ:' + chid)

    def get_channel_name_query(self, chid):
        if isinstance(chid, list):
            chid = '&CNQ:'.join(chid)
        return self.cmd('CNQ:' + chid)
    
    def send_command_stub(self, command):
        print(command)
    
    def create_socket_and_send(self, command):
        def sendGetReply(command):
            expected_results = command.count('&') + 1
            reply = b''
            try:
                message = chr(2) + command + ';'
                sock.sendall(bytes(message, 'ascii'))
                while reply.count(b';') < expected_results and reply[-1:] != bytes(chr(6), 'ascii'):
                    reply += sock.recv(64)
            except socket.timeout:
                reply = None
        
            if reply:
                reply = reply.replace(bytes(chr(6), 'ascii'), b"<ack>")
                reply = reply.replace(bytes(chr(2), 'ascii'), b"<stx>")
                reply = str(reply, 'ascii')
        
            return reply
    
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect the socket to the port where the server is listening
        server_address = (self.ip, self.port)
        #print('connecting to %s port %s' % server_address, file=sys.stderr)
        sock.connect(server_address)
        sock.settimeout(5)
        
        reply = sendGetReply(command)
        
        #print(reply)
        
        #print('closing socket', file=sys.stderr)
        sock.close()
        
        return reply

class SendsScene(Scene):
    def __init__(self, parent_scene, ch_id, *args, **kwargs):
        self.parent_scene = parent_scene
        self.out_channel = ch_id
        super().__init__(*args, **kwargs)
    
    def setup(self):
        self.ch_ids = ['I'+str(i) for i in range(1, 33)]
        self.ch_count = len(self.ch_ids)
        self.panel_width = max(
            self.bounds.width,
            self.parent_scene.CHANNEL_SCREEN_WIDTH * self.ch_count
        )
        self.background_color = self.parent_scene.background_color
        self.cmd = self.parent_scene.cmd
        self.dragging = False
        self.all_noninteractive_elems = []
        self.all_ui_elements = []
        self.get_channel_properties()
        self.create_ui_elements()
    
    def get_channel_properties(self):
        # names
        self.channel_names = self.parent_scene.get_channel_names(self.ch_ids)
        if self.channel_names is None:
            self.channel_names = ['CH '+str(v) for v in range(1, 33)]
        else:
            self.channel_names = [
                v.split('"')[1] if v.count('"') == 2
                else 'CH '+str(i+1)
                for i, v in enumerate(self.channel_names)
            ]
        # volumes
        self.init_volumes = self.get_channel_volumes(self.ch_ids)
        if self.init_volumes is None:
            self.init_volumes = ['0.0']*self.ch_count
        else:
            self.init_volumes = [
                v.split(',')[1] if v.count(',') == 1 else v.split(',')[2] if v.count(',') == 3
                else '0.0'
                for v in self.init_volumes
            ]
    
    def create_ui_elements(self):
        # main panel
        self.fake_panel = ShapeNode(
            Path.rect(0, 0, self.bounds.width, self.parent_scene.panel_height),
            self.background_color,
            parent=self,
            position=(
                0,
                self.parent_scene.SCROLLBAR_HEIGHT
            ),
            anchor_point=(0, 0)
        )
        self.panel = Node(
            position=(0, self.parent_scene.SCROLLBAR_HEIGHT),
            parent=self
        )
        # scroll bar
        self.scroll = HorizontalScrollBar(
            self.bounds.width,
            self.parent_scene.SCROLLBAR_HEIGHT,
            '#AAA',
            '#FFF',
            parent=self,
            position=(0, self.parent_scene.SCROLLBAR_HEIGHT)
        )
        # close button - requires custom handling in touch handler because it floats
        self.close_button = MyButton(
            'X', lambda x:self.dismiss_modal_scene(),
            Path.rect(0, 0, 50, 50),
            '#F33',
            '#400',
            parent=self,
            position=(30, self.bounds.height-30)
        )
        self.close_button.command = None;
        # channel elements
        for r, channel_id in enumerate(self.ch_ids):
            # name tag
            channel_name = self.channel_names[r]
            self.all_noninteractive_elems.append(
                ChannelName(
                    self.parent_scene.CHANNEL_SCREEN_WIDTH * 7 / 8,
                    0,
                    channel_name,
                    parent=self.panel,
                    position=(
                        self.parent_scene.CHANNEL_SCREEN_WIDTH * (r + 0.5),
                        self.parent_scene.panel_height - 100
                    )
                )
            )
            self.all_ui_elements.append(
                RSendFader(
                    'FDC:' if self.out_channel == 'MAL' else
                    'AXC:' if self.out_channel[:2] == 'AX' else
                    'MXC:',
                    self.out_channel,
                    channel_id,
                    self.cmd,
                    init_value=self.init_volumes[r],
                    length=240 if self.bounds.height >= 600 else 120,
                    parent=self.panel,
                    position=(
                        self.parent_scene.CHANNEL_SCREEN_WIDTH * (r + 0.5),
                        self.parent_scene.panel_height / 2
                    )
                )
            )
    
    def aux_send_query(self, chid):
        temp = ',' + self.out_channel
        if isinstance(chid, list):
            chid = (temp + '&AXQ:').join(chid)
        return self.cmd('AXQ:' + chid + temp)
    
    def mtx_send_query(self, chid):
        temp = ',' + self.out_channel
        if isinstance(chid, list):
            chid = (temp + '&MXQ:').join(chid)
        return self.cmd('MXQ:' + chid + temp)
    
    def get_channel_volumes(self, chids):
        query = (
            self.parent_scene.get_channel_volume_query if self.out_channel == 'MAL' else
            self.aux_send_query if self.out_channel[:2] == 'AX' else
            self.mtx_send_query
        )
        return self.parent_scene.get_multiple_results(chids, query)
    
    def mirror_scroll_pos(self):
        norm_pos = min(1,
            max(0,
                -self.panel.position.x / (self.panel_width - self.bounds.width)
            )
        )
        self.scroll.set_value(norm_pos)
    
    def update_scroll_pos(self):
        self.panel.position = (
            min(0, -self.scroll.get_value() * (self.panel_width - self.bounds.width)),
            self.parent_scene.SCROLLBAR_HEIGHT
        )
    
    def touch_ended(self, touch):
        pos = touch.location
        has_interacted = self.close_button.handle_touch_ended(pos, pos)
        if has_interacted:
            return
        if self.scroll.handle_touch_ended_safe(pos):
            self.update_scroll_pos()
            has_interacted = True
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            has_interacted = (has_interacted or
                elem.handle_touch_ended(pos, pos_panel)
            )
        if has_interacted:
            return True
        if self.dragging:
            self.dragging = False
            bounded_pos = max(
                -(self.panel_width - self.bounds.width), 
                min(0, self.panel.position.x)
            )
            self.panel.run_action(
                Action.sequence(
                    Action.move_to(
                        bounded_pos,
                        self.parent_scene.SCROLLBAR_HEIGHT,
                        0.5,
                        TIMING_SINODIAL
                    ),
                    Action.call(self.mirror_scroll_pos)
                )
            )
    
    def touch_moved(self, touch):
        pos = touch.location
        has_interacted = self.close_button.handle_touch_drag(pos, pos)
        if has_interacted:
            return
        #if pos[1] >= self.bounds.height - SCROLLBAR_HEIGHT:
        if self.scroll.handle_touch_drag_safe(pos):
            self.update_scroll_pos()
            has_interacted = True
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            has_interacted = (has_interacted or
                elem.handle_touch_drag(pos, pos_panel)
            )
        if has_interacted:
            return
        if self.dragging:
            dx = touch.location[0] - touch.prev_location[0]
            self.panel.run_action(Action.move_by(dx, 0, 0))
            self.mirror_scroll_pos()
    
    def touch_began(self, touch):
        pos = touch.location
        has_interacted = self.close_button.handle_touch_begin(pos, pos)
        if has_interacted:
            return
        if pos[1] <= self.parent_scene.SCROLLBAR_HEIGHT:
            self.scroll.handle_touch_begin_safe(pos)
            has_interacted = True
            return
        pos_panel = self.panel.point_from_scene(pos)
        for elem in self.all_ui_elements:
            has_interacted = (has_interacted or
                elem.handle_touch_begin(pos, pos_panel)
            )
        if has_interacted:
           return
        self.dragging = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    orientation = DEFAULT_ORIENTATION
    if min(get_screen_size()) < 600:
        # lock to portrait orientation for small devices
        orientation = PORTRAIT
    run(Main(), orientation)

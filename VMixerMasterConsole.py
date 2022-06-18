import socket
import sys
import time
import random
from scene import *
from ui import Path

DEBUG = True

class myFader(ShapeNode):
    def __init__(self, layout, action, *args, **kwargs):
        super().__init__(Path.rect(), *args, **kwargs)
    
    def get_value():
        return self.value

class MyButton(ShapeNode):
    def __init__(self, label, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button_text = LabelNode(label, font=('Monospace', 18), parent=self)
        self.button_held = False
        self.action = action
    
    # called for EVERY touch, not just ones in the area of the button
    def handle_touch(self, pos):
        if self.frame.contains_point(pos):
            self.action(self.command)
            self._reverseHeldAnimation()
    
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
    
    # like above
    def handle_selection(self, pos):
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
        self.mute_scene = Node(parent=self)
        self.volume_scene = Node(parent=self, position=(self.bounds.width, 0))
        self.scenes = [self.mute_scene, self.volume_scene]
        action = send_command_stub if DEBUG else create_socket_and_send
        self.muteGroupMuteButtons = []
        for i in range(8):
            self.muteGroupMuteButtons.append(MuteButton(
                Path.rect(
                    0,
                    0,
                    48,
                    48,
                ),
                action,
                'MG'+str(i + 1),
                'G'+str(i + 1),
                position=(
                    (i + 4.5) * self.bounds.width / 16,
                    256 + self.bounds.height / 2    
                ),
                parent=self
            ))
        self.muteGroupUnmuteButtons = []
        for i in range(8):
            self.muteGroupUnmuteButtons.append(UnmuteButton(
                Path.rect(
                    0,
                    0,
                    48,
                    48,
                ),
                action,
                'UG'+str(i + 1),
                'G'+str(i + 1),
                position=(
                    (i + 4.5) * self.bounds.width / 16,
                    192 + self.bounds.height / 2    
                ),
                parent=self
            ))
        self.muteButtons = []
        for i in range(32):
            self.muteButtons.append(MuteButton(
                Path.rect(
                    0,
                    0,
                    48,
                    48,
                ),
                action,
                'M'+str(i + 1),
                'I'+str(i + 1),
                position=(
                    ((i % 16) + 0.5) * self.bounds.width / 16,
                    (96 if i < 16 else 32) + self.bounds.height / 2
                ),
                parent=self
            ))
        self.unmuteButtons = []
        for i in range(32):
            self.muteButtons.append(UnmuteButton(
                Path.rect(
                    0,
                    0,
                    48,
                    48,
                ),
                action,
                'U'+str(i + 1),
                'I'+str(i + 1),
                position=(
                    ((i % 16) + 0.5) * self.bounds.width / 16,
                    (-32 if i < 16 else -96) + self.bounds.height / 2
                ),
                parent=self
            ))
        self.panicButton = MuteButton(
            Path.rect(
                0,
                0,
                128,
                64,
            ),
            action,
            'MUTE ALL',
            'I1-32',
            position=(
                0.5 * self.bounds.width,
                0.25 * self.bounds.height
            ),
            parent=self
        )
        self.allButtons = [self.panicButton] \
            + self.muteGroupMuteButtons + self.muteGroupUnmuteButtons \
            + self.muteButtons + self.unmuteButtons;
        
    def touch_ended(self, touch):
        pos = self.point_from_scene(touch.location)
        for button in self.allButtons:
            button.handle_touch(pos)
            
    def touch_moved(self, touch):
        pos = self.point_from_scene(touch.location)
        for button in self.allButtons:
            button.handle_selection(pos)
            
    def touch_began(self, touch):
        pos = self.point_from_scene(touch.location)
        for button in self.allButtons:
            button.handle_selection(pos)


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

from bluetooth import *
from threading import Thread
import RPi.GPIO as GPIO
from qhue import Bridge

from light_sensor import rc_time

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(3)
uuid = "00001101-0000-1000-8000-00805f9b7541"
advertise_service(server_sock, "JRServer",
                  service_id = uuid,
                  service_classes = [uuid, SERIAL_PORT_CLASS],
                  profiles = [SERIAL_PORT_PROFILE]
                )

global client_sock, light_state
client_sock = None
light_state = False
light_sensor_state = False
bridge = Bridge("192.168.1.175", "CPwFyahZcgzQ8c1pGRpG8kZz30t3Dl0HVa6j0SgO")
light = bridge.lights[5]

def set_light(state):
  global light_state
  if state == light_state:
    return
  light_state = state
  if state:
    print('On')
    light.state(on=True)
    # TODO actually turn the light on
    if client_sock is not None:
      client_sock.send('1|')
    else:
      print('No connection')
  else:
    print('Off')
    light.state(on=False)
    # TODO actually turn the light off
    if client_sock is not None:
      client_sock.send('0|')
    else:
      print('No connection')

class LightSensorManager(Thread):
  def read_light(self):
    return rc_time() > 1000
  def run(self):
    light_state = self.read_light()
    try:
      while True:
        new_light_state = self.read_light()
        if new_light_state != light_state:
          light_state = new_light_state
          set_light(new_light_state)
    finally:
      GPIO.cleanup()
LightSensorManager().start()

def handle_connection(client_sock):
  data = ''
  while True:
    read = client_sock.recv(32)
    print 'Partial message: ', repr(read)
    if read == '':
      return
    data = data + read
    while '|' in data:
      message = data[:data.index('|')]
      data = data[data.index('|')+1:]
      print 'Got message', repr(message), 'remaining:', repr(data)

      if message == '0':
        set_light(False)
      elif message == '1':
        set_light(True)
      elif message == '?':
        if light_state:
          client_sock.send('1|')
        else:
          client_sock.send('0|')
      else:
        print('Unknown message ' + repr(message))

try:
  while True:
    print 'Waiting for connection'
    client_sock, client_info = server_sock.accept()
    try:
      handle_connection(client_sock)
    except BluetoothError:
      print('Lost connection')
    finally:
      client_sock.close()
finally:
  server_sock.close()

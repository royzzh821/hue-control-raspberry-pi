from bluetooth import *

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(3)

client_sock = None
uuid = "dd88ab89-517f-489d-05cf95300b15"

def set_light(state):
  # TODO set the light
  if state:
    print('On')
    # TODO actually turn the light on
    client_sock.send('1|')
  else:
    print('Off')
    # TODO actually turn the light off
    client_sock.send('0|')

def handle_connection(client_sock):
  data = ''
  while True:
    read = client_sock.recv(32)
    if read == '':
      return
    data = data + read
    while '|' in data:
      message = data[:data.index('|')]
      data = data[data.index('|')+1:]

      if message == '0':
        set_light(True)
      elif message == '1':
        set_light(False)
      # TODO other messages

try:
  while True:
    print 'Waiting for connection'
    client_sock, client_info = server_sock.accept()
    try:
      handle_connection(client_sock)
    finally:
      client_sock.close()
finally:
  server_sock.close()

import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12347               # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.
print("Was listening before...")

while True:
   c, addr = s.accept()     # Establish connection with client.
   print( 'Got connection from', addr )
   #c.send(1)
   output = 'Thank you for connecting'
   c.sendall(output.encode('utf-8'))
   c.close()                # Close the connection


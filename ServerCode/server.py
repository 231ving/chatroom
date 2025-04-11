from threading import Thread
import socket

HOST = '127.0.0.1'
PORT = 5000
clients = []  # Array containing all client connections


def broadcast(message: str):
    """ Simply sends the message to all clients in chat.
    Args:
        message (str): The message string being broadcast to all clients
    Returns:
        none
    Except:
        Connection Error: If the message couldn't be sent to a client, remove said client.
    """

    global clients  # Use the global clients array
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            if client in clients:
                clients.remove(client)


def handle_client(sock: socket.socket, addr: tuple[str, int]):
    """ Handles the connection for a single client
    Args:
        sock (socket.socket): The socket object for the client
        addr: (IP Address, Port Number) of the client
    Returns:
        none
    """
    sock.send("Welcome to the chat! What's your username?".encode('utf-8'))
    try:
        data = sock.recv(1024).decode('utf-8')
    except:
        clients.remove(sock)
        print('Connection at', addr, 'unexpectedly terminated')
        sock.close()
        return
    if data == "{QUIT-CHAT}":
        clients.remove(sock)
        sock.close()
        return
    username = data
    print(f'User {username} has entered the chat.')
    broadcast(f'User {username} has entered the chat.')
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if data == "{QUIT-CHAT}":
                msg = username + " has left the chat."
                print(msg)
                clients.remove(sock)
                broadcast(msg)
                break
            elif data:
                msg = username + ': ' + data
                print(msg)
                broadcast(msg)
        except:
            print('Connection at', addr, 'unexpectedly terminated')
            return
    sock.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen()
while True:
    connection_socket, conn_addr = server_socket.accept()
    clients.append(connection_socket)
    t = Thread(target=handle_client, args=(connection_socket, conn_addr))
    t.start()
server_socket.close()

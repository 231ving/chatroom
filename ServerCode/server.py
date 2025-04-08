from threading import Thread
import socket
import queue

HOST = '127.0.0.1'
PORT = 5000
clients = []


def broadcast(message, sender_socket):
    global clients
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                if client in clients:
                    clients.remove(client)


def handle_client(sock, addr):
    # Handle communication with one client
    host, port = sock.getsockname()
    username = 'Client at ' + str(addr)
    sock.send("Welcome to the chat!\nWhat's your username?".encode('utf-8'))
    data = sock.recv(1024).decode('utf-8')
    username = data
    print(f'User {username} has entered the chat.')
    broadcast(f'User {username} has entered the chat.', host)
    while True:
        data = sock.recv(1024).decode('utf-8')
        if data == "{QUIT-CHAT}":
            msg = username + " has left the chat."
            print(msg)
            clients.remove(sock)
            broadcast(msg, host)
            break
        elif data:
            msg = username + ': ' + data
            print(msg)
            broadcast(msg, host)
    sock.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen()
while True:
    connection_socket, conn_add = server_socket.accept()
    clients.append(connection_socket)
    t = Thread(target=handle_client, args=(connection_socket, conn_add))
    t.start()
server_socket.close()

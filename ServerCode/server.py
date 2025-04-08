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
                client.send(message.encode())
            except:
                if client in clients:
                    clients.remove(client)


def handle_client(sock):
    # Handle communication with one client
    host, port = sock.getsockname()
    username = None
    while True:
        data = sock.recv(1024).decode()
        if data[0: 14] == "{Username-Set}":
            _, username = data.split(" ", 1)
            broadcast(username, host)
        elif data:
            text = username + ':\n' + data
            print(data)
            broadcast(data, host)


    #socket_thread = Thread(target=read_socket)
    #socket_thread.daemon = True  # Allow program to exit even if thread is running
    #socket_thread.start()

    # Remember to close the socket when done
    #sock.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen()
while True:
    connection_socket, _ = server_socket.accept()
    clients.append(connection_socket)
    t = Thread(target=handle_client, args=(connection_socket,))
    t.start()
server_socket.close()

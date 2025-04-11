import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import socket
import time


class App:
    """
    This class contains the GUI and contains operations to
     send and receive messages and update the GUI.
    """

    def __init__(self, master):
        """ Constructor for the Chat GUI
        Args:
            master: The Tkinter root object
        """
        self.master = master
        master.title("Socket Reader")

        self.text_area = ScrolledText(master, width=100, height=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.typing_area = ScrolledText(master, width=80, height=5)
        self.typing_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.send_button = tk.Button(master, text='Send', command=lambda: self.send_text())
        self.send_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 10))

        self.running = True

        self.receive_thread = threading.Thread(target=self.read_socket)
        self.receive_thread.start()

    def append_text(self, text: str):
        """ Appends text to the GUI's chat window and scrolls to the bottom of said chat window.
        Args:
            text (str): The text to be appended that was received from the server
        Returns:
            none
        """

        self.text_area.configure(state='normal')  # Enable editing temporarily
        self.text_area.insert(tk.END, text + '\n')
        self.text_area.configure(state='disabled')  # Disable editing again
        self.text_area.see(tk.END)  # Autoscroll to the bottom

    def send_text(self):
        """ Function for sending text to the chat server and resets the typing area for the next message.
        Returns:
            none
        Except:
            Server Error: If the server terminates unexpectedly, close the GUI
        """
        if self.running is True:
            msg = self.typing_area.get("1.0", tk.END)
            try:
                s.send(bytes(msg[:-1], 'utf8'))
                self.typing_area.delete("1.0", tk.END)
            except:
                self.append_text('Unexpected server termination. Chat closing.')
                self.send_button.destroy()
                self.typing_area.configure(state='disabled')
                self.close()

    def read_socket(self):
        """ Function for parsing the incoming data from the chat server.
        Returns:
            none
        Except:
            Server Error: If the server terminates unexpectedly, close the GUI
        """
        try:
            while self.running is True:
                if s:
                    data = s.recv(1024)
                    self.append_text(data.decode('utf-8'))
                    if not data:
                        break
        except:
            self.append_text('Unexpected server termination. Chat closing.')
            self.send_button.destroy()
            self.typing_area.configure(state='disabled')
            self.close()

    def close(self):
        """ Function handling how to close the App.
        Tries to tell the server that the user is leaving the chat as well
        Returns:
            none
        """
        self.running = False
        try:
            s.send('{QUIT-CHAT}'.encode('utf-8'))
            time.sleep(.1)
            s.close()
        finally:
            time.sleep(1)
            self.master.destroy()


host = '127.0.0.1'  # Or "localhost"
port = 5000

global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

root = tk.Tk()
root.geometry("500x400")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close)  # Handle window close event
root.mainloop()

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import socket
import queue
import time


class App:
    def __init__(self, master):
        self.master = master
        master.title("Socket Reader")

        self.text_area = ScrolledText(master, width=100, height=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.typing_area = ScrolledText(master, width=80, height=5)
        self.typing_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.send_button = tk.Button(master, text='Send', command=lambda: self.send_text())
        self.send_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 10))

        self.data_queue = queue.Queue()
        self.running = True

        host = '127.0.0.1'  # Or "localhost"
        port = 5000

        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self.username = None

        self.receive_thread = threading.Thread(target=self.read_socket)
        self.receive_thread.start()

        self.update_gui()

    def append_text(self, text):
        self.text_area.configure(state='normal')  # Enable editing temporarily
        self.text_area.insert(tk.END, text + '\n')
        self.text_area.configure(state='disabled')  # Disable editing again
        self.text_area.see(tk.END)  # Autoscroll to the bottom

    def send_text(self):
        if self.running is True:
            msg = self.typing_area.get("1.0", tk.END)
            if msg[:-1] == "{QUIT-CHAT}":
                self.typing_area.pack_forget()
                self.send_button.pack_forget()
            try:
                s.send(bytes(msg[:-1], 'utf8'))
                self.typing_area.delete("1.0", tk.END)
                if self.username is not None:
                    global master
                    self.username = msg
                    print(self.username)
                    self.master.title(f'User {self.username} in Chatroom')
            except:
                self.append_text('Unexpected server termination. Chat closing.')
                self.send_button.destroy()
                self.typing_area.configure(state='disabled')
                if s:
                    s.close()
                self.close()

    def read_socket(self):
        try:
            while self.running is True:
                if s:
                    data = s.recv(1024)
                    self.append_text(data.decode('utf-8'))
                    if not data:
                        break
                    self.data_queue.put(data.decode('utf-8'))
        except Exception as e:
            self.data_queue.put(f"Error: {e}")
            self.append_text('Unexpected server termination. Chat closing.')
            self.send_button.destroy()
            self.typing_area.configure(state='disabled')
            if s:
                s.close()
            self.close()

    def update_gui(self):
        try:
            data = self.data_queue.get_nowait()
        except queue.Empty:
            pass  # No data yet, ignore
        if self.running:
            self.master.after(100, self.update_gui)  # Check every 100 ms

    def close(self):
        self.running = False
        try:
            s.send('{QUIT-CHAT}'.encode('utf-8'))
            time.sleep(.1)
            s.close()
        finally:
            time.sleep(.5)
            self.master.destroy()


root = tk.Tk()
root.geometry("500x400")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close)  # Handle window close event
root.mainloop()
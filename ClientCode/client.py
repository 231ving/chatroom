import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import socket
import queue
# Use tkinter.scrolledtext module for textbox+scrollbar

class App:
    def __init__(self, master):
        self.master = master
        master.title("Socket Reader")

        self.label_text = tk.StringVar()
        self.label = tk.Label(master, textvariable = self.label_text)
        self.label.pack()
        self.text_area = ScrolledText(master, width=100, height=10)
        self.text_area.configure(state='disabled')
        self.text_area.pack(padx=10, pady=10)
        self.typing_area = ScrolledText(master, width=80, height=5, pady=5)
        self.typing_area.pack()

        self.send_button = tk.Button(master, text='Submit', command=lambda: self.send_text())
        self.send_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(0, 10))

        self.data_queue = queue.Queue()
        self.running = True

        self.receive_thread = threading.Thread(target=self.read_socket)
        self.receive_thread.daemon = True  # Allow program to exit even if thread is running
        self.receive_thread.start()
        self.send_thread = threading.Thread(target=self.send_text)
        self.text_area.insert(tk.END, 'Please enter your username')

        self.text_area.pack_forget()
        self.typing_area.pack_forget()
        self.send_button.pack_forget()

        self.frame = tk.Frame(master, bg='grey')
        self.frame.place(relx=.5, rely=.5)
        self.username_entry = tk.Entry(self.frame, width=15)
        self.username_entry.pack(anchor='center')
        self.username_submit = tk.Button(self.frame, text='Submit Username',command=lambda: self.send_username())
        self.username_submit.pack(anchor='center')

        self.update_gui()

    def append_text(self, text):
        self.text_area.configure(state='normal')  # Enable editing temporarily
        self.text_area.insert(tk.END, text + '\n')
        self.text_area.configure(state='disabled')  # Disable editing again
        self.text_area.see(tk.END)  # Autoscroll to the bottom

    def send_text(self):
        host = '127.0.0.1'  # Or "localhost"
        port = 5000
        print(self.typing_area.get("1.0", tk.END))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.send(self.typing_area.get("1.0", tk.END).encode())
                self.typing_area.delete("1.0", tk.END)
        except Exception as e:
             self.data_queue.put(f"Error: {e}")

    def send_username(self):
        host = '127.0.0.1'  # Or "localhost"
        port = 5000
        text_string = self.username_entry.get()
        text_string = '{Username-Set} ' + self.username_entry.get()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.send(text_string.encode())
                self.frame.destroy()
                self.text_area.pack()
                self.typing_area.pack()
                self.send_button.pack()
        except Exception as e:
            self.data_queue.put(f"Error: {e}")

    def read_socket(self):
        host = '127.0.0.1'  # Or "localhost"
        port = 5000         # Replace with your port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                while self.running:
                    data = s.recv(1024)
                    self.append_text(data.decode())
                    if not data:
                        break
                    self.data_queue.put(data.decode())
        except Exception as e:
             self.data_queue.put(f"Error: {e}")

    def update_gui(self):
        try:
            data = self.data_queue.get_nowait()
            #self.label_text.set(data)
        except queue.Empty:
            pass  # No data yet, ignore
        if self.running:
            self.master.after(100, self.update_gui) # Check every 100 ms

    def close(self):
        self.running = False
        self.master.destroy()


root = tk.Tk()
root.geometry("500x300")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close) # Handle window close event
root.mainloop()
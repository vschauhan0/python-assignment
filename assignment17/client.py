# client.py
# Simple chat client with Tkinter UI.
# Connects to server.py above. Both send/receive messages.

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

BUFFER = 4096

class ClientUI:
    def __init__(self, root):
        self.root = root
        root.title("Chat Client")

        top = tk.Frame(root)
        top.pack(fill="x", padx=6, pady=6)

        tk.Label(top, text="Username:").pack(side="left")
        self.username_entry = tk.Entry(top)
        self.username_entry.pack(side="left", padx=(4,10))
        self.username_entry.insert(0, "ClientUser")

        tk.Label(top, text="Host:").pack(side="left")
        self.host_entry = tk.Entry(top, width=15)
        self.host_entry.pack(side="left", padx=(4,10))
        self.host_entry.insert(0, "localhost")

        tk.Label(top, text="Port:").pack(side="left")
        self.port_entry = tk.Entry(top, width=6)
        self.port_entry.pack(side="left", padx=(4,10))
        self.port_entry.insert(0, "12345")

        self.connect_btn = tk.Button(top, text="Connect", command=self.connect)
        self.connect_btn.pack(side="left")
        self.disconnect_btn = tk.Button(top, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=(6,0))

        self.status_var = tk.StringVar(value="Status: Disconnected")
        tk.Label(root, textvariable=self.status_var).pack(anchor="w", padx=6)

        self.chat_area = scrolledtext.ScrolledText(root, state="disabled", wrap="word", height=18)
        self.chat_area.pack(fill="both", expand=True, padx=6, pady=(4,6))

        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=6, pady=(0,6))
        self.msg_entry = tk.Entry(bottom)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        self.send_btn = tk.Button(bottom, text="Send", command=self.send_message, state="disabled")
        self.send_btn.pack(side="left")

        # networking
        self.sock = None
        self.recv_thread = None
        self.connected = False
        self.peer_name = None

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def append_text(self, txt):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, txt)
        self.chat_area.see(tk.END)
        self.chat_area.configure(state="disabled")

    def set_status(self, s):
        self.status_var.set("Status: " + s)

    def connect(self):
        if self.connected:
            return
        host = self.host_entry.get().strip()
        try:
            port = int(self.port_entry.get().strip())
        except:
            messagebox.showerror("Error", "Port must be integer")
            return
        username = self.username_entry.get().strip() or "ClientUser"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except Exception as e:
            messagebox.showerror("Connect failed", f"Could not connect to {host}:{port}\n{e}")
            try:
                s.close()
            except:
                pass
            return

        self.sock = s
        # send our username as first line
        try:
            s.sendall((username + "\n").encode("utf-8"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send username: {e}")
            s.close()
            self.sock = None
            return

        self.append_text(f"[SYSTEM] Connected to {host}:{port}\n")
        self.set_status(f"Connected to {host}:{port}")
        self.connected = True
        self.send_btn.config(state="normal")
        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="normal")

        self.recv_thread = threading.Thread(target=self.recv_loop, daemon=True)
        self.recv_thread.start()

    def recv_loop(self):
        sock = self.sock
        buffer = ""
        try:
            # read server's username first line
            while True:
                data = sock.recv(BUFFER)
                if not data:
                    raise ConnectionError("Server disconnected")
                buffer += data.decode("utf-8", errors="replace")
                if "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.peer_name = line.strip() or "Server"
                    self.append_text(f"[SYSTEM] Server username: {self.peer_name}\n")
                    break
            if buffer:
                for ln in buffer.split("\n"):
                    if ln:
                        self.append_text(f"{self.peer_name}: {ln}\n")
            while True:
                data = sock.recv(BUFFER)
                if not data:
                    raise ConnectionError("Server disconnected")
                txt = data.decode("utf-8", errors="replace")
                buffer += txt
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        self.append_text(f"{self.peer_name}: {line}\n")
        except Exception as e:
            self.append_text(f"[SYSTEM] Connection closed: {e}\n")
        finally:
            self.cleanup()

    def send_message(self):
        if not self.sock:
            messagebox.showwarning("Not connected", "Not connected to server")
            return
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        try:
            self.sock.sendall((msg + "\n").encode("utf-8"))
            self.append_text(f"You: {msg}\n")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            self.append_text(f"[ERROR] Send failed: {e}\n")
            self.cleanup()

    def disconnect(self):
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except:
            pass
        self.cleanup()

    def cleanup(self):
        self.connected = False
        self.peer_name = None
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.sock = None
        self.send_btn.config(state="disabled")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.set_status("Disconnected")

    def on_close(self):
        self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ui = ClientUI(root)
    root.mainloop()

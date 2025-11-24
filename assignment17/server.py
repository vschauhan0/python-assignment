# server.py
# Simple chat server with Tkinter UI.
# Accepts one client and then both sides can send/receive messages.

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

HOST = "0.0.0.0"   # listen on all interfaces
PORT_DEFAULT = 12345
BUFFER = 4096

class ServerUI:
    def __init__(self, root):
        self.root = root
        root.title("Chat Server")

        top = tk.Frame(root)
        top.pack(fill="x", padx=6, pady=6)

        tk.Label(top, text="Port:").pack(side="left")
        self.port_entry = tk.Entry(top, width=6)
        self.port_entry.pack(side="left", padx=(4,10))
        self.port_entry.insert(0, str(PORT_DEFAULT))

        self.start_btn = tk.Button(top, text="Start Listening", command=self.start_listen)
        self.start_btn.pack(side="left")
        self.stop_btn = tk.Button(top, text="Stop", command=self.stop_listen, state="disabled")
        self.stop_btn.pack(side="left", padx=(6,0))

        self.status_var = tk.StringVar(value="Status: Not listening")
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
        self.listen_sock = None
        self.client_sock = None
        self.client_addr = None
        self.recv_thread = None
        self.listen_thread = None
        self.listening = False
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

    def start_listen(self):
        if self.listening or self.connected:
            return
        try:
            port = int(self.port_entry.get().strip())
        except:
            messagebox.showerror("Error", "Port must be an integer")
            return
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.listen_sock.bind((HOST, port))
            self.listen_sock.listen(1)
        except Exception as e:
            messagebox.showerror("Error", f"Could not bind/listen: {e}")
            try:
                self.listen_sock.close()
            except:
                pass
            self.listen_sock = None
            return

        self.listening = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.set_status(f"Listening on port {port}")
        self.append_text(f"[SYSTEM] Listening on port {port}\n")
        self.listen_thread = threading.Thread(target=self.accept_loop, daemon=True)
        self.listen_thread.start()

    def accept_loop(self):
        try:
            while self.listening and not self.connected:
                try:
                    self.listen_sock.settimeout(1.0)
                    client, addr = self.listen_sock.accept()
                except socket.timeout:
                    continue
                self.client_sock = client
                self.client_addr = addr
                self.append_text(f"[SYSTEM] Client connected from {addr}\n")
                # perform username handshake: server expects client to send username first,
                # but to be robust we read the first line and treat it as peer name.
                self.recv_thread = threading.Thread(target=self.recv_loop, daemon=True)
                self.connected = True
                self.recv_thread.start()
                self.send_btn.config(state="normal")
                self.set_status(f"Connected to {addr}")
                break
        except Exception as e:
            self.append_text(f"[ERROR] Accept loop: {e}\n")
        finally:
            try:
                if self.listen_sock:
                    self.listen_sock.close()
            except:
                pass
            self.listen_sock = None
            self.listening = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def recv_loop(self):
        sock = self.client_sock
        buffer = ""
        try:
            # read first line as peer name
            while True:
                data = sock.recv(BUFFER)
                if not data:
                    raise ConnectionError("Client disconnected")
                buffer += data.decode("utf-8", errors="replace")
                if "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.peer_name = line.strip() or "Peer"
                    self.append_text(f"[SYSTEM] Peer username: {self.peer_name}\n")
                    break
            # process remaining buffer lines
            if buffer:
                for ln in buffer.split("\n"):
                    if ln:
                        self.append_text(f"{self.peer_name}: {ln}\n")
            # main receive loop
            while True:
                data = sock.recv(BUFFER)
                if not data:
                    raise ConnectionError("Client disconnected")
                txt = data.decode("utf-8", errors="replace")
                buffer += txt
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        self.append_text(f"{self.peer_name}: {line}\n")
        except Exception as e:
            self.append_text(f"[SYSTEM] Connection closed: {e}\n")
        finally:
            self.cleanup_connection()

    def send_message(self):
        if not self.client_sock:
            messagebox.showwarning("Not connected", "No client is connected")
            return
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        try:
            self.client_sock.sendall((msg + "\n").encode("utf-8"))
            self.append_text(f"You: {msg}\n")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            self.append_text(f"[ERROR] Send failed: {e}\n")
            self.cleanup_connection()

    def stop_listen(self):
        self.listening = False
        try:
            if self.listen_sock:
                self.listen_sock.close()
        except:
            pass
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.set_status("Not listening")
        self.append_text("[SYSTEM] Stopped listening\n")

    def cleanup_connection(self):
        self.connected = False
        self.peer_name = None
        try:
            if self.client_sock:
                self.client_sock.close()
        except:
            pass
        self.client_sock = None
        self.client_addr = None
        self.send_btn.config(state="disabled")
        self.set_status("Disconnected")

    def on_close(self):
        self.listening = False
        try:
            if self.listen_sock:
                self.listen_sock.close()
        except:
            pass
        try:
            if self.client_sock:
                self.client_sock.shutdown(socket.SHUT_RDWR)
                self.client_sock.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ui = ServerUI(root)
    root.mainloop()

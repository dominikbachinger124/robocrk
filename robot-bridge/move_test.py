import socket, time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect(('192.168.2.1', 40923))

def send(cmd, wait=0.3):
    print("→", cmd)
    s.send(cmd.encode())
    time.sleep(wait)
    try:
        r = s.recv(1024); print("←", r); return r
    except socket.timeout:
        print("⏱️ TIMEOUT"); return None

try:
    send("command;")
    time.sleep(1)
    send("version ?;")
    send("robot mode ?;")     # 🧪 Welcher Modus ist aktiv?
    send("battery ?;")        # 🧪 Noch eine Abfrage
finally:
    s.close()                 # ✅ NUR schließen, KEIN quit;!
    print("🔒 Socket zu (ohne quit)")

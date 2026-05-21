import paramiko
import socket
import threading
from database import init_db, log_attempt

# Honeypot settings
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 2222       # Using 2222 instead of 22 to avoid conflicts

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        """This is called every time someone tries to login."""
        log_attempt(self.client_ip, username, password)
        return paramiko.AUTH_FAILED  # Always reject, we're a honeypot

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

def generate_key():
    """Generate a fake RSA host key."""
    return paramiko.RSAKey.generate(2048)

def handle_connection(client_socket, client_ip, host_key):
    """Handle each incoming SSH connection."""
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(host_key)

        server = FakeSSHServer(client_ip)
        transport.start_server(server=server)

        # Wait a bit then close
        transport.join(timeout=10)

    except Exception as e:
        print(f"[ERROR] {client_ip} -> {e}")
    finally:
        client_socket.close()

def start_honeypot():
    """Start the honeypot SSH listener."""
    init_db()
    host_key = generate_key()

    # Create the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"[*] Honeypot listening on {HOST}:{PORT}")

    while True:
        client_socket, client_addr = server_socket.accept()
        client_ip = client_addr[0]
        print(f"[+] Connection from {client_ip}")

        # Handle each connection in a separate thread
        thread = threading.Thread(
            target=handle_connection,
            args=(client_socket, client_ip, host_key)
        )
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_honeypot()
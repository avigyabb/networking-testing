import socket

HOST = ''           # Listen on all interfaces
PORT = 65432        # Arbitrary non-privileged port

print("Starting server...")

def recv_counter():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("Server listening on port", PORT)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    print("No data received. Closing connection.")
                    break
                try:
                    # Convert received data to an integer
                    counter = int(data.decode())
                except ValueError:
                    print("Received invalid data:", data)
                    continue
                # Increment the counter
                counter += 1
                print("Received counter, incremented to:", counter)
                # Send the new counter back to the client
                conn.sendall(str(counter).encode())

def recv_matrix():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("Server listening on port", PORT)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(2048)
                if not data:
                    print("No data received. Closing connection.")
                    break
                try:
                    # Convert received data to an integer
                    # counter = int(data.decode())
                    print(data)
                except ValueError:
                    print("Received invalid data:", data)
                    continue
                # print("Received counter, incremented to:", counter)
                # Send the new counter back to the client
                conn.sendall(data)

if __name__ == "__main__":
    # recv_counter()
    recv_matrix()
import socket
import time
import subprocess
from time import sleep
import torch


# SSH tunnel configuration
SSH_USER = 'ubuntu'
SSH_HOST = '38.128.233.70'
LOCAL_PORT = 65432
REMOTE_PORT = 65432

def create_tunnel():
    # Kill any existing tunnels first
    subprocess.run(['pkill', '-f', f'ssh.*{LOCAL_PORT}:localhost:{REMOTE_PORT}'])

    # Create SSH tunnel
    # -N: do not execute a remote command (don't create the interactive shell)
    # -L: local port forwarding
    # -T: disable pseudo-terminal allocation (prevents SSH from daemonizing)
    ssh_command = f'ssh -N -T -L {LOCAL_PORT}:localhost:{REMOTE_PORT} {SSH_USER}@{SSH_HOST}'
    print(f"Creating SSH tunnel: {ssh_command}")
    # can pass in string if shell=True, but there are security risks
    # subprocess.Popen() runs as a child process of python script
    # no need to terminate the tunnel process, it will close automatically when script ends (child process)
    # ~ for some reason, we still need to kill the child process manually
    tunnel_process = subprocess.Popen(ssh_command.split())
    return tunnel_process

def ping_counter(tunnel_process):
    HOST = 'localhost'
    PORT = LOCAL_PORT

    try:
        counter = 0
        print("Starting client...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
                # Send the current counter value to the server
                print("Sending counter:", counter)
                s.sendall(str(counter).encode())
                # Wait for the server's response
                data = s.recv(1024)
                if not data:
                    print("No response received. Exiting.")
                    break
                try:
                    counter = int(data.decode())
                    if counter == 10:
                        print("Counter reached 10. Exiting.")
                        break
                except ValueError:
                    print("Invalid data received:", data)
                    break
                print("Received new counter:", counter)
                # Pause a bit to see the output clearly
                time.sleep(1)
    finally:
        # Explicitly kill the tunnel process
        print("Cleaning up SSH tunnel...")
        tunnel_process.kill()  # More forceful than terminate()
        tunnel_process.wait()  # Wait for the process to actually end
        print("SSH tunnel closed")

def ping_matrix(tunnel_process, size):
    HOST = 'localhost'
    PORT = LOCAL_PORT

    try:
        print("Starting matrix client...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            for i in range(10):
                # Create a random 3x3 tensor
                matrix = torch.randint(0, 100, (size, size), dtype=torch.int32)
                print("Sending matrix:\n", matrix)
                
                # Serialize the tensor to bytes
                matrix_bytes = matrix.numpy().tobytes()
                s.sendall(matrix_bytes)
                
                # Wait for the server's response
                data = s.recv(2048)
                if not data:
                    print("No response received. Exiting.")
                    break
                try:
                    # Deserialize the received data to a tensor
                    received_matrix = torch.frombuffer(data, dtype=torch.int32).reshape(size, size)
                    print("Received matrix:\n", received_matrix)
                except Exception as e:
                    print("Error decoding received matrix:", e)
                    break
                
                # Pause to see the output clearly
                time.sleep(1)
    finally:
        # Explicitly kill the tunnel process
        print("Cleaning up SSH tunnel...")
        tunnel_process.kill()
        tunnel_process.wait()
        print("SSH tunnel closed")


if __name__ == "__main__":
    # Start timer
    start_time = time.time()
    tunnel_process = create_tunnel()
    # Wait a moment for the tunnel to establish
    sleep(2)
    tunnel_time = time.time()
    # ping_counter(tunnel_process)
    ping_matrix(tunnel_process, 32)
    # Calculate and print total execution time
    end_time = time.time()
    print(f"Execution time: {end_time-tunnel_time:.2f} seconds")
    print(f"Tunnel setup time: {tunnel_time - start_time:.2f} seconds")

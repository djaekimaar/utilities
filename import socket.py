import socket
import logging

target_host = 'www.google.com'
target_port = 80

# create a tcp client for a given host and port
def create_tcp_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except socket.error as e:
        logging.error("Error connecting to %s:%d - %s" % (host, port, e))
        return None

    return client   

# send data to a client
def send_data(client, data):
    try:
        client.send(data)
    except socket.error as e:
        logging.error("Error sending data: %s" % e)
        return False
    return True

# receive data from a client
def receive_data(client):
    try:
        return client.recv(4096)
    except socket.error as e:
        logging.error("Error receiving data: %s" % e)
        return None

# print the response
def print_response(response):
    print(response)

# close the client
def close_client(client):
    client.close()

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    client = create_tcp_client(target_host, target_port)
    if client is None:
        logging.error("Failed to create TCP client")
        exit(1)
        
    if not send_data(client, b'GET / HTTP/1.1\r\nHost: google.com\r\n\r\n'):
        close_client(client)
        exit(1)
        
    response = receive_data(client)
    if not response:
        logging.error("No response from %s:%d" % (target_host, target_port))
    else:
        print_response(response)
    close_client(client)

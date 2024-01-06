'''
Made by avycado13
'''
import socket
import threading
import argparse
from cryptography.fernet import Fernet

parser = argparse.ArgumentParser(description='Chat Server')
parser.add_argument('--host', '-h', type=str, default='127.0.0.1', help='Host IP address')
parser.add_argument('--port', '-p', type=int, default=7976, help='Port number')
parser.add_argument('--blacklist', '-b', type=str, help='Path to blacklist file')
parser.add_argument('--whitelist', '-w', type=str, help='Path to whitelist file')
parser.add_argument('--password', '-pwd', type=str, help='Password for the server')
args = parser.parse_args()

HOST = args.host
PORT = args.port
PASSWORD = args.password

blacklist = []
if args.blacklist:
    with open(args.blacklist, 'r', encoding='utf8') as file:
        for line in file:
            blacklist.append(line.strip())

# Read the whitelist file and populate the whitelist list
whitelist = []
if args.whitelist:
    with open(args.whitelist, 'r', encoding='utf8') as file:
        for line in file:
            whitelist.append(line.strip())

# Enable whitelist if whitelist file is provided
whitelist_enabled = bool(args.whitelist)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

# Generate a random encryption key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def broadcast(message):
    '''
    broadcasts message to all clients
    '''
    encrypted_message = cipher_suite.encrypt(message)
    for client in clients:
        client.send(encrypted_message)

def handle(client):
    '''
    handles messages and user leave
    '''
    while True:
        try:
            encrypted_message = client.recv(1024)
            # Get the client's IP address
            
            broadcast(encrypted_message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left!'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    '''
    handles join
    '''
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        client_address = client.getpeername()[0]
            
            # Check if the client's IP address is in the blacklist
        if client_address in blacklist:
                # Ignore the message from the blacklisted client
                client.close()
            
            # Check if the whitelist is enabled and the client's IP address is not in the whitelist
        if whitelist_enabled and client_address not in whitelist:
                # Ignore the message from the client not in the whitelist
                client.close()
        client.send('KEY\n'.encode('ascii') + key.encode('ascii'))
        if PASSWORD:
            client.send('PASSWORD'.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            if password != PASSWORD:
                client.send('WRONG PASSWORD'.encode('ascii'))
                client.close()
                continue
        client.send('NICKNAME'.encode('ascii'))
        nickname = cipher_suite.decrypt(client.recv(1024).decode('ascii'))
        nicknames.append(nickname)
        clients.append(client)
        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined!".encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()

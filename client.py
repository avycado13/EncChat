'''
Made by avycado13
'''
import socket
import threading
import argparse
import configparser
import os
from cryptography.fernet import Fernet

home_dir = os.path.expanduser("~")

# Read from the configuration file
config = configparser.ConfigParser()

try:
    with open(os.path.join(home_dir, '.encchatrc'), encoding='utf8') as f:
        config.read_file(f)
    HOST_DEFAULT = config.get('DEFAULT', 'Host')
    PORT_DEFAULT = config.getint('DEFAULT', 'Port')
    PASSWORD_DEFAULT = config.get('DEFAULT', 'Password')
except (configparser.Error, IOError):
    HOST_DEFAULT = '127.0.0.1'
    PORT_DEFAULT = 7976
    PASSWORD_DEFAULT = None

parser = argparse.ArgumentParser(description='EncChat Client')

parser.add_argument('--host', '-h', type=str, default=HOST_DEFAULT, help='Host IP address')
parser.add_argument('--port', '-p', type=int, default=PORT_DEFAULT, help='Port number')
parser.add_argument('--password', '-pwd', type=str, nargs='?', default=PASSWORD_DEFAULT, help='Password for the server')

args = parser.parse_args()

HOST = args.host
PORT = args.port
PASSWORD = args.password
nickname = input("Choose your nickname: ")

# socket initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))  # connecting client to server

def receive():
    while True:  # making valid connection
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'KEY':
                lines = message.splitlines()
                key = lines[1].strip()
                global cipher_suite
                cipher_suite = Fernet(key)
            if message == 'PASSWORD':
                if PASSWORD:
                    password = PASSWORD
                else:
                    password = input(f'Password for {HOST}: ')
                client.send(cipher_suite.encrypt(password).encode('ascii'))
            if message == 'NICKNAME':
                client.send(cipher_suite.encrypt(nickname).encode('ascii'))
            else:
                print(message)
        except (BrokenPipeError, ConnectionResetError):
            print("Connection closed by the client!")
            client.close()
            break
        except (socket.gaierror, ConnectionRefusedError):
            print("Invalid IP address or port!")
            client.close()
            break
        except Exception as e:  # case on wrong ip/port details
            print(f"An error occured: {str(e)}")
            client.close()
            break


def write():
    while True:  # message layout
        message = f'{nickname}: {input("")}'
        encrypted_message = cipher_suite.encrypt(message)
        client.send(encrypted_message.encode('ascii'))


receive_thread = threading.Thread(
    target=receive)  # receiving multiple messages
receive_thread.start()
write_thread = threading.Thread(target=write)  # sending messages
write_thread.start()

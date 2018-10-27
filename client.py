import threading
import sys
from time import sleep
import re
import yaml
from Crypto.Cipher import AES
import grpc

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import messenger_pb2 as chat;
import messenger_pb2_grpc as rpc;

address = 'localhost'

name = ''
othername = ''

with open("config.yaml", 'r') as stream:
    try:
        yaml_file = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

port = yaml_file['port']

class Client:

    def __init__(self, u: str, user_list):
        self.name = u
       
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)

        nUsr = chat.User()
        nUsr.name = u
        nRetUsr = chat.User()
        nRetUsr = self.conn.CheckMessageList(nUsr)

        if(nRetUsr.name != "NA"):
            askToChat = input(nRetUsr.name + " is requesting to chat with you. Enter 'yes' to accept or different user: ")
            if(askToChat == "yes"):
                o = nRetUsr.name
            else:
                o = askToChat
        else:
            o = input("[Spartan] Enter a user whom you want to chat with: ")

        if o not in user_list:
            print(o + " is not allowed to use the messenger.")
            print("Try again with one of the following users: " + ','.join(str(x) for x in user_list))
            return

        print("[Spartan] You are now ready to chat with " + o + ".")

        n = chat.User()
        n.name = u
        n.othername = o
        self.othername = o
        if(not(self.conn.CreateConnection(n).successful)):
            print("[Spartan] Connection failed!!")
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        self.send_message()
    
    def encrypt_message(self, message):
        byte_message = message.encode()
        key = b"Sixteen byte key"

        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(byte_message)
        file_out = open("encrypted.bin", "wb")
        [ file_out.write(x) for x in (nonce, tag, ciphertext) ]
        return(nonce, ciphertext, tag)

    def decrypt_message(self, nonce, ciphertext, tag):
        key = b'Sixteen byte key'
        
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        byte_message = cipher.decrypt_and_verify(ciphertext, tag)
        
        message = byte_message.decode()
        
        return(message)

    def __listen_for_messages(self):

        nl = chat.User()
        nl.name = self.name
        nl.othername = self.othername
        def findWholeWord(w, s):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search(s)
        while True:
            for note in self.conn.ChatStream(nl):
                message = self.decrypt_message(note.nonce, note.ciphertext, note.tag)
                if(findWholeWord(nl.name, message) == None):
                    print(message)
    
    def send_message(self):

        n1 = chat.WarningMsg
        try:
            while True:
                msg = input("[" + self.name + "] > ")
                message = "[" + self.name + "] " + msg
                n = chat.Msg()
                n.name = self.name
                n.othername = self.othername

                encrypted_msg = self.encrypt_message(message)
                n.nonce = encrypted_msg[0]
                n.ciphertext = encrypted_msg[1]
                n.tag = encrypted_msg[2]

                n1 = self.conn.SendMessage(n)
                for w in n1:
                    if(w.warning != ""):
                        print(w.warning)
        except KeyboardInterrupt:
            print("\nBye {}".format(name))
            
if __name__ == '__main__':
    name = ""
    try:
        print('[Spartan] Connected to Spartan Server at port {}.'.format(port))
        if len(sys.argv) != 2:
            name = input("[Spartan] What's your name?: ")
        else:
            name = sys.argv[1]
        yaml_file = {}
        with open("config.yaml", 'r') as stream:
            try:
                yaml_file = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        users = yaml_file['users']

        if name in users:
            user_list = users
            user_list.remove(name)

            print("[Spartan] User list: " + ','.join(str(x) for x in user_list))

            c = Client(name, user_list)
        else:
            print(name + " is not allowed to use the messenger.")
            print("Try again with one of the following users: " + ','.join(str(x) for x in users))
    except KeyboardInterrupt:
            print("\nBye {}".format(name))
import socket
import os
import threading
from Models.Message import Message
import time

class Client:
    def __init__(self):
        # all the client's attributes
        self.PORT = 50000
        self.SERVER = ""
        print("Input the address of the server")
        self.SERVER = input("> ")
        self.ADDR = (self.SERVER, self.PORT)
        self.DISCONNECT_MESSAGE = "goodbye"
        self.message = Message(object)
        self.Connected = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        try:
            self.client.connect(self.ADDR)
        except:
            print("[CONNECTION ERROR]Could not connect to host.\nEither the host isn't up or your not connected to the network.")

        try:
            #Message handler will deal with the sending of all messages.
            self.message = Message(self.client)
            self.Connected = True

        except:
            print("Error creating the message Handler")
            self.Connected = False

        self.handleServer()

    def handleServer(self):
        print("\n[LISTENING FOR MESSAGES]")
        # Constantly listening to the server for messages.
        while self.Connected:
            try:
                msg = self.message.read()

                try:
                    self.processMessage(msg)
                    self.send("Process Completed")
                except:
                    print("Error processing message")
            except:
                print("\n[CONNECTION ERROR] Disconnecting")
                self.connected = False
                break
            print(f"{msg}")

    # this will send our message into the message handler
    def send(self, msg):
        time.sleep(0.5)
        if msg == "":
            # empty strings caused my encryption to give out bad results so ive added this to the client
            print("please dont send empty strings... it breaks the server.")
        else:
            write = self.message.write(msg)

    def processMessage(self, message):
        print("\n[MESSAGE PROCESSING]")
        if message.lower() == "shutdown":
            self.shutdown()


    def shutdown(self):
        os.system('shutdown -s')

# let's run out client!!!!
client = Client()
client.run()

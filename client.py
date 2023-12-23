import socket #we import from py library
import time
import uuid
import datetime
import threading

class TimeoutInputThread(threading.Thread): #this is a funtion that allows the functions to run in parallel rather than waiting for them to finish since we need it for timeout
    def __init__(self):
        threading.Thread.__init__(self)
        self.result = None

    def run(self):
        try:
            self.result = input("\033[1;32mEnter an integer: ")
        except:
            pass


mezahost = 'localhost'
host = str(mezahost)
serverport = 12000
#initializing the ports
try:
    clientsocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket1.connect((host, serverport)) #connecting to ports
except ConnectionError:
    print("\033[1;31mThere was a connection error. Please check your connection and try again later.")
#in case of connection error

welcomemessagefromserver = clientsocket1.recv(1024).decode()
print(welcomemessagefromserver)#recieve welcome message

connect1= True
for i in range(3):
    if not connect1: #if a client has disconnected we need to exit the game hence the break
        break
    outputfrom1 = None#initalize output to be none
    try:
        message = clientsocket1.recv(2048).decode()#recieve the number or game over message
    except socket.error as err: #in case of disconnection we need to abort the game
        if err.errno == 10053 or err.errno == 10054:
            print("\033[1;31mPlayers has disconnected.")
            break
        else:
            raise
    if "game over" in message: #if the client recieves game over they need to stop exceuting the code
        print("\033[1;31mGame over")
        connect1 = False
        break
    else:
        messageint = message #if the client reccieved the number they  need to continue the game and print it
        
    try:
        print("\033[1;30mRandom number from server", messageint) #recieving number and recording time for timeout 
        input_thread = TimeoutInputThread()
        input_thread.start()
        input_thread.join(timeout=5)
        print("\n\n")
        if input_thread.is_alive():
            print("\033[1;31mError: Timeout occurred")
            break
        else:
            outputfrom1 = input_thread.result
        
        if outputfrom1: #if the player entered a number out of range or the input wasnt a number we have to raise value error
            outputfrom1 = int(outputfrom1)
            if (outputfrom1 < 0 or outputfrom1 > 9) and outputfrom1 != None:
                raise ValueError 
            else:
                clientsocket1.sendall(str(outputfrom1).encode()) #if no value error we send the number
    
    except ValueError:
            print("\033[1;31mThe number you entered is out of range, please try again later") 
    outputfrom1 = None #reinitialize output to be none

    

clientsocket1.close()

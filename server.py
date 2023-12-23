import random
import time
import socket
from socket import *
import pygame

pygame.init()
pygame.mixer.music.load("bensound-summer_mp3_music.mp3")  
pygame.mixer.music.play()#adding music got it from link: https://www.askpython.com/python-modules/pygame-adding-background-music

number_of_players_max = 2 #number of payers is a variable and can be updated to any number but we chose 2 for simplicity of executing the game 
number_of_rounds = 3 #also a variable
timeout = 10 #used in case a player takes too long or disconnects mid game

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(('localhost', serverPort))
serverSocket.listen(number_of_players_max)

RTT = [[0,0] for i in range(number_of_players_max)] #creatng an array where its inputs are arrays which specifies tthat each player has 2 inputs, one for his player number in the game and the other for his round trip time
Score = [0 for i in range(number_of_players_max)] #an array keeping track of the scores of the players
Socket = [] #storing the sockets of the players
Disqualified = [] #storing the disqualified players if any to be able to extract their numbers
timeoutL = [] #storing the timedout playrs if any to be able to extract their numbers

print('\033[1;33m\U0001F525Welcome to EECE 350 game\nThe server is ready to receive\U0001F525\n')
Welcome_Message = "\033[1;32mWELCOME TO THE DELAY OF DOOM\U0001F480"
cap_wel_message = Welcome_Message.upper()

nb = 0
while nb < number_of_players_max: #we need to check that we have the required minimum numbers of players present to be able to start the game
    
    connectionSocket, addr = serverSocket.accept() 
    Socket.append(connectionSocket) #after we accept connections from sockets we add then to the socket array
    connectionSocket.send(str(Welcome_Message).encode()) #we send the welcome message
    nb += 1 #we incremenet nb everytime a player joins till we get minimum amount of players needed 
disconnection= False #consider an initial condition where no one has disconnected
for i in range(number_of_rounds): #we need to repeat the following code for all players and then for multiple rounds hence the 2 for loops
    for j in range(nb):
        if j in timeoutL: #check if the player has timed out
            RTT[j][1] = "TMT" # thier input would be that player has timed out
        else:
            RTT[j][0] = j #we initialize the round trip time to the players number
            random_num = str(random.randint(0,9))
            x1 = time.time() #start measuring time it takes for players to input their numbers
            try: #check if any of the players disconnected
                Socket[j].send(random_num.encode()) #send random number
                Socket[j].settimeout(timeout) #set timeout time
            except OSError as e: #this is used to check if a player has disconnected and error 10054 is if player has forcibly diconnected
                if e.errno==10054:
                    print("\033[1;31mGame over")
                    disconnection=True #we set that disconnection has occured 
                    break#we get out of the loop
            try:
                num_str = Socket[j].recv(2048).decode() #we need to recieve players input if any
            except OSError as e: #with every step we need to check if player has disconnected to be bale to see if we can go on to the next instruction or no
                if e.errno==10054:
                    print("\033[1;31mGame over")
                    disconnection=True
                    break
            x2 = time.time()#stop recording time
            try:
                if (int(num_str) == int(random_num)):
                    RTT[j][1] = x2 - x1 #if the number entered is corrected, we record rtt and put it in second index of the players array
                else:
                    RTT[j][1] = "DQ" 
                    Disqualified.append(RTT[j][0])#if disqaulified(nb didnt match) we have to append it to the disqualified array and set its rtt to dq

            except Exception: #if timeout occurs
                RTT[j][1] = "TMT"
                timeoutL.append(RTT[j][0])#we add said player number to the timeout array
    if disconnection:# if a player did disconnect we need to send that the game is over and get out of the first for loop
        try:
            Socket[j].send("\033[1;31mGame over".encode())
        except OSError as e:
            if e.errno == 10054:
                print("\033[1;31mCould not send game over to client")
        break
                


            
    if (len(Disqualified) != 0): 
        for n in range(len(RTT)-1,-1,-1):#we need to loop over rtt
            if(RTT[n][1]=="DQ"):#if there has been disqaulified players, we need to delete their rtts since we need to eliminate them for when we need to print rtts of players who did input a number
                del RTT[n]
                
    if (len(timeoutL) != 0):
        for n in range(len(RTT)-1,-1,-1): #the same concept appies here, if a player has timed out, we need to delete their rtt
            if(RTT[n][1]=="TMT"):
                del RTT[n]
                
    for d in range(len(RTT)-len(Disqualified)-len(timeoutL)-1,-1,-1):
        if RTT[d] == [0,0]: #we need to delete the ones that had an error
            del RTT[d]
            
    if(len(RTT) != 0):       
        sorted_list = sorted(RTT, key=lambda x: x[1])  #we sort rtt in increasing order of the second index of every index so that it would be easier to extract the winner
        for k in range(nb-len(Disqualified)-len(timeoutL)):

            print("\033[1;34mThe RTT \U0001F570 of Player ",RTT[k][0]+1," \033[1;34mis ", round(RTT[k][1],2))
        #printing rtts of each player
    for m in range(len(Disqualified)):
        print("\033[1;31mPlayer ", Disqualified[m]+1, " \033[1;31mhas typed in a wrong number!")
        #printing player numbers that were disqualified
    for f in range(len(timeoutL)):
        print("\033[1;31mPlayer ", timeoutL[f]+1, " \033[1;31mhas timed out, no more answers will be recieved from this player!")
        #printing player numbers that timed out
    if(len(Disqualified)+len(timeoutL)!=nb) and len(RTT) != 0:
        player = sorted_list[0][0]#if there was a player who was not disqualified nor timed out, we extract him from the sorted array(first index of the first index of the sorted_list)
        print("\033[1;33mThe winner in round", "\033[1;33m"+str(i+1), " \033[1;33mis player ","\033[1;33m"+str(player+1) ,"\033[1;33mwith RTT: ","\033[1;33m"+str(round(RTT[player-len(Disqualified)-len(timeoutL)][1],2)) ,"\n\n")
        #we print said player
        Score[player] += 1 #edit the score of the player by one to keep track of his wins

    else:
        print("\033[1;31mNobody has gained a point!\n")
        

    RTT = [[0,0] for i in range(number_of_players_max)] #reinitalize for te new upcoming rounds
    Disqualified = []
for i in range(nb): #we need to send that the game over message was not recived by disconnected players
    try:
        Socket[i].send("\033[1;31mCould not send game over message to client".encode())
    except OSError as err: #for the disconnected ones that couldn't recieve it
        if err.errno == 10054:
            print("\033[1;31mClient has disconnected")

if disconnection: #if a disconnection occurs we need to use the built in function in the Python sys module that allows us to end the execution of the program
    raise SystemExit(0)
maxScore = max(Score) #extract the max score of all rounds in general
for i in range(nb):
    Socket[i].close() #close all sockets 
winner = Score.count(maxScore)
if(winner ==1):
    print("\033[1;33m\U0001F389The winner is Player ", "\033[1;33m{}\033[0m".format(Score.index(maxScore)+1), "\033[1;33mwith a score of: ", "\033[1;33m{}\033[0m".format(maxScore), " \033[1;33mrounds\U0001F389")
else:
    draw = []
    for index, number in enumerate(Score):#iterating over score to check if scores of players are = to the maximum score. Source: https://realpython.com/python-enumerate/
        if number == maxScore:
            draw.append(index+1)#if score of player is = to max, we append him to lis draw whch means there are more than one winner
    print("\033[1;33mThere has been a draw between Players:", ', '.join(str(num) for num in draw))
    #source: https://stackoverflow.com/questions/29244076/list-with-numbers-and-strings-to-single-string-python
pygame.mixer.music.stop()
pygame.quit()

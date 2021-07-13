#PACKAGES TO BE IMPORTED
import socket
import select
import time

#NUMBER OF CLIENT REQUIRED TO START THE GAME
CLIENT_NUM = 3 
SCORE = 3
PORT = 6543

#TCP CONNECTION
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = PORT
s.bind(('',port))
s.listen(CLIENT_NUM)

# the NUM_CLIENT connections to the game participants
clients = [0]*CLIENT_NUM

for i in range(CLIENT_NUM): 
    clients[i], addr = s.accept()
    clients[i].send(str(i))
    print "Connection to player ",i," established."

time.sleep(0.001)

for i in range(CLIENT_NUM):
    clients[i].send(str(SCORE))

SB = [0]*CLIENT_NUM 
time.sleep

#QUIZ LOOP
while True: 
    
    time.sleep(0.001)
    #TELLS PLAYER NUMBER WHO BUZZED
    buzzed = -1
    
    question = raw_input("Enter Question to Ask : ")
    trueAnswerStr = raw_input("Enter Answer of Above Question: ")

    #CONVERTING TO LOWER CASE TO AVOID UPPER CASE ANSWER
    trueAnswer = (trueAnswerStr.lower()).split()

    for s in clients:
        s.send(question)
    for s in clients:
        s.setblocking(0)

    #GETTING BUZZER    
    while True:
       
        # 'r' MONITORS SELECT FOR READING BY SOURCES
        r, w, x = select.select(clients, [], [])
        s = r[0]

        #SEND PLAYER NUMBER WHO BUZZED
        buzzed = s.recv(1024)
        if buzzed:
            break
    
    buzzed = int(buzzed)
    print "Player", buzzed, "buzzed."

    #TELL OTHER PLAYER WHO BUZZED
    for i in range(CLIENT_NUM):
        s = clients[i]
        if i != buzzed:
            s.send(str(buzzed) + " buzzed.")
        else:
            s.send("You buzzed.")
    
    for s in clients:
        s.setblocking(1)
    time.sleep(0.1)
    givenAnswer = (clients[buzzed]).recv(1024)
    print "Given Your Answer: ", givenAnswer

    #TELL THE OTHER PLAYER WHO GAVE ANSWER
    for i in range(CLIENT_NUM):
        if i != buzzed:
            clients[i].send(givenAnswer)
    time.sleep(0.01)

    givenAnswer = (givenAnswer.lower()).split()

    answeredCorrectly = True

    print trueAnswer, givenAnswer
    
    #CHECK FOR CORRECT ANSWER
    for i in trueAnswer:
        if not (i in givenAnswer):
            answeredCorrectly = False
            break

    if answeredCorrectly:
        print "You Answered correctly."
        for s in clients:
            s.send("Correct!")
        SB[buzzed]+=1
    else:
        print "You Answered incorrectly."
        for s in clients:
            s.send("Incorrect!")

    #CONVERT SB(SCOREBOARD) INTO STRING TO SEND ACCROSS OTHERS
    SBStr = '' 
    time.sleep(0.01)

    for i in SB:
        SBStr += ' ' + str(i)

    for s in clients:
        s.send(trueAnswerStr)
        time.sleep(0.01)
        s.send(SBStr)
        
    time.sleep(0.01)

    #IF ANY PLAYER REACH THE WINNING SCORE THEN GAME STOPS
    if(SCORE in SB):
        for s in clients:
            s.send("0")
        break
    else:
        for s in clients:
            s.send("1")

time.sleep(0.01)

for i in range(CLIENT_NUM):    
    if SB[i] == SCORE:
        clients[i].send("Congratulations! You won")
    else:
        clients[i].send("Sorry! You lose")
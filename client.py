#PACKAGES TO BE IMPORTED 
import socket
import threading
import time
import random
import sys
import select
import termios

#CHANGES AS NEEDED
SERVER_IP = ''
PORT = 6543


try:

    # 's' IS NAME GIVVEN TO SOCKET, 'killrequest' FOOR MULTITHREADING 
    def receiveMessage(s,killRequest):

        #UNTIL NO CLIENT LOOK FOR BUZZER IT WILL LOOKFOR THE BUZZER
        while not killRequest.isSet(): 
            r, w, x = select.select([s], [], [])
            data = r[0].recv(1024)
            print data
            if data:
                killRequest.set()

    def sendMessage(s, userid, killRequest, youBuzzed):
        #NO OTHER CAN HIT THE BUZZER AS ONE HIT THEM
        while not killRequest.isSet():
            r, w, x = select.select([sys.stdin], [], [], 0.02)

            if r:
                s.send(str(userid))
                youBuzzed.set()
                time.sleep(0.01)
                break

    serverip = SERVER_IP
    serverport = PORT

    #ASSIGNING RANDOM PORT TO THE CLIENT
    clientport = random.randint(2000, 3000)

    #MAKING OF SOCKET SCORE AND PLAYER ID
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', clientport))
    s.connect((serverip, serverport))
    userid = s.recv(1024)
    print "You are player number ", userid
    win_score = s.recv(1024)
    print win_score, " points needed to win."

    #GAME LOOP
    continue_next_round = 1 
    
    #GOING TO NEXT ROUND
    while continue_next_round:
        
        question = s.recv(1024)
        #IF ANY PLAYER HIT THE BUZZER KILL THE THREAD WHICH RECEIVE FOR BUZZER
        killRequest = threading.Event()

        #CHECK WHETHER BUZZER WAS HITTED BY YOU
        youBuzzed = threading.Event()

        sendThread = threading.Thread(target = sendMessage, args = [s, userid, killRequest, youBuzzed]) #thread to hit the buzzer
        receiveThread = threading.Thread(target = receiveMessage, args = [s, killRequest]) #thread to hear if anyone else has hit buzzer

        time.sleep(0.1)
        print "Question Is:", question
        print "Press Buzzer to Answer "

        #ENABLE TO PERFORME FUNCTIONALITY FROM SERVER SIDE
        s.setblocking(0)
        sendThread.start()
        receiveThread.start()
        receiveThread.join()
        sendThread.join()

        #AFTER BUZZER IS OVER TURN SOCKET TO PERFORM SEQUENTIAL TASK
        s.setblocking(1)

        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
        time.sleep(0.01)
        if youBuzzed.isSet():
            print "Answer the question."
            givenAnswer = raw_input()
            s.send(givenAnswer)
        else:
            givenAnswer = s.recv(1024)
            print "The given answer is:", givenAnswer

        #IS ANSWER CORRECT    
        is_correct_str = s.recv(1024)
        time.sleep(0.001)
        print is_correct_str
        trueAnswer = s.recv(1024)
        print "The real answer is:",trueAnswer

        #PREPARE SCOREBOARD
        SB = s.recv(1024) 
        SB = SB.split()

        print "P S"
        for i in range(len(SB)):
            print i, SB[i]
        
        #CHECK WHETER SOMEONE WON OR NOT
        continue_next_round = s.recv(1024)
        continue_next_round = int(continue_next_round)

    #DISPLAY W
    final_message = s.recv(1024)
    print final_message
except Exception as e:
    print 
finally: 
    s.close()
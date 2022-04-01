import socket
import threading
import sys
import time
from random import randint
import sqlite3
import sqlite3
from chain import Chain
import rsa
import face_recognition
import imutils
import pickle
import time
import cv2
import os
candidates = []

bob_pub , bob_priv = rsa.newkeys(512)
Data_rec = [[]]
z = 0
X_IP_ADDRESS = '192.168.1.101'
with open('keys/pubkey.pem', mode='wb') as f:
    f.write(bob_pub.save_pkcs1('PEM'))
with open('keys/privkey.pem', mode='wb') as f:
    f.write(bob_priv.save_pkcs1('PEM'))
def load_keys(message):
    with open('keys/privkey.pem','rb') as f:
        priv_key = rsa.PrivateKey.load_pkcs1(f.read)
    print("Decrypted value is ",rsa.decrypt(message,priv_key))

chain = Chain(20,bob_pub , bob_priv)
voter_id_global = None
flag = 1

def Authenticate(name_from_func):
    cascPathface = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())
    
    print("Streaming started , please continue with your option and input it down below")
    video_capture = cv2.VideoCapture(0)
    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60, 60),flags=cv2.CASCADE_SCALE_IMAGE)
    
        # convert the input frame from BGR to RGB 
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []
        # loop over the facial embeddings incase
        # we have multiple embeddings for multiple fcaes
        for encoding in encodings:
        #Compare encodings with encodings in data["encodings"]
        #Matches contain array with boolean values and True for the embeddings it matches closely
        #and False for rest
            matches = face_recognition.compare_faces(data["encodings"],encoding)
            #set name =inknown if no encoding matches
            name = "Unknown"
            # check to see if we have found a match
            if True in matches:
                #Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    #Check the names at respective indexes we stored in matchedIdxs
                    name = data["names"][i]
                    #increase count for the name we got
                    counts[name] = counts.get(name, 0) + 1
                #set name which has highest count
                name = max(counts, key=counts.get)
    
    
            # update the list of names
            names.append(name)
            # loop over the recognized faces
            if names[0] == name_from_func and len(names) == 1:
                #print("Only one person found",names)
                for ((x, y, w, h), name) in zip(faces, names):
                    # rescale the face coordinates
                    # draw the predicted face name on the image
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
            else:
                print("Authentication Failed or Multiple People found Please Try again")
                video_capture.release()
                cv2.destroyAllWindows()
                break
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()
    
def vote():
    global flag
    print("Input Voter ID ")
    text = input()
    with sqlite3.connect("mini_pro.db") as con:
        cur = con.cursor()
        cur_2 = con.cursor()
        cur.execute("SELECT * FROM voter_info")
        data=cur.fetchall()
        candidates = []
        for i in data:
            #print(i)
            if int(text) == i[1] and i[4] == 0:
                name = i[3]
                print("The Voter name is",name)
                Thread = threading.Thread(target = Authenticate,args = (name,))
                Thread.daemon = True
                Thread.start()
                print("Thread is Running")
                cur.execute("UPDATE voter_info SET vote_status = 1 WHERE voter_id = ?",(int(text),))
                cur_2.execute("SELECT * FROM candidates_list")
                data_2 = cur_2.fetchall()
                for j in data_2:
                    if int(i[2]) == int(j[2]):
                        candidates.append(j[1])
                flag = 0
        if flag:
            print("The candidate has already Voted or you have given an invalid Voter ID")
            print("Do you want to try again ? Y or N")
            choice = input()
            if choice == "Y":
                vote()
            else:
                return text
        print("The candidates are ",candidates)
        flag = 1
        print("Please select the candidates by pressing there corresponding array number")
        option = input()
        if int(option) < len(candidates):
            message = candidates[int(option)] + text + str(randint(0,10))
            print("Are you sure ? Type Y or N")
            status = input()
            if status == "Y":
                con.commit()
                chain.mine()
                chain.add_to_pool(str(message))
                minor_key = bob_pub
                chain.add_to_DB(text)
                print("Your vote has been added to the chain")
                return text
            else:
                vote()
        else:
            print("Enter a Valid option")
            vote()
connections = []
listt = []
def boardcast_after_voting():
    con = sqlite3.connect("mini_pro.db")
    curr = con.cursor()
    curr.execute("SELECT * FROM remote_ledger_copy")
    data = curr.fetchall()
    for i in data:
        listt.append(i)
    #print(listt)
previous_hashing = ""
def receive_from_broadcast(sock):
    global previous_hashing
    print("In recieve block")
    lists = []

    for i in range(6):
    #while True:
        data = sock.recv(1024)
        print("NEW DATA",data)
        if "END".encode('utf-8') in data:
            print("DONE with recieving")
        lists.append(data.decode('utf-8'))

    textpart = lists[4]
    previous_hashing = lists[1]
    print("REcieved text is ",textpart)
    conn = sqlite3.connect("mini_pro.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM voter_info")
    data_2=cur.fetchall()
    for i in data_2:
        #print(i)
        if int(textpart) == i[1] and i[4] == 0:
            cur.execute("UPDATE voter_info SET vote_status = 1 WHERE voter_id = ?",(int(textpart),))
    cur.execute("INSERT INTO remote_ledger_copy VALUES(?,?,?,?)",(str(lists[0]),(str(lists[1])),str(lists[2]),str(lists[3])))
    conn.commit()
    cur.execute("SELECT * FROM remote_ledger_copy")
    data_print = cur.fetchall()
    print(data_print)
    print("Updated the Database")
    conn.close()
    return
final_texts = ""
class Server:
    global connections
    peers = []
    texting = ""
    def __init__(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)         
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((X_IP_ADDRESS,10000))
        sock.listen(1)
        print("Server running .....")
        self.texting = vote()
        print("Input text is ",self.texting)
        boardcast_after_voting()
        print("Done with Voting")
        while True:
            c , a = sock.accept()
            cThread = threading.Thread(target = self.handler,args = (c,a))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            print("Connection appended")
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]),"connected")
            self.sendPeers()
            break
    def handler(self,c,a):
        global connections
        global listt
        print("I am in Handler")
        lists = []
        while True:
            data = c.recv(1024)
            lists.append(data)
            print("The data i got in Server is ",data)
            if data == "END".encode():
                conn = sqlite3.connect("mini_pro.db")
                textpart = lists[4]
                cur = conn.cursor()
                cur.execute("SELECT * FROM voter_info")
                data_2=cur.fetchall()
                for i in data_2:
                    #print(i)
                    if int(textpart) == i[1] and i[4] == 0:
                        cur.execute("UPDATE voter_info SET vote_status = 1 WHERE voter_id = ?",(int(textpart),))
                cur.execute("INSERT INTO remote_ledger_copy VALUES(?,?,?,?)",(str(lists[0]),(str(lists[1])),str(lists[2]),str(lists[3])))
                conn.commit()
                cur.execute("SELECT * FROM remote_ledger_copy")
                conn.close()
            if not data:
                print(str(a[0]) + ':' + str(a[1]), " disconnected.")
                connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break
    def sendPeers(self):
        print("THIS IS IT ",self.texting)
        p = ""
        for peer in self.peers:
            p = p + peer + ","
            for connection in connections:
                connection.send(listt[-1][0].encode('utf-8')) #previous_hash
                time.sleep(2)
                connection.send(listt[-1][1].encode('utf-8'))#current_hash
                time.sleep(2)
                connection.send(listt[-1][2].encode('utf-8')) #public_key
                time.sleep(2)
                connection.send(listt[-1][3].encode('utf-8')) #message
                time.sleep(2)
                connection.send(str(self.texting).encode('utf-8'))
                time.sleep(2)
                connection.send("END".encode('utf-8'))

class Client:
    texting = ""
    def __init__(self,address):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address,10000))
        receive_from_broadcast(sock)
        self.texting = vote()
        print("THe cliend text is",self.texting)
        boardcast_after_voting()
        if self.texting:
            Thread = threading.Thread(target = self.sendMsg,args = (sock,))
            Thread.daemon = True
            Thread.start()
        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data[0:1] ==b'\x11':
                print("Peer Connected")
                self.updatePeers(data[1:])
            else:
                print(str(data,'utf8'))
    def sendsomeMsg(self,sock):
        print("THIs is Threadddding")
        sock.send(bytes(input("").encode('utf8')))
        return
    def sendMsg(self,sock):
        print("This is iThread")
        final_list = []
        for i in listt:
            final_list.append(list(i))
        final_list[-1][0] = previous_hashing
        print(final_list)
        sock.send(previous_hashing.encode('utf-8')) #previous_hash
        time.sleep(2)
        sock.send(listt[-1][1].encode('utf-8'))#current_hash
        time.sleep(2)
        sock.send(listt[-1][2].encode('utf-8')) #public_key
        time.sleep(2)
        sock.send(listt[-1][3].encode('utf-8')) #message
        time.sleep(2)
        sock.send(str(self.texting).encode('utf-8'))
        time.sleep(2)
        sock.send("END".encode('utf-8'))
        #sock.send(bytes(input("").encode('utf8')))
        return
    def updatePeers(self,peerData):
        p2p.peers = str(peerData,"utf-8").split(",")[:-1]
        #print(str(peerData,"utf-8").split(",")[:-1])

class p2p:
    peers = [X_IP_ADDRESS]

while True:
    try:
        print("Trying to connect...")
        time.sleep(randint(1, 5))
        for peer in p2p.peers:
            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass
            if randint(1,20) < 10:
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldn't start the server...")
    except KeyboardInterrupt:
        sys.exit(0)








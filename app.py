from flask import Flask,render_template,request, redirect,url_for , session
import sqlite3
from chain import Chain
import random
import rsa
import os
from flask import send_file
port = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
bob_pub , bob_priv = rsa.newkeys(512)
Data_rec = [[]]
z = 0
chain = Chain(20,bob_pub , bob_priv)
voter_id_global = None
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# def face_recog(name_from_func):
#     cascPathface = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
#     # load the harcaascade in the cascade classifier
#     faceCascade = cv2.CascadeClassifier(cascPathface)
#     # load the known faces and embeddings saved in last file
#     data = pickle.loads(open('face_enc', "rb").read())
    
#     print("Streaming started , please continue with your option and input it down below")
#     video_capture = cv2.VideoCapture(0)
#     # loop over frames from the video file stream
#     while True:
#         # grab the frame from the threaded video stream
#         ret, frame = video_capture.read()
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60, 60),flags=cv2.CASCADE_SCALE_IMAGE)
    
#         # convert the input frame from BGR to RGB 
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         # the facial embeddings for face in input
#         encodings = face_recognition.face_encodings(rgb)
#         names = []
#         # loop over the facial embeddings incase
#         # we have multiple embeddings for multiple fcaes
#         for encoding in encodings:
#         #Compare encodings with encodings in data["encodings"]
#         #Matches contain array with boolean values and True for the embeddings it matches closely
#         #and False for rest
#             matches = face_recognition.compare_faces(data["encodings"],encoding)
#             #set name =inknown if no encoding matches
#             name = "Unknown"
#             # check to see if we have found a match
#             if True in matches:
#                 #Find positions at which we get True and store them
#                 matchedIdxs = [i for (i, b) in enumerate(matches) if b]
#                 counts = {}
#                 # loop over the matched indexes and maintain a count for
#                 # each recognized face face
#                 for i in matchedIdxs:
#                     #Check the names at respective indexes we stored in matchedIdxs
#                     name = data["names"][i]
#                     #increase count for the name we got
#                     counts[name] = counts.get(name, 0) + 1
#                 #set name which has highest count
#                 name = max(counts, key=counts.get)
    
    
#             # update the list of names
#             names.append(name)
#             # loop over the recognized faces
#             if names[0] == name_from_func and len(names) == 1:
#                 #print("Only one person found",names)
#                 for ((x, y, w, h), name) in zip(faces, names):
#                     # rescale the face coordinates
#                     # draw the predicted face name on the image
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                     cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.75, (0, 255, 0), 2)
#             else:
#                 print("Authentication Failed or Multiple People found Please Try again")
#                 video_capture.release()
#                 cv2.destroyAllWindows()
#                 break
#         cv2.imshow("Frame", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break


@app.route('/')
def home():
    con = sqlite3.connect("mini_pro.db")
    curr = con.cursor()
    message = ""
    curr.execute("SELECT * FROM remote_ledger_copy")
    
    data = curr.fetchall()
    listt = []
    for i in data:
        listt.append(i)
    return render_template('Page_1.html',public_ledger = listt)
    
@app.route('/validate',methods = ["POST"])
def validate():
    items = request.form["Candidate"]
    print(items)
    message = (str(items) + str(session.get("my_var",None)) + str(random.randint(0,100)))
    print(message)
    p_key , m_key = rsa.newkeys(512)
    chain.mine(p_key , m_key)
    chain.add_to_pool(str(message))
    chain.add_to_DB(text,p_key , m_key)
    #should send using a socket server to other systems ........
    return render_template("Page_4.html")
@app.route('/download',methods = ['GET','POST'])
def download():
    return send_file(r'D:\Mini_project_2021_2\Mini_project_2021\Only_block\keys\1\privkey.pem')

text = ""
@app.route('/page_2',methods = ['GET','POST'])
def my_form_get(cadidates_list = None):
    global text
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind((HOST, PORT))
    #     s.listen()
    #     conn, addr = s.accept()
    #     print("Waiting for fingerpring Authentication.............")
    text = request.form['u']
    candidates = []
    name = "unknown"
    with sqlite3.connect("mini_pro.db") as connec:
        cur = connec.cursor()
        cur_2 = connec.cursor()
        cur.execute("SELECT * FROM voter_info")
        data=cur.fetchall()
        for i in data:
            print(i)
        for i in data:
            if int(text) == i[1] and i[4] == 0:
                name = str(i[3])
                print("===========================")
                print("MY NAME IS ",name)
                print("=================================")
                break
    connec.close()
    #Thread = threading.Thread(target = face_recog,args = (name,))
    #Thread.daemon = True
    #Thread.start()
    with sqlite3.connect("mini_pro.db") as con:
        cur = con.cursor()
        cur_2 = con.cursor()
        cur.execute("SELECT * FROM voter_info")
        data=cur.fetchall()
        for i in data:
            print(i)
            for i in data:
                if int(text) == i[1] and i[4] == 0 and name == i[3]:
                    cur_2.execute("SELECT * FROM candidates_list")
                    data_2 = cur_2.fetchall()
                    print(data_2)
                    for j in data_2:
                        if int(i[2]) == int(j[2]):
                            candidates.append(j[1])
                    session['my_var'] = str(text)
                    return render_template('Page_2.html',cadidates_list = candidates)
        cur.execute("SELECT * FROM voter_info")
        print(cur.fetchall())
        return render_template('Page_3.html')


if __name__ == '__main__':
    
    #should have a thread running behind to get transactions from other nodes and be updated all the time....
    #socketio.run(app)
    
    app.run(host='0.0.0.0', debug=False, port=5000)


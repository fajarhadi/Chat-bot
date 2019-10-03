'''
    Simple socket server using threads
'''
 
import socket
import sys
from thread import *
import select, pickle, time
import MySQLdb

class Parser:
    keyword = set(["lokasi","kawah","putih", "bisa", "dilakukan", "kuliner", "wisata", "harga", "tiket",
    "peta","animasi","gambar", "foto", "video", "ke", "penginapan", "ngopi", "gratis", "anak",
    "jajanan", "malam", "air", "panas", "pemandangan", "restaurant", "floating", "market",
    "komunitas", "vespa", "kota", "taman", "sejarah", "hotel", "bintang", "lima", "alamat",
    "gedung", "sate", "masjid", "raya", "taman", "vanda", "harris", "terima", "kasih"])
    picInd = set(["peta", "gambar", "foto"])
    vidInd = set(["video", "animasi"])

    def parseQuest(self,text):
        ek = set()
        db = "text"
        text = filter(lambda ch: ch not in "?.!/;:,", text)
        x = text.lower().split(" ")
        for i in x:
            for j in self.keyword:
                if (i == j):
                    ek.add(i)
        if (len(ek & self.picInd) > 0):
            db = "gambar"
        elif (len(ek & self.vidInd) > 0):
            db = "video"
        query = "select answer from "+db+" where keyword = \""+(' '.join(sorted(ek)))+"\""
        return query, db
 
def answerSend(sock,msg):
    print "send answer"
    sock.send(msg)

def answerResp(sock):
    print "wait for resp"
    data = sock.recv(BUFFER_SIZE)
    print "get data: "+data

def questConf(sock):
    print "send conf"
    sock.send("v")

def questInd(sock):
    print "wait for data"
    data = sock.recv(BUFFER_SIZE) 
    print "get data: "+data
    return data

def connInd(addr):
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

def connResp(sock):
    sock.send("Yay, welcome!")

def disconnInd():
    print "A client disconnected"

def disconnResp(conn):
    print "send disconn response"
    conn.send("You have disconnected") 

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 5005 # Arbitrary non-privileged port
BUFFER_SIZE = 40960000
p = Parser()
db = MySQLdb.connect(host="localhost",user="root",passwd="@nim@ri@n142434",db="rekpro")
cur = db.cursor()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 
#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    connResp(conn) #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data = questInd(conn)
        if data == 'exit':
            disconnInd()
            disconnResp(conn)
            break
        questConf(conn)
        time.sleep(1)
        query, db = p.parseQuest(data)
        cur.execute(query)
        answer = "Maaf, mohon ulangi."
        for row in cur.fetchall():
            answer = row[0]
        print answer
        if (answer != "Maaf, mohon ulangi."):
            if (db == "text"):
                pesan = pickle.dumps([answer, db])
            else:
                obj = open(answer,'rb')
                x = obj.read(BUFFER_SIZE)
                pesan = pickle.dumps([x, db])
        else:
            x = answer
            db = "text"
            print x
            pesan = pickle.dumps([x, db])
        answerSend(conn,pesan)  # echo
        answerResp(conn)
     
    #came out of loop
    conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    connInd(addr)
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()
import socket, numpy, cv2, time
import cPickle as pickle
from Tkinter import *
import tkFileDialog
import tkMessageBox

class gui:
	def __init__(self):
		self.root = Tk()				
		self.root.title("Client")
		self.root.state('zoomed')

		self.client = Client()
		self.client.connReq()
		resp = self.client.connConf()

		lbl = Label(self.root,text="Dumb Personal Assistant", font=("Times", 14))
		lbl.grid(row=1, column=0, padx=4, pady=3, sticky=W)

		self.question = StringVar()
		self.question.set("")
		lbl = Label(self.root,text="Inquiry", font=("Times", 11))
		lbl.grid(row=2, column=0, padx=4, pady=3, sticky=W)
		self.alp = Entry(self.root, width=130, textvariable=self.question, font=("Times", 11))
		self.alp.grid(row=2, column=1, padx=4, pady=3, sticky=W)

		self.T = Text(self.root, height=30, width=170, font=("Times", 11), spacing1=3)
		self.S = Scrollbar(self.root)
		self.T.grid(row=4, column=0, columnspan=2, sticky=W)
		self.S.grid(row=4, column=3, sticky=N+S)
		self.S.config(command=self.T.yview)
		self.T.config(yscrollcommand=self.S.set)

		self.T.insert(END,"Server: "+resp+"\n")
		#self.showText("Yay, welcome!")

		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.root.bind('<Return>', self.getQuest)
		self.root.mainloop()

	def on_closing(self):
		if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
			self.client.disconnReq()
			data = self.client.disconnConf()
			self.T.insert(END,"Server: "+data)
			time.sleep(2)
			self.root.destroy()

	def getQuest(self,event):
		message = self.question.get()
		self.alp.delete(0, 'end')
		self.T.insert(END,"You: "+message)
		self.client.questSend(message)
		resp = self.client.questResp()
		self.T.insert(END,"\t"+resp+"\n")
		ans = self.client.answerInd()
		self.client.answerConf()
		if (ans[1] == "text"):
			self.showText(ans[0])
		elif (ans[1] == "gambar"):
			self.showImage(ans[0])
		elif (ans[1] == "video"):
			self.showVideo(ans[0])

	def showText(self,txt):
		self.T.insert(END,"Server: "+txt+"\n")

	def showImage(self,data):
		img = open('recv.png','wb') 
		img.write(data)
		img.close()
		cap = cv2.imread('recv.png')
		cv2.imshow('image',cap)

	def showVideo(self,data):
		vid = open('recv.avi','wb') 
		vid.write(data)
		vid.close()
		cap = cv2.VideoCapture('recv.avi')
		while(cap.isOpened()):
			ret, frame = cap.read()
			cv2.imshow('frame',frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		cap.release()
		cv2.destroyAllWindows()

class Client:
	TCP_IP = '127.0.0.1'
	TCP_PORT = 5005
	BUFFER_SIZE = 40960000 
	MESSAGE = ""
 
	tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	
	def connReq(self):
		self.tcpClientA.connect((self.TCP_IP, self.TCP_PORT))

	def connConf(self):
		data = self.tcpClientA.recv(self.BUFFER_SIZE)
		return data

	def disconnReq(self):
		self.tcpClientA.send("exit")

	def disconnConf(self):
		data = self.tcpClientA.recv(self.BUFFER_SIZE)
		self.tcpClientA.close()
		return data

	def questSend(self,msg):
		print "send question"
		self.tcpClientA.send(msg)

	def questResp(self):
		print "wait for resp"
		data = self.tcpClientA.recv(self.BUFFER_SIZE)
		return data

	def answerInd(self):
		print "wait for answer"
		data = self.tcpClientA.recv(self.BUFFER_SIZE)
		return pickle.loads(data)

	def answerConf(self):
		print "send conf"
		self.tcpClientA.send("v\n")

g = gui()
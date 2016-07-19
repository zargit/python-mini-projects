import threading
from threading import *
from Tkinter import *
import tkFileDialog
import os


class StringMatcher(object):
	def __init__(self, pattern):
		self.updatePattern(pattern)

	def initPattern(self):
		self.pl = len(self.pattern)
		self.pi = [0 for i in range(self.pl)] 

	def preparePattern(self):
		self.initPattern()
		k = 0
		for i in range(1,self.pl):
			if self.pattern[k]==self.pattern[i]:
				k+=1
				self.pi[i] = k
			elif self.pattern[k]!=self.pattern[i] and k>0:
				k = self.pi[k-1]

	def getMatch(self, text):
		text = text.lower()
		k, i, j, l, c = 0,0,0,len(text),self.pl
		while i < l:
			if self.pattern[j]==text[i]:
				k+=1
				i+=1
				j+=1
				if j == c:
					return (i-c)
					k, j = 0, 0
			else:
				if k==0:
					i+=1
				elif k>0:
					i-=self.pi[k-1]
					k, j = 0,0
		return -1

	def updatePattern(self, pattern):
		self.pattern = pattern
		self.preparePattern()


class PathEntry(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		self.entry = Entry(self)
		self.button = Button(self, text="Select Path",command=self.getDir)
		self.initUI()

	def initUI(self):
		dL = Label(self, text="Directory")
		dL.pack(side=LEFT, padx=5, pady=5)
		self.entry.pack(fill=X, side=LEFT, padx=5, pady=5, expand = 1)
		self.button.pack(side=LEFT,padx=5, pady=5)
		self.pack(fill=X)

	def getDir(self):
		self.entry.delete(0,END)
		self.entry.insert(0,tkFileDialog.askdirectory())

class SearchEntry(Entry):
	def __init__(self, parent):
		self.tf = Frame(parent)
		Entry.__init__(self, self.tf)
		self.parent = parent
		self.mm = StringMatcher("")
		self.initUI()

	def initUI(self):
		patternL = Label(self.tf, text="Search:")
		patternL.pack(side=LEFT, padx=5, pady=5)

		self.bind("<KeyRelease>", self.onKeyRelease)
		self.pack(side=LEFT, fill=X, padx=5, pady=5, expand = 1)
		self.tf.pack(fill=X, padx=5, pady=5)

	def displayResult(self):
		self.parent.textBox.tag_delete("mark")
		self.parent.statusLabel.setStatus("")
		self.parent.textBox.delete("1.0",END)
		pat = self.get().lower()
		if len(pat)<1:
			return
		self.mm.updatePattern(pat)
		root = self.parent.pathBox.entry.get()
		found, depth = 1, 0
		stack = [(root,depth)]
		marks = []
		self.parent.textBox.tag_config("mark", background="yellow", foreground="blue")
		while len(stack)>0:
			curPath = stack.pop()
			isDir = os.path.isdir(curPath[0])
			if isDir:
				items = os.listdir(curPath[0])
				for i in range(len(items)):
					newPath = curPath[0]+"/"+items[i]
					if os.path.isdir(newPath):
						stack.insert(0,(newPath,curPath[1]+1))
					else:
						match = self.mm.getMatch(items[i])
						if match !=-1:
							self.parent.textBox.insert(INSERT,items[i]+str("\t\t\t-->\t("+curPath[0]+")\n"))
							self.parent.textBox.tag_add("mark",str(found)+"."+str(match),str(found)+"."+str(match+self.mm.pl))
							found += 1
							self.parent.textBox.update_idletasks()
							self.parent.statusLabel.setStatus(str(found-1)+" match found")
			

	def onEnter(self,event):
		if event.keycode == 13:
			t = self.get()

	def onKeyRelease(self,event):
		self.displayResult()


class TextBox(Text):
	def __init__(self,parent):
		self.parent = parent
		Text.__init__(self,parent)
		self.sbar = Scrollbar(self)
		self.initUI()

	def getText(self):
		return self.text

	def initUI(self):
		self.sbar.pack(side=RIGHT, fill=Y)
		self['yscrollcommand'] = self.sbar.set
		self.bind("<KeyRelease>", self.onChange)
		self.pack(fill=BOTH, padx=5, pady=5, expand=1)
		self.sbar.config(command=self.yview)

	def onChange(self,event):
		self.parent.searchBox.onKeyRelease(None)

class StatusLabel(Label):
	def __init__(self, parent):
		Label.__init__(self, parent)
		self.parent = parent
		self.label = StringVar()
		self['textvariable'] = self.label
		self['anchor'] = W
		self.initUI()

	def setStatus(self, status):
		self.label.set(status);

	def initUI(self):
		self.pack(fill=X, side=LEFT, padx=5, pady=5, expand=1)


class MainFrame(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent, background="white")
		self.parent = parent
		self.initUI()

	def initUI(self):
		self.parent.title("Search File")
		self.pathBox = PathEntry(self)
		self.searchBox = SearchEntry(self)
		self.textBox = TextBox(self)
		self.statusLabel = StatusLabel(self)
		self.pack(fill=BOTH, expand=1)

def main():
	root = Tk()
	root.geometry("650x450+0+0")
	mf = MainFrame(root)
	root.mainloop()

if __name__=='__main__':
	main()
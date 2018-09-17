'''
Created on Sep 12, 2018

@author: Default
'''
import sys
sys.path.append("../")
import Pyro4
import xml.etree.ElementTree as ElementTree
import utilities.Utilities as utilities
import zipfile
import shutil
import subprocess
import socket
import os
from threading import Thread

def getNIP():    
    tree = ElementTree.parse("..\configClient.xml")  
    root = tree.getroot()
    return(root[0][0].text)
def getBNIP():    
    tree = ElementTree.parse("..\configClient.xml")  
    root = tree.getroot()
    return(root[0][1].text)
def getExecutables():    
    tree = ElementTree.parse("..\configClient.xml")  
    root = tree.getroot()
    executables=[]
    for child in root[0][2]:
        executables.append(child.text)
        
    return(executables)

@Pyro4.expose
class stubClass(object):
    def __init__(self):
        self.ip = getNIP()
        self.bip = getBNIP()
        self.executables=getExecutables()
        self.sub_processes={}
    '''
    def update(self,zip_ref):
        utilities.checkExistOrCreate("../files")
        zip_ref.extractall("../files")
        zip_ref.close()
        return True
    '''
    def stopNodeExecution(self):
        executables=getExecutables()

        try:
            for i in range(len(executables)):
                if executables[i] in self.sub_processes:
                    self.sub_processes[executables[i]].terminate()
                    self.sub_processes.pop(executables[i])   
                else:
                    continue
        except:
            raise 
    def startNodeExecution(self):
        executables=getExecutables()
        
        for i in range(len(executables)):
            if executables[i] in self.sub_processes:
                continue
            else:
                if os.path.isfile("../files/"+executables[i]):
                    sub_process = subprocess.Popen(['python', "../files/"+executables[i]])
                    self.sub_processes[executables[i]]=sub_process
    def startNodeFileReceiver(self,nodeip,filesizeinp):
        host = nodeip
        port = 5051
        filesize=int(filesizeinp)
        s = socket.socket()
        s.connect((host, port))
        utilities.createOrReplace("../receiveFolder" )

        f = open('../receiveFolder/receivedFile.zip', 'wb')
        data = s.recv(1024)
        totalRecv = len(data)
        f.write(data)
        while totalRecv < filesize:
            data = s.recv(1024)
            totalRecv += len(data)
            f.write(data)
            print ("{0:.2f}".format((totalRecv/float(filesize))*100)+ "% Done")
        print ("Download Complete!")
        f.close()
        
        
    def loaderNode(self):

        utilities.createOrReplace("../temp" )
        zip_ref = zipfile.ZipFile("../receiveFolder/receivedFile.zip", 'r')
        zip_ref.extractall("../temp")
        zip_ref.close()

        shutil.rmtree("../files")

        shutil.copytree("../temp","../files" )
        shutil.move('../files/configClient.xml','../configClient.xml')
 


    def test(self):
        print(getNIP())
        return("returnval :"+getNIP())

stub_class_object = stubClass()
stub_class_object.sub_processes={}
ip=getNIP()
daemon = Pyro4.Daemon(host=ip, port=5050)
Pyro4.Daemon.serveSimple(
    { stub_class_object: ip+".stub" },
    ns=False,
    daemon=daemon,
    verbose = True
)
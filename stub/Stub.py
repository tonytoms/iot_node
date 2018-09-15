'''
Created on Sep 12, 2018

@author: Default
'''

import Pyro4
import xml.etree.ElementTree as ElementTree
import utilities.Utilities as utilities
import zipfile
import shutil
import subprocess
import socket

def getNIP():    
    tree = ElementTree.parse("..\configClient.xml")  
    root = tree.getroot()
    return(root[0].text)
def getBNIP():    
    tree = ElementTree.parse("..\configClient.xml")  
    root = tree.getroot()
    return(root[1].text)
def getExecutables():    
    tree = ElementTree.parse("..\configClient.xml")  
    root = tree.getroot()
    executables=[]
    for child in root[2]:
        executables.append(child.text)
        
    return(executables)

@Pyro4.expose
class stubClass(object):
    def __init__(self):
        self.ip = getNIP()
        self.version = getBNIP()
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
                sub_process = subprocess.Popen(['python', "../files/"+executables[i]])
                self.sub_processes[executables[i]]=sub_process
    def startNodeFileReceiver(self,nodeip):
        HOST = nodeip
        PORT = 5051
        ADDR = (HOST,PORT)
        BUFSIZE = 4096
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(ADDR)
        serv.listen(5)
        #while True:
        conn, addr = serv.accept()
        utilities.createOrReplace('../temp/receivedFile.zip')
        myfile = open('../temp/receivedFile.zip', 'w')
        while True:
            data = conn.recv(BUFSIZE)
            if not data: break
            myfile.write(data.decode())
        myfile.close()
        conn.close()
        
        
    def loaderNode(self):

        utilities.createOrReplace("../files" )
        zip_ref = zipfile.ZipFile("../temp/receivedFile.zip", 'r')
        zip_ref.extractall("../files")
        zip_ref.close()


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
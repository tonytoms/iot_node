'''
Created on Sep 12, 2018

@author: Default
'''

import Pyro4
import xml.etree.ElementTree as ElementTree
import utilities.Utilities as utilities
import zipfile
import threading
import subprocess

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
    def update(self,zip_ref):
        utilities.checkExistOrCreate("../files")
        zip_ref.extractall("../files")
        zip_ref.close()
        return True
    def killExecutor(self):
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
    def executor(self):
        executables=getExecutables()
        
        for i in range(len(executables)):
            if executables[i] in self.sub_processes:
                continue
            else:
                sub_process = subprocess.Popen(['python', "../files/"+executables[i]])
                self.sub_processes[executables[i]]=sub_process

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
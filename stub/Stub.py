'''
Created on Sep 12, 2018

@author: Default
'''

import Pyro4
import xml.etree.ElementTree as ElementTree
    
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
    def test(self):
        print(getNIP())
        return("returnval :"+getNIP())

stub_class_object = stubClass()
ip=getNIP()
daemon = Pyro4.Daemon(host=ip, port=5050)
Pyro4.Daemon.serveSimple(
    { stub_class_object: ip+".stub" },
    ns=False,
    daemon=daemon,
    verbose = True
)
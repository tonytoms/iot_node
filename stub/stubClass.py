'''
Created on Sep 12, 2018

@author: Tony Toms

-------------Desc:----------------------

This class is executed at main node.
This handles all the requests from controller node.

----------------main variables--------------
# ret_status-  this list has all the informations regarding the running of each method. this variable is returned to the controller at the end
            ret_status[0] - True if task completed and false if an issue occurred
--------------------------------------
'''
import os
import sys
sys.path.append(".."+os.sep)
import Pyro4
import xml.etree.ElementTree as ElementTree
import utilities.Utilities as utilities
import zipfile
import shutil
import subprocess
import socket
from threading import Thread
import traceback

def getNIP():    
    tree = ElementTree.parse(".."+os.sep+"configClient.xml")  
    root = tree.getroot()
    return(root[0][0].text)
def getBNIP():    
    tree = ElementTree.parse(".."+os.sep+"configClient.xml")  
    root = tree.getroot()
    return(root[0][1].text)
def getExecutables():    
    tree = ElementTree.parse(".."+os.sep+"configClient.xml")  
    root = tree.getroot()
    executables=[]
    for child in root[0][2]:
        executables.append(child.text)
        
    return(executables)
def sub_process_call(sub_processes,executable):
    
    if os.path.isfile(".."+os.sep+"files"+os.sep+executable):
        if ".py" in executable:
            sub_process = subprocess.Popen(['python',".."+os.sep+"files"+os.sep+executable])
            sub_processes[executable]=sub_process 
            
               
    return True
        
def sub_process_terminate(sub_processes,executable):
    
    if ".py" in executable:
        sub_processes[executable].terminate()
        sub_processes.pop(executable)
    return True

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

        ret_status=[True,"Step 1(of 2) - Getting Execution File List","Step 2(of 2) - Executing Files"]
        print("\n Running stopNodeExecution() \n")        
    
        executables=getExecutables()
        ret_status[1]=ret_status[1]+" :Done"

        try:
            for i in range(len(executables)):
                if executables[i] in self.sub_processes:
                    sub_process_terminate(self.sub_processes,executables[i])
                    #self.sub_processes[executables[i]].terminate()
                    
                    #self.sub_processes.pop(executables[i])    
                else:
                    continue
            ret_status[2]=ret_status[2]+" :Done"
        except:
            ret_status[0]=False
            ret_status.append("\n**** Exception Occurred: "+str(sys.exc_info()[1])+str(traceback.print_exc()))
        
        print("\n Done \n")
        return ret_status  
    
    #This function executes the programs
    def startNodeExecution(self):

        ret_status=[True,"Step 1(of 2) - Getting Execution File List","Step 2(of 2) - Executing Files"]
        print("\n Running startNodeExecution() \n")        
        
        try:
            executables=getExecutables()
            ret_status[1]=ret_status[1]+" :Done"
            
            for i in range(len(executables)):
                if executables[i] in self.sub_processes:
                    continue
                else:
    
                    ret_val=sub_process_call(self.sub_processes,executables[i])
            ret_status[2]=ret_status[2]+" :Done"
        except:
            ret_status[0]=False
            ret_status.append("\n**** Exception Occurred: "+str(sys.exc_info()[1])+str(traceback.print_exc()))
        
        print("\n Done \n")
        return ret_status 
    
                
    #This function Receives files from the controller
    def startNodeFileReceiver(self,nodeip,filesizeinp):
        ret_status=[True,"Step 1(of 3) - Accept Connection","Step 2(of 3) - Replace receiveFolder","Step 3(of 3) - Write to receiveFolder.zip"]
        print("\n Running startNodeFileReceiver() \n")
        try:
            host = nodeip
            port = 5051
            filesize=int(filesizeinp)
            s = socket.socket()
            s.connect((host, port))
            ret_status[1]=ret_status[1]+" :Done "
            
            utilities.createOrReplace(".."+os.sep+"receiveFolder" )
            ret_status[2]=ret_status[2]+" :Done "
   
            f = open(".."+os.sep+"receiveFolder"+os.sep+"receivedFile.zip", 'wb')
            data = s.recv(1024)
            totalRecv = len(data)
            f.write(data)
            while totalRecv < filesize:
                data = s.recv(1024)
                totalRecv += len(data)
                f.write(data)
                print ("{0:.2f}".format((totalRecv/float(filesize))*100)+ "% Done")
            
            f.close()
            ret_status[3]=ret_status[3]+" :Done "
            
            
        except:
            ret_status[0]=False
            ret_status.append("\n**** Exception Occurred: "+str(sys.exc_info()[1])+str(traceback.print_exc()))
        
        print("\n Done \n")
        return ret_status    


      
    # This function loads the files from temporary destination to main execution destination
    def loaderNode(self):

        ret_status=[True,"\n Step 1(of 5) - Replacing temp folder","\n Step 2(of 5) - Extracting Files to temp","Step 3(of 5)- remove folder 'files' ",
                    "step 4(of 5) - Copy from temp to files","Step 5(of 5) - Replacing the configClient.xml"]
        print("\n Running loaderNode() \n")
        try:
            
            utilities.createOrReplace(".."+os.sep+"temp" )
            ret_status[1]=ret_status[1]+": done"

            zip_ref = zipfile.ZipFile(".."+os.sep+"receiveFolder"+os.sep+"receivedFile.zip", 'r')
            zip_ref.extractall(".."+os.sep+"temp")
            zip_ref.close()
            ret_status[2]=ret_status[2]+": done"
    
            shutil.rmtree(".."+os.sep+"files")
            ret_status[3]=ret_status[3]+": done"
    
            shutil.copytree(".."+os.sep+"temp",".."+os.sep+"files" )
            ret_status[4]=ret_status[4]+": done"

            shutil.move(".."+os.sep+"files"+os.sep+"configClient.xml",".."+os.sep+"configClient.xml")
            ret_status[5]=ret_status[5]+": done"
            
        except:
            ret_status[0]=False
            ret_status.append("\n**** Exception Occurred: "+str(sys.exc_info()[1])+str(traceback.print_exc()))
        
        print("\n Done \n")
        return ret_status    
    
    
    # getNodeStatus returns the node status    
    def getNodeStatus(self):
        ret_status=[True,"\n Step 1(of 2) - Getting Node IP","\n Step 2(of 2) - Getting Running Program List"]
        print("\n Running getNodeStatus():\n")

        try:
            
            ret_status[1]=ret_status[1]+"NODE IP:"+getNIP()
            ret_status[2]=ret_status[2]+"NODE TYPE: MAIN \n"
            ret_status[2]=ret_status[2]+"----------------Running Programs-------------------------:\n"
            
            for key in self.sub_processes.keys():
                ret_status[1]=ret_status[1]+"#  "+key+"\n"
        
        except:
            ret_status[0]=False
            ret_status.append("\n**** Exception Occurred: "+str(sys.exc_info()[1])+str(traceback.print_exc()))
        
        print("\n Done:\n")
        return ret_status
    
    
    # Test function is to test the working of the node
    def test(self):
        ret_status=[True,"\n Step 1(of 1) - Getting Node IP "]
        print("\n Running test():")
        
        try:
            print("NODE IP: "+getNIP())
            ret_status[1]=("\n Step 1(of 1) - "+"Getting NODE IP: "+getNIP())
        
        except:
            ret_status[0]=False
            ret_status.append("\n**** Exception Occurred: "+str(sys.exc_info()[1])+str(traceback.print_exc()))
            
        print("\n Done")
        return ret_status

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
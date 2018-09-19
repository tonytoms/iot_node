import os as os
import shutil as shutil
import zipfile
'''
Created on Sep 9, 2018

@author: Tony Toms

-------------Desc----------------------
Supporting functions to perform activities
'''


#This function create a directory if it doesn't exist. If the Directory exist , it will be replaced
def createOrReplace(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)

#Zip the folder        
def zipdir(source, dest):
    shutil.make_archive(dest, 'zip', source)



def checkExistOrCreate(path):
    if os.path.isdir(path):
        return True
    else:
        os.mkdir(path)
        return True

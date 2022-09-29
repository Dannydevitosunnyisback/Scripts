from ast import If
from itertools import count
from operator import ne
from xml.etree.ElementTree import tostring
from numpy import size
import requests
import os
import shutil
import sys
from yaml import parse

hosts_file = "/etc/hosts"
old_name = "/etc/hosts_old.txt"
newName = "/etc/hosts"

#checking if response has change,if it did that means we got something
notValidContentLength = 5480

modified_ = False
def initialize():
    global modified_
    try:
        os.rename(hosts_file, old_name)
        shutil.copy(old_name, newName) 
        modified_ = True
    except:
        exit("didnt worked 1")

def restore():
    global modified_
    print(modified_)
    if modified_:
        modified_ = False
        try:
            os.remove(newName)
            os.rename(old_name, newName)
            print("/etc/hosts restored!")
            print("If you had some positive result, you should add them to your /etc/hosts and see if they really work")
            exit()
        except:
            exit("didnt worked 2")
    exit()


def makeRequestIsOk(checkDns):
    global notValidContentLength
    try:
        response = requests.get(checkDns, timeout=1)
        if notValidContentLength==len(response.content):
            return False
        if len(response.content)>notValidContentLength:
            print("this one seems to work-->"+checkDns)
            return True
    except Exception as e:
        print(e)
        print(f" {checkDns }: nop")
        return False

def writeToNewDnsFile(lines, list_domain_words, indexToFuzz, ip):
     with open (newName, "a", newline="\n") as f:
        for l in lines:
            list_domain_words[indexToFuzz] = l.strip()
            checkDns= "".join(list_domain_words) 
            f.write("\n")
            f.write(ip+ "    " +checkDns)


def enum():
    if "-u" in sys.argv and "-w" in sys.argv and "-ip" in sys.argv:
        print(sys.argv)
        params = sys.argv
        ip = params[6]
        print("correct domain")
        if "FUZZ" not in params[2]:
            print(f"You must indictate FUZZ in place of the word you wanna to brute. . . ")
            exit()
        yes = input(f"Are you sure your wanna to attack {params[2]}?, write 'yes' if you're sure \n")
        if yes!="yes":
            exit()
        list_domain_words = params[2].split("FUZZ")
        indexToFuzz = 0
        lastIndex = size(list_domain_words)-1
        if list_domain_words[0]=="":

            indexToFuzz = 0
        elif list_domain_words[lastIndex]=="":

            indexToFuzz = lastIndex
        else:
            list_domain_words.insert(1,"")        
            indexToFuzz= 1
            
        print(list_domain_words)
        try:
            initialize()        
            lines = ""
            if params[4].endswith(".txt") and str(params[4]):   
                with open(params[4], "r", newline="\n") as f:
                    lines = f.readlines()
                writeToNewDnsFile(lines, list_domain_words, indexToFuzz ,ip)
                #after the function above /etc/hosts has all bruteforced domains included, so now we can make requests to see if they exist
                #DONT WORRY, BEFORE THE PROGRAM ENDING /etc/hosts is restored
                print("enumeratig... please wait")
                for l in lines:
                    list_domain_words[indexToFuzz] = l.strip()
                    checkDns= "".join(list_domain_words)
                    withHttp = "http://"+checkDns        
                    makeRequestIsOk(withHttp)
                restore()
            else:
                print("bad file format")
                restore()
        except:
            restore()
    
    else:
        print(f"wrong args" )
        print(f"eg: sudo python3 dns-enumerator.py -u preprod-FUZZ.trick.htb. -w wordlist.txt -ip 10.10.11.166 "  )
        restore()
    


if __name__ == '__main__':
    try:
        enum()
    except KeyboardInterrupt:
        restore()


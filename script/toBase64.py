import os
import time
import base64

start  = time.time()
oldCwd = os.getcwd()

homePath = os.getenv("HOME")
txtPath = "{}/GIT/uBot/uBot_firmware/resources/txt".format(homePath)

txtFiles = [name for name in os.listdir(txtPath) if not name.startswith("b64_")]

def printJob(job):
    print("\r\nJOB: {}\r\n\r\n".format(job))

def printResult(result):
    print("\r\nRESULT: {}\r\n\r\n".format(result))

printJob("CHANGE DIR: {}".format(txtPath))
os.chdir(txtPath)


printJob("ENCODING FILES")

for filename in txtFiles:
    encoded = ""

    with open("{}/{}".format(txtPath, filename)) as file:
        for line in file:
            encoded += line

    encoded = base64.b64encode(encoded.encode("utf-8")).decode("ascii")

    with open("{}/b64_{}".format(txtPath, filename), "w") as file:
        file.write(encoded)


printJob("CHANGE DIR: {}".format(oldCwd))
os.chdir(oldCwd)

print("FINISHED IN {} SECONDS.\r\n\r\n".format(round(time.time() - start)))

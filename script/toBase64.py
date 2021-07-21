import os
import time
import base64

start  = time.time()
oldCwd = os.getcwd()

homePath = "{}/GIT/uBot/uBot_firmware/resources/{{}}".format(os.getenv("HOME"))
rawPath = homePath.format("raw")
b64Path = homePath.format("B64")


def printJob(job):
    print("\r\nJOB: {}\r\n\r\n".format(job))

def printResult(result):
    print("\r\nRESULT: {}\r\n\r\n".format(result))

printJob("CHANGE DIR: {}".format(rawPath))
os.chdir(rawPath)


printJob("ENCODING FILES")

for filename in [name for name in os.listdir(rawPath)]:
    encoded = ""

    with open("{}/{}".format(rawPath, filename), "rb") as file:
        encoded = base64.b64encode(file.read()).decode("ascii")

    with open("{}/{}".format(b64Path, filename), "w") as file:
        file.write(encoded)


printJob("CHANGE DIR: {}".format(oldCwd))
os.chdir(oldCwd)

print("FINISHED IN {} SECONDS.\r\n\r\n".format(round(time.time() - start)))

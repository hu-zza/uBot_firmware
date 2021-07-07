import os
import shutil

oldCwd = os.getcwd()

homePath = os.getenv("HOME")
microPythonPath = "{}/GIT/uBot/micropython".format(homePath)
espModulesPath  = "{}/ports/esp8266/modules".format(microPythonPath)
artifactPath    = "{}/ports/esp8266/build-GENERIC/firmware-combined.bin".format(microPythonPath)

firmwarePath = "{}/GIT/uBot/uBot_firmware".format(homePath)
modulesPath  = "{}/modules".format(firmwarePath)
sandboxPath  = "{}/sandbox".format(firmwarePath)

fileNameFormat = "uBot_firmware_{}.{}.{}.bin"

def printJob(job):
    print("\nJOB: {}\n\n".format(job))

def printResult(result):
    print("\nRESULT: {}\n\n".format(result))

major = 0
minor = 0
patch = 0

with open("{}/inisetup.py".format(modulesPath)) as file:
    for line in file:
        if line.startswith("firmware"):
            major, minor, patch = eval(line.split("=")[1])

print("\n\nBUILD AND DEPLOY VERSION: {}.{}.{}\n\n".format(major, minor, patch))

printJob("COPY MODULES")
moduleList = [name for name in os.listdir(modulesPath) if name[-3:] == ".py"]
for module in moduleList:
    shutil.copyfile("{}/{}".format(modulesPath, module), "{}/{}".format(espModulesPath, module))

printJob("CHANGE DIR: {}".format(microPythonPath))
os.chdir(microPythonPath)

printJob("BUILD SUBMODULES")
printResult(os.system("docker run --rm -ti -v $PWD:$PWD -w $PWD larsks/esp-open-sdk make -C ports/esp8266 submodules V=1"))

printJob("COMPILE WITH MPY-CROSS")
printResult(os.system("docker run --rm -ti -v $PWD:$PWD -w $PWD larsks/esp-open-sdk make -C mpy-cross V=1"))

printJob("BUILD ARTIFACT")
printResult(os.system("docker run --rm -ti -v $PWD:$PWD -w $PWD larsks/esp-open-sdk make -C ports/esp8266 V=1"))

fileName = fileNameFormat.format(major, minor, patch)
printJob("COPY ARTIFACT")
shutil.copyfile(artifactPath, "{}/{}".format(sandboxPath, fileName))

printJob("ERASE FLASH")
printResult(os.system("esptool.py --port /dev/ttyUSB0 erase_flash"))

printJob("FLASH FIRMWARE")
printResult(os.system("esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 {}/{}"
                      .format(sandboxPath, fileName)))

printJob("CHANGE DIR: {}".format(oldCwd))
os.chdir(oldCwd)

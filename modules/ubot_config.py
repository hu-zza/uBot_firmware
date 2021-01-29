import ujson, uos

import ubot_logger as logger



################################
## PUBLIC METHODS

def get(module, attribute):
    """ Returns the value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r")


def set(module, attribute, value):
    """ Sets the value of the attribute. Firstly serializes it and then writes it out. """
    return _manageAttribute(module, attribute, "w", value)



################################
## PRIVATE, HELPER METHODS

def _manageAttribute(dir, file, mode, value = None):
    try:
        with open("etc/{}/{}.txt".format(dir, file), mode) as file:
            if mode == "r":
                return ujson.loads(file.readline())
            elif mode == "w":
                return file.write("{}\n".format(ujson.dumps(value)))
    except Exception as e:
        logger.append(e)

import socket
import time
import logging
log = logging.getLogger()

class TelnetClient:
    def __init__(self, ip, port, password):
        if (password != None):
            log.debug('Trying to build up a telnet connection to %s:%s with a password'
                % (str(ip), str(port)))
        else:
            log.debug('Trying to build up a telnet connection to %s:%s without a password'
                % (str(ip), str(port)))

        self.ip = ip
        self.port = port
        self.password = password
        self.connected = False

        self.__sock = socket.socket()
        attempts = 0
        while (not self.__connectSocket() and attempts < 10):
            time.sleep(1)
        if (self.__sock is None):
            raise ValueError('Socket not connected')
        else:
            self.connected = True
        #Retrieve the help instructions to have auth only receive "OK"
        self.__sock.recv(1024)
        self.authenticated = self.__auth()

        #print(authenticated)


    def __del__(self):
        self.__sock.close()

    def __connectSocket(self):
        try:
            self.__sock.connect((self.ip, self.port))
            return True
        except socket.error as ex:
            return False

    def __sendCommandWithoutChecks(self, command):
        self.__sock.send(command)
        #TODO: handle socketError
        return self.__sock.recv(1024)

    def __sendCommandRecursive(self, command, again):
        x = self.__sendCommandWithoutChecks(command)
        log.debug("__sendCommandRecursive: Sending '%s' resulted in '%s'" % (str(command), x))
        if "OK" in x:
            return True
        elif ("KO: password required. Use 'password' or 'auth'" in x
            and not again):
            #handle missing auth
            log.debug('__sendCommandRecursive: Auth required')
            self.__auth();
            self.__sendCommandRecursive(command, True);
        else:
            log.debug('__sendCommandRecursive: Input failed. Aborting')
            self.authenticated = False
            return False

    #just a function to make the function call look better
    def sendCommand(self, command):
        return self.__sendCommandRecursive(command, False)

    def __auth(self):
        if (self.password == None):
            log.debug("__auth: No password configured, not authenticating")
            return False
        log.debug("__auth: Trying to authenticate")
        toSend = "auth %s\r\n" % str(self.password)
        result = self.__sendCommandWithoutChecks(toSend)
        log.debug("__auth: got: %s" % str(result))
        authenticated = ("OK" in result)
        self.authenticated = authenticated
        log.debug("__auth: Authenticated: %s" % str(authenticated))
        return authenticated

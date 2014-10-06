#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 - Ronan Delacroix
FTP utils
:author: Ronan Delacroix
"""
import logging
import pyftpdlib.servers
import pyftpdlib.handlers
from . import text


class FTPEventLogger:

    def log(self, msg, logfun=None, error=False):
        raise Exception('Sub classes should override this function.')

    def on_login(self, username):
        self.log("User %s logged in." % username)

    def on_logout(self, username):
        self.log("User %s logged out." % username)

    def on_file_sent(self, filepath):
        filepath = text.convert_to_unicode(filepath)
        self.log(u"File %s has been successfully sent (User %s)." % (filepath, self.username))

    def on_file_received(self, filepath):
        filepath = text.convert_to_unicode(filepath)
        self.log(u"User %s has uploaded a new file : %s" % (self.username, filepath))

    def on_incomplete_file_sent(self, filepath):
        filepath = text.convert_to_unicode(filepath)
        self.log(u"File %s has been Incompletely sent by user %s... Waiting for the user to resume his download." % (filepath, self.username), error=True)

    def on_incomplete_file_received(self, filepath):
        filepath = text.convert_to_unicode(filepath)
        self.log(u"A new file %s has been uploaded but is incomplete by user %s... Waiting for the user to resume his upload." % (filepath, self.username), error=True)


class FTPHandler(FTPEventLogger, pyftpdlib.handlers.FTPHandler):

    def log(self, msg, logfun=None, error=False):
        if error:
            logging.error("[FTP] %s" % msg)
        else:
            logging.info("[FTP] %s" % msg)


class SecureFTPHandler(FTPEventLogger):

    def log(self, msg, logfun=None, error=False):
        if error:
            logging.error("[FTPS] %s" % msg)
        else:
            logging.info("[FTPS] %s" % msg)


class DummyDictFTPAuthorizer(pyftpdlib.handlers.DummyAuthorizer):
    """
    Dummy Dict FTP Authorizer class.
    Provide authentication through FTP for users stored in a dict.

    About permissions:

        Read permissions:
         - "e" = change directory (CWD command)
         - "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
         - "r" = retrieve file from the server (RETR command)

        Write permissions:
         - "a" = append data to an existing file (APPE command)
         - "d" = delete file or directory (DELE, RMD commands)
         - "f" = rename file or directory (RNFR, RNTO commands)
         - "m" = create directory (MKD command)
         - "w" = store a file to the server (STOR, STOU commands)
    """

    read_perms = "elr"
    write_perms = "adfmw"

    def __init__(self, users):
        """
        Constructor
        """
        super(DummyDictFTPAuthorizer, self).__init__()
        for username, user in users.iteritems():
            self.add_user(username,
                          user['password'],
                          user['homedir'],
                          perm=user.get('perm', 'elr'),
                          msg_login="Hi %s, you're welcome here." % user.get('name', username),
                          msg_quit="Bye %s, hoping you get back soon!" % user.get('name', username)
            )
        self.users = users

class FTPLogger:
    """
    Dummy class to encapsulate pyftpdlib logging.
    """

    def __init__(self, name):
        """
        Constructor
        """
        self.name = name

    def log(self, msg):
        """
        Log a message using the default logging handler.
        """
        logging.info("[%s] %s" % (self.name, msg) )

    def __call__(self, msg):
        """
        Calling the object will result in logging using the default logging handler.
        """
        self.log(msg)

def create_server(handler, users, listen_to="", port=21, data_port_range='5500-5700', name="Virtual FTP Server", masquerade_ip=None, max_connection=500, max_connection_per_ip=10):
    """
    Runs the FTP Server
    """

    try:
        start, stop = data_port_range.split('-')
        start = int(start)
        stop = int(stop)
    except ValueError:
        raise Exception('Invalid value for data ports')
    else:
        data_port_range = range(start, stop + 1)

    handler.authorizer = DummyDictFTPAuthorizer(users=users)

    handler.banner = "Ronan Python FTP Server. (Advice : Please use UTF-8 encoding and always use Binary mode)"
    handler.passive_ports = data_port_range

    if masquerade_ip:
        handler.masquerade_address = masquerade_ip

    # Instantiate FTP server class and listen to 0.0.0.0:21 or whatever is written in the config
    address = (listen_to, port)
    server = pyftpdlib.servers.FTPServer(address, handler)
    #if not isinstance(pyftpdlib.ftpserver.log, FTPLogger):
    #    pyftpdlib.ftpserver.log = FTPLogger(name)
    #    pyftpdlib.ftpserver.logline = FTPLogger(name)
    #    pyftpdlib.ftpserver.logerror = FTPLogger(name + " ERROR")

    # set a limit for connections
    server.max_cons = max_connection
    server.max_cons_per_ip = max_connection_per_ip

    return server


def create_ftp_server(users, listen_to="", port=21, data_port_range='5500-5700', name="FTP Server",
                      masquerade_ip=None,max_connection=500, max_connection_per_ip=10):
    """
        FTP Server implements normal FTP mode.
    """
    handler = FTPHandler
    return create_server(handler, users, listen_to=listen_to, port=port, data_port_range=data_port_range,
                         name=name, masquerade_ip=masquerade_ip, max_connection=max_connection,
                         max_connection_per_ip=max_connection_per_ip)


def create_secure_ftp_server(users, certificate, listen_to="", port=990, data_port_range='5700-5900', name="FTP Server",
                             masquerade_ip=None, max_connection=500, max_connection_per_ip=10):
    """
        FTP Server implements FTPS (FTP over TLS/SSL) mode.
          Note: Connect from client using "FTP over TLS/SSL explicit mode".
    """
    handler = SecureFTPHandler
    handler.certfile = certificate
    return create_server(handler, users, listen_to=listen_to, port=port, data_port_range=data_port_range,
                         name=name, masquerade_ip=masquerade_ip, max_connection=max_connection,
                         max_connection_per_ip=max_connection_per_ip)
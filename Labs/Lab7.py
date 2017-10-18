"""
- CS2911 - 011
- Fall 2017
- Lab N
- Names:
  - Chris Betances
  - Ben Halligan

A simple HTTP server
"""

import socket
import re
import threading
import os
import mimetypes
import datetime


def main():
    """ Start the server """
    http_server_setup(8080)


def http_server_setup(port):
    """
    Start the HTTP server
    - Open the listening socket
    - Accept connections and spawn processes to handle requests

    :param port: listening port number
    """

    # data_socket.send() place this in somewhere to send the info

    num_connections = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_address = ('', port)
    server_socket.bind(listen_address)
    server_socket.listen(num_connections)
    try:
        while True:
            request_socket, request_address = server_socket.accept()
            print('connection from {0} {1}'.format(request_address[0], request_address[1]))
            # Create a new thread, and set up the handle_request method and its argument (in a tuple)
            request_handler = threading.Thread(target=handle_request, args=(request_socket,))
            # Start the request handler thread.
            request_handler.start()
            # Just for information, display the running threads (including this main one)
            print('threads: ', threading.enumerate())
    # Set up so a Ctrl-C should terminate the server; this may have some problems on Windows
    except KeyboardInterrupt:
        print("HTTP server exiting . . .")
        print('threads: ', threading.enumerate())
        server_socket.close()


def handle_request(request_socket):
    """
    Handle a single HTTP request, running on a newly started thread.

    Closes request socket after sending response.

    Should include a response header indicating NO persistent connection

    :param request_socket: socket representing TCP connection from the HTTP client_socket
    :return: None
    """

    # Listen to port
    incoming_request = read_line(request_socket)
    file_name = get_file_name(incoming_request)
    # decipher requested info
    # find data
    # package data
    build_msg(file_name)
    # send msg


def request_thread(request_socket):
    handle_request(request_socket)


def build_msg(file_name):
    file_path = './', file_name
    # open file
    file_handle = open(file_path)
    # read header info
    header = build_header(file_path)
    file_data = file_handle.read().encode('ASCII')
    file_handle.close()
    return header, file_data


def build_header(file_path):
    status_code = b'500'
    if get_file_size(file_path) > 0:
        status_code = b'200'
    # fix length of to_bytes conversions from 4 to correct number
    timestamp = datetime.datetime.utcnow();
    timestring = timestamp.strftime('%a, %d, %b, %Y, %H:%M:%S GMT') + '\r\n'
    file_size = get_file_size(file_path).to_bytes(4, 'big')
    status_line = b'http/1.1 ' + status_code + b' OK\r\n'
    header = b'Content-Length: ' + file_size + b'\r\n'
    header = header + timestring.encode('big')
    header = header + b'Content-Type: ' + get_mime_type(file_path).to_bytes(4, 'big') + b'\r\n'
    return status_line + header + b'\r\n'


def get_file_name(request):
    file_name = ''
    request_dict = {}
    request = request.split(b'\r\n')
    for i in range(0, len(request)):
        request_part = request[i].split(b': ')
        request_dict[request_part[0]] = request_part[1]
    request = request.decode('ASCII')

    return file_name


def read_line(request_socket):
    """
    This method decodes the combined bytes

    :param int request_socket: The socket to read from
    :return: the decoded message in ASCII
    """
    b = read_bytes(request_socket)
    while b'\r\n' not in b:
        b = b + read_bytes(request_socket)
    return b.decode('ASCII')


def read_bytes(request_socket):
    """
    collects the bytes in the data stream

    :param request_socket: The socket that is being monitored
    :return: number of bytes determined by the nun_bytes
    :rtype: bytes
    """

    b = request_socket.recv(1)
    if len(b) == 0:
        raise Exception("End of Stream")
    return b


# ** Do not modify code below this line.  You should add additional helper methods above this line.

# Utility functions
# You may use these functions to simplify your code.


def get_mime_type(file_path):
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """
    Try to get the size of a file (resource) as number of bytes, given its path

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If file_path designates a normal file, an integer value representing the the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """

    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size



main()

# Replace this line with your comments on the lab


"""
Quarentine
"""



#
# def read_msg(data_socket):
#     """
#     This method converts a message in Hexadecimal to a human readable language
#
#     :param int data_socket: The socket to read from
#     :return: the decoded message to the console
#     """
#     total_length = get_length(data_socket)
#     if total_length == 0:
#         return b'Q'
#     else:
#         message = ''
#         for i in range(0, total_length):
#             message = message + read_line(data_socket)
#         print(message)
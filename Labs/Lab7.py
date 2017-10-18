"""
- CS2911 - 011
- Fall 2017
- Lab 7
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
            # handle_request(request_socket)
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

    request_status = b'404'
    # Listen to port
    incoming_request = read_line(request_socket)
    file_name = get_file_name(incoming_request)
    if file_name == '/':
        file_name = '/index.html'
    file_path = '.' + file_name
    message = b''
    if os.path.exists(file_path):
        request_status = b'200'
        message = build_msg(file_path)
    header = build_header(file_path, request_status)
    request_socket.sendall(header + message)
    request_socket.close()


def request_thread(request_socket):
    handle_request(request_socket)


def build_msg(file_path):
    """
    Gets selected file and returns data as bytes
    :param file_path: file location
    :return: file's data as bytes
    :author: halliganbs
    """
    file_handle = open(file_path, 'rb')
    file_data = file_handle.read()
    file_handle.close()
    return file_data


def build_header(file_path, request_status):
    """
    Creates a dictionary of header parts and then creates header
    :param file_path: provided file path
    :param request_status: numerical status code
    :return: Combined Status line and header
    :author: betanoes-leblancc
    """
    print(request_status)
    header_dict = {}
    header = ''
    if request_status == b'200':
        status_phrase = b'OK'
    elif request_status == b'404':
        status_phrase = b'Not Found'
    file_size = get_file_size(file_path)
    if file_size == None:
        file_size = 0
    timestamp = datetime.datetime.utcnow()
    time_string = timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')
    header_dict['Content-Length'] = str(file_size)
    header_dict['Content-Type'] = get_mime_type(file_path)
    header_dict['Date'] = time_string
    header_dict['Connection'] = 'close'
    status_line = b'http/1.1 ' + request_status + b' ' + status_phrase + b'\r\n'
    for k, v in header_dict.items():
        header += k + ': ' + v + '\r\n'
    print(status_line + header.encode('ASCII') + b'\r\n')
    return status_line + header.encode('ASCII') + b'\r\n'


def get_file_name(request):
    """
    Gets file name from HTTP request
    :param request: http request
    :return: name of file
    :author: betanoes-leblancc
    """
    file_name = ''
    print(request)
    request = request.split('\r\n')
    name_line = request[0].split(' ')
    if name_line[0] == 'GET':
        file_name = name_line[1]
    return file_name


def read_line(request_socket):
    """
    This method decodes the combined bytes

    :param int request_socket: The socket to read from
    :return: the decoded message in ASCII
    :author: halliganbs
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
    :author: betanoes-leblancc
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
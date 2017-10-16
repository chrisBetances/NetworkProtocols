"""
- CS2911 - 011
- Fall 2017
- Lab 6
- Names:
  - Chris Betances
  - Ben Halligan

A simple HTTP client
"""

# import the "socket" module -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket

# import the "regular expressions" module
import re


def main():
    """
    Tests the client on a variety of resources
    """

    # this resource request should result in "chunked" data transfer
    # get_http_resource('http://seprof.sebern.com/', 'index.html')
    # this resource request should result in "Content-Length" data transfer
    # get_http_resource('http://seprof.sebern.com/sebern1.jpg', 'sebern1.jpg')
    # get_http_resource('http://seprof.sebern.com:8080/sebern1.jpg', 'sebern2.jpg')
    
# another resource to try for a little larger and more complex entity
    get_http_resource('http://seprof.sebern.com/courses/cs2910-2014-2015/sched.md','sched-file.md')


def get_http_resource(url, file_name):
    """
    Get an HTTP resource from a server
           Parse the URL and call function to actually make the request.

    :param url: full URL of the resource to get
    :param file_name: name of file in which to store the retrieved resource

    (do not modify this function)
    """

    # Parse the URL into its component parts using a regular expression.
    url_match = re.search('http://([^/:]*)(:\d*)?(/.*)', url)
    url_match_groups = url_match.groups() if url_match else []
    #    print 'url_match_groups=',url_match_groups
    if len(url_match_groups) == 3:
        host_name = url_match_groups[0]
        host_port = int(url_match_groups[1][1:]) if url_match_groups[1] else 80
        host_resource = url_match_groups[2]
        print('host name = {0}, port = {1}, resource = {2}'.format(host_name, host_port, host_resource))
        status_string = make_http_request(host_name.encode(), host_port, host_resource.encode(), file_name)
        print('get_http_resource: URL="{0}", status="{1}"'.format(url, status_string))
    else:
        print('get_http_resource: URL parse failed, request not sent')


def make_http_request(host, port, resource, file_name):
    """
    Get an HTTP resource from a server

    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL after the domain name,
           including the first /.
    :param str file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :rtype: int
    """

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))
    # find status code
    request = b'GET ' + resource + b' HTTP/1.1\r\nHost: ' + host + b'\r\n\r\n'
    tcp_socket.send(request)
    status_code = get_status_code(tcp_socket)
    read_message(tcp_socket, file_name)
    return status_code


def read_size(tcp_socket):
    """
    Reads the size of the following chunk

    :param tcp_socket: The socket that is being monitored
    :rtype bytes
    :return: size of the next chunk
    """
    size_bytes = read_bytes(tcp_socket, 1)
    while b'\n' not in size_bytes:
        size_bytes = size_bytes + read_bytes(tcp_socket, 1)
    size_bytes = size_bytes[:-2]
    return int.from_bytes(size_bytes, 'big')


def read_chunk(tcp_socket, chunk_size):
    """
    collects and combines the chunk of bytes data

    :param tcp_socket: The socket that is being monitored
    :param chunk_size: Number of bytes to be collected
    :rtype: bytes
    :return: the total line of data
    """
    chunk = b''
    tgt_size = chunk_size + 2
    while len(chunk) < tgt_size:
        tgt_diff = tgt_size - len(chunk)
        read_bytes(tcp_socket, tgt_diff)
    return chunk


def read_chunk_body(tcp_socket):
    """
    reads the body of the data transmission

    :param tcp_socket: The socket that is being monitored
    :return: the whole combined body
    :rtype: bytes
    """

    complete_body = b''
    chunk_size = 1
    while chunk_size != 0:
        chunk_size = read_size(tcp_socket)
        if chunk_size != 0:
            complete_body = complete_body + read_chunk(tcp_socket, chunk_size)
    return complete_body


def read_body(tcp_socket, con_len):
    """
    reads the body of the data transmission

    :param tcp_socket: The socket that is being monitored
    :return: the whole combined body
    :rtype: bytes
    """

    complete_body = b''
    tgt_size = con_len
    while len(complete_body) < tgt_size:
        tgt_diff = tgt_size - len(complete_body)
        complete_body = complete_body + read_bytes(tcp_socket, tgt_diff)
    print(len(complete_body))
    return complete_body


def read_header(tcp_socket, file_handle):
    """
    reads the header of the data stream

    :param tcp_socket: The socket that is being monitored
    :return: the header data needed to process format
    :rtype:
    """
    header = b''
    header_dict = {}
    entry = b' '
    while len(entry) != 0:
        entry = pop_lib(tcp_socket, header)
        if len(entry) == 2:
            header_dict[entry[0]] = entry[1]
    if b'Transfer-Encoding' in header_dict:
        file_handle.write(read_chunk_body(tcp_socket))
        print(header_dict)
    elif b'Content-Length' in header_dict:
        con_len = int(header_dict[b'Content-Length'])
        print(header_dict)
        file_handle.write(read_body(tcp_socket, con_len))



def pop_lib(tcp_socket, header):
    while b'\r\n' not in header:
        header = header + read_bytes(tcp_socket, 1)
    if b': ' in header:
        data = header.split(b': ')
    else:
        data = b''
    return data


def get_status_code(tcp_socket):
    status_line = b''
    status_code = b''
    status_end = b''
    while status_line[-1:] != b' ':
        status_line = status_line + read_bytes(tcp_socket, 1)
    while status_code[-1:] != b' ':
        status_code = status_code + read_bytes(tcp_socket, 1)
    while status_end[-2:] != b'\r\n':
        status_end = status_end + read_bytes(tcp_socket, 1)
    status_code = status_code[:-1]
    status_code = status_code
    return status_code


def read_message(tcp_socket, file_name):
    # open file
    file_handle = open(file_name, 'wb')
    # read header info
    read_header(tcp_socket, file_handle)
    # close file and socket
    file_handle.close()
    tcp_socket.close()


def read_bytes(tcp_socket, num_bytes):
    """
    collects the bytes in the data stream

    :param tcp_socket: The socket that is being monitored
    :param num_bytes: number of bytes to be collected
    :return: number of bytes determined by the nun_bytes
    :rtype: bytes
    """

    b = tcp_socket.recv(num_bytes)
    if len(b) == 0:
        raise Exception("End of Stream")
    return b


main()
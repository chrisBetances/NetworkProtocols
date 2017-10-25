"""
- CS2911 - 011
- Fall 2017
- Lab 8
- Names:
  - Chris Betances
  - Ben Halligan

A simple email sending program.

Thanks to Trip Horbinski from the Fall 2015 class for providing the password-entering functionality.
"""

# GUI library for password entry
import tkinter as tk

# Socket library
import socket

# SSL/TLS library
import ssl

# base-64 encode/decode
import base64

# Python date/time and timezone modules
import datetime
import time
import pytz
import tzlocal

# Module for reading password from console without echoing it
import getpass

# Modules for some file operations
import os
import mimetypes

# Host name for MSOE (hosted) SMTP server
SMTP_SERVER = 'smtp.office365.com'

# The default port for STARTTLS SMTP servers is 587
SMTP_PORT = 587

# SMTP domain name
SMTP_DOMAINNAME = 'msoe.edu'


def main():
    """Main test method to send an SMTP email message.

    Modify data as needed/desired to test your code,
    but keep the same interface for the smtp_send
    method.
    """
    (username, password) = login_gui()

    message_info = {}
    message_info['To'] = 'halliganbs@msoe.edu'
    message_info['From'] = username
    message_info['Subject'] = 'Yet another test message'
    message_info['Date'] = 'Thu, 9 Oct 2014 23:56:09 +0000'
    message_info['Date'] = get_formatted_date()

    print("message_info =", message_info)

    message_text = 'Test message_info number 6\r\nAnother line.'

    smtp_send(password, message_info, message_text)


def login_gui():
    """
    Creates a graphical user interface for secure user authorization.

    :return: (email_value, password_value)
        email_value -- The email address as a string.
        password_value -- The password as a string.

    :author: Tripp Horbinski
    """
    gui = tk.Tk()
    gui.title("MSOE Email Client")
    center_gui_on_screen(gui, 370, 120)

    tk.Label(gui, text="Please enter your MSOE credentials below:") \
        .grid(row=0, columnspan=2)
    tk.Label(gui, text="Email Address: ").grid(row=1)
    tk.Label(gui, text="Password:         ").grid(row=2)

    email = tk.StringVar()
    email_input = tk.Entry(gui, textvariable=email)
    email_input.grid(row=1, column=1)

    password = tk.StringVar()
    password_input = tk.Entry(gui, textvariable=password, show='*')
    password_input.grid(row=2, column=1)

    auth_button = tk.Button(gui, text="Authenticate", width=25, command=gui.destroy)
    auth_button.grid(row=3, column=1)

    gui.mainloop()

    email_value = email.get()
    password_value = password.get()

    return email_value, password_value


def center_gui_on_screen(gui, gui_width, gui_height):
    """Centers the graphical user interface on the screen.

    :param gui: The graphical user interface to be centered.
    :param gui_width: The width of the graphical user interface.
    :param gui_height: The height of the graphical user interface.
    :return: The graphical user interface coordinates for the center of the screen.
    :author: Tripp Horbinski
    """
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    x_coord = (screen_width / 2) - (gui_width / 2)
    y_coord = (screen_height / 2) - (gui_height / 2)

    return gui.geometry('%dx%d+%d+%d' % (gui_width, gui_height, x_coord, y_coord))

# *** Do not modify code above this line ***


def smtp_send(password, message_info, message_text):
    """Send a message via SMTP.
    :param password: String containing user password.
    :param message_info: Dictionary with string values for the following keys:
                'To': Recipient address (only one recipient required)
                'From': Sender address
                'Date': Date string for current date/time in SMTP format
                'Subject': Email subject
    :param message_text:  String message that is to be sent
            Other keys can be added to support other email headers, etc.
    """
    # Set up socket
    old_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    old_socket.connect((SMTP_SERVER, SMTP_PORT))
    # Start pre SMTP steps
    pre_encrypt(old_socket)

    # Encryption starts here
    # encrypt socket and send message
    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(old_socket, server_hostname=SMTP_SERVER)
    auth_step(wrapped_socket, password, message_info)
    send_msg(wrapped_socket, message_info, message_text)
    # close everybody
    wrapped_socket.close()
    old_socket.close()
    pass  # Replace this line with your code


def build_header(message_info):
    """
    Helper method that builds header according to given format
    :param message_info: Dictionary of message info
    :return: header part : data \r\n
    :author: Halliganbs
    """
    header = ''
    for k, v in message_info.items():
        header += k + ':' + v + '\r\n'
    return header


def pre_encrypt(socket):
    response = read_line(socket)
    if response[:3] != '220':
        raise Exception('Server not ready to receive the EHLO')
    send(socket, b'EHLO ' + SMTP_DOMAINNAME.encode('ASCII'))
    response = read_line(socket)
    while '-' in response:
        response = read_line(socket)
    send(socket, b'STARTTLS')
    response = read_line(socket)
    # TODO there is a 90% chance that I need to change
    if '220' not in response:
        print(response)
        raise Exception('Not correct response, found response: ', response)
    print('--Everything beyonds this point is encrypted--')


def auth_step(socket, password, header):
    """
    Does the authentication with the SMTP server
    :param socket: encrypted socket to send/receive the responses
    :param password: user's password
    :param header: the message information -Might need some of this
    :return: might be void, most likely
    """
    send(socket, b'EHLO ' + SMTP_DOMAINNAME.encode('ASCII'))
    response = read_line(socket)
    while '-' in response:
        response = read_line(socket)
    auth_login = b'AUTH LOGIN'
    user_name = base64.b64encode(b'halliganbs@msoe.edu')  # rip inbox
    encode_pass = base64.b64encode(password.encode('ASCII'))

    send(socket, auth_login)

    # Server ask for username
    response_user = read_line(socket)
    if response_user[:3] != '334':
        raise Exception('Username question expected')
    send(socket, user_name)

    # server ask for password
    response_pass_ask = read_line(socket)
    if response_pass_ask[:3] != '334':
        raise Exception('Password Request Expected')
    send(socket, encode_pass)

    # server success?
    response_success = read_line(socket)
    if response_success[:3] != '235':
        print(response_success)
        raise Exception('Authentication was NOT successful')
    print('Authentication Successful')


def send_msg(socket, message_info, message_text):
    """
    Sends the message to the SMTP server and closes quits connections
    :param socket: socket to send/receive responses
    :param message_info: Data need about the Message
    :param message_text: Message itself
    :return: None
    """
    send(socket, b'MAIL FROM:' + message_info['From'].encode('ASCII'))
    response = read_line(socket)
    if response[:3] != '250':
        print(response)
        raise Exception('Did not like Mail From')
    send(socket, b'RCPT TO:' + message_info['To'].encode('ASCII'))
    response = read_line(socket)
    if response[:3] != '250':
        print(response)
        raise Exception('Did not like RCPT TO')
    send(socket, b'DATA')
    response = read_line(socket)
    if response[:3] != '354':
        print(response)
        raise Exception('')
    send(socket, build_header(message_info).encode('ASCII'))
    send(socket, message_text.encode('ASCII'))
    send(socket, b'.')
    response = read_line(socket)
    if response[:3] != '250':
        raise Exception('not OK')
    send(socket, b'QUIT')


def send(socket, data):
    socket.send(data + b'\r\n')


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


# Your code and additional functions go here. (Replace this line, too.)

# ** Do not modify code below this line. **

# Utility functions
# You may use these functions to simplify your code.


def get_formatted_date():
    """Get the current date and time, in a format suitable for an email date header.

    The constant TIMEZONE_NAME should be one of the standard pytz timezone names.
    If you really want to see them all, call the print_all_timezones function.

    tzlocal suggested by http://stackoverflow.com/a/3168394/1048186

    See RFC 5322 for details about what the timezone should be
    https://tools.ietf.org/html/rfc5322

    :return: Formatted current date/time value, as a string.
    """
    zone = tzlocal.get_localzone()
    print("zone =", zone)
    timestamp = datetime.datetime.now(zone)
    timestring = timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')  # Sun, 06 Nov 1994 08:49:37 +0000
    return timestring


def print_all_timezones():
    """ Print all pytz timezone strings. """
    for tz in pytz.all_timezones:
        print(tz)


# You probably won't need the following methods, unless you decide to
# try to handle email attachments or send multi-part messages.
# These advanced capabilities are not required for the lab assignment.


def get_mime_type(file_path):
    """Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: String containing path to (resource) file, such as './abc.jpg'
    :return: If successful in guessing the MIME type, a string representing the content
             type, such as 'image/jpeg'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """Try to get the size of a file (resource) in bytes, given its path

    :param file_path: String containing path to (resource) file, such as './abc.html'

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
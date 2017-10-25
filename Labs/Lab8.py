"""
- CS2911 - 0NN
- Fall 2017
- Lab 8
- Names:
  -
  -

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
    message_info['To'] = 'betances-leblancc@msoe.edu'
    message_info['From'] = username
    message_info['Subject'] = 'Yet another test message'
    message_info['Date'] = 'Thu, 9 Oct 2014 23:56:09 +0000'
    message_info['Date'] = get_formatted_date()

    print("message_info =", message_info)

    message_text = 'Test message_info number 6\r\n\r\nAnother line.'

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
            Other keys can be added to support other email headers, etc.
    """
    # old socket is tcp socket
    # wrapped is encrypted
    # check want is received then send response

    # Set up socket
    old_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    old_socket.connect((SMTP_SERVER, SMTP_PORT))
    # Start pre SMTP steps
    pre_enycript(old_socket)
    # Encryption starts here
    # encrypt socket and send message
    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(old_socket, server_hostname=SMTP_SERVER)
    auth_step(old_socket, password, message_info)
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
    header = header + 'To:'+message_info['To']+'\r\n' \
        + 'From:'+message_info['From']+'\r\n' \
        + 'Date:'+message_info['Date']+'\r\n' \
        + 'Subject:'+message_info['Subject']+'\r\r'
    return header


def pre_enycript(socket):
    socket.send(b'EHLO' + SMTP_DOMAINNAME.encode('ASCII'))
    response = socket.recv(200)
    print(response)
    socket.send(b'STARTTLS')
    response = socket.recv(3)
    # TODO there is a 90% chance that I need to change
    if response != '220 2.0.0 SMTP server ready':
        raise Exception('Not corrtect response, found repsonse: ' + response)
    print('--Everything beyonds this point is encrypted--')


def auth_step(socket, password, header):
    """
    Does the authentication with the SMTP server
    :param socket: encrypted socket to send/receive the responses
    :param password: user's password
    :param header: the message information -Might need some of this
    :return: might be void, most likely
    """
    auth_login = 'AUTH LOGIN'
    user_name = base64.b64encode(b'hallliganbs@msoe.edu')  # rip inbox
    encode_pass = base64.b64encode(password.encode('ASCII'))

    socket.send(auth_login)

    # Server ask for username
    response_user = socket.recv(3)
    if response_user != '354':
        raise Exception('Username question expected')
    socket.send(user_name)

    # server ask for password
    response_pass_ask = socket.recv(3)
    if response_pass_ask != '354':
        raise Exception('Password Request Expected')
    socket.send(encode_pass)

    # server success?
    response_success = socket.recv(3)
    if response_success != '235':
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
    socket.send(b'RCPT TO:' + message_info['To'].encode('ASCII'))
    response = socket.recv(3)
    if response != b'250':
        raise Exception('Response for the RCPT TO is not OK')
    socket.recv(3)
    socket.send('DATA')
    response = socket.recv(3)
    if response != b'354':
        raise Exception('')
    socket.recv(38) # may need to be 34
    socket.send(message_text)
    header = ''
    for k, v in message_info.items():
        header += k + ':' + v + "\n"
    socket.send(header.encode('ASCII'))
    socket.send('.')
    response = socket.recv(3)
    if response != b'250':
        raise Exception('not OK')
    socket.recv(3)
    socket.send(b'QUIT')


def build_attachment():
    pass


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

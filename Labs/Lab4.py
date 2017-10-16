def get_length():
    """
    THis method reads the number of lines in the message by reading the
    first 4 bytes and converting them to an int.

    :return: the length as an int
    """
    for i in range(0,4):
        line_length = line_length + int.from_bytes(next_byte(),'big')
    return line_length


def read_line():
    """
    This method decodes the combined bytes
    :return:
    """
    b = next_byte()
    while b != b'\x0a':
        msg =  msg + b.decode('ASCII')
    return msg + '\n'


def next_byte():
        """
        Enter the byte in hexadecimal shorthand
        e.g.
          input a byte: e3

        :return: the byte as a bytes object holding one byte
        :author: Eric Nowac
        """

        msg = input("input a byte: ")
        return (int(msg, 16).to_bytes(1, 'big'))


def read_msg():
    """
    This method converts a message in Hexadecimal to a human readable language

    :return: the decoded message to the console
    """
    message = ''
    for i in range(0,get_length()):
        message = message + read_line()
    print(message)


def main():
    read_msg()


if __name__ == '__name__':
    main()
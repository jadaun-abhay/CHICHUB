def encode(string):
    encoded_string = bin(string)[2:].replace('0', 'A').replace('1', 'B')
    return encoded_string

def decode(string):
    decoded_string = int('0b' + string.replace('A', '0').replace('B', '1'), 2)
    return decoded_string
from PIL import Image
from random import choice
import argparse

#   #   #   #   #   #   #   #   #   #   #   #   #   #   #    #
# Define basic bin -> ascii and ascii -> bin functions here. #
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #    #

def to_bin(s: str):
    """
    Returns a string of bytes from a string of text;
    "hello" => "0110100001100101011011000110110001101111"
    """
    return "".join([ str(bin(ord(char)))[2:].zfill(8) for char in s])

def to_ascii(b: str):
    """
    Returns a string of characters from a string of bytes:
    "0110100001100101011011000110110001101111" => "hello"
    """
    pos = 0
    s = ""
    while pos * 8 < len(b):
        s += decode_byte(b[pos * 8:pos * 8 + 8])
        pos += 1
    return s

def decode_byte(b: str):
    """
    Returns string representation of a byte into a character:
    "11000001" => "a"
    """
    return chr(int(bytes(b, "utf-8"), 2))



#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
# Actual image encodings and decodings here.                #
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #

channels = {"red": 0, "green": 1, "blue": 2}

def encode_message(img, msg, ch="red"):
    """
    writes an ascii message (msg) into the ch channel
    of your chosen image as a sequence of 1s and 0s.
    """
    write_binary_data(img, to_bin(msg), ch)

def decode_message(img, ch="red"):
    """
    Reads a potential message encoded by this program from
    an image file (img), hidden in the ch colour channel.
    A message begins with 24 0s and ends with 24 0s in a row.
    """
    return to_ascii(get_binary_data(img, ch))

def remove_message(img, ch="red"):
    for x in range(width):
        for y in range(height):
            new_val = img[x, y][channels[ch]] + choice([0, choice([-1,1])])
            img[x, y] = replace_pixel(img[x, y], new_val, ch)

def get_binary_data(img, ch="red"):
    """
    Reads ch channels' parity as 0 or 1 into b and returns.
    Terminates on 24 bits of "10101010..."
    """
    b = ""
    key_seq = "10"*12
    for x in range(width):
        for y in range(height):
            b += str(img[x, y][channels[ch]] % 2)
            if width * y + x == 24 and b[:24] != key_seq:
                return to_bin("no message found!")
    return b[24: b[24:].index(key_seq) + 24] # cut out everything outside key_seq

def write_binary_data(img, msg, ch="red"):
    """
    Writes an already encoded string of bytes into the pixels of
    the chosen image from a given message. msg is a sequence
    of 1s and 0s.
    """
    # message ends and starts with 24 bits of alternating 1s and 0s.
    msg = "10"*12 + msg + "10"*12
    msg_pos = 0
    for x in range(width):
        for y in range(height):
            if msg_pos >= len(msg):
                return 1
            if msg[msg_pos] == "0":
                img[x, y] = replace_pixel(img[x, y], round_even(img[x, y][channels[ch]]), ch)
            else:
                img[x, y] = replace_pixel(img[x, y], round_odd(img[x, y][channels[ch]]), ch)
            msg_pos += 1

def round_even(n):
    """
    Rounds an integer to a near even number.
    """
    if n == 255:
        return 254
    return n if (n % 2 == 0) else n + choice([-1,1])

def round_odd(n):
    """
    Rounds an integer to near odd number.
    """
    if n == 0:
        return 1
    return n if (n % 2 == 1) else n + choice([-1,1])

# this is really clumsy and slow.
def replace_pixel(pixel, new_val, ch="red"):
    """
    Returns a pixel 3-tuple (r,g,b), where the ch-corresponding
    colour is replaced by new_val.
    """
    r, g, b = pixel
    if ch == "red":
        return (new_val, g, b)
    elif ch == "green":
        return (r, new_val, b)
    else:
        return (r, g, new_val)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog="Simple Binary Stenography Tool", 
                    description="Encode and decode a message into and from one of the colour channels\nof an image.",
                    epilog="")
    
    parser.add_argument("filename", help="name of the image file.")
    parser.add_argument("-e", "--encode", metavar="MESSAGE", nargs=1, help="encode a message into the image file.")
    parser.add_argument("-d", "--decode", action="store_true", help="read a message from the image file.")
    parser.add_argument("-c", "--channel", metavar="COLOUR", nargs=1, help="red/green/blue")
    parser.add_argument("-s", "--scramble", action="store_true", help="remove any message from given channel.")
    args = parser.parse_args()
    
    image = Image.open(args.filename).convert("RGB")
    img = image.load()
    width, height = image.size

    try:
        channel = args.channel[0]
    except Exception:
        channel = "red"

    if args.decode:
        print(decode_message(img, channel))
    elif args.encode:
        encode_message(img, args.encode[0], channel)
        image.save("encoded.png")
    elif args.scramble:
        remove_message(img, channel)
        image.save(args.filename)
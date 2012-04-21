#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Lorenz SZ40/42 Cipher Machine simulator
#
# Author(s): Mike Dusseault
#

import sys
import random

#
# Stuff to convert between ASCII and Baudot code
#

# LTRS is the control code for Baudot letters mode.
# LTRS = 11111 = 31
LTRS = 31

# FIGS is the control code for the Baudot figures mode.
# FIGS = 11011 = 27
FIGS = 27

# SPACE = 00100
# CR = 00010, LF = 01000  Use in pairs

# For converting from ASCII to Baudot
#                            \b       \n       \r
ATOB = [ 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 2, 0, 0, 8, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#       ' ' !  "  #  $  %  &  ' (  )   *  +  ,  -  .  /
         4, 0, 0,20, 0,13, 0, 5,15,18, 0,17,12, 3,28,29,
#        0  1  2  3  4  5  6  7  8  9  :  ;  <  =  >  ?
        22,23,19, 1,10,16,21, 7, 6,24,14, 0, 0,30, 0,25,
#        @  A  B  C  D  E  F  G  H  I  J  K  L  M  N  O
        31, 3,25,14, 9, 1,13,26,20, 6,11,15,18,28,12,24,
#        P  Q  R  S  T  U  V  W  X  Y  Z  [  \  ]  ^  _
        22,23,10, 5,16, 7,30,19,29,21,17,15,29,18, 0, 0,
#        `  a  b  c  d  e  f  g  h  i  j  k  l  m  n  o
         5, 3,25,14, 9, 1,13,26,20, 6,11,15,18,28,12,24,
#        p  q  r  s  t  u  v  w  x  y  z  {  |  }  ~  DEL
        22,23,10, 5,16, 7,30,19,29,21,17,15, 0,18, 9, 0]

# For converting from Baudot to ASCII
# From http://www.codesandciphers.org.uk/lorenz/fish.htm
#           0    1    2    3    4    5    6    7    8    9
B2A_LTRS = ['*', 'E','\n', 'A', ' ', 'S', 'I', 'U','\r', 'D',
#           10   11  12    13   14   15   16   17   18   19
            'R', 'J', 'N', 'F', 'C', 'K', 'T', 'Z', 'L', 'W',
#           20   21   22   23   24   25   26   27   28   29
            'H', 'Y', 'P', 'Q', 'O', 'B', 'G',  '', 'M', 'X',
#           30   31
            'V', '']
# Tilda (~) here represents "WHO ARE YOU" message. * is a nul.
#           0    1    2    3    4    5    6    7    8    9
B2A_FIGS = ['*', '3','\n', '-', ' ','\'', '8', '7','\r', '~',
#           10   11   12   13   14   15   16   17   18   19
            '4','\b', ',', '%', ':', '(', '5', '+', ')', '2',
#           20   21   22   23   24   25   26   27   28   29
            '#', '6', '0', '1', '9', '?', '@',  '', '.', '/',
#           30   31
            '=', '']

# ITA2 Letters - In case I need them later, or just want to
# use them. NOTE: I haven't checked them well.
#                            \b       \n       \r
#ATOB = [ 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 2, 0, 0, 8, 0, 0,
#         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#       ' ' !  "  #  $  %  &  ' (  )   *  +  ,  -  .  /
#         4,11,13, 2,20, 2, 9, 5,15,18, 0,17,12, 3,28,29,
#        0  1  2  3  4  5  6  7  8  9  :  ;  <  =  >  ?
#        22,23,19, 1,10,16,21, 7, 6,24,14,12, 8,30, 8,25,
#        @  A  B  C  D  E  F  G  H  I  J  K  L  M  N  O
#        31, 3,25,14, 9, 1,13,26,20, 6,11,15,18,28,12,24,
#        P  Q  R  S  T  U  V  W  X  Y  Z  [  \  ]  ^  _
#        22,23,10, 5,16, 7,30,19,29,21,17,15,29,18,13,26,
#        `  a  b  c  d  e  f  g  h  i  j  k  l  m  n  o
#         5, 3,25,14, 9, 1,13,26,20, 6,11,15,18,28,12,24,
#        p  q  r  s  t  u  v  w  x  y  z  {  |  }  ~  DEL
#        22,23,10, 5,16, 7,30,19,29,21,17,31,27,28, 4, 0]
#B2A_LTRS = ['*', 'E', '\n', 'A', ' ', 'S', 'I', 'U', '\r', 'D',
#            'R', 'J', 'N',  'F', 'C', 'K', 'T', 'Z', 'L',  'W',
#            'H', 'Y', 'P',  'Q', 'O', 'B', 'G', '', 'M',  'X',
#            'V', '']
#B2A_FIGS = ['*', '3', '\n', '-', ' ', '\b', '8', '7', '\r', '$',
#            '4', '\'', ',', '!', ':', '(', '5', '\"', ')',  '2',
#            '#', '6', '0',  '1', '9', '?', '&', '', '.',  '/',
#            ';', '']

def ascii_to_baudot_char(ch):
    return ATOB[ch & 0x7f]

def baudot_to_ascii_char(c, letters):
    if letters:
        return B2A_LTRS[c & 0x7f]
    else:
        return B2A_FIGS[c & 0x7f]

def baudot_to_ascii(s):
    """ Converts a string in Baudot, with 5 bits per byte, into an ASCII string.
    
    >>> [ord(c) for c in baudot_to_ascii(''.join([chr(d) for d in [3, 25, 27, 12, 31, 4, 14]]))]
    [65, 66, 44, 32, 67]
    """

    result = []
    mode = LTRS
    for ch in s:
        if ord(ch) == LTRS:
            mode = LTRS
        elif ord(ch) == FIGS:
            mode = FIGS

        result.append(baudot_to_ascii_char(ord(ch), mode == LTRS))

    return ''.join(result)

def ascii_to_baudot(s):
    """ Converts a string in ASCII (containing only allowable characters for
        Baudot code), into a string in Baudot with 5 bits per byte.

    >>> [ord(c) for c in ascii_to_baudot('AB, C')]
    [3, 25, 27, 12, 31, 4, 14]
    """

    result = []
    mode = LTRS
    for ch in s:
        # If LETTERS, and in FIGS mode, change
        if ((ord(ch) >= ord('A') and ord(ch) <= ord('Z')) or
            ord(ch) == ord(' ') or ord(ch) == ord('\n') or
            ord(ch) == ord('\r')):
            if mode == FIGS:
                mode = LTRS
                result.append(chr(mode))
        # If FIGS and in LTRS, change
        else:
            if mode == LTRS:
                mode = FIGS
                result.append(chr(mode))
        result.append(chr(ATOB[ord(ch) & 0x7f]))

    return ''.join(result)


class Wheel:
    """ Class representing a specific wheel. """

    def __init__(self, wheel_data, initial):
        self.wheel_data = wheel_data
        self.wheel_size = len(wheel_data)
        self.state = initial

    def advance(self):
        self.state = (self.state + 1) % self.wheel_size

    def get_val(self):
        return self.wheel_data[self.state]

    def get_current_pos(self):
        return self.state

    def __repr__(self):
        return "State:" + str(self.state) + "; Size:" +\
               str(self.wheel_size) + "; Wheel:" + str(self.wheel_data)


class WheelBank:
    """ Class for a bank of wheels. """

    def __init__(self, wheels):
        self.wheels = wheels

    def advance(self):
        for w in self.wheels:
            w.advance()

    def get_val(self):
        result = []
        for i in xrange(5):
            result.append(self.wheels[i].get_val())
        # Wheel numbered 1 is low bit, so we need to flip the bit order.
        # NOTE: I'm not 100% sure which wheel has the MSB and which the
        # LSB. Would be nice to confirm this better. Diagrams seem to show
        # wheel K1, for example, on input 1. And a Baudot code chart nearby
        # shows bit #1 as LSB. So I think this is right...
        return int("0b" + ''.join([str(i) for i in result[::-1]]), 2)

    def __repr__(self):
        result = []
        for e in self.wheels:
            result.append(str(e))
        return '\n'.join(result)

class MotorWheelBank(WheelBank):
    """ Class for the motor wheel bank, which is slightly different than
        the other wheel banks. Inherits from WheelBank, but overrides the
        advance() method and adds an is_active() method to see if the S
        wheels should be advanced.
    """

    def advance(self):
        self.wheels[0].advance()
        if self.wheels[0].get_val():
            self.wheels[1].advance()

    def is_active(self):
        return self.wheels[1].get_val()
        # Following is what the course video says, but that is not
        # supported by any other documentation, and I think it's wrong.
        #return self.wheels[0].get_val() ^ self.wheels[1].get_val()

def make_wheel(size):
    """ Used to randomly generate the on/off pin positions for a wheel. """

    return [random.choice([0, 1]) for _ in xrange(size)]


class LorenzCipher:
    """ Represents an instance of a Lorenz Cipher Machine. """

    def __init__(self, K, S, M, initial=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
        self.K_wheels = WheelBank([Wheel(data, i)
                                   for data, i in zip(K, initial[:5])])
        self.S_wheels = WheelBank([Wheel(data, i)
                                   for data, i in zip(S, initial[7:])])
        self.M_wheels = MotorWheelBank([Wheel(data, i)
                                        for data, i in zip(M, initial[5:8])])

    def advance(self):
        """ Advances the wheels. Should be called after every encrypt or
            decrypt.
        """

        # K wheels advance every time
        self.K_wheels.advance()

        # M wheels "advance" every time. They do not all advance, like
        # K and S wheels. See MotorWheelBank class for details.
        self.M_wheels.advance()

        # If the M_wheels are set such that the S wheels should advance,
        # do so.
        if self.M_wheels.is_active():
            self.S_wheels.advance()

    def crypt_char(self, c):
        """ Encrypt/decrypt a single character. Expects an ordinal of the
            character.
        """

        result = c ^ self.K_wheels.get_val() ^ self.S_wheels.get_val()
        self.advance()
        return result


    def crypt(self, m):
        """ Encrypt/decrypt a message string. Uses Baudot encoding. """

        return ''.join([chr(self.crypt_char(ord(c))) for c in m])


def test():
    K_sizes = [41, 31, 29, 26, 23]
    S_sizes = [43, 47, 51, 53, 59]
    M_sizes = [61, 37]

    # This will generate new wheel settings
    #K_wheels = [make_wheel(K_sizes[i]) for i in xrange(len(K_sizes))]
    #S_wheels = [make_wheel(S_sizes[i]) for i in xrange(len(S_sizes))]
    #M_wheels = [make_wheel(M_sizes[i]) for i in xrange(len(M_sizes))]

    # Hard coded wheel settings for reproduceability during testing
    K_wheels = [
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1,
         1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
         0, 1, 1, 1, 0, 0, 1, 1],
        [0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1,
         1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1,
         0, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1]]
    S_wheels = [
        [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1,
         0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1,
         0],
        [1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1,
         0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0,
         1, 1, 1, 0, 1],
        [0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0,
         1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0,
         1, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0,
         0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0,
         1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0]]
    M_wheels = [
        [1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0,
         0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1,
         0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0,
         1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0]]

    # Indicator represents the start positions of the wheels, in this order:
    # [K1, K2, K3, K4, K5, M1, M2, S1, S2, S3, S4, S5]
    indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # Instatiate a cipher machine for the sending and receiving end.
    src_cipher = LorenzCipher(K_wheels, S_wheels, M_wheels, indicator)
    dst_cipher = LorenzCipher(K_wheels, S_wheels, M_wheels, indicator)

    # Display the wheel settings
    print "--- K Wheels ---"
    print src_cipher.K_wheels
    print "--- S Wheels ---"
    print src_cipher.S_wheels
    print "--- M Wheels ---"
    print src_cipher.M_wheels


    print "------------------------------"
    m = 'WE ATTACK AT DAWN AT 0600 HOURS. BRING BEER.'
    print "Plaintext:", m
    m_e = ascii_to_baudot(m)
    print "m_e:", [ord(c) for c in m_e]

    c = src_cipher.crypt(m_e)
    print 'Ciphertext: "%s"' % baudot_to_ascii(c)
    print "Ciphertext ordinals:", [ord(ch) for ch in c]

    decr = dst_cipher.crypt(c)
    print "Decrypted:", baudot_to_ascii(decr)
    
    
def write_keyfile(output_file, K_sizes, S_sizes, M_sizes,
                  K_wheels, S_wheels, M_wheels, indicator):
    f = open(output_file, 'w')
    f.write("# Number of teeth on each wheel [K1, K2, K3, K4, K5]\n")
    f.write("K_sizes = %s\n" % str(K_sizes))
    f.write("# Number of teeth on each wheel [S1, S2, S3, S4, S5]\n")
    f.write("S_sizes = %s\n" % str(S_sizes))
    f.write("# Number of teeth on each wheel [M1, M2]\n")
    f.write("M_sizes = %s\n" % str(M_sizes))
    f.write("\n# Pin settings for the wheels\n")
    f.write("K_wheels = %s\n" % str(K_wheels))
    f.write("S_wheels = %s\n" % str(S_wheels))
    f.write("M_wheels = %s\n" % str(M_wheels))
    f.write("\n# Indicator represents the start positions of the wheels, in "\
            "this order:\n")
    f.write("# [K1, K2, K3, K4, K5, M1, M2, S1, S2, S3, S4, S5]\n")
    f.write("indicator = %s\n\n" % str(indicator))
    f.close()


def main():
    if len(sys.argv) == 3:
        cmd = sys.argv[1]

        if cmd == 'k':
            key_file = sys.argv[2]
            # This will generate new wheel settings
            K_sizes = [41, 31, 29, 26, 23]
            S_sizes = [43, 47, 51, 53, 59]
            M_sizes = [61, 37]
            K_wheels = [make_wheel(K_sizes[i]) for i in xrange(len(K_sizes))]
            S_wheels = [make_wheel(S_sizes[i]) for i in xrange(len(S_sizes))]
            M_wheels = [make_wheel(M_sizes[i]) for i in xrange(len(M_sizes))]
            # Indicator represents the start positions of the wheels,
            #   in this order:
            # [K1, K2, K3, K4, K5, M1, M2, S1, S2, S3, S4, S5]
            indicator = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            write_keyfile(key_file, K_sizes, S_sizes, M_sizes, K_wheels, S_wheels, M_wheels, indicator)
            print "New key data written to", key_file
        elif cmd == 'b':
            baudot_file = sys.argv[2]
            f = open(baudot_file, 'r')
            bcode = f.read()
            f.close()
            print baudot_to_ascii(bcode)
            #print
        else:
             print_usage()

    elif len(sys.argv) == 5:
        cmd = sys.argv[1]
        input_file = sys.argv[2]
        key_file = sys.argv[3]
        output_file = sys.argv[4]

        #print input_file, output_file, key_file
        f = open(key_file, 'r')
        exec f
        f.close()
        
        if cmd == 'e':
            f = open(input_file, 'r')
            input_ascii = f.read()
            f.close()
            input_baudot = ascii_to_baudot(input_ascii)

            cipher = LorenzCipher(K_wheels, S_wheels, M_wheels, indicator)

            ciphertext = cipher.crypt(input_baudot)

            f = open(output_file, 'w')
            f.write(ciphertext)
            f.close()
            print "Encrypted message written to", output_file
            
        elif cmd == 'd':
            f = open(input_file, 'r')
            input_ciphertext = f.read()
            f.close()

            cipher = LorenzCipher(K_wheels, S_wheels, M_wheels, indicator)

            plaintext_baudot = cipher.crypt(input_ciphertext)
            plaintext_ascii = baudot_to_ascii(plaintext_baudot)

            f = open(output_file, 'w')
            f.write(plaintext_ascii)
            f.close()
            print "Decrypted message written to", output_file
            
        else:
            print_usage()
            
    else:
        print_usage()

def print_usage():
    print "Usage: %s <command> <arguments>" % sys.argv[0]
    print "    <commands>"
    print "        k <key file>: Creates a random key file with normal SZ40/42 teeth"
    print "            counts and 0 indicators. Edit the file to suit."
    print "        e <input file> <key file> <output file>: Encode ASCII plaintext to"
    print "            Baudot code (5 bits per byte) and encrypt with wheel settings"
    print "            in key file, writing ciphertext to output file."
    print "        d <input file> <key file> <output file>: Decrypt the input file"
    print "            with wheel settings in key file, decode from Baudot code and"
    print "            and output ASCII plaintext to output file."
    print "        b <input file>: Read input file in Baudot code and display ASCII"
    print "            equivalent."
    print

if __name__ == "__main__":
    #test()
    main()




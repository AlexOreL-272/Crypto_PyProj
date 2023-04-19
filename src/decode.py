from src.globals import Globals

from PIL import Image, ImageDraw
from random import randint

import re


class Decrypt:
    """
    Class with decryption methods
    """
    base64_step = 4

    frequency_in_english = (43.31, 10.56, 23.13, 17.25, 56.88, 9.24,
                            12.59, 15.31, 38.45, 1, 5.61, 27.98, 15.36,
                            33.92, 36.51, 16.14, 1, 38.64, 29.23, 35.43,
                            18.51, 5.13, 6.57, 1.48, 9.06, 1.39
                            )  # occurrence in english alphabet for a-z respectively

    @staticmethod
    def __get_caesar_rot__(cypher_text):
        """
        :param cypher_text: encoded text
        :return: rotation of Caesar cypher

        Uses frequency analysis to find the rotation of Caesar cypher
        """
        # assume that length of cypher text is big enough to use frequency method
        mp = {Globals.base64_alphabet[i]: 0 for i in range(Globals.alphabet_len)}
        text_copy = re.sub('[^\w]', '', cypher_text).upper()

        for item in text_copy:
            if item in Globals.base64_alphabet[0:Globals.alphabet_len]:
                mp[item.upper()] += 1

        max_sum = 0
        max_idx = 0

        for i in range(Globals.alphabet_len):  # iterate through possible rotations of caesar cypher
            total = 0
            for j in range(Globals.alphabet_len):
                total += mp[Globals.base64_alphabet[j]] * Decrypt.frequency_in_english[(j - i) % Globals.alphabet_len]
            if total > max_sum:
                max_sum = total
                max_idx = i

        return max_idx

    @staticmethod
    def caesar(cypher_text):
        """
        :param cypher_text: encoded text
        :return: decrypted string

        Performs automatic Caesar decryption using frequency analysis. Works for pretty long inputs
        """
        decrypted = ''
        rot = Decrypt.__get_caesar_rot__(cypher_text)

        for item in cypher_text:
            if item.islower():
                decrypted += chr((ord(item) - ord('a') - rot) % Globals.alphabet_len + ord('a'))
            elif item.isupper():
                decrypted += chr((ord(item) - ord('A') - rot) % Globals.alphabet_len + ord('A'))
            else:
                decrypted += item

        return decrypted

    @staticmethod
    def __get_vigenere_key__(cypher_text, key_len):
        """
        :param cypher_text: text to decrypt
        :param key_len: length of key
        :return: key used to encrypt this text

        Finds Vigenere key using frequency analysis. Does not needed in this version of project
        """
        text_copy = re.sub('[^\w]', '', cypher_text)
        output = ''

        for i in range(key_len):
            cur = ''
            for j in range(i, len(text_copy), key_len):
                cur += text_copy[j]
            output += chr(ord('A') + Decrypt.get_caesar_rot(cur))

        return output

    @staticmethod
    def vigenere(cypher_text, key):
        """
        :param cypher_text: encoded text
        :param key: key to decrypt the text
        :return: decrypted string

        Performs Vigenere decryption of given text
        """
        # Firstly, I wanted to decrypt Vigenere automatically like Caesar, but...
        # key = Decrypt.get_vigenere_key(cypher_text, Decrypt.get_vigenere_key_len(cypher_text))
        codes = [ord(elem.lower()) - ord('a') for elem in key]
        size = len(codes)
        current_position = 0

        output = ''

        for item in cypher_text:
            if item.islower():
                output += chr((ord(item) - ord('a') - codes[current_position]) % Globals.alphabet_len + ord('a'))
                current_position = (current_position + 1) % size
            elif item.isupper():
                output += chr((ord(item) - ord('A') - codes[current_position]) % Globals.alphabet_len + ord('A'))
                current_position = (current_position + 1) % size
            else:
                output += item

        return output

    @staticmethod
    def vernam(cypher_text, key):
        """
        :param cypher_text: encoded text
        :param key: key to decrypt the text
        :return: decrypted string

        Performs Vernam decryption of given text
        """
        codes = [ord(elem.upper()) - ord('A') for elem in key]
        size = len(key)

        current_position = 0
        output = ''

        for item in cypher_text:
            possible_char_low = chr(((ord(item) - ord('a')) ^ codes[current_position]) + ord('a'))
            possible_char_high = chr(((ord(item) - ord('A')) ^ codes[current_position]) + ord('A'))

            if possible_char_low.isalpha():
                output += possible_char_low
                current_position = (current_position + 1) % size
            elif possible_char_high.isalpha():
                output += possible_char_high
                current_position = (current_position + 1) % size
            else:
                output += item

        return output

    @staticmethod
    def base64(cypher_text):
        """
        :param cypher_text: encoded text
        :return: decrypted string

        Performs Base64 decryption of given text
        """
        tail = cypher_text.count('=')
        cypher_text = cypher_text.replace('=', 'A')

        decrypted = ''
        for i in range(0, len(cypher_text), Decrypt.base64_step):
            # need to convert 4 chars from 6-bit to 3 chars in 8-bit
            cur = 0
            for j in range(Decrypt.base64_step):
                cur = (cur << Globals.char_6bit) | (Globals.base64_alphabet.find(cypher_text[i + j])
                                                    & Globals.bitmask_6right_bit)

            for j in range((Decrypt.base64_step * Globals.char_6bit) // Globals.char_8bit):
                decrypted += chr((cur >> 2 * Globals.char_8bit) & Globals.bitmask_8right_bit)
                cur <<= Globals.char_8bit

        if tail:
            decrypted = decrypted[0:-tail]

        return decrypted

    @staticmethod
    def stega(keys_path, image_path):
        """
        :param keys_path: path to file with steganography keys
        :param image_path: path to encrypted image
        :return: decrypted string

        Performs steganography decryption of given image (in .bmp, .png or .jpeg format)
        """
        decrypted = ''
        img = Image.open(image_path)
        pixels = img.load()

        with open(keys_path) as coords:
            for line in coords:
                current_pos = (int(re.findall('\((\d+),', line)[0]), int(re.findall(', (\d+)\)', line)[0]))
                key = int(re.findall(':: (\d+)', line)[0])
                r, g, b = pixels[current_pos][0:Globals.color_model_sz]

                char = ((r ^ (key >> (2 * Globals.char_8bit))) << Globals.stega_bit_shift[0]) | \
                       ((g ^ ((key >> Globals.char_8bit) & Globals.bitmask_8right_bit)) << Globals.stega_bit_shift[1]) \
                    | (b ^ (key & Globals.bitmask_8right_bit))
                decrypted += chr(char)

        return decrypted

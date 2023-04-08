from src.encode import Encrypt
from src.globals import Globals

from PIL import Image, ImageDraw
from random import randint

import re


class Decrypt:
    base64_step = 4

    frequency_in_english = (43.31, 10.56, 23.13, 17.25, 56.88, 9.24,
                            12.59, 15.31, 38.45, 1, 5.61, 27.98, 15.36,
                            33.92, 36.51, 16.14, 1, 38.64, 29.23, 35.43,
                            18.51, 5.13, 6.57, 1.48, 9.06, 1.39
                            )  # occurrence in english alphabet for a-z respectively

    @staticmethod
    def __get_caesar_rot__(cypher_text):
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
        return Encrypt.vernam(cypher_text, key)

    @staticmethod
    def base64(cypher_text):
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
from src.globals import Globals

from PIL import Image, ImageDraw
from random import randint

import re


class Encrypt:
    base64_step = 3

    @staticmethod
    def caesar(plain_text, rot):
        encrypted = ''

        for item in plain_text:
            if item.islower():
                encrypted += chr((ord(item) - ord('a') + rot) % Globals.alphabet_len + ord('a'))
            elif item.isupper():
                encrypted += chr((ord(item) - ord('A') + rot) % Globals.alphabet_len + ord('A'))
            else:
                encrypted += item

        return encrypted

    @staticmethod
    def vigenere(plain_text, key):
        codes = [ord(elem.lower()) - ord('a') for elem in key]
        current_position = 0
        size = len(codes)

        output = ''
        for item in plain_text:
            if item.islower():
                output += chr((ord(item) - ord('a') + codes[current_position]) % Globals.alphabet_len + ord('a'))
                current_position = (current_position + 1) % size
            elif item.isupper():
                output += chr((ord(item) - ord('A') + codes[current_position]) % Globals.alphabet_len + ord('A'))
                current_position = (current_position + 1) % size
            else:
                output += item

        return output

    @staticmethod
    def vernam(plain_text, key):
        plain_text = plain_text.upper()
        codes = [ord(elem.upper()) - ord('A') for elem in key]
        size = len(key)

        current_position = 0
        output = ''

        for item in plain_text:
            if not item.isalpha():
                output += item
                continue

            output += chr(((ord(item) - ord('A')) ^ codes[current_position]) + ord('A'))
            current_position = (current_position + 1) % size

        return output

    @staticmethod
    def base64(plain_text):
        # default base64 encryption
        tail = (-len(plain_text)) % Encrypt.base64_step  # need size of plain text to be divisible by 6
        plain_text += '\x00' * tail  # adding zero-bits to the end for padding

        encrypted = ''
        for i in range(0, len(plain_text), Encrypt.base64_step):
            # need to convert 3 chars from 8-bit to 4 chars in 6-bit
            cur = 0
            for j in range(Encrypt.base64_step):
                cur = (cur << Globals.char_8bit) | ord(plain_text[i + j])

            for j in range((Encrypt.base64_step * Globals.char_8bit) // Globals.char_6bit):
                encrypted += Globals.base64_alphabet[(cur >> (Encrypt.base64_step * Globals.char_6bit))
                                                     & Globals.bitmask_6right_bit]
                cur <<= Globals.char_6bit

        if tail:
            encrypted = encrypted[0:-tail] + '=' * tail

        return encrypted

    @staticmethod
    def stega(text, image_path):
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size[0], img.size[1]

        text = [ord(elem) for elem in text]

        with open('coords.keys', 'w') as coords:
            # will XOR 3-2-3 last bits of red, green and blue parts of a pixel respectively
            for elem in text:
                pos = (randint(1, width - 1), randint(1, height - 1))
                r_init, g_init, b_init = pixels[pos][0:Globals.color_model_sz]  # initial values of RGB

                r_enc, g_enc, b_enc = elem >> Globals.stega_bit_shift[0], \
                    (elem >> Globals.stega_bit_shift[1]) & Globals.bitmask_2right_bit, \
                    elem & Globals.bitmask_3right_bit  # values to encode a char

                ImageDraw.Draw(img).point(pos, (r_init ^ r_enc, g_init ^ g_enc, b_init ^ b_enc))
                coords.write('{pos} :: {key}\n'.format(pos=pos, key=(r_init << (2 * Globals.char_8bit)) |
                                                                    (g_init << Globals.char_8bit) | b_init))
            img.save('encoded.png', 'PNG')

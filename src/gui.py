from src.decode import Decrypt
from src.encode import Encrypt

import re
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class CoderGUI:
    font_sz = 12
    padding = 10
    text_area_width = 40
    text_area_height = 20

    def __init__(self):
        self.loaded_file = ""

        self.root = tk.Tk()
        self.root.title('Encode-Decode')

        # Left text area
        self.encode_area = tk.Text(self.root, font=('Arial', CoderGUI.font_sz), width=CoderGUI.text_area_width,
                                   height=CoderGUI.text_area_height, wrap='word')
        self.encode_area.pack(side=tk.LEFT, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # Right text area
        self.decode_area = tk.Text(self.root, font=('Arial', CoderGUI.font_sz), width=CoderGUI.text_area_width,
                                   height=CoderGUI.text_area_height, wrap='word')
        self.decode_area.pack(side=tk.RIGHT, padx=CoderGUI.padding, pady=CoderGUI.padding)
        self.decode_area.insert(tk.END, 'Output area')

        # Drop-down list
        self.options = ('Caesar', 'Vigenere', 'Vernam', 'Base64', 'Steganography')
        self.select_coding = tk.StringVar(self.root)
        self.select_coding.set(self.options[0])
        self.dropdown = ttk.Combobox(self.root, textvariable=self.select_coding, values=self.options)
        self.dropdown.pack(side=tk.TOP, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # Switcher between encrypt and decrypt mode
        self.select_mode = tk.StringVar(self.root)
        self.select_mode.set('Encrypt')
        self.switcher = ttk.Combobox(self.root, textvariable=self.select_mode, values=['Encrypt', 'Decrypt'])
        self.switcher.pack(side=tk.TOP, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # 'Let's go!' button
        self.go_button = tk.Button(self.root, text="Let's go!", command=self.execute)
        self.go_button.pack(side=tk.TOP, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # Create key text area
        self.key_label = tk.Label(self.root, text='Enter key:')
        self.key_text = tk.Text(self.root, font=('Helvetica', CoderGUI.font_sz), width=15, height=1)
        self.key_text.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
        self.key_label.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # Wanna load the file
        self.load_file_button = tk.Button(self.root, text='Load file', command=self.load_file)
        self.load_file_button.pack(side=tk.TOP, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # Wanna save the keys for steganography
        self.save_keys_button = tk.Button(self.root, text='Save keys', command=self.save_keys)
        self.save_keys_button.pack_forget()

        # Wanna save en-/decoded text to file
        self.save_file_button = tk.Button(self.root, text='Save file', command=self.save_file)
        self.save_file_button.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)

        # Wanna save encoded image
        self.save_img_button = tk.Button(self.root, text='Save image', command=self.save_image)
        self.save_img_button.pack_forget()

    @staticmethod
    def encrypt(mode, input_text, key=''):
        match mode:
            case 'Caesar':
                if not re.fullmatch('^\d+$', key):
                    return 'Please enter right key for encryption'
                return Encrypt.caesar(input_text, int(key))
            case 'Vigenere':
                return Encrypt.vigenere(input_text, key)
            case 'Vernam':
                return Encrypt.vernam(input_text, key)
            case 'Base64':
                return Encrypt.base64(input_text)
            case 'Steganography':
                image_path = filedialog.askopenfilename()
                if re.match('.+(png|jpg|jpeg|bmp)\s*$', image_path):
                    Encrypt.stega(input_text, image_path)  # self.root.clipboard_get()
                    return "Your text was encrypted. You can download the '.png' encrypted image and " \
                           "file with keys to decrypt it."
                else:
                    return 'Please choose image with .png, .jpg, .jpeg or .bmp format'

    def decrypt(self, mode, cypher_text, key):
        match mode:
            case 'Caesar':
                return Decrypt.caesar(cypher_text)
            case 'Vigenere':
                return Decrypt.vigenere(cypher_text, key)
            case 'Vernam':
                return Decrypt.vernam(cypher_text, key)
            case 'Base64':
                return Decrypt.base64(cypher_text)
            case 'Steganography':
                image_path = filedialog.askopenfilename()
                if image_path.endswith('.png'):
                    return Decrypt.stega(self.loaded_file, image_path)
                else:
                    return 'Please select encoded image (it is in .png format)'

    def execute(self):
        # Get the selected option and switcher value
        selected_option = self.select_coding.get()
        selected_mode = self.select_mode.get()

        # Get the text from the left text area
        input_text = self.encode_area.get('1.0', tk.END).strip()
        key = self.key_text.get('1.0', tk.END).strip()

        if not key and (selected_option in ('Vigenere', 'Vernam')
                        or (selected_option == 'Caesar' and selected_mode == 'Encrypt')):
            self.decode_area.delete('1.0', tk.END)
            self.decode_area.insert(tk.END, 'Enter appropriate key before proceeding')
            return

        output_text = CoderGUI.encrypt(selected_option, input_text, key) if selected_mode == 'Encrypt' else \
            self.decrypt(selected_option, input_text, key)

        # Set the output text to the right text area
        self.decode_area.delete('1.0', tk.END)
        self.decode_area.insert(tk.END, output_text)

    def run(self):
        self.select_coding.trace_add('write', lambda *_: self.show_elements())
        self.select_mode.trace_add('write', lambda *_: self.show_elements())
        self.root.mainloop()

    def show_elements(self):
        # Show the key label and text area if the selected option requires a key
        coding = self.select_coding.get()
        mode = self.select_mode.get()

        self.save_keys_button.pack_forget()
        self.save_file_button.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
        self.load_file_button.pack(side=tk.TOP, padx=CoderGUI.padding, pady=CoderGUI.padding)

        self.load_file_button.config(text='Load file')

        if coding in ('Vigenere', 'Vernam') or (coding == 'Caesar' and mode == 'Encrypt'):
            # do need text area for key
            self.show_key_area()
        else:
            # do not need that area
            self.delete_key_area()
            if coding == 'Steganography':
                self.configure_stega(mode)

    def show_key_area(self):
        self.save_file_button.pack_forget()
        self.key_text.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
        self.key_label.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
        self.save_file_button.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
        self.save_img_button.pack_forget()

    def delete_key_area(self):
        self.key_label.pack_forget()
        self.key_text.pack_forget()
        self.save_img_button.pack_forget()

    def configure_stega(self, mode):
        if mode == 'Encrypt':
            self.save_file_button.pack_forget()
            self.save_keys_button.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
            self.save_img_button.pack(side=tk.BOTTOM, padx=CoderGUI.padding, pady=CoderGUI.padding)
        else:
            self.load_file_button.config(text='Load keys')

    def load_file(self):
        filename = filedialog.askopenfilename()
        if filename and re.fullmatch('.+\.(txt|keys)', filename):
            with open(filename, 'r') as f:
                file_contents = f.read()
                self.encode_area.delete('1.0', tk.END)
                self.encode_area.insert(tk.END, file_contents)
            self.loaded_file = filename
        else:
            self.decode_area.delete('1.0', tk.END)
            self.decode_area.insert('1.0', 'Please choose file in .txt or .keys format')

    def load_image(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(filedialog.askopenfilename())
        self.decode_area.delete('1.0', tk.END)
        self.decode_area.insert(tk.END, "Your image was loaded")

    def save_file(self):
        filename = filedialog.asksaveasfilename(defaultextension='.txt',
                                                filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.decode_area.get('1.0', tk.END))

    @staticmethod
    def save_keys():
        filename = filedialog.asksaveasfilename(defaultextension='.keys', filetypes=[('All files', '*.*')])
        if filename:
            shutil.copyfile('coords.keys', filename)

    @staticmethod
    def save_image():
        filename = filedialog.asksaveasfilename(defaultextension='.png',
                                                filetypes=[('Image files', '*.png'), ('All files', '*.*')])
        if filename:
            shutil.copyfile('encoded.png', filename)

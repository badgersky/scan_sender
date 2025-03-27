import os
import pathlib as pl
import smtplib
from email.message import EmailMessage
from string import ascii_letters, digits, punctuation

from PyPDF2 import PdfWriter
from pdf2image import convert_from_path
import pytesseract as pt

from settings import *


class Sender:

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def get_file_list(self):
        files = os.listdir(self.dir_path)
        files.sort(key = lambda x: os.path.getctime(os.path.join(self.dir_path, x)))
        return [os.path.join(self.dir_path, f) for f in files if f.endswith('.pdf')]

    def merge_files(self):
        files = self.get_file_list()
        merger = PdfWriter()
        filename = "protocol.pdf"

        for i, f in enumerate(files):
            if i == 0:
                pages = convert_from_path(f, 600, poppler_path=poppler)
                new_filename = self.get_title(pages)
                if new_filename:
                    filename = new_filename
            with open(f, "rb") as page:
                merger.append(page)
            os.remove(f)

        with open(os.path.join(self.dir_path, filename), "wb") as output:
            merger.write(output)

        return os.path.join(self.dir_path, filename)

    def send_file(self):
        file = self.merge_files()
        path = pathlib.PurePath(file)
        msg = EmailMessage()

        msg['to'] = receiver
        msg['from'] = sender
        msg['subject'] = path.name

        with open(path, "rb") as pdf:
            pdf_data = pdf.read()
        msg.add_attachment(pdf_data, maintype="document", subtype="pdf", filename=path.name)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, passwd)

        server.send_message(msg)
        server.quit()
        os.remove(file)

    @staticmethod
    def get_title(pages):
        text = ""
        filename = ""
        chars = ascii_letters + digits + punctuation + " "
        pt.pytesseract.tesseract_cmd = tesseract

        for page in pages:
            text += pt.image_to_string(page)

        text = text.split("\n")
        for line in text:
            if "protokol" in line.lower():
                for char in line:
                    if char not in chars:
                        line = line.replace(char, "")
                line = line.strip()
                filename = line.replace(" ", "_")
                filename = filename.replace("/", "-")

        return filename + ".pdf"


if __name__ == '__main__':
    p = pl.Path(os.getcwd())
    path = os.path.join(p.home(), 'Pictures', 'Scans')
    s = Sender(path)
    s.send_file()
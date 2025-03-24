import os
import pathlib as pl
import smtplib
from email.message import EmailMessage

from PyPDF2 import PdfWriter
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
        for f in files:
            with open(f, "rb") as page:
                merger.append(page)
            os.remove(f)

        with open(os.path.join(self.dir_path, "protocol.pdf"), "wb") as output:
            merger.write(output)

        return os.path.join(self.dir_path, "protocol.pdf")

    def send_file(self):
        file = self.merge_files()
        msg = EmailMessage()

        msg['to'] = sender
        msg['from'] = sender
        msg['subject'] = 'protocol'

        with open(file, "rb") as pdf:
            pdf_data = pdf.read()
        msg.add_attachment(pdf_data, maintype="document", subtype="pdf", filename="protocol.pdf")

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, passwd)

        server.send_message(msg)
        server.quit()


if __name__ == '__main__':
    p = pl.Path(os.getcwd())
    path = os.path.join(p.home(), 'Pictures', 'Scans')
    s = Sender(path)
    s.send_file()
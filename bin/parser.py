#!/usr/bin/env python3
#
# Copyright 2019 Juan Carizza
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Extraer titulo y cuerpo de los archivos HTML de cada email."""

import os
import sys
import io
import glob
import json
import argparse
from html.parser import HTMLParser


class MailParser(HTMLParser):   # pylint: disable=W0223
    """Buscar h1 y pre"""
    is_content = False
    is_title = False
    title = ''
    content = ''
    temp = io.StringIO()

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'pre':
            self.is_content = True
        if tag.lower() == 'h1':
            self.is_title = True

    def handle_data(self, data):
        """Escribir a buffer temporal la data del tag"""

        if self.is_content or self.is_title:
            self.temp.write(data)

    def clear_buffer(self):
        """Limpia el buffer temporal"""
        self.temp.seek(0)
        self.temp.truncate(0)

    def handle_endtag(self, tag):
        """Guarda el texto de h1 y pre"""

        value = self.temp.getvalue().strip()
        if tag.lower() == 'h1' and value.startswith('[pyar]'):
            self.title = value
            self.is_title = False  # Termino con el title
            self.clear_buffer()
        if tag.lower() == 'pre':
            self.content = '\n'.join(
                filter(
                    lambda x: not x.strip().startswith('>'),
                    self.temp.getvalue().split('\n')
                )
            )
            self.is_content = False  # Termino con el tag pre
            self.clear_buffer()

    def get_content(self):
        """Retorna el contenido final parseado"""

        return self.title, self.content

    def reset(self):
        """Resetear todas las variables"""

        super(MailParser, self).reset()
        self.temp.seek(0)
        self.temp.truncate(0)
        self.title = ''
        self.content = ''


epilog = """
Usar este script para extraer titulo y cuerpo de cada mail que fueron
descargados con el script `scrapper.py`

Ejemplo de uso:
parser.py --input-dir=./months/ --output-dir="./output-mails"
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='PROG', epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input-dir',
                        action='store',
                        required=True,
                        help=('Path to scraped emails\n'))
    parser.add_argument('--output-dir',
                        action='store',
                        required=True,
                        help=('Path to store procesed mails\n'))
    parser.add_argument('-e', '--encoding',
                        action='store',
                        default='iso-8859-1',
                        help=('Encoding used by file\n'))

    args = parser.parse_args()
    mails_folder = args.input_dir
    output_dir = args.output_dir
    encoding = args.encoding

    try:
        os.makedirs(output_dir)
    except FileExistsError:
        pass

    mail_parser = MailParser()
    files = glob.glob('{}/*.html'.format(mails_folder))
    total = len(files)
    parsed = 0
    for file in files:
        sys.stdout.write('{}/{}\r'.format(parsed, total))
        with open(file, 'r', encoding=encoding) as f:
            mail_parser.feed(f.read())
        parsed += 1
        title, body = mail_parser.get_content()
        mail_parser.reset()
        name, extension = os.path.basename(file).split('.')
        output_file = os.path.join(output_dir, '%s.json' % name)

        with open(output_file, 'w') as f:
            json.dump({
                'title': title,
                'body': body
            }, f)

    sys.stdout.write('Finish...')

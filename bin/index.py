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

"""Create Whoosh index from parsed mails"""


import os
import json
import sys
import argparse
import glob
from whoosh import index
from whoosh.fields import (
    TEXT,
    Schema
)

epilog = """
Usar este script para indexar los correos procesados por el script `parser.py`

Example of use:
index.py --mails='./data/mails' --ram 512 --procs 4
--out-index='./data/indexdir'

"""


def get_url(file):
    name, _ = os.path.basename(file).split('.')
    return '{}-{}/{}.html'.format(*name.split('-'))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='PROG', epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input-mails', action='store',
                        help=('Path to procesed mails\n'),
                        required=True)
    parser.add_argument('--ram', action='store',
                        type=int,
                        default=128,
                        help=('RAM limit in MB for each index process.\n'))
    parser.add_argument('--procs', action='store',
                        type=int,
                        default=1,
                        help=('Number of process that index writer can start.\n'))
    parser.add_argument('--out-index', action='store',
                        help=('Output path for the index.\n'),
                        required=True)
    args = parser.parse_args()

    try:
        os.makedirs(args.out_index)
    except FileExistsError:
        pass

    schema = Schema(title=TEXT(stored=True),
                    path=TEXT,
                    content=TEXT(stored=True), url=TEXT(stored=True))
    ix = index.create_in(args.out_index, schema)
    writer = ix.writer(procs=args.procs,
                       limitmb=args.ram,
                       multisegment=True)

    files = glob.glob('{}/*.json'.format(args.input_mails))
    total = len(files)
    count = 0
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            writer.add_document(title=data['title'],
                                path=file,
                                content=data['body'],
                                url=get_url(file))
        count += 1
        sys.stdout.write('{}/{}\r'.format(count, total))
    writer.commit()

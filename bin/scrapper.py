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

"""Download html email files from https://listas.python.org.ar/pipermail/pyar/"""

import tempfile
import os
import glob
import queue
import threading
import shutil
import argparse
import logging
import urllib.request
from html.parser import HTMLParser

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

URL_TEMPLATE = "https://listas.python.org.ar/pipermail/pyar/{year}-{month}/date.html"
URL_THREAD_TEMPLATE = "https://listas.python.org.ar/pipermail/pyar/{year}-{month}/{mail}"

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


def check_folders():
    try:
        os.makedirs(OUTPUT_FOLDER)
    except FileExistsError:
        pass
    try:
        os.makedirs(args.output_dir)
    except FileExistsError:
        pass


def download_month_archives(year):

    # Descarga secuencial
    for month in ["March"]:
        params = {
            "year": year,
            "month": month
        }

        # Agregar a cola de descarga de meses
        queue_months.put(params)


def scrap_emails():
    """Scrapea todos los mails del año/mes"""

    folder = "{0}/*.html".format(OUTPUT_FOLDER)

    for file in glob.glob(folder):
        year, month = os.path.splitext(os.path.basename(file))[0].split("-")
        parser = MonthParser(year, month)
        logger.debug("Parseando archivo %s", file)
        data = open(file, "r", encoding="iso-8859-1").read()

        parser.feed(data)
        for email in parser.get_emails():
            # Agregar a la cola de descarga
            logger.debug("Encolando archivo %r", email)
            queue_emails.put(email)
        parser.reset()


def worker_scrap_email():
    while True:
        email = queue_emails.get()

        if email is None:
            break

        try:
            url = email["url"]
            name = os.path.join(args.output_dir, email["name"])
            if os.path.exists(name):
                logger.debug("Skipping  %s", url)

            logger.debug("Downloading %s", url)
            with urllib.request.urlopen(url) as response:
                with open(name, "wb") as out_file:
                    shutil.copyfileobj(response, out_file)
        except Exception as e:
            logger.debug("Error %s al descargar %s", e, url)
        finally:
            queue_emails.task_done()


def worker_month_archives():
    while True:
        params = queue_months.get()

        if params is None:
            logger.debug('Nothing more to download...')
            break

        try:
            file_path = os.path.join(OUTPUT_FOLDER, "{year}-{month}.html".format(**params))

            # Si existe el archivo descargado ignorarlo
            if os.path.exists(file_path):
                logger.debug("Skiping %s-%s", params["year"], params["month"])

            url = URL_TEMPLATE.format(**params)
            logger.debug("Downloading %s", url)
            with urllib.request.urlopen(url) as response:
                with open(file_path, "wb") as out_file:
                    shutil.copyfileobj(response, out_file)

        except Exception as error:
            logger.debug(" %s %s", error, url)
        finally:
            queue_months.task_done()


class MonthParser(HTMLParser):
    is_link = None
    href = None
    mails = []

    def __init__(self, year, month):
        super(MonthParser, self).__init__()
        self.year = year
        self.month = month

    def is_link_tag(self, tag):
        return tag.lower() == "a"

    def handle_starttag(self, tag, attrs):
        if self.is_link_tag(tag):
            try:
                self.href = list(filter(lambda x: x[0] == "href", attrs))[0][1]
                self.is_link = True
            except IndexError:
                pass

    def handle_data(self, data):
        if self.is_link and data.startswith("[pyar]") and self.href is not None:
            self.mails.append({
                "url": URL_THREAD_TEMPLATE.format(
                    year=self.year,
                    month=self.month,
                    mail=self.href
                ),
                "name": "{}-{}-{}".format(
                    self.year,
                    self.month,
                    self.href
                )
            })

        self.is_link = None
        self.href = None

    def reset(self, *args, **kwargs):
        super(MonthParser, self).reset(*args, **kwargs)
        self.mails = list()

    def get_emails(self):
        return self.mails


YEARS = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
OUTPUT_FOLDER = ""

epilog = """
Script para descargar todos los mails de todos los meses de la lista de PyAr

Example of use:
scrapper.py --output-dir='./data/months' -t 5

"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='PROG', epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output-dir', action='store',
                        help=('Path store output mails\n'),
                        required=True)
    parser.add_argument('-t', '--threads', action='store',
                        type=int,
                        help='How many threads to start.\n')
    parser.add_argument('--debug', action='store_true',
                        help=('Show debug info\n'),
                        required=True)
    parser.add_argument('--years', nargs="+",
                        help=('Run scrapper on given years\n'))
    parser.add_argument('--months', nargs="+",
                        help=('Run scrapper on given months\n'))

    args = parser.parse_args()

    if args.months:
        for month in args.months:
            assert month in MONTHS, 'Misspelled month?'

        MONTHS = list(map(str.strip, args.months))

    if args.years:
        YEARS = list(map(str.strip, args.years))

    OUTPUT_FOLDER = tempfile.mkdtemp(dir=".")
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    check_folders()

    queue_months = queue.Queue()
    queue_emails = queue.Queue()
    threads = []
    num_of_threads = args.threads or 2

    # Threads para los meses
    for i in range(num_of_threads):
        t = threading.Thread(target=worker_month_archives)
        t.start()
        threads.append(t)

    # Threads para mails
    for i in range(num_of_threads):
        t = threading.Thread(target=worker_scrap_email)
        t.start()
        threads.append(t)

    # Empezar a encolar archivos de meses
    for year in ["2018"]:
        download_month_archives(year)

    # Bloquear hasta que se termine la descarga de todos los meses
    queue_months.join()

    # Empezar a encolar mails cuando termina de scrappear los meses
    scrap_emails()

    # Bloquear hasta que se termine la descarga detodos los mails
    queue_emails.join()

    for i in range(num_of_threads):
        queue_months.put(None)
        queue_emails.put(None)

    for t in threads:
        t.join()

    shutil.rmtree(OUTPUT_FOLDER)

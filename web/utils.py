"""
Utilidades
"""


class Paginator():

    def __init__(self, results):
        self.results = results

    def has_next(self):
        return self.results.pagenum < self.results.pagecount

    def has_previous(self):
        return not self.results.pagenum == 1

    def pages(self):
        return range(1, self.results.pagecount + 1)

    def next(self):
        return self.results.pagenum + 1

    def previous(self):
        return self.results.pagenum - 1

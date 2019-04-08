import os
from whoosh import qparser
from whoosh.index import open_dir
from whoosh.query import Term
from whoosh.highlight import HtmlFormatter

RESULT_LIMITS = int(os.environ.get("RESULT_LIMITS"))
RESULT_SURROUND = int(os.environ.get("RESULT_SURROUND"))
INDEX_DIR = os.environ.get("INDEX_DIR")


class Searcher():
    def __init__(self,
                 index=None,
                 search_fields=["title", "content"],
                 html_formatter=None,
                 parser=None,
                 termclass=Term):
        """Clase para buscar por distintos fields

        :param: index
        :type: whoosh.index.Index - Instancia del objeto Index

        :param: search_fields - Lista de los campos donde se busca
        :type: list

        :param: html_formatter - Instancia que formatea los hits
        :type: whoosh.highlight.HtmlFormatter
        """

        self.index = index or open_dir(INDEX_DIR)
        self.html_formatter = html_formatter or HtmlFormatter(
            between="...",
            tagname="strong",
            classname="search-match",
            termclass="search-term"
        )

        self.search_fields = search_fields
        self.termclass = termclass

        self.parser = parser or qparser.MultifieldParser(
            self.search_fields, self.index.schema, termclass=termclass
        )

    def search(self, phrase):
        """Ejecuta la busqueda y retorna una lista de hits"""

        query = self.parser.parse(phrase)
        s = self.index.searcher()
        result = s.search(query, limit=RESULT_LIMITS)
        result.fragmenter.surround = RESULT_SURROUND
        result.formatter = self.html_formatter
        return result

    def search_page(self, phrase, page):
        """Ejecuta la busqueda y retorna una pagina de la busqueda"""

        query = self.parser.parse(phrase)
        s = self.index.searcher()
        result = s.search_page(query, page, RESULT_LIMITS)
        result.results.fragmenter.surround = RESULT_SURROUND
        result.results.formatter = self.html_formatter
        return result

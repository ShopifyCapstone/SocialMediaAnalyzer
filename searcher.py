from whoosh.analysis import Filter
from whoosh import index as Index
from whoosh import writing
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter, StemFilter
from whoosh import qparser
from whoosh.qparser import QueryParser, GtLtPlugin, PhrasePlugin, SequencePlugin
from whoosh import scoring
import os, os.path  # os - portable way of using operating system dependent functionality
import shutil  # High-level file operations
import pandas
import nltk


class CustomFilter(Filter):
    # This filter will run for both the index and the query
    is_morph = True
    def __init__(self, filterFunc, *args, **kwargs):
        self.customFilter = filterFunc
        self.args = args
        self.kwargs = kwargs
    def __eq__(self):
        return (other
                and self.__class__ is other.__class__)
    def __call__(self, tokens):
        for t in tokens:
            if t.mode == 'query': # if called by query parser
                t.text = self.customFilter(t.text, *self.args, **self.kwargs)
                yield t
            else: # == 'index' if called by indexer
                t.text = self.customFilter(t.text, *self.args, **self.kwargs)
                yield t


class WhooshInterfacer:

    def __init__(self, path="index/"):
        self.path=path

    def set_schema(self):
        customWordFilter = RegexTokenizer() | \
                           LowercaseFilter() | \
                           CustomFilter(nltk.stem.porter.PorterStemmer().stem) | \
                           CustomFilter(nltk.WordNetLemmatizer().lemmatize)

        return Schema(comment_ID=ID(stored=True),
                      comment_Subreddit=ID(stored=True),
                      comment_Content=TEXT(analyzer=customWordFilter),
                      comment_Content_raw=STORED,
                      )

    def create_index(self):
        schema = self.set_schema()

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.ix = Index.create_in(self.path, schema)

    def fill_index(self, df):
        with writing.BufferedWriter(self.ix, period=20, limit=1000) as writer :
            for row in df.iterrows():
                index, data = row
                writer.add_document(comment_ID=data['name'],
                                    comment_Subreddit=data['subreddit'],
                                    comment_Content=data['body'],
                                    comment_Content_raw=data['body'],
                                    )

    def open_index(self):
        self.ix = open_dir(self.path)

    def search_keywords(self, terms):
        userQuery = terms
        qp = QueryParser("comment_Content", schema=self.ix.schema)

        # Once you have a QueryParser object, you can call parse() on it to parse a query string into a query object:
        # default query lang:
        # If the user doesn’t explicitly specify AND or OR clauses:
        # by default, the parser treats the words as if they were connected by AND,
        # meaning all the terms must be present for a document to match
        # we will change this
        # to phrase search "<query>" - use quotes

        qp.add_plugin(qparser.GtLtPlugin)
        # qp.remove_plugin_class(qparser.PhrasePlugin)
        qp.add_plugin(qparser.PhrasePlugin)
        query = qp.parse(userQuery)
        print("##Query: ")
        print(query)


        resultsDF = pandas.DataFrame()
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            queryResults = searcher.search(query, limit=None)
            print("Total Number of Results:", len(queryResults))
            print("Number of scored and sorted docs in this Results object:", queryResults.scored_length())
            results = [item.fields() for item in queryResults]

        resultsDF = pandas.DataFrame.from_dict(results)
        resultsDF = resultsDF.rename(columns={'comment_ID': 'name', 
                                              'comment_Subreddit': 'subreddit',
                                              'comment_Content_raw': 'body',
                                              })
        return resultsDF


def search(df, userQuery):
    """kept here for compatibility but this function will have to be removed."""
    searcher = WhooshInterfacer("index_test")
    searcher.create_index()
    searcher.fill_index(df)
    return searcher.search_keywords(userQuery)


if __name__ == "__main__":
    import pandas
    masterDF = pandas.read_pickle('commentDF.pkl')
    searcher = WhooshInterfacer("index_test")
    searcher.create_index()
    searcher.fill_index(masterDF.head(1000))
    resultsDF = searcher.search_keywords(terms='capital')

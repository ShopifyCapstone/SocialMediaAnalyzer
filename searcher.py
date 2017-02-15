from whoosh.analysis import Filter
from whoosh import index as Index
from whoosh.index import open_dir
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


class Whoosher:

    def __init__(self, path="index/"):
        self.path=path

    def set_schema(self, df_schema):
        """ Whoosh schema = all df_schema fields, stored but not indexed, 
            + extra field 'body_processed', processed, indexed."""
        customWordFilter = RegexTokenizer() | \
                           LowercaseFilter() | \
                           CustomFilter(nltk.stem.porter.PorterStemmer().stem) | \
                           CustomFilter(nltk.WordNetLemmatizer().lemmatize)

        whoosh_schema = {item:STORED for item in df_schema}
        whoosh_schema.update({'body_processed':TEXT(analyzer=customWordFilter)})
        print('Whoosh_schema', whoosh_schema)
        return Schema(**whoosh_schema)

    def create_index(self, df_schema):
        schema = self.set_schema(df_schema)

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.ix = Index.create_in(self.path, schema)

    def fill_index(self, df):
        ii = 0
        with writing.BufferedWriter(self.ix, period=20, limit=1000) as writer :
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                row_dict.update({'body_processed':row['body']})
                try:
                    writer.add_document(**row_dict)
                except:
                    print("Couldn't index document in Whoosh",index, len(row['body']), row['body'])
                    ii += 1

        print('{} documents could not be indexed out of {}. Not an issue if small %.'.format(ii, len(df)))

    def open_index(self):
        try:
            self.ix = open_dir(self.path)
            return True
        except:
            print("No whoosh data in {}".format(self.path))
            return False

    def search_keywords(self, user_query, ranking_function=scoring.BM25F()):

        qp = QueryParser("body_processed", schema=self.ix.schema)

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
        query = qp.parse(user_query)
        print("# user_query", user_query, ", Query: ", query)
        print(query)

        with self.ix.searcher(weighting=ranking_function) as searcher:
            matches = searcher.search(query, limit=None)
            print("Total Number of Results:", len(matches))
            print("Number of scored and sorted docs in this Results object:", matches.scored_length())
            results = [item.fields() for item in matches]

        resultsDF = pandas.DataFrame.from_dict(results)
        return resultsDF


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


if __name__ == "__main__":
    # build index from scratch ('commentDF.pkl') and search
    import pandas
    masterDF = pandas.read_pickle('commentDF.pkl')
    whoosher = Whoosher("index_test")
    whoosher.create_index(masterDF.columns)
    whoosher.fill_index(masterDF.head(1000))
    resultsDF = whoosher.search_keywords(user_query='capital')
    print('# resultsDF', resultsDF)

    # search existing index
    other_whoosher = Whoosher("index_test")
    other_whoosher.open_index()
    resultsDF = other_whoosher.search_keywords(user_query='capital')
    print('# resultsDF', resultsDF)

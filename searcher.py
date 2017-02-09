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


def search(df, userQuery):
    # Defining constants for the data paths ***** MODIFY ACCORDINGLY *****
    # INDEX_DIR = "C:/UofT/4th_year/Capstone/Python_directory/schema"
    INDEX_DIR = "/Users/aprevot/projects/UoT_Capstone/code/SocialMediaAnalyzer/index"
    # INDEX_DIR = "index/"

    # BUILD SCHEMA ****
    # schema has fields - piece of info for each doc in the index
    customWordFilter = RegexTokenizer() | LowercaseFilter() | CustomFilter(
        nltk.stem.porter.PorterStemmer().stem) | CustomFilter(nltk.WordNetLemmatizer().lemmatize)

    ixSchema = Schema(comment_ID=ID(stored=True),
                      comment_Subreddit=ID(stored=True),
                      # note analyzer is a wrapper for a tokenizer and zero or more filters -- i.e. allows you to combine them
                      comment_Content=TEXT(analyzer=customWordFilter))

    # BUILD INDEX ****


    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    # if index exists - remove it
    #     #Return True if path is an existing directory.
    #     if os.path.isdir(INDEX_DIR):
    #         #Delete an entire directory tree; path must point to a directory
    #         shutil.rmtree(INDEX_DIR)
    #     #create the directory for the index
    #     os.makedirs(INDEX_DIR)

    # initiate index - takes two inputs, the index directory and the schema for the index
    ix = Index.create_in(INDEX_DIR, ixSchema)

    # INDEX COMMENTS ****
    # creating a utility writer
    # params: index – the whoosh.index.Index to write to.
    # period – the maximum amount of time (in seconds) between commits.
    # limit – the maximum number of documents to buffer before committing/between commits.
    writer = writing.BufferedWriter(ix, period=20, limit=1000)
    try:
        # write each file to index
        # enumerate returns index,value index points too --> index,a[index]

        counter1 = 0
        for row in df.iterrows():
            index, data = row
            writer.add_document(comment_ID=data['name'],
                                comment_Subreddit=data['subreddit'],
                                comment_Content=data['body'])
            counter1 = counter1 + 1

            #             if (counter1 % 100 == 0):
            #                 print("already indexed:", counter1+1)

    finally:
        # save the index
        # print("done indexing")
        # *** Note *** -> Must explictly call close() on the writer object to release the write lock and makesure uncommited changes are saved
        writer.close()


        # PARSE USER QUERY ****

    # in the query parser --> we pass the DEFAULT field to search and the schema of the index we are searching
    # NOTE: Users can still specify a search on a different field in the schema via --> <fieldname>: <query>
    qp = QueryParser("comment_Content", schema=ix.schema)

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
    print("\n\n Query: ")
    print(query)
    print("\n\n")

    ##IMPLEMENT SEARCHER ****
    resultsDF = pandas.DataFrame()  # creates a new dataframe that's empty to store the results comment content
    with ix.searcher(weighting=scoring.BM25F()) as searcher:
        queryResults = searcher.search(query, limit=None)
        print("Total Number of Results:", len(queryResults))
        print("Number of scored and sorted docs in this Results object:", queryResults.scored_length())
        for result in queryResults:
            #             print(result)
            #             print("\n",result['comment_ID'])
            resultsDF = resultsDF.append(df.loc[df['name'] == result['comment_ID']][['name', 'subreddit', 'body']])

    # print(dataDf.loc[dataDf['body']==comment].index.values[0])

    return resultsDF
import nltk
from nltk.data import find
from nltk.tag import PerceptronTagger
from nltk.corpus import stopwords
import pandas
import numpy
import sklearn
from collections import Counter
import math
nltk.download('punkt')
nltk.download("wordnet")
nltk.download("brown")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")

class Extractor():
    ###Initialize things
    def __init__(self, whoosher):
        self.whoosher = whoosher
        self.masterDF = self.whoosher.masterDF

    def get_keyphrases(self, textInput, min_freq=2):

        # setting up tagger
        # (from http://stackoverflow.com/a/35964709)
        PICKLE = "averaged_perceptron_tagger.pickle"
        AP_MODEL_LOC = 'file:' + str(find('taggers/averaged_perceptron_tagger/' + PICKLE))
        tagger = PerceptronTagger(load=False)
        tagger.load(AP_MODEL_LOC)

        lemmatizer = nltk.WordNetLemmatizer()
        stemmer = nltk.stem.porter.PorterStemmer()

        # This grammar is described in the paper by S. N. Kim,
        # T. Baldwin, and M.-Y. Kan.
        # Evaluating n-gram based evaluation metrics for automatic
        # keyphrase extraction.
        # Technical report, University of Melbourne, Melbourne 2010.

        StopWords = stopwords.words('english')

        def leaves(tree):
            """Finds NP (nounphrase) leaf nodes of a chunk tree."""
            for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
                yield subtree.leaves()

        def acceptable_word(word):
            """Checks conditions for acceptable word: length, stopword."""
            accepted = bool(2 < len(word) and word.lower() not in StopWords)
            return accepted

        def normalise(word):
            """Normalises words to lowercase and stems and lemmatizes it."""
            word = word.lower()
            word = stemmer.stem(word)
            word = lemmatizer.lemmatize(word)
            return word

        def get_terms(tree):
            for leaf in leaves(tree):
                # can modify normalise to w.lower() if dont want to normalize word
                term = [normalise(w) for w, t in leaf if acceptable_word(w)]
                yield term

        def get_nounPhrases(textInput, minWordLength=2):

            grammar = r"""

            NBAR:
                {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

            NP:
                {<NBAR>}
                {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
                      """

            chunker = nltk.RegexpParser(grammar)

            toks = nltk.word_tokenize(textInput)
            # print(toks)
            pos_tag = tagger.tag
            postoks = pos_tag(toks)

            tree = chunker.parse(postoks)
            terms = get_terms(tree)

            nounPhraseList = []
            for tid, term in enumerate(terms):
                templist = []
                for wid, word in enumerate(term):
                    # print("TID: ",tid," WID: ",(wid+1), word)
                    templist.append(word)

                s = " "
                nounPhraseList.append(s.join(templist))

            nounPhraseList = [word for word in nounPhraseList if len(word.split()) >= minWordLength]
            return nounPhraseList

        counter = Counter()
        for nounPhrase in get_nounPhrases(textInput):
            # print(nounPhrase)
            counter.update([nounPhrase])

        keyphraseDF = pandas.DataFrame([[key, value] for key, value in counter.items() if value>=min_freq],
                                       columns=['keyphrase_stemmed', 'frequency'])
        (docsDF, occurrenceDF) = self.get_occurrence(keyphraseDF)
        print("docs", docsDF)
        print("keys", keyphraseDF)
        keyphraseDF = keyphraseDF.join(docsDF["docs"])
        print(occurrenceDF)
        keyphraseDF = keyphraseDF.join(self.get_MIs(occurrenceDF=occurrenceDF)["MI"])
        keyphraseDF = keyphraseDF.join(
            self.get_PMIs(occurrenceDF=occurrenceDF, metric="sentiment_class", value="positive")["PMI_pos"])
        keyphraseDF = keyphraseDF.join(
            self.get_PMIs(occurrenceDF=occurrenceDF, metric="sentiment_class", value="negative")["PMI_neg"])
        #keyphraseDF = keyphraseDF.join(self.get_PMIs(keyphraseDF["Keyphrase_stemmed"].tolist(), "neg"))

        return keyphraseDF

    def get_occurrence(self, keyphraseDF):

        keyphrases = keyphraseDF["keyphrase_stemmed"].tolist()
        no_keyphrases = len(keyphrases)

        occurrences = []
        for keyphrase in keyphrases:
            (docs, tempDF) = self.whoosher.search(user_query=keyphrase, phraseSearch=True)
            occurrences.append(docs)
        print("occurences: ", occurrences)

        docsDF = keyphraseDF.copy()
        docsDF.columns = ["keyphrase_stemmed", "docs"]
        docsDF["docs"] = docsDF["docs"].astype(object)
        for i in range(no_keyphrases):
            docsDF.set_value(i, 'docs', occurrences[i])

        occurrenceDF = pandas.DataFrame(numpy.zeros(shape=(len(self.masterDF), no_keyphrases), dtype=numpy.int8))
        occurrenceDF.columns = keyphrases

        for keyphrase_no in range(len(keyphrases)):
            for doc in occurrences[keyphrase_no]:
                occurrenceDF.loc[doc, keyphrases[keyphrase_no]] = 1

        return (docsDF, occurrenceDF.join(self.masterDF["sentiment_class"]))

    def get_MIs(self, occurrenceDF):

        vaderScores = []
        for i in range(len(self.masterDF)):
            if (self.masterDF['sentiment_class'][i]) == "positive":
                vaderScores.append(1)
            else:
                vaderScores.append(0)

        miScore = []
        for keyphrase in occurrenceDF.columns:
            miScore.append([keyphrase] + [sklearn.metrics.mutual_info_score(vaderScores, occurrenceDF[keyphrase].as_matrix())])
        miDF = pandas.DataFrame(miScore)
        miDF.columns = ['keyphrase_stemmed', 'MI']
        print(miDF)

        return miDF


    def get_PMIs(self, occurrenceDF, metric, value):

        length = len(occurrenceDF)
        px = sum(occurrenceDF[metric] == value) / length
        keyphrases = occurrenceDF.columns

        pmis = []

        for keyphrase in keyphrases:
            py = sum(occurrenceDF[keyphrase] == 1) / length
            pxy = len(occurrenceDF[(occurrenceDF[metric] == value) & (occurrenceDF[keyphrase] == 1)]) / length
            if pxy == 0:  # Log 0 cannot happen
                pmi = math.log10((pxy + 0.0001) / (px * py))
            else:
                pmi = math.log10(pxy / (px * py))
            pmis.append(pmi)

        pmiDF = pandas.DataFrame({'keyphrase_stemmed': keyphrases, 'PMI_'+value[:3]: pmis})

        return pmiDF
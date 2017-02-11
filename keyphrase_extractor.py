import nltk
from nltk.data import find
from nltk.tag import PerceptronTagger
from nltk.corpus import stopwords

import pandas

from collections import Counter

nltk.download('punkt')
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")
nltk.download("brown")
nltk.download("stopwords")


def get_keyphrases(textInput, k=15, version='Summary'):
    # version = Summary or version = PMI

    # setting up tagger
    # (from http://stackoverflow.com/a/35964709)
    PICKLE = "averaged_perceptron_tagger.pickle"
    AP_MODEL_LOC = 'file:' + str(find('taggers/averaged_perceptron_tagger/' + PICKLE))
    tagger = PerceptronTagger(load=False)
    tagger.load(AP_MODEL_LOC)
    pos_tag = tagger.tag

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
        lemmatizer = nltk.WordNetLemmatizer()
        stemmer = nltk.stem.porter.PorterStemmer()

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
    if version.lower() == 'summary':
        topkNPdf = pandas.DataFrame([[key, value] for key, value in counter.items()], columns=['Term', 'Frequency'])
        # topkNPdf = topkNPdf.reset_index(drop=True)

        # if less than max (15), use correct number of key phrases
        if topkNPdf.shape[0] < k:
            print("\n \nTop", topkNPdf.shape[0], "key phrases (minimum phrase length = 2 ): \n")
        else:
            print("\n \nTop", k, "key phrases (minimum phrase length = 2): \n")

        topkNPdf = topkNPdf.sort_values('Frequency', axis=0, ascending=False).head(k)
        topkNPdf = topkNPdf.reset_index(drop=True)
        return topkNPdf

    elif version.lower() == 'pmi':
        return counter.most_common(k);
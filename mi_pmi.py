
from keyphrase_extractor import  get_keyphrases

def concat_DfColumn(df,columnIndicator):
    import pandas
    tempSeries = df[columnIndicator]
    strcat = tempSeries.str.cat(sep=', ')
    return strcat




# # PMI Function



def cleanData(df,datatype='filtered'):
    
    if(datatype=='filtered'):
        return df
    elif(datatype=='unfiltered'):
        import re
        URL_REGEX_1 = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        SHOPIFY_REGEX = r"[S|s]hopify"
        HIRING_REGEX = r"[H|h]iring"
        POPULARCOMMENT_REGEX = r"\**Most Popular Comments\**"
        HISTORY_REGEX = r"[R|r]ecent [S|s]ubmission [H|h]istory "

        dfCopy = df.copy()
        dfCopy['bodyCopy'] =dfCopy['body']

        #list to store ids of comments to keep 
        commentKeep =[]

        for cid,comment in enumerate(dfCopy['bodyCopy']):
            #print(cid)
            #print(dfCopy.loc[dfCopy['body']==comment].index.values[0])
            if (len(re.findall(URL_REGEX_1,comment))>0):
                dfCopy['bodyCopy'][cid] = re.sub(URL_REGEX_1,'WEBSITE_FILLER',comment)
                #print(dfCopy['bodyCopy'][cid])

        # 2nd loop to check if post meets requirements after subbing in URL FILLER    
        for cid,comment in enumerate(dfCopy['bodyCopy']):    
            #only keep comments with links if they mention shopify w/o it occuring in link    
            if (len(re.findall(SHOPIFY_REGEX,comment))>0):
                    #remove any post with 'Hiring' or 'Recent Submission History'
                    if(len(re.findall(HIRING_REGEX,comment))==0 and  len(re.findall(HISTORY_REGEX,comment))==0 and len(re.findall(POPULARCOMMENT_REGEX,comment))==0):
                        commentKeep.append(cid)


        print("****Done****")
        dfClean=df.loc[commentKeep]


        return dfClean


# In[4]:

def buildCommentByKPdf(df, k = 100):
   
    import pandas
    import numpy as np
    import math
    import nltk
    from nltk.sentiment import SentimentAnalyzer
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    #from nltk.sentiment.util import *
    from nltk import tokenize
    from nltk.corpus import stopwords

    df = cleanData(df,datatype = 'filtered')
    
    def commentPolarity(df):
        commentContent = df['body'].as_matrix()
        #Instantiation
        sid = SentimentIntensityAnalyzer()
        pdlist = []
        ##Assign Vader score to individual review using Vader compound score
        ##creating a list of the reviews along with their polarity score as assigned by Vader
        ##list containing a list where each element is [review,polarity]
        for rownum, comment in enumerate(commentContent):
            ss = sid.polarity_scores(comment)
            pdlist.append([comment,ss['compound']])
#             if (rownum % 100 == 1):
#                     print("processed %d reviews" % (rownum+1))
#         print("****Done****")
        commentDf = pandas.DataFrame(pdlist)
        commentDf.columns = ['commentCol','vader']
#         commentDf.head()
        return commentDf
        
    def commentTermDF(df):
        
        top_k =  get_keyphrases(concat_DfColumn(df,'commentCol'), k, version = 'pmi')
        #print(top_k)
        freqReview = []
        #create a list, one entry for each review; the entry is binary list indicating whether this review as the term i or not in the top k
        for i in range(len(df)):
            commentKP = get_keyphrases(df['commentCol'][i], k, version = 'pmi')
        #     print('commentKP: ' , commentKP)
            keyPhraseDict = {commentKP[i][0]: commentKP[i][1] for i in range(0, len(commentKP))}
        #     print('\n keyPhraseDict',keyPhraseDict)
            topkinComment = [1 if  keyPhraseDict.get(word, 0) > 0 else 0 for (word,wordCount) in top_k]
        #     print('\n topkinComment',topkinComment)
            freqReview.append(topkinComment)
        freqReviewDf = pandas.DataFrame(freqReview)
        #print(freqReviewDf.head(2))

        dfName = []
        for c in top_k:
            dfName.append(c[0])
            #print(c)
        freqReviewDf.columns = dfName
#         freqReviewDf.head()
        return top_k,freqReviewDf
    
    
    df1 = commentPolarity(df)
    top_k, df2 = commentTermDF(df1)
    finalcommentDf = df1.join(df2)
    df_reindexed = df.reset_index(drop=True)
    finaldf = df_reindexed.join(finalcommentDf)
    return top_k,finaldf


# In[5]:

# Calcualte MI scores
def miCalc(df, topK, scoreMetric = 'vader'):
    import sklearn
    import sklearn.metrics as metrics
   
    gtScore = []
    threshold = 0
    
    # Convet score metric to binary values
    for i in range(len(df)):
        if df[scoreMetric].as_matrix()[i]>threshold:
            gtScore.append(1)
        else:
            gtScore.append(0)            

    # Perform MI Analysis for each word
    miScore = []
    for word, wordCount in topK:
        miScore.append([word]+[metrics.mutual_info_score(gtScore, df[word].as_matrix())])
       
    
    miScoredf = pandas.DataFrame(miScore).sort_values(1,ascending=0)
    miScoredf = miScoredf.reset_index(drop = True)
    miScoredf.columns = ['Word','MI Score']
    return miScoredf


# In[6]:

# Calcualte a PMI score for word x using a scoring metric (PMI/MI are correlation measures)
# PMI(x,y) = 0 means that the particular values of x and y are statistically independent
# if >0 --> occurence of a term is an indicator for the particular class 
# if <0 --> opposite, term is an indicator for not being that particular class
def pmiCalc(df, x):
    vaderPosThreshold = 0
    vaderNegThreshold = 0
    try:
        pmilist=[]
        for i in ['positive','negative']:
            for j in [0,1]:
                
                # Initialize probability values
                px = 0 #probability of the term x
                py = 0 #probability of the class/category y
                pxy = 0 #probability of term x appearing in text classfied as y
                
                # Compute binary representation using VADER scores and thresholds for positive/negative sentiment
                if i =='positive':
                    py = sum(df['vader']>vaderPosThreshold)/len(df)
                    #probability of term x appearing in comments 
                    pxy = len(df[(df['vader']>vaderPosThreshold) & (df[x]==j)])/len(df)
                elif i =='negative':
                    py = sum(df['vader']<=vaderNegThreshold)/len(df)
                    pxy = len(df[(df['vader']<=vaderNegThreshold) & (df[x]==j)])/len(df)
                        
                px = sum(df[x]==j)/len(df)
                
                if pxy==0:#Log 0 cannot happen
                    pmi = math.log(((pxy+0.0001)/(px*py)),2.0)
                else:
                    pmi = math.log((pxy/(px*py)),2.0)
                pmilist.append([x]+[i]+[j]+[py]+[px]+[pxy]+[pmi])
        
        # Format and return results
        pmidf = pandas.DataFrame(pmilist)
        pmidf.columns = ['term', 'y - category','x - occurrence','py','px','pxy','pmi']
        return pmidf
    # Print error if term is not found
    except KeyError:
        print("Error: Term not found")


# In[ ]:




# In[32]:

# Perform PMI calculation for each word in top k
def pmiTopK(df, topK, usecase = 'PMI'):
    import pandas
    
    tempDF = pandas.DataFrame()
    
    for word,wordcount in topK:
        pmiDF = pmiCalc(finalDF,word)
        tempDF = pandas.concat([tempDF,pmiDF],ignore_index=True)
    
    
    if usecase.lower() == 'pmi':
        return tempDF
    
    elif usecase.lower() == 'mi':
        return


# In[8]:

for x in range(1,4,2):
    print(x)


# # Example

# In[9]:

#!pip --quiet install nltk
import nltk
nltk.download("vader_lexicon")
nltk.download("stopwords")

#for candidate key phrase code
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download("wordnet")
nltk.download("brown")

from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.stem import *
from nltk.tag import PerceptronTagger
from nltk.data import find
import pandas
import numpy as np
import math


import json
from collections import Counter


# In[10]:

#location of data
DATA_DIR = r'C:\Users\Jason\MIE490 - Capstone - Shopify\Data\Comments'


# In[11]:

# first we build a list of all the full paths of the files in DOCUMENTS_DIR
import os
file_in = []
# os.walk - 
#Generate the file names in a directory tree by walking the tree either top-down or bottom-up. For each directory
#in the tree rooted at directory top (including top itself), it yields a 3-tuple (dirpath, dirnames, filenames).
for root, dirs, files in os.walk(DATA_DIR):
    #print(root  + '\n')
    #print(files)
    #print(files +"\n")
    filePaths = [os.path.join(root, fileName) for fileName in files if not fileName.startswith('.')]
    #print(filePaths)
    file_in.extend(filePaths)
    #print(file_in)


# In[12]:

dataDf = pandas.DataFrame()
#following code courtesy of: https://www.reddit.com/r/MachineLearning/comments/33eglq/python_help_jsoncsv_pandas/
for file in file_in:
    with open(file, 'r') as f:
        data = f.readlines()

    # remove the trailing "\n" from each line
    data = map(lambda x: x.rstrip(), data)

    # each element of 'data' is an individual JSON object.
    # i want to convert it into an *array* of JSON objects
    # which, in and of itself, is one large JSON object
    # basically... add square brackets to the beginning
    # and end, and have all the individual business JSON objects
    # separated by a comma
    data_json_str = "[" + ','.join(data) + "]"
    # now, load it into pandas
    dataDf = dataDf.append(pandas.read_json(data_json_str),ignore_index=True)
    #print(dataDf.head())


# In[13]:

dataDf.head(n=2)


# In[14]:

dataDf.shape


# In[15]:

cleanDF = cleanData(dataDf,datatype='unfiltered')


# In[16]:

cleanDF.shape


# In[17]:

cleanDF.columns


# In[18]:

topK,finalDF = buildCommentByKPdf(cleanDF)


# In[19]:

temp2=  miCalc(finalDF, topK, scoreMetric = 'vader')


# In[ ]:




# In[20]:

temp2


# In[34]:

pmitopk = pmiTopK(finalDF,topK)


# In[35]:

pmitopk.head(2)


# In[36]:

pmitopk['weight'] = pmitopk.pxy*pmitopk.pmi


# In[37]:

pmitopk.head(2)


# In[39]:

grouped = pmitopk.groupby(by='term')


# In[51]:

pmitopk.groupby(['term'])[["weight"]].sum()




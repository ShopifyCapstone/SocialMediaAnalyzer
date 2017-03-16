import pandas
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle

def read_json_as_pandas(file_in):
    with open(file_in, 'rt') as f:
        data = f.readlines()
        data = map(lambda x: x.rstrip(), data)
        data_json_str = "[" + ','.join(data) + "]"
        dataDF = pandas.read_json(data_json_str)
    return dataDF

def add_sentiment(df):
    sid = SentimentIntensityAnalyzer()
    scores = []
    sentiments = []
    for index, row in df.iterrows():
        ss = sid.polarity_scores(row['body'])
        score = ss['compound']
        if score > 0:
            sentiments.append('positive')
        else:
            sentiments.append('negative')
        scores.append(score)
        if (index % 1000 == 1):
            print("processed %d comments" % (index+1))
    scores = pandas.Series(scores)
    sentiments = pandas.Series(sentiments)
    df['sentiment_score'] = scores
    df['sentiment_class'] = sentiments

def read_comments(pickle_name, dir='data/'):

    print('read_comments')
    files = os.listdir(dir)
    size = len(files)

    commentDF = read_json_as_pandas(dir+files[0])
    print(files[0])
    for i in range(1,size,1):
        file = files[i]
        print(file)
        tempDF = read_json_as_pandas(dir+file)
        commentDF = pandas.concat([commentDF, tempDF], ignore_index=True)

    add_t1 = lambda id: "t1_" + id
    commentDF["name"] = commentDF["id"].apply(add_t1)
    selected_columns = ['author','body','created_utc','link_id','name','parent_id','score','subreddit']
    commentDF = pandas.DataFrame(commentDF, columns=selected_columns)

    add_sentiment(commentDF)

    #return commentDF
    commentDF.to_pickle(pickle_name)

if __name__ == "__main__":
    read_comments(dir='data_old/', pickle_name='commentDF_old.pkl')
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

def read_comments(pickle_name, pickle=False, dir='Data/comments/'):

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

    if pickle==True:
        commentDF.to_pickle(pickle_name)

    return commentDF

def read_submissions(pickle_name, pickle=False, dir='Data/submissions/'):

    print('read_submissions')
    files = os.listdir(dir)
    size = len(files)

    submissionDF = read_json_as_pandas(dir+files[0])
    print(files[0])
    for i in range(1,size,1):
        file = files[i]
        print(file)
        tempDF = read_json_as_pandas(dir+file)
        submissionDF = pandas.concat([submissionDF, tempDF], ignore_index=True)

    add_t3 = lambda id: "t3_" + id
    submissionDF["name"] = submissionDF["id"].apply(add_t3)
    submissionDF["body"] = submissionDF["title"] +  "\n" + submissionDF["selftext"]
    submissionDF["link_id"] = submissionDF["name"]
    submissionDF["parent_id"] = "N/A"

    selected_columns = ['author','body','created_utc','link_id','name','parent_id','score','subreddit']
    submissionDF = pandas.DataFrame(submissionDF, columns=selected_columns)

    add_sentiment(submissionDF)

    if pickle==True:
        submissionDF.to_pickle(pickle_name)

    return submissionDF

if __name__ == "__main__":
    #read_comments(dir='Data/comments/', pickle=True, pickle_name='commentDF.pkl')
    read_submissions(dir='Data/submissions/', pickle=True, pickle_name='submissionDF.pkl')
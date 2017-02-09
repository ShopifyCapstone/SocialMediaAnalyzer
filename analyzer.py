from GUI import App
from data_handler import read_comments
import pandas

import pandas

# load comments df
masterDF = pandas.read_pickle('commentDF.pkl')
#masterDF = read_comments()
'''
masterDF = pandas.DataFrame(columns=['name','subreddit', 'body', 'link'],index=[0,1,2,3,4,5])
masterDF.loc[0] = pandas.Series({'body':"Awesome room service", 'name':'1', 'subreddit':'0.75', 'link':'http://google.com'})
masterDF.loc[1] = pandas.Series({'body':"Good view", 'name':'0.5', 'subreddit':'0.75', 'link':'http://google.com'})
masterDF.loc[2] = pandas.Series({'body':"Ok view", 'name':'0', 'subreddit':'0.5', 'link':'http://google.com'})
masterDF.loc[3] = pandas.Series({'body':"Bad room service", 'name':'-0.5', 'subreddit':'0', 'link':'http://google.com'})
masterDF.loc[4] = pandas.Series({'body':"Terrible prices", 'name':'-1', 'subreddit':'-0.75', 'link':'http://google.com'})
masterDF.loc[5] = pandas.Series({'body':"Disastrous prices", 'name':'-1', 'subreddit':'-1', 'link':'http://google.com'})
'''

# load submissions df

root = App(masterDF.head(1000))
root.title('Shopify Reddit Analyzer')
root.mainloop()
from GUI import App
from data_handler import read_comments
import pandas
import sys

from keyphrase_extractor import get_keyphrases
from searcher import search

# load comments df
masterDF = pandas.read_pickle('commentDF.pkl')
masterDF = masterDF.head(100)
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


if len(sys.argv)==1 :
	root = App(masterDF)
	root.title('Shopify Reddit Analyzer')
	root.mainloop()
elif len(sys.argv)==2:
	search_terms = sys.argv[1]
	search_results_df = search(masterDF, search_terms)
	print('## search_results_df',search_results_df)
	key_phrases_df = get_keyphrases(". ".join(search_results_df["body"].tolist()))
	print('## key_phrases_df',key_phrases_df)
else:
	raise("There shouldn't be more than 1 arg. Usage: python analyzer.py ['some terms']")


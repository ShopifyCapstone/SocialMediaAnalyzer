from GUI import App
from data_handler import read_comments
import pandas
import sys
from keyphrase_extractor import get_keyphrases
from searcher import Whoosher


# Point to Whoosh data or build it if required
masterDF = pandas.read_pickle('commentDF.pkl').head(1000) #for testing
whoosher = Whoosher(df=masterDF)
success = whoosher.open_index()
if success == False:
	whoosher.create_index(masterDF.columns)
	whoosher.fill_index(masterDF)

# Run app or command line mode.
if len(sys.argv)==1 :
	root = App(whoosher)
	root.title('Shopify Reddit Analyzer')
	root.mainloop()
elif len(sys.argv)==2:
	user_query = sys.argv[1]
	search_results_df = whoosher.search_keywords(user_query)
	print('# search_results_df', search_results_df)
	key_phrases_df = get_keyphrases(". ".join(search_results_df["body"].tolist()))
	print('# key_phrases_df',key_phrases_df)
else:
	raise("There shouldn't be more than 1 arg. Usage: python analyzer.py ['some terms']")
# TODO: get arg to force rebuild index


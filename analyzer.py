from GUI import App
from data_handler import read_comments
import pandas
import sys
from keyphrase_extractor import Extractor
from searcher import Whoosher


# Point to Whoosh data or build it if required
masterDF = pandas.read_pickle('commentDF.pkl').head(15000) #for testing
whoosher = Whoosher(path="index/")
success = whoosher.open_index()
if success == False:
	whoosher.create_index(masterDF.columns)
	whoosher.fill_index(masterDF)

extractor = Extractor(whoosher)

# Run app or command line mode.
if len(sys.argv)==1:
	root = App(whoosher, extractor)
	root.title('Shopify Reddit Analyzer')
	root.mainloop()
elif len(sys.argv)==2:
	user_query = sys.argv[1]
	search_results_df = whoosher.search(user_query)
	print('# search_results_df', search_results_df)
	key_phrases_df = extractor.get_keyphrases(". ".join(search_results_df["body"].tolist()))
	print('# key_phrases_df',key_phrases_df)
else:
	raise("There shouldn't be more than 1 arg. Usage: python analyzer.py ['some terms']")
# TODO: get arg to force rebuild index


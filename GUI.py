import tkinter
from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter.ttk import Combobox,Treeview,Scrollbar
import pandas


# TODO: clean up this entire class once the overall architecture is more or less finalized
class TableApp(Frame):
    def __init__(self, parent, masterDF, window, clicked_keyphrase="", columns=[], secondWindowDF=pandas.DataFrame({'body' : []}),
                 keyphraseDF=pandas.DataFrame({'keyphrase_stemmed' : []}), searchResults=set([])):
        Frame.__init__(self, parent)
        self.masterDF = masterDF
        if window=="second":
            self.loadTableWindow2(secondWindowDF, columns, clicked_keyphrase)
        elif window=="third":
            self.loadTableWindow3(keyphraseDF, columns, searchResults)
        else:
            self.loadTable(keyphraseDF, columns, searchResults)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def loadTableWindow3(self):
        #TODO: !!!
        print("empty")

    def loadTableWindow2(self, secondWindowDF, columns, clicked_keyphrase):
        # TODO: make reusable for various df's
        self.secondWindowDF = secondWindowDF
        tv = Treeview(self)
        #tv['columns'] = columns

        tv.heading("#0", text='#')
        tv.column("#0", anchor="w", width=600)

        #for column in tv['columns']:
        #    tv.heading(column, text=column)
        #    tv.column(column, anchor='center', width=350)

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for (i, row) in self.secondWindowDF.iterrows():
            #print(clicked_keyphrase)
            #print(row["body"])
            highlighted_text = highlight(keyphrase=clicked_keyphrase, text=row['body'], words=5)
            self.treeview.insert('', 'end', text=str(i) + " " + highlighted_text)

        self.treeview.bind("<Double-1>", self.onClick2)

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        print("l",l)
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            print("index",index,"val",val,"k",k)
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
            self.treeview_sort_column(tv, col, not reverse))

    def loadTable(self, keyphraseDF, columns, searchResults):
        # TODO: make reusable for various df's
        self.keyphraseDF = keyphraseDF
        self.searchResults = searchResults
        tv = Treeview(self)
        tv['columns'] = columns

        tv.heading("#0", text='keyphrase_full')
        tv.column("#0", anchor="w", width=300)

        for column in tv['columns']:
            tv.heading(column, text=column, command=lambda _col=column: self.treeview_sort_column(tv, _col, True))
            tv.column(column, anchor='center', width=100)

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for (i, row) in self.keyphraseDF.iterrows():
            self.treeview.insert('', 'end', text=row["keyphrase_full"],
                                 values=tuple(row[column] for column in columns))

        self.treeview.bind("<Double-1>", self.onClick)

        self.treeview.bind("<Enter>", self.onEnter)
        #self.treeview.bind("<Leave>", self.onLeave)

    def onEnter(self, event):
        region = self.treeview.identify('region', event.x, event.y)
        if region == "heading":
            print("double_click")

    def onClick2(self, event):
        item = self.treeview.identify('item', event.x, event.y)
        string = self.treeview.item(item, "text")
        index = int(string.split(" ")[0])
        link_id = self.secondWindowDF.iloc[index]["link_id"]
        print("you clicked on", link_id)

        child = tkinter.Toplevel(self)
        child.title("Window 3")
        t_child = Text(child)
        t_child.pack()
        t_child.delete(1.0, END)
        thirdWindowDF = self.masterDF[self.masterDF["link_id"] == link_id].sort_values(by='created_utc')
        for (index,row) in thirdWindowDF.iterrows():
            author = row['author']
            body = row['body']
            time = row['created_utc']
            text = "on " + str(time) + author + " wrote:\n" + body
            t_child.insert(END, text + '\n-----------------\n')

    def onClick(self, event):
        item = self.treeview.identify('item', event.x, event.y)
        region = self.treeview.identify('region', event.x, event.y)
        if region == "heading":
            print("clicked heading")
            return
        keyphrase_full = self.treeview.item(item, "text")
        keyphrase_stemmed = self.keyphraseDF[self.keyphraseDF["keyphrase_full"]==keyphrase_full]["keyphrase_stemmed"].values[0]
        docs = self.keyphraseDF[self.keyphraseDF["keyphrase_full"]==keyphrase_full]["docs"].values[0]
        print("you clicked on", keyphrase_full)
        print("searchResults: ", *self.searchResults)
        print("docs: ", *docs)
        intersection = list(docs & self.searchResults)
        print("intersection: ", *intersection)
        secondWindowDF = self.masterDF.iloc[intersection]
        print(secondWindowDF)

        child = tkinter.Toplevel(self)
        child.title("Window 2")

        windowfirst = Frame(child, bg='yellowgreen', width=1000, height=50, padx=3, pady=3)
        windowsecond = Frame(child, bg='gray', width=1000, height=100, padx=3, pady=3)

        windowfirst.pack()
        windowsecond.pack()

        TableApp(window="second", parent=windowsecond, columns=["body"], clicked_keyphrase=keyphrase_stemmed,
                 masterDF=self.masterDF, secondWindowDF=secondWindowDF.reset_index(drop=True))

###Main Application
class App(tkinter.Tk):
    ###Initialize things
    def __init__(self, whoosher, extractor):
        tkinter.Tk.__init__(self)
        self.whoosher = whoosher
        self.masterDF = self.whoosher.masterDF
        self.extractor = extractor
        self.initialize()

    ###Actually initialize the program
    def initialize(self):

        ###Create the main container frames
        firstframe = Frame(self, bg='yellowgreen', width=1000, height=50, padx=3, pady=3)
        secondframe = Frame(self, bg='gray', width=1000, height=100, padx=3, pady=3)
        #thirdframe = Frame(self, bg='white', width=1000, height=100, padx=3, pady=3)
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)

        ###layout all of the main containers
        firstframe.grid(row=0, sticky="ew")
        secondframe.grid(row=1, sticky="nsew")
        #thirdframe.grid(row=3, sticky="ew")
        self.fourthframe.grid(row=4, sticky="ew")

        ###first frame = search box
        submit = Button(firstframe, text="Search", background="yellowgreen", command=self.OnButtonClick)

        ###self.entryVariable is the search item
        self.entryVariable = tkinter.StringVar()
        self.entry = tkinter.Entry(firstframe, textvariable=self.entryVariable)
        self.entry.bind("<Return>", self.OnButtonClick)
        self.entryVariable.set("")

        ###top frame layout
        submit.grid(row=0, column=1)
        self.entry.grid(row=0, column=0, sticky='EW')

        ###second frame = summary stats
        commentsTotalLabel = Label(secondframe, text="Comments, total:", bg="gray")
        subredditsLabel = Label(secondframe, text="Subreddits:", bg="gray")
        commentsPositiveLabel = Label(secondframe, text="+ive comments:", bg="gray", fg="darkgreen")
        commentsNegativeLabel = Label(secondframe, text="-ive mentions:", bg="gray", fg="red")
        linksLabel = Label(secondframe, text="Threads:", bg="gray")

        self.commentsTotalVar = tkinter.StringVar()
        self.subredditsVar = tkinter.StringVar()
        self.commentsPositiveVar = tkinter.StringVar()
        self.commentsNegativeVar = tkinter.StringVar()
        self.linksVar = tkinter.StringVar()

        self.commentsTotalVar.set("0")
        self.subredditsVar.set("0")
        self.commentsPositiveVar.set("0")
        self.commentsNegativeVar.set("0")
        self.linksVar.set("0")

        commentsTotal = Label(secondframe, textvariable=self.commentsTotalVar, bg="gray")
        subreddits = Label(secondframe, textvariable=self.subredditsVar, bg="gray")
        commentsPositive = Label(secondframe, textvariable=self.commentsPositiveVar, bg="gray")
        commentsNegative = Label(secondframe, textvariable=self.commentsNegativeVar, bg="gray")
        links = Label(secondframe, textvariable=self.linksVar, bg="gray")

        ###second frame layout
        subredditsLabel.grid(row=0, column=0)
        linksLabel.grid(row=0, column=2)

        commentsTotalLabel.grid(row=1, column=0)
        commentsPositiveLabel.grid(row=1, column=2, sticky="w")
        commentsNegativeLabel.grid(row=1, column=4)

        subreddits.grid(row=0, column=1)
        links.grid(row=0, column=3)

        commentsTotal.grid(row=1, column=1)
        commentsPositive.grid(row=1, column=3)
        commentsNegative.grid(row=1, column=5)

        '''
        ###third frame = Keyphrases sorted by MI
        keyphraselabel = Label(thirdframe, text="Show keyphrases for")

        #choice = StringVar()
        choice.set("all")
        self.RB1 = Radiobutton(thirdframe, text="all", variable=choice, value="all", state="disabled")
        self.RB2 = Radiobutton(thirdframe, text="pos", variable=choice, value="pos", state="disabled")
        self.RB3 = Radiobutton(thirdframe, text="neg", variable=choice, value="neg", state="disabled")
        self.RB4 = Radiobutton(thirdframe, text="freq", variable=choice, value="freq", state="disabled")

        ###third frame layout
        keyphraselabel.grid(row=0, column=0)
        self.RB1.grid(row=0, column=4)
        self.RB2.grid(row=0, column=5)
        self.RB3.grid(row=0, column=6)
        self.RB4.grid(row=0, column=7)
        '''

        ###fourthframe = Table
        self.table = TableApp(self.fourthframe, window="first", masterDF=self.masterDF, columns=[])

    ###Click Submit Button and show all search
    def OnButtonClick(self, event=None):
        if event is not None:
            print("Enter")
        else:
            print("Button")

        user_query = self.entryVariable.get()
        (searchResults, searchDF) = self.whoosher.search(user_query)
        text = ". ".join(searchDF["body"])
        comments_total = len(searchDF)
        self.commentsTotalVar.set(comments_total)
        comments_positive = len(searchDF[searchDF['sentiment_class'] == 'positive'])
        share_positive = comments_positive/comments_total
        self.commentsPositiveVar.set(str(comments_positive) + " (" + str(share_positive) + ")")
        self.commentsNegativeVar.set(str(comments_total - comments_positive)  + " (" + str(1-share_positive) + ")")
        self.subredditsVar.set(len(searchDF['subreddit'].unique()))
        self.linksVar.set(len(searchDF['link_id'].unique()))
        #print("comments_total", self.commentsTotalVar.value())
        #print("comments_positive", self.commentsPositiveVar.value())
        keyphraseDF = self.extractor.get_keyphrases(textInput=text)
        print("############################")
        print(keyphraseDF)
        #self.RB1.configure(state="normal")
        #self.RB2.configure(state="normal")
        #self.RB3.configure(state="normal")
        #self.RB4.configure(state="normal")
        #self.RB1.select()
        self.fourthframe.destroy()
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)
        self.fourthframe.grid(row=4, sticky="ew")
        TableApp(parent=self.fourthframe, keyphraseDF=keyphraseDF, window="first",
                 masterDF=self.masterDF, columns=["MI", "PMI_pos", "PMI_neg", "frequency"], searchResults=searchResults)

    ###summary statistics

    ###button
    ###DF = DF.sort_values('Frequency', axis=0, ascending=False)
    ###miDF = miDF.sort_values(by="MI", axis=0, ascending=False)


def highlight(keyphrase, text, words=5):

    parts = keyphrase.lower().split(" ")
    search_term = parts[0][:3] + "[a-zA-Z]*"
    for i in range(1, len(parts)):
        search_term = search_term + " " + parts[i][:3] + "[a-zA-Z]*"

    print(search_term)

    search_result = re.search(search_term, text.lower())
    left = search_result.start()
    right = search_result.end()

    print(left, right)

    highlighted_text = "..." + " ".join(text[:left].split(" ")[-words-1:]) + text[left:right].upper() + " ".join(
        text[right:].split(" ")[:words+1]) + "..."

    print(highlighted_text)

    return highlighted_text
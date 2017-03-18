import tkinter
from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter.ttk import Combobox,Treeview,Scrollbar
import pandas


#df.ix[List]

###Create Table
class TableApp(Frame):
    def __init__(self, parent, masterDF, columns=[], secondWindowDF=pandas.DataFrame({'body' : []}),
                 keyphraseDF=pandas.DataFrame({'keyphrase_stemmed' : []}), searchResults=set([]), secondWindow=False):
        Frame.__init__(self, parent)
        # TODO: deal with default keyphraseDF
        self.masterDF = masterDF
        if secondWindow:
            self.loadTableWindow2(secondWindowDF, columns)
        else:
            self.loadTable(keyphraseDF, columns, searchResults)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def loadTableWindow2(self, secondWindowDF, columns):
        # TODO: make reusable for various df's
        self.secondWindowDF = secondWindowDF
        tv = Treeview(self)
        #columns = list(self.keyphraseDF.columns[1:].values)
        tv['columns'] = columns

        tv.heading("#0", text='#')
        tv.column("#0", anchor="w", width=300)

        for column in tv['columns']:
            tv.heading(column, text=column)
            tv.column(column, anchor='center', width=100)

        #tv.heading('pointwisemutual', text='PMI')
        #tv.column('pointwisemutual', anchor='center', width=50)

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for (i, row) in self.secondWindowDF.iterrows():
            self.treeview.insert('', 'end', text=i,
                                 values=tuple(row[column] for column in columns))

        self.treeview.bind("<Button-1>", self.onClick2)

    ###Get Table Values
    def loadTable(self, keyphraseDF, columns, searchResults):
        # TODO: make reusable for various df's
        self.keyphraseDF = keyphraseDF
        self.searchResults = searchResults
        tv = Treeview(self)
        #columns = list(self.keyphraseDF.columns[1:].values)
        tv['columns'] = columns

        tv.heading("#0", text='keyphrase_stemmed')
        tv.column("#0", anchor="w", width=300)

        for column in tv['columns']:
            tv.heading(column, text=column)
            tv.column(column, anchor='center', width=100)

        #tv.heading('pointwisemutual', text='PMI')
        #tv.column('pointwisemutual', anchor='center', width=50)

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for (i, row) in self.keyphraseDF.iterrows():
            self.treeview.insert('', 'end', text=row["keyphrase_stemmed"],
                                 values=tuple(row[column] for column in columns))

        self.treeview.bind("<Button-1>", self.onClick)

    def onClick2(self, event):
        item = self.treeview.identify('item', event.x, event.y)
        index = int(self.treeview.item(item, "text"))
        link_id = self.secondWindowDF.iloc[index]["link_id"]
        print("you clicked on", link_id)

        child = tkinter.Toplevel(self)
        child.title("Window 3")
        t_child = Text(child)
        t_child.pack()
        t_child.delete(1.0, END)
        for comment in self.masterDF[self.masterDF["link_id"] == link_id]['body'].values.tolist():
            t_child.insert(END, comment + '\n-----------------\n')

    def onClick(self, event):
        item = self.treeview.identify('item', event.x, event.y)
        keyphrase = self.treeview.item(item, "text")
        docs = self.keyphraseDF[self.keyphraseDF["keyphrase_stemmed"]==keyphrase]["docs"].values[0]
        print("you clicked on", keyphrase)
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

        TableApp(parent=windowsecond, columns=["body"],
                 masterDF=self.masterDF, secondWindowDF=secondWindowDF.reset_index(drop=True), secondWindow=True)


        '''
    ###Create Second Window
    def SecondWindow(self):
        child = tkinter.Toplevel(self)
        child.title("Comments")
        ###Create the main container frames


        ###layout all of the main containers


        ##comment
        ctr_left = Frame(windowsecond, bg='red', width=500, height=300, padx=3, pady=3)
        ctr_right = Frame(windowsecond, bg='brown', width=500, height=300, padx=3, pady=3)

        ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_right.grid(row=0, column=2, sticky="ns")
    ######################################################
        t_child = Text(child)
        t_child.pack()
        print(keyphrase)
        t_child.delete(1.0, END)
        for comment in self.masterDF[self.masterDF[keyphrase]==1]['body'].values.tolist():
            t_child.insert(END, comment + '\n-----------------\n')
        #call second window
        '''
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
        thirdframe = Frame(self, bg='white', width=1000, height=100, padx=3, pady=3)
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)

        ###layout all of the main containers
        firstframe.grid(row=0, sticky="ew")
        secondframe.grid(row=1, sticky="nsew")
        thirdframe.grid(row=3, sticky="ew")
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
        statslabel1 = Label(secondframe, text="Total Comments", bg="gray")
        statslabel2 = Label(secondframe, text="Total Subreddits", bg="gray")
        statslabel3 = Label(secondframe, text="Total Positive", bg="gray", fg="darkgreen")
        statslabel4 = Label(secondframe, text="Total Neutral", bg="gray", fg="yellow")
        statslabel5 = Label(secondframe, text="Total Negative", bg="gray", fg="red")

        self.statResult1 = tkinter.StringVar()
        self.statResult2 = tkinter.StringVar()
        self.statResult3 = tkinter.StringVar()
        self.statResult4 = tkinter.StringVar()
        self.statResult5 = tkinter.StringVar()

        self.statResult1.set(u"0")
        self.statResult2.set(u"0")
        self.statResult3.set(u"0")
        self.statResult4.set(u"0")
        self.statResult5.set(u"0")

        resultlabel1 = Label(secondframe, textvariable=self.statResult1, bg="gray")
        resultlabel2 = Label(secondframe, textvariable=self.statResult2, bg="gray")
        resultlabel3 = Label(secondframe, textvariable=self.statResult3, bg="gray")
        resultlabel4 = Label(secondframe, textvariable=self.statResult4, bg="gray")
        resultlabel5 = Label(secondframe, textvariable=self.statResult5, bg="gray")

        ###second frame layout
        statslabel1.grid(row=0, column=0)
        statslabel2.grid(row=0, column=2)
        statslabel3.grid(row=1, column=0, sticky="w")
        statslabel4.grid(row=1, column=2)
        statslabel5.grid(row=1, column=4)

        resultlabel1.grid(row=0, column=1)
        resultlabel2.grid(row=0, column=3)
        resultlabel3.grid(row=1, column=1)
        resultlabel4.grid(row=1, column=3)
        resultlabel5.grid(row=1, column=5)

        ###third frame = Keyphrases sorted by MI
        keyphraselabel = Label(thirdframe, text="Show keyphrases for")

        choice = StringVar()
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

        ###fourthframe = Table
        self.table = TableApp(self.fourthframe, masterDF=self.masterDF, columns=[])

    ###Click Submit Button and show all search
    def OnButtonClick(self, event=None):
        if event is not None:
            print("Enter")
        else:
            print("Button")

        user_query = self.entryVariable.get()
        (searchResults, searchDF) = self.whoosher.search(user_query)
        text = ". ".join(searchDF["body"])
        keyphraseDF = self.extractor.get_keyphrases(textInput=text)
        print("############################")
        print(keyphraseDF)
        self.RB1.configure(state="normal")
        self.RB2.configure(state="normal")
        self.RB3.configure(state="normal")
        self.RB4.configure(state="normal")
        self.RB1.select()
        self.fourthframe.destroy()
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)
        self.fourthframe.grid(row=4, sticky="ew")
        TableApp(parent=self.fourthframe, keyphraseDF=keyphraseDF,
                 masterDF=self.masterDF, columns=["MI", "PMI_pos", "PMI_neg", "frequency"], searchResults=searchResults)

    ###summary statistics



    #####button
    #####DF = DF.sort_values('Frequency', axis=0, ascending=False)
    #####miDF = miDF.sort_values(by="MI", axis=0, ascending=False)
import tkinter
from tkinter import *
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter.ttk import Combobox,Treeview,Scrollbar
from keyphrase_extractor import get_keyphrases
import pandas
import webbrowser


###Create Table
class TableApp(Frame):
    def __init__(self, parent, keyphraseDF=pandas.DataFrame({'Term' : []}),commentsDF=pandas.DataFrame({'a' : [1]})):
        Frame.__init__(self, parent)
        self.loadTable(keyphraseDF)
        self.commentsDF = commentsDF
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    ###Get Table Values
    def loadTable(self, keyphraseDF):
        # TODO: make reusable for various df's
        self.keyphraseDF = keyphraseDF
        tv = Treeview(self)
        #tv['columns'] = ('pointwisemutual', 'mutual', 'viewfull')
        tv.heading("#0", text='Key Phrase')
        tv.column("#0", anchor="w", width=300)
        '''
        tv.heading('pointwisemutual', text='PMI')
        tv.column('pointwisemutual', anchor='center', width=50)
        tv.heading('mutual', text='MI')
        tv.column('mutual', anchor='center', width=50)
        tv.heading('viewfull', text='See Full Thread')
        tv.column('viewfull', anchor='center', width=100)
        '''
        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for (i, row) in self.keyphraseDF.iterrows():
            self.treeview.insert('', 'end', text=row["Keyphrase"])
            #self.treeview.insert('', 'end', text=row["body"], values=(row["name"], row["subreddit"], 'View'))

        self.treeview.bind("<Button-1>", self.onClick)


    def onClick(self, event):
        # change to the highlighted view
        item = self.treeview.identify('item', event.x, event.y)
        keyphrase = self.treeview.item(item, "text")
        print("you clicked on", keyphrase)
        #link = self.keyphraseDF[self.keyphraseDF['body'] == body]["link"].tolist()[0]

        child = tkinter.Toplevel(self)
        t_child = Text(child)
        t_child.pack()
        print(keyphrase)
        t_child.delete(1.0, END)
        for comment in self.commentsDF[self.commentsDF[keyphrase]==1]['body'].values.tolist():
            t_child.insert(END, comment + '\n-----------------\n')
        #call second window
        #webbrowser.open(link)

'''
###Create Timeline Bar Graph
class TimelineApp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.CreateGraph()
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def CreateGraph(self):
        timetable = pandas.DataFrame(columns=['month', 'total'], index=[0, 1, 2])
        timetable.loc[0] = pandas.Series({'month': "Jan", 'total': 50})
        timetable.loc[1] = pandas.Series({'month': "Feb", 'total': 35})
        timetable.loc[2] = pandas.Series({'month': "Mar", 'total': 29})
        timetable.loc[3] = pandas.Series({'month': "Apr", 'total': 15})
        timetable.loc[4] = pandas.Series({'month': "May", 'total': 10})
        timetable.loc[5] = pandas.Series({'month': "Jun", 'total': 47})
        timetable.loc[6] = pandas.Series({'month': "Jul", 'total': 38})
        timetable.loc[7] = pandas.Series({'month': "Aug", 'total': 7})
        timetable.loc[8] = pandas.Series({'month': "Sep", 'total': 23})
        timetable.loc[9] = pandas.Series({'month': "Oct", 'total': 19})
        timetable.loc[10] = pandas.Series({'month': "Nov", 'total': 28})
        timetable.loc[11] = pandas.Series({'month': "Dec", 'total': 33})

        ###month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        c_width = 55
        c_height = 180
        c = Canvas(self, width=c_width, height=c_height, bg='gray')
        c.pack()

        ###sizing the graph
        ###y height = max value * y_stretch
        y_height = timetable.total.max()
        y_stretch = 140 / y_height
        # gap between lower canvas edge and x axis
        y_gap = 20
        # stretch enough to get all data items in
        x_stretch = 15
        x_width = 28
        # gap between left canvas edge and y axis
        x_gap = 20

        c.create_line(0, c_height - y_gap, 550, c_height - y_gap)

        for i, row in timetable.iterrows():
            # calculate reactangle coordinates (integers) for each bar
            x0 = i * x_stretch + i * x_width + x_gap
            y0 = c_height - (row["total"] * y_stretch + y_gap)
            x1 = i * x_stretch + i * x_width + x_width + x_gap
            y1 = c_height - y_gap
            # draw the bar
            c.create_rectangle(x0, y0, x1, y1, fill="midnightblue")
            # put the y value above each bar
            c.create_text(x1, y0, anchor=SE, text=row["total"])
            c.create_text(x1, c_height - 2, anchor=SE, text=row["month"])
            print(i)
'''

###Main Application
class App(tkinter.Tk):
    ###Initialize things
    def __init__(self, whoosher):
        tkinter.Tk.__init__(self)
        self.whoosher = whoosher
        self.initialize()

    ###Actually initialize the program
    def initialize(self):

        ###Create the main container frames
        firstframe = Frame(self, bg='yellowgreen', width=1000, height=50, padx=3, pady=3)
        secondframe = Frame(self, bg='gray', width=1000, height=100, padx=3, pady=3)
        thirdframe = Frame(self, bg='white', width=1000, height=100, padx=3, pady=3)
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)
        #fifthframe = Frame(self, bg='yellowgreen', width=1000, height=300, padx=3, pady=3)
        #sixthframe = Frame(self, bg='gray', width=1000, height=300, padx=3, pady=3)

        ###layout all of the main containers
        firstframe.grid(row=0, sticky="ew")
        secondframe.grid(row=1, sticky="nsew")
        thirdframe.grid(row=3, sticky="ew")
        self.fourthframe.grid(row=4, sticky="ew")
        #fifthframe.grid(row=5, sticky="ew")
        #sixthframe.grid(row=6, sticky="ew")

        ###first frame = search box
        submit = Button(firstframe, text="Search", background="yellowgreen", command=self.OnButtonClick)

        ###self.entryVariable is the search item
        self.entryVariable = tkinter.StringVar()
        self.entry = tkinter.Entry(firstframe, textvariable=self.entryVariable)
        self.entry.bind("<Return>", self.OnPressEnter)
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
        #keyphrasesearch = Label(thirdframe, textvariable=self.entryVariable)
        #keyphraseshow = Label(thirdframe, text="Show: ")

        choice = StringVar()
        choice.set("all")
        self.RB1 = Radiobutton(thirdframe, text="all", variable=choice, value="all", state="disabled")
        self.RB2 = Radiobutton(thirdframe, text="pos", variable=choice, value="pos", state="disabled")
        self.RB3 = Radiobutton(thirdframe, text="neg", variable=choice, value="neg", state="disabled")

        #showallcomments = Button(thirdframe, text="Show All Comments", command=self.SecondWindow)

        ###third frame layout
        keyphraselabel.grid(row=0, column=0)
        #keyphrasesearch.grid(row=0, column=1)
        #keyphraseshow.grid(row=0, column=3)
        self.RB1.grid(row=0, column=4)
        self.RB2.grid(row=0, column=5)
        self.RB3.grid(row=0, column=6)
        #showallcomments.grid(row=0, column=7)

        ###fourthframe = Table
        self.table = TableApp(self.fourthframe)

        ###fifth frame = Timeline Header
        #timelinehead = Label(fifthframe, text="Comment Frequency Timeline", bg="yellowgreen")

        #timelinehead.grid(row=0, column=0)

        ###sixth frame = Actual Timeline
        #TimelineApp(sixthframe)

    ###Click Submit Button and show all search
    def OnButtonClick(self):
        print("OnButtonClick")
        user_query = self.entryVariable.get()
        search_results_df = self.whoosher.search_keywords(user_query)
        print('# search_results_df', search_results_df)
        keyphrases = get_keyphrases(". ".join(search_results_df["body"].tolist()))['Term'].tolist()
        self.currentDF, self.totalDF = self.whoosher.get_MIs(keyphrases)
        self.RB1.configure(state="normal")
        self.RB2.configure(state="normal")
        self.RB3.configure(state="normal")
        self.RB1.select()
        self.fourthframe.destroy()
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)
        self.fourthframe.grid(row=4, sticky="ew")
        TableApp(self.fourthframe, self.currentDF, self.totalDF)

    ###summary statistics

    ###Click Enter and show all search
    def OnPressEnter(self, event):
        # TODO: broken, to be fixed.
        print("OnPressEnter")
        user_query = self.entryVariable.get()
        self.currentDF = self.whoosher.search_keywords(user_query)
        print('# currentDF',self.currentDF)
        self.RB1.configure(state="normal")
        self.RB2.configure(state="normal")
        self.RB3.configure(state="normal")
        self.RB1.select()
        self.fourthframe.destroy()
        self.fourthframe = Frame(self, bg='lavender', width=1000, height=100, padx=3, pady=3)
        self.fourthframe.grid(row=4, sticky="ew")
        TableApp(self.fourthframe, self.currentDF)

    '''
    ###Create Second Window
    def SecondWindow(self):
        child = tkinter.Toplevel(self)
        child.title("Comments")
        ###Create the main container frames
        windowfirst = Frame(child, bg='yellowgreen', width=1000, height=50, padx=3, pady=3)
        windowsecond = Frame(child, bg='gray', width=1000, height=100, padx=3, pady=3)

        ###layout all of the main containers
        windowfirst.pack()
        windowsecond.pack()

        ##comment
        ctr_left = Frame(windowsecond, bg='red', width=500, height=300, padx=3, pady=3)
        ctr_right = Frame(windowsecond, bg='brown', width=500, height=300, padx=3, pady=3)

        ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_right.grid(row=0, column=2, sticky="ns")
    '''
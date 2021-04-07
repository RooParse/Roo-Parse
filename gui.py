from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox
# from tkinter import ttk
# from PIL import Image, ImageTk
import os
import shutil
import tempfile
import pandas as pd
# from mine import *
import mine as mine
from earnings_graphs import create_graphs_from_data

'''
After initial release changes to mine.py, the parsing script increase the version number to the next whole number.
After changes to gui.py add 0.1 to version number.
'''

VERSION = "0.1"

liscense = '''

This program was created to make tax returns easier and facilitate gathering of data so riders can see what the effects of changes in the algorythms are having on hourly rate over time.

Begin license text.
Copyright 2019

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

End license text.
'''

help_str = '''
1. Slect a folder containing the invoices you wish to parse, it should then show the file path at the bottom of the window. \n

2. Click run to extract the data from the pdfs to csv files. \n

3. Select the folder you wish to save a zip file containing the csv files in, it should then show the file path at the bottom of the window. \n

4. Click save. This will overwrite any folder called "data.zip" in the directory you selected. \n
'''

data_str = '''
Greetings valued user! \n
Please consider sending in your earnings data, i'm compiling a database to
look into fees over time so the more data I can add to that database the 
better. The results and the database will be published online so anyone 
can view and analyse it themselves if they wish. All data is anonomous, 
no identifyable information is harvested from the invoces. The only personal
info in the invoices is the ridersname but this is not saved. The source 
code of this app can be viewed on github at: https://github.com/RooParse/Roo_Parse 
 
If you would like to contribute to the database please send the zip
file ouput containing the csv data to: rooparse@gmail.com

Please also email with any questions and if you would like to 
contribute to rooparse itself.
'''


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Roo Parse " + VERSION)
        master.configure(background='black')

        self.run_button = Button(master, text="Run", command=lambda: self.miner(self.inv_folder), anchor='w', width=20,
                                 justify=LEFT)
        self.run_button.pack(fill=X)

        self.help_button = Button(master, text="Help", command=self.help, width=20, anchor='w', justify=LEFT)
        self.help_button.pack(fill=X)

        self.about_button = Button(master, text="About", command=self.about, anchor='w', width=20, justify=LEFT)
        self.about_button.pack(fill=X)

        self.save_button = Button(master, text="Save", command=lambda: self.zipdir(self.save_folder), anchor='w',
                                  width=20, justify=LEFT)
        self.save_button.pack(fill=X)

        self.browse_file = Button(master, text="Select invoice folder", command=self.browseFile, anchor='w', width=20,
                                  justify=LEFT)
        self.browse_file.pack(fill=X)

        self.save_file = Button(master, text="Select folder to save data", command=self.saveFile, anchor='w', width=20,
                                justify=LEFT)
        self.save_file.pack(fill=X)

        # image = Image.open("roo.png")
        # photo = ImageTk.PhotoImage(image)

        self.label_data_message = Label(self.master, text=data_str, bg="black", fg="green", anchor='w', width=20,
                                        justify=LEFT)
        self.label_data_message.pack(fill=X)

        # label = Label(image=photo, borderwidth=0 , highlightthickness=0, relief=None, padx=0,pady=0)
        # label.image = photo # keep a reference!
        # label.pack()

        self.label_inv = Label(self.master, text="Invoices file path: ", bg="black", fg="green", anchor='w', width=20,
                               justify=LEFT)
        self.label_inv.pack(fill=X, side=BOTTOM)

        self.label_save = Label(self.master, text="Save file path: ", bg="black", fg="green", anchor='w', width=20,
                                justify=LEFT)
        self.label_save.pack(fill=X, side=BOTTOM)

        # Directories for extracting and saving
        self.inv_folder = ""
        self.save_folder = ""

        # initialise dataframes to keep data in
        self.fa_df = pd.DataFrame()
        self.data_df = pd.DataFrame()
        self.summary_df = pd.DataFrame()

        # Initialise dictionary for graphs
        self.graphs = {}

        # Temporary directory to save data before zipping
        self.tempdir = tempfile.mkdtemp()
        print(self.tempdir)

        # Text input bar---------------------#
        # self.text = StringVar()
        # self.e = Entry(root, textvariable=self.text)
        # self.e.pack()
        # self.run_button = Button(master, text="Run", command = lambda: main(self.e.get()))
        # self.run_button.pack(fill=X)

        # self.close_button = Button(master, text="Close", command=master.quit)
        # self.close_button.pack(fill=X)

    def miner(self, invoice_path):  # trying to move function to this file

        if self.inv_folder == "":
            messagebox.showinfo("Help", "Please first select a directory containing all (and only) invoice pdfs.")

        else:
            text_list = mine.get_text_list(invoice_path)

            self.fa_df = mine.concat_fee_adjustments(text_list)
            # print(self.fa_df)
            self.fa_df.to_csv(os.path.join(self.tempdir, "adjustments.csv"))

            self.data_df = mine.concat_invoices(text_list)
            # print(self.data_df)
            self.data_df.to_csv(os.path.join(self.tempdir, "data.csv"))

            self.summary_df = mine.concat_summary(text_list)
            # print(self.summary_df)
            self.summary_df.to_csv(os.path.join(self.tempdir, "summary.csv"))

            self.graphs = create_graphs_from_data(self.data_df)

            for key, plot in self.graphs.items():
                print(plot)
                plot.save(filename=os.path.join(self.tempdir, key + ".png"))

    def browseFile(self):
        self.label_inv.destroy()
        self.inv_folder = askdirectory()
        self.label_inv = Label(self.master, text="Invoices file path: " + self.inv_folder, bg="black", fg="green",
                               anchor='w', width=20, justify=LEFT)
        self.label_inv.pack(fill=X, side=BOTTOM)

    def saveFile(self):
        self.label_save.destroy()
        self.save_folder = askdirectory()
        self.label_save = Label(self.master, text="Save file path: " + self.save_folder, bg="black", fg="green",
                                anchor='w', width=20, justify=LEFT)
        self.label_save.pack(fill=X, side=BOTTOM)

    def zipdir(self, path_to_save):
        if path_to_save == "":
            messagebox.showinfo("Help", "Please first select a directory to save the output summary data.")
        else:
            f = os.path.join(path_to_save, "data-RooParse" + VERSION + ".zip")
            if os.path.exists(f):  # Check if file exists, and delete if true
                os.remove(f)
            shutil.make_archive(os.path.join(path_to_save, "data"), 'zip', self.tempdir)
            messagebox.showinfo("Thanks!",
                                "Data saved to :" + path_to_save + "\n\n Please consider sending in your earnings data, we are compiling a database to look into how fees have been changing over the years, so the more data we can add to that database the better. The results and the database will be published online so anyone can view and analyse it themselves if they wish. All data is completely anonymous, no identifiable information is harvested from the invoices. Only information about earnings, and not the rider, is saved to the data.zip archive. The source code of this app can be viewed on github. Send it to: rooparse@gmail.com")
            shutil.rmtree(self.tempdir)

    def save_message(self):
        messagebox.showinfo("Thanks!", "Data saved to :" + str(
            self.save_folder) + "\n\n Please consider sending in your earnings data, we are compiling a database to look into how fees have been changing over the years, so the more data we can add to that database the better. The results and the database will be published online so anyone can view and analyse it themselves if they wish. All data is completely anonymous, no identifiable information is harvested from the invoices. Only information about earnings, and not the rider, is saved to the data.zip archive. The source code of this app can be viewed on github. Send it to: rooparse@gmail.com")

    def help(self):
        messagebox.showinfo("Help", help_str)

    def about(self):
        messagebox.showinfo("Help", liscense)


root = Tk()
my_gui = GUI(root)
root.mainloop()

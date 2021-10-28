from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox
import os
import shutil
import tempfile
import pandas as pd
import mine as mine
from create_summaries import calculate_summaries, create_summary_graphs
from terms_and_conditions_window import show_terms_window
from datetime import datetime
from resources import resources_dict

help_str = resources_dict['help_str']
after_extraction_str = resources_dict['after_extraction_str']
license_str = resources_dict['license']
about_str = resources_dict['about']
VERSION = resources_dict['version']


# GUI Interface class
class GUI:

    def __init__(self, master):
        self.master = master
        master.title('Roo Parse ' + VERSION)
        master.configure(background='white')

        self.inv_folder = None
        self.save_folder = None

        self.help_button = Button(master, text='Help and instructions', command=self.help_window, width=25, anchor='w',
                                  justify=LEFT)
        self.help_button.pack(fill=X)

        self.payslip_dir_select_button = Button(master, text='1. Select folder containing invoices',
                                                command=self.select_payslip_dir, anchor='w', width=25, justify=LEFT)
        self.payslip_dir_select_button.pack(fill=X)

        self.save_dir_select_button = Button(master, text='2. Select folder to save data',
                                             command=self.select_save_dir, anchor='w', width=25, justify=LEFT)
        self.save_dir_select_button.pack(fill=X)

        self.run_and_save_button = Button(master, text='3. Analyse and save summary', state=DISABLED,
                                          command=self.run_and_save, anchor='w', width=25, justify=LEFT)
        self.run_and_save_button.pack(fill=X)

        self.about_button = Button(master, text='About', command=self.show_about_window, anchor='w', width=25, justify=LEFT)
        self.about_button.pack(fill=X)

        # Directories for extracting and saving
        self.inv_folder = ''
        self.save_folder = ''

        # initialise dataframes to keep data in
        self.fa_df = pd.DataFrame()
        self.data_df = pd.DataFrame()

        self.summaries_dict = None

        # Temporary directory to save data before zipping
        self.tempdir = tempfile.mkdtemp()
        print(self.tempdir)

    def run_and_save(self):
        self.miner()
        self.zipdir()

    def miner(self):  # trying to move function to this file

        if self.inv_folder == '' or self.inv_folder is None:
            messagebox.showinfo('Help', 'Please first select a directory containing all (and only) invoice pdfs.')

        else:
            text_list = mine.get_text_list(self.inv_folder)

            self.fa_df = mine.concat_fee_adjustments(text_list)
            self.fa_df.to_csv(os.path.join(self.tempdir, 'All fee adjustments.csv'))

            self.data_df = mine.concat_invoices(text_list)
            self.data_df.to_csv(os.path.join(self.tempdir, 'All sessions.csv'))

            self.summaries_dict = calculate_summaries(data_df=self.data_df, output_dir=self.tempdir)
            create_summary_graphs(summaries_dict=self.summaries_dict, output_dir=self.tempdir)

    def select_payslip_dir(self):
        self.inv_folder = askdirectory()

        if bool(self.inv_folder):
            self.payslip_dir_select_button['text'] = '1. Select folder containing invoices (' + self.inv_folder + ')'
            if bool(self.save_folder):
                self.run_and_save_button['state'] = NORMAL

    def select_save_dir(self):
        self.save_folder = askdirectory()

        if bool(self.save_folder):
            self.save_dir_select_button['text'] = '2. Select folder to save data (' + self.save_folder + ')'
            if bool(self.inv_folder):
                self.run_and_save_button['state'] = NORMAL

    def zipdir(self):
        if self.save_folder == '':
            messagebox.showinfo('Help', 'Please first select a directory to save the output summary data.')
        else:
            zip_output_path = os.path.join(self.save_folder, 'Extracted data - RooParse ' + VERSION + ' - ' +
                                           datetime.now().date().strftime('%Y-%m-%d') + '.zip')
            if os.path.exists(zip_output_path):  # Check if file exists, and delete if true
                os.remove(zip_output_path)
            shutil.make_archive(zip_output_path, 'zip', self.tempdir)
            messagebox.showinfo('Thanks!\n\n',
                                'Data saved to:  ' + self.save_folder + '\n\n' + after_extraction_str)

    @staticmethod
    def help_window():
        messagebox.showinfo('Help', help_str)

    @staticmethod
    def show_about_window():
        messagebox.showinfo('About', about_str)


accepted_terms = show_terms_window()

if accepted_terms:
    root = Tk()
    root.geometry('500x130')
    root.resizable(False, False)
    my_gui = GUI(root)
    root.mainloop()
sys.exit(0)

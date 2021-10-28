import tkinter as tk
from resources import resources_dict

agreed_to_terms = False


# GUI Interface class
class TermsWindow:
    def __init__(self, master):
        self.master = master
        master.title("Terms and conditions")
        master.configure(background='white')

        self.frame1 = tk.Frame(master, width=70, height=30, bg='#ffffff',
                               borderwidth=1, relief="sunken")
        self.frame1.grid(row=0, column=0, columnspan=4)
        self.scrollbar = tk.Scrollbar(self.frame1)
        self.editArea = tk.Text(self.frame1, width=70, height=28, wrap="word",
                                yscrollcommand=self.scrollbar.set,
                                borderwidth=0, highlightthickness=0)
        self.editArea.insert(tk.END, resources_dict['full_terms'])
        self.scrollbar.config(command=self.editArea.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.editArea.pack(side="left", fill="both", expand=True)
        self.frame1.place(x=10, y=30)

        self.agree_button = tk.Button(master, text="Reject", command=self.reject_terms)
        self.agree_button.grid(row=1, column=2, sticky='nw')

        self.agree_button = tk.Button(master, text="Accept", command=self.accept_terms)
        self.agree_button.grid(row=1, column=3, sticky='nw')

        master.grid_columnconfigure([0, 1], minsize=250)
        master.grid_rowconfigure(0, minsize=500)

    def accept_terms(self):
        global agreed_to_terms
        agreed_to_terms = True
        self.master.destroy()

    def reject_terms(self):
        global agreed_to_terms
        agreed_to_terms = False
        self.master.destroy()


def show_terms_window():
    root = tk.Tk()
    root.geometry('600x550')
    root.resizable(False, False)
    my_gui = TermsWindow(root)
    root.mainloop()
    return agreed_to_terms

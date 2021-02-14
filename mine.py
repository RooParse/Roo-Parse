import io
import os 
import zipfile
import shutil
import re 
from datetime import datetime
import pandas as pd

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

'''
After initial release changes to mine.py, the parsing script increase the version number to the next whole number.
After changes to gui.py add 0.1 to version number.
'''

VERSION = "0.1"

def extract_text(pdf_path): # Stolen function to convert pdfs to text
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
 
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
 
        text = fake_file_handle.getvalue()
 
    # close open handles
    converter.close()
    fake_file_handle.close()
 
    if text:
        return text

def create_df(text):
    s = text.split('Summary')[0] # Take all text before 'Summary'
    s = s.split('DayDateTime')[1]
    s = s.split('Fee Adjustments')[0] # Take all text before 'Fee Adjustments'

    with open("raw.txt", "w") as raw:
        raw.write(s)
    # get time in and out as one then split
    t = re.findall('..:....:..',s) # re for time in
    ti = [i [ :int(len(i)/2)] for i in t]
    to = [i [int(len(i)/2): ] for i in t]

    h = re.findall(':..\d{1,2}.\d{1}h', s) # re for hours worked and :xx of time out
    h = [re.sub('h','' , i) for i in h] # remove h
    h = [re.sub(':..','' , i) for i in h] # remove :xx

    #d = re.findall('\d{2}\D{3,}\d{4}',s) # re for date
    date_list = re.findall('\d{2} [A-Za-z]{3,} \d{4}',s)
    dt = [datetime.strptime(x, '%d %B %Y') for x in date_list]
    d = [datetime.strftime(x, "%d-%m-%y") for x in dt]

    ov = re.findall('\d*: £\d{1,}.\d{2}',s) # get number of orders and value in £
    o = [i.split(': ')[0] for i in ov] # Split into orders and value 

    v = [re.sub('£', '', i.split(': ')[1]) for i in ov]

    day = re.findall('Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday', s)

    #print(s)
    #print(str(day) + '\n' + str(d) + '\n' + str(ti) + '\n' + str(to) + '\n' + str(h) + '\n' + str(o) + '\n' + str(v))

    df = pd.DataFrame(
        {
            'Day': day,
            'Date': d,
            'Time_in': ti,
            'Time_out': to,
            'Hours_worked': h,
            'Orders': o,
            'Total': v
        }
    )

    return df

def concat_invoices(text_list):
    data_df = pd.DataFrame(columns = ['Day', 'Date', 'Time_in', 'Time_out', 'Hours_worked', 'Orders', 'Total'])
    
    for i in text_list:
        df = create_df(i)
        # Could use keys arg to concat lable by date
        data_df = pd.concat([data_df, df]) # ineficient could do better 
        data_df.reset_index(drop=True, inplace=True)
    return data_df

def create_summary_df(text):
    s = text.split('Summary')[1] # Take all text after 'Summary'
    split = re.split('(.\d+.\d+)',s) # Split based £xx.xx where x is a didget
    date_list = re.findall('\d{2} [A-Za-z]{3,} \d{4}',text)
    dt = [datetime.strptime(x, '%d %B %Y') for x in date_list]
    date_list_converted = [datetime.strftime(x, "%d-%m-%y") for x in dt]
    date = date_list_converted[0]

    for i in range(len(split)): # Remove weird thing
        if split[i] == "\x0c":
            split.remove(split[i])
    
    split = [re.sub('£|Â', '', i) for i in split]

    names = []
    values = [] 
    for i in range(len(split)): # Deinterleave list into names and values
        if (i % 2) == 0:
            names.append(split[i])
        else:
            values.append(split[i])
    # Create pandas dataframe from names and values

    #val = [re.sub('£', '', i) for i in values]

    df = pd.DataFrame(
        {
            'names_' + date: names,
            '' + date: values
        }
    )
    df.set_index('names_' + date, inplace=True)
    return(df)

def concat_summary(text_list):

    df_list = []
    full_df = pd.DataFrame()

    for i in text_list:
        summary_df = create_summary_df(i)
        df_list.append(summary_df)

    for i, df in enumerate(df_list):
        print(df)
        full_df = pd.merge(full_df, df_list[i], left_index=True, right_index=True, how='outer')

    return full_df
 
def create_fee_adjustments_df(text):
    head = ["Category","Note","Amount", "Date"]

    date_list = re.findall('\d{2}\D{3,}\d{4}',text)[0]
    print(type(date_list))
    if type(date_list) == str:
        date_list = [date_list]

    dt = [datetime.strptime(x, '%d %B %Y') for x in date_list]
    print(dt)
    date = [datetime.strftime(x, "%d-%m-%y") for x in dt]
    print(date)
    date = [re.sub("\[|'","", i) for i in date]
    s = text.split('Summary')[0] # Take all text after 'Summary'
    if re.search('Fee Adjustments', s):
        s = s.split('CategoryNoteAmount')[1] # Take all text after 'Fee Adjustments'
    else:
        return 'No Adjustments'

    total = re.split('(£\d+.\d{2})',s)[-3:-1]
    ex_total = re.split('(£\d+.\d{2})',s)[:-3]
    
    cat = re.findall("[A-Z]{2,} [A-Z]{2,}", str(ex_total))
    cat = [i[:-1] for i in cat]

    note = re.findall("[A-Z][a-z][A-Za-z0-9 ]*", str(ex_total))

    amount = re.findall('(£\d+.\d{2})', str(ex_total))
    amount = [re.sub('£|Â|-', '', i) for i in amount]

    list_list = []
    for c, n, a, d in zip(cat, note, amount, date):
        list_list.append([c, n, a, d])

    total.insert(1,"-")

    df = pd.DataFrame()

    for row in list_list:
        df = df.append(pd.DataFrame(data=[row]), ignore_index=True)

    return df

def concat_fee_adjustments(text_list):

    df_list = []
    full_df = pd.DataFrame()

    for i in text_list:
        df = create_fee_adjustments_df(i)
        if type(df) != str:
            df_list.append(df)
    for i, df in enumerate(df_list):
        full_df = full_df.append(df)

    return full_df

def get_text_list(invoice_path):
    text_list = []
    for filename in os.listdir(invoice_path):
        if filename.endswith(".pdf"):
            print(os.path.join(invoice_path, filename))
            text = extract_text(os.path.join(invoice_path, filename))
            text_list.append(text)
    return text_list


def main(invoice_path):
    text_list = get_text_list(invoice_path)

    fa_df = concat_fee_adjustments(text_list)
    fa_df.to_csv("outputs/adjustments.csv")
    print(fa_df)

    data_df = concat_invoices(text_list)
    data_df.to_csv("outputs/data.csv")
    print(data_df)

    summary_df = concat_summary(text_list)
    summary_df.to_csv("outputs/summery.csv")
    print(summary_df)

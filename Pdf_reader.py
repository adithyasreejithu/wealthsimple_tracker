"""
Things that will need to be added/changed 

TOP PRIORTY 
- Issue with reading empty files 
    - This can be done by reading all the data from the 
- some files arent being read properly (create log to find which ones)
and find a better regrex statement to read it

- The list files will need to be read in chroniclogical order 
(check if this matters bc I can query the order)

- What happens when I read empty files (no data exists in that file) 

- Need to create a masterfile that contains a file with all the keys 
    - db name 
    - folder locations 
    - etc 

- could also add logging methods. 
"""

import os
import re 
import shutil
import db_func as func
import numpy as np 
from pypdf import PdfReader

# Make this a dictionary later - use os lib to get file current location 
folder_path = r"C:\Projects\Python\Stocks\Data\Wealthsimple_Files"  
destination = r"C:\Projects\Python\Stocks\Data\Wealthsimple_Files\Scanned"

def move_file(file): 
    file_name = os.path.basename(file)
    dest = os.path.join(destination, file_name)
    print(dest)

    shutil.move(file,dest)

# Check if Folder paths exist 
def check_folders(folder): 
    if os.path.isdir(folder): 
        return True; 
    else: 
        os.makedirs(folder)

# Reads dir all the unread files
def unread_files():
    files = []
    with os.scandir(folder_path) as entries: 
        for entry in entries: 
            if entry.is_file():
                # file_name = entry.name
                file_location = os.path.abspath(entry)
                files.append(file_location)
    return files

# Extracts and reads the pdf files
def read_file(file_name):
    
    i = 0
    index = 0
    flag = False
    data = {
        "div": [],
        "buy": [],
        "cont": [],
        "lend": []
    }

    # Retriving file location
    file_location = os.path.abspath(file_name)
    print(file_location)
    
    # Reading file
    reader = PdfReader(file_location)
    page = reader.pages[1]

    read_values = np.array([])
    for lines in page.extract_text().split("\n"):
        if lines.__contains__("Activity - Current period"):
            flag = True
        
        # Will need an else statement to catch if it does not find the information
        # Most likely will be on the third page and will need to change line 37 "page = reader.pages[1]"
        
        if flag == True:
            read_values = np.append(read_values,lines)

    parsed = read_values[1:2]
    for value in parsed: 
        col_headings = re.split(r'(?=[A-Z])', value)
    col_headings = [x for x in col_headings if x]

    parse = np.array(read_values[2:])
    parse = list(parse)

    while index < len(parse) - 1:
        if "DIV" in parse[index]:
            if index + 2 < len(parse):  
                combined_text = parse[index] + " " + parse[index+1] + " " + parse[index+2]
                # del parse[index+1]
                # del parse[index+1]  # Since list shifted, index+1 now refers to old index+2

            data["div"].append(combined_text)  
    
        elif "BUY" in parse[index]:
            if "$" in parse[index]: 
                data["buy"].append(parse[index])
            else: 
                if index + 2 < len(parse):
                    combined_text = parse[index] + " " + parse[index + 1] + " "+ parse[index + 2]
                    # del parse[index+1]
                    # del parse[index+1]
                    
                data["buy"].append(combined_text)   

        elif "CONT" in parse[index]:
            if "$" in parse[index]: 
                data["cont"].append(parse[index])
            else: 
                if index + 2 < len(parse):
                    combined_text = parse[index] + " " + parse[index + 1] + " "+ parse[index + 2]
                    # del parse[index+1]
                    # del parse[index+1]
                    
                data["cont"].append(combined_text) 
        
        elif "FPLINT" in parse[index]:
            if index + 2 < len(parse):
                combined_text = parse[index] 
                # del parse[index+1]

            data["lend"].append(combined_text)
        
        index += 1 

    for item in data["div"]:

        trans_type = "Dividend"
        fx_rate = 0
        shares = 0

        # Regular Expression with Capture Groups
        pattern = r'(\d{4}-\d{2}-\d{2})DIV\s(\w+)\s-\s(.+):\s(.+),\sreceived at (\d{4}-\d{2}-\d{2})\s\$(\d+\.\d+)\s\$(\d+\.\d+)\s\$(\d+\.\d+)'

        match = re.match(pattern, item)

        if match:
            date, ticker, company, desc, recv_date, amount1, amount2, amount3 = match.groups()
            stock_id = func.pull_stock_id(ticker, company)
            func.add_nine(stock_id,date, trans_type, recv_date, shares, fx_rate, amount1, amount2, amount3)
        else:
            print("No match found for:", item)  # Debugging

    for item in data["buy"]:

        trans_type = "Buy"

        # regex pattern
        pattern = r'(\d{4}-\d{2}-\d{2})BUY\s(\S+)\s-\s(.+?):\sBought\s(\d+\.\d+)\sshares\s\(executed\sat\s(\d{4}-\d{2}-\d{2})\)(?:,\sFX Rate:\s([\d.]+))?\s?\$(\d+(?:\.\d+)?)\s\$(\d+(?:\.\d+)?)\s\$(\d+(?:\.\d+)?)'

        match = re.match(pattern, item)

        if match:
            groups = match.groups()
            date, ticker, company, shares, recv_date, fx_rate, amount1, amount2, amount3 = groups
            stock_id = func.pull_stock_id(ticker, company)
            func.add_nine(stock_id,date, trans_type, recv_date, shares, fx_rate, amount1, amount2, amount3)
        else:
            print("No match found for:", item)  # Debugging

    for item in data["cont"]:

        trans_type = "Contribution"
        shares = 0
        
        pattern = r'(\d{4}-\d{2}-\d{2})(?:CONT Contribution\s\(executed at \d{4}-\d{2}-\d{2}\))\s\$(\d+\.\d+)\s\$(\d+\.\d+)\s\$(\d+\.\d+)'

        match = re.match(pattern, item)

        if match:
            groups = match.groups()
            date, amount1, amount2, amount3 = groups
            func.add_five(date, trans_type, amount1, amount2, amount3)
            # func.add_four(date, amount1, amount2, amount3) 
        else:
            print("No match found for:", item)  # Debugging


    for item in data["lend"]: 

        trans_type = "Lending"
        
        pattern = r'(\d{4}-\d{2}-\d{2})FPLINT\s.*?\$(\d+\.\d+)\s+\$(\d+\.\d+)\s+\$(\d+\.\d+)'

        match = re.match(pattern, item)

        if match: 
            groups = match.groups()
            date, amount1, amount2, amount3 = groups
            func.add_five(date, trans_type, amount1, amount2, amount3) # this is the working verion
            # func.add_four(date, amount1, amount2, amount3)            
        else: 
            print("No match found for:", item)  # Debugging
        return data


# Caling Function 
check_folders(folder_path)
check_folders(destination)

# Checking what files do not exist 
file_list = unread_files()
# read_file(file_list[12])

for files in file_list:
    read_file(files)
    move_file(files)
    















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
import logging
import db_func as func
import numpy as np 
from pypdf import PdfReader

# Setting up Logging Operations 
logger = logging.getLogger("pdf_Reader")
logger.setLevel(logging.DEBUG)

# File Handlers for Logging 
file_handler = logging.FileHandler("file_processing.log")
file_handler.setLevel(logging.DEBUG)

# Creating Formatter 
formatter = logging.Formatter(
    "%(levelname)s - %(name)s: %(message)s"
)

# Adding formatter and handler to logger
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Make this a dictionary later - use os lib to get file current location 
folder_path = r"C:\Projects\Python\Stocks\Data\Wealthsimple_Files"  
destination = r"C:\Projects\Python\Stocks\Data\Wealthsimple_Files\Scanned"


def page_search(reader):
    page_len = []
    search_text = "Activity - Current period"

    for i, page in enumerate(reader.pages):
        lines = page.extract_text().split("\n") if page.extract_text() else []
        if search_text in lines:
            page_len.append(i)
    return page_len

def extract_pages(arr):
    arr = np.array(arr)
    max = arr.max()
    min  = arr.min()
    return (max,min)

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

def single_page(reader, min): 
    logger.info("File only has data on a single page")
    flag = False
    page = reader.pages[int(min)]

    read_values = np.array([])

    for lines in page.extract_text().split("\n"):
        if lines.__contains__("Activity - Current period"):
            flag = True
        
        if flag == True:
            read_values = np.append(read_values,lines)
    return read_values

def multiple_pages(reader, min, max):
    logger.info("File only has data on multple pages")
    flag = False 
    read_values = np.array([])

    for i in range(min, max+ 1):
        page = reader.pages[i]
        # print(f'this is {i}')
        page_text = page.extract_text()

        if not page_text:
            continue  # skip if no extractable text

        for line in page_text.split("\n"):
            if "Activity - Current period" in line:
                flag = True

            if flag:
                read_values = np.append(read_values, line)

    # print(read_values)
    return read_values

    
# Extracts and reads the pdf files
def read_file(file_name):

    i = 0
    index = 0
    data = {
        "div": [],
        "buy": [],
        "cont": [],
        "lend": []
    }

    # Reading file
    reader = PdfReader(file_name)

    # Understanding page information
    pagelen = page_search(reader)
    max, min = extract_pages(pagelen)

    logger.info(f'File data is being extracted from pages {pagelen}')

    if min == max: 
        read_values = single_page(reader, min)
        # print(read_values)
    
    else:
        read_values = multiple_pages(reader, min, max)
        print("wellfuck")



    # # page_search(reader)
    # # page = reader.pages[1]

    # read_pages = page_search(reader)
    # max,min = extract_pages(read_pages)
    # print(max)
    # text = ""

    # print(f"Number of pages: {len(reader.pages)}")
    
    # # Accessing the first page
    # pagelen = page_search(reader)
    # max, min = extract_pages(pagelen)
    # print(f"\nthis is the min{min} and this is the max{max}")
    # page = reader.pages[int(min)]
    # print(page.extract_text())

    
    # for i in range(min, max):
    #     page = reader.pages[i]
    #     text = page.extract_text()
    #     print(f"\n--- Page {i + 1} ---\n{text}")
   
    
    # read_values = np.array([])
    
    # # Loop through the pages between min and max
    # for page in reader.pages[min:max]:
    #     text = page.extract_text() or ""
    #     for line in text.split("\n"):
    #         print(f"this is the {line}")
    #         if line.__contains__("Activity - Current period"):
    #             print("hello")
    #             flag = True

    #         if flag:
    #             read_values = np.append(read_values, line)

    # print(read_values)
    # for lines in page.extract_text().split("\n"):
    #     if lines.__contains__("Activity - Current period"):
    #         flag = True
        
        
    #     if flag == True:
    #         read_values = np.append(read_values,lines)




        # Extract text from the page and append it to 'text'
        # page_text = page.extract_text() or ""  # In case extract_text returns None
        # text += page_text + "\n"
        # print(f"This is the text: {text}")

    # read_values = np.array([])
    # for lines in page.extract_text().split("\n"):
    #     if lines.__contains__("Activity - Current period"):
    #         flag = True
        
        # Will need an else statement to catch if it does not find the information
        # Most likely will be on the third page and will need to change line 37 "page = reader.pages[1]"
        
        # if flag == True:
        #     read_values = np.append(read_values,lines)

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
            logger.debug(f" No Match found for: {item}")

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
            logger.debug(f" No Match found for: {item}")

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
            logger.debug(f" No Match found for: {item}")

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
            logger.debug(f" No Match found for: {item}")
        return data


# Caling Function 
check_folders(folder_path)
check_folders(destination)

# Checking what files do not exist 
file_list = unread_files()
# read_file(file_list[6])


for files in file_list:
    logger.info(f"Started reading file: {os.path.basename(files)}")
    read_file(files)
    move_file(files)
    















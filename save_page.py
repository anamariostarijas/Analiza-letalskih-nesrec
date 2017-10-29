import os
import re
import string
import requests
import csv
#pip install more-itertools
from itertools import chain

frontpage_basename = 'plane_crashes.html'
frontpage_url = 'https://en.wikipedia.org/wiki/List_of_accidents_and_incidents_involving_commercial_aircraft'
dirname ='C:\Analiza-letalskih-nesrec'
frontpage_fn = os.path.join(dirname, frontpage_basename)
csv_filename = 'plane_crashes.csv'


###############################################################
#saving url to file, reading a file
###############################################################

def download_url_to_string(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("failed to connect to url " + url)
        return
    return r.text
    
def save_string_to_file(text, directory, filename):
    '''Write "text" to the file "filename" located in directory "directory",
    creating "directory" if necessary. If "directory" is the empty string, use
    the current directory.'''
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding = 'utf8') as file_out:
        file_out.write(text)
    return 

def download_frontpage_to_file(plane_crash_url, directory, filename):
    url_text = download_url_to_string(plane_crash_url)
    file = save_string_to_file(url_text, directory, filename)

def read_file_to_string(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf8') as file_in:
        return file_in.read()

####################################################################################
# saving all urls to files, from which we extract wanted data
####################################################################################
    
def get_urls_from_frontpage(directory, filename):
    '''gets urls of specific plane crashes and puts them in list of dictionaries'''
    urls_in_page = []
    urls = re.compile(r'<b><a href="(?P<url>/wiki/.*?)"', re.DOTALL)
    num_of_matches = 0
    for match in urls.finditer(read_file_to_string(directory, filename)):
        data = match.groupdict()
        num_of_matches +=1
        urls_in_page.append(data)
    return urls_in_page
    #print(num_of_matches)
    
def urls():
    '''gets all urls of plane crashes from frontpage and makes a list of urls of these pages'''
    urls_of_crashes = get_urls_from_frontpage(dirname, frontpage_basename)
    all_urls = []
    for url in urls_of_crashes: 
        plane_crash_url = 'https://en.wikipedia.org{}'.format(url['url'])
        all_urls.append(plane_crash_url)
    return all_urls

def save_all_files():
    '''saves all urls to files'''
    all_urls = urls()
    for i in range(1, len(all_urls) + 1):
        filename = 'crash-{}.html'.format(i)   
        download_frontpage_to_file(all_urls[i], dirname, filename)
        i += 1
    return 
        
def search_block(plane_crash_file):
    '''takes needed block from file'''
    page_contents = read_file_to_string(dirname, plane_crash_file)
    rx = re.compile(r'<div id="siteSub" class="noprint">From Wikipedia, the free encyclopedia</div>'
                    r'.*?'
                    r'</table>',
                    re.DOTALL)
    block = rx.findall(page_contents)
    return block

def data_from_one_url(plane_crash_block):
    '''takes a string and extracts date, summary, operator of the plane, number of passengers, crew members, fatalities and survivors of
    one plane crash'''
    no_match = 0   
    rx = re.compile(r'style="padding-bottom:0.3em;">(?P<title>.*?)</caption>'
                    
                    r'.*?'
                    r'<td style="line-height:1.3em;">(?P<date>.*?)<'
                    r'.*?'
                    r'Summary</th>.*?<td style="line-height:1.3em;">(?P<summary>.*?)</td>'
                    r'\s*?'    
                    r'.*?'
                    r'Passengers</th>.*?">(?P<passengers>\d+).*?</td>'
                    r'.*?'
                    r'Crew</th>.*?<td style="line-height:1.3em;">(?P<crew>\d+).*?</td>'
                    r'.*?'
                    r'Fatalities</th>.*?<td style="line-height:1.3em;">.*?(?P<fatalities>\d+).*?</td>'
                    r'.*?'
                    r'Survivors</th>.*?<td style="line-height:1.3em;">(?P<survivors>\d+).*?</td>'
                    r'.*?'
                    r'Operator</th>(.*?)<a href="(.*?)" title="(?P<operator>.*?)">',
                    re.DOTALL)
    
    match = re.search(rx, plane_crash_block)
    if match:
        crash = match.groupdict()
        crash['passengers'] = int(crash['passengers'])
        crash['crew'] = int(crash['crew'])
        crash['fatalities'] = int(crash['fatalities'])
        crash['survivors'] = int(crash['survivors'])
        return crash
    else:
        print('no match found')
        
def block_from_file(filename):
    '''splits file into blocks and extracts data'''
    blocks = search_block(filename)
    ads = [data_from_one_url(block) for block in blocks]
    return ads

def all_data():
    all_urls = urls()
    all_data = []
    for i in range(1, len(all_urls) + 1):
        plane_crash_url = 'crash-{}.html'.format(i)
        data = block_from_file(plane_crash_url)
        all_data.append(data)
        i += 1
        #print(data)
    return list(chain.from_iterable(all_data))
        
########################################################################
# saving data to csv
########################################################################

def write_csv(directory, filename):
    '''Write a CSV file to directory/filename. The fieldnames must be a list of
    strings, the rows a list of dictionaries each mapping a fieldname to a
    cell-value.
    '''
    fieldnames = ['title','date','summary','operator','passengers',
                 'crew','fatalities','survivors']
    rows = all_data()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding = 'utf8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            if row:
                writer.writerow(row)
    return None


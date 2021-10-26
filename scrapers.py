'''
What does this file do?

Provided the following parameters
- `state_code`: 2 letter upper or lower case state code for which you want to extract data for
- `url`: the url or the file path of the pdf, image or html
- `type`: can be either 1 of the 3  pdf, image or html for the url that you provided above

this file will do the following

1. extracts parameters passed from command line or if not, takes defaults from `states.yaml` file
2. based on the provided `url` and the `type`
...

'''

#!/usr/bin/python3
import os
import re
import sys
import csv
import yaml
import json
import urllib
import logging
import camelot
import argparse
import html5lib
import requests
import datetime
import pdftotext
from bs4 import BeautifulSoup
# from deltaCalculator import DeltaCalculator


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cache')
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_inputs')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')
OUTPUT_FILE = "output.txt"

# read the config file first
with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

## ------------------------ Custom format line functions for specific states START
def ka_format_line(row):
  district = ""
  modifiedRow = []
  for value in row:
    if len(value) > 0:
      modifiedRow.append(value)

  if type(modifiedRow[0]) == int:
    district = " ".join(re.sub(' +', ' ', modifiedRow[0]).split(' ')[1:])
    modifiedRow.insert(0, 'a')
  else:
    district = re.sub('\*', '', modifiedRow[1])
  print(modifiedRow)

  return district + "," + modifiedRow[3] + "," + modifiedRow[5] + "," + modifiedRow[8] + "\n"

def hr_format_line(row):
  row[1] = re.sub('\*', '', row[1])
  if '[' in row[3]:
    row[3] = row[3].split('[')[0]
  if '[' in row[4]:
    row[4] = row[4].split('[')[0]
  if '[' in row[7]:
    row[7] = row[7].split('[')[0]
  if '[' in row[6]:
    row[6] = row[6].split('[')[0]

  line = row[1] + "," + row[3] + "," + row[4] + "," + str(int(row[6]) + int (row[7])) + "\n"
  return line

def pb_format_line(row):
  return row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "," + row[5] + "\n"

def kl_format_line(row):
  return row[0] + "," + row[1] + "," + row[2] + "\n"

def ap_format_line(row):
  line = row[1] + "," + row[3] + "," + row[5] + "," + row[6] + "\n"
  return line

def wb_format_line(row):
  row[2] = re.sub(',', '', re.sub('\+.*', '', row[2]))
  row[3] = re.sub(',', '', re.sub('\+.*', '', row[3]))
  row[4] = re.sub('\#', '', re.sub(',', '', re.sub('\+.*', '', row[4])))
  row[5] = re.sub(',', '', re.sub('\+.*', '', row[5]))
  line = row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "\n"
  return line

## ------------------------ Custom format line functions for specific states END

def run_for_ocr(opt):
  ## step 1 - run something to generate the poly.txt file
  print('Running ocr_vision.py file to generate poly.txt')
  os.system('python ocr_vision.py {} > bounds.txt'.format(opt['url']))

  ## step 2 - generate ocrconfig.meta file for that state
  print('Generating ocrconfig.meta file for {}'.format(opt['state_code']))
  os.system('bash generate_ocrconfig.sh {} {} {}'.format(
    opt['state_code'].lower(),
    "auto,auto",
    False
  ))
  ## step 3 - run googlevision.py file
  print('running googlevision.py using ocrconfig.meta file for {}'.format(opt['state_code']))
  os.system('python googlevision.py ocrconfig.meta {}'.format(opt['url']))

def read_pdf_from_url(opt):
  '''
  :param: opt

  Example `opt` dict sample

  ```
  {
    'name': 'Tamil Nadu',               - full name of the state
    'state_code': 'TN'                  - 2 letter state code in capital letters
    'url': 'http://path/to/file.pdf'    - this is the url to the PDF file
    'type': pdf                         - the type of file link you are passing
    'config': {
      'start_key': 'Districts'          - the word at which the table starts i.e. start reading page
      'end_key': 'Total'                - the word at which the table ends i.e. stop reading page
      'page': '2, 3'                    - pages for the PDF containing the table to be read
    }
  }
  ```


  '''

  # if len(opt['url']) > 0:
  # if url provided is a remote url like (http://)

  if urllib.parse.urlparse(opt['url']).scheme != '':
    #print("--> Requesting download from {} ".format(url))
    r = requests.get(opt['url'], allow_redirects=True, verify=False)
    open(opt['state_code'] + ".pdf", 'wb').write(r.content)
    opt['url'] = os.path.abspath(opt['state_code'] + '.pdf')

  opt['config']['page'] = str(opt['config']['page'])
  if len(opt['config']['page']) > 0:
    pid = ""
    if ',' in opt['config']['page']:
      startPage = int(opt['config']['page'].split(',')[0])
      endPage = int(opt['config']['page'].split(',')[1])
      for pages in range(startPage, endPage + 1, 1):
        print(pages)
        pid = pid + "," + str(pages) if len(pid) > 0 else str(pages)
        print(pid)
    else:
      pid = opt['config']['page']
  else:
    pid = input("Enter district page:")
  print("Running for {} pages".format(pid))

  tables = camelot.read_pdf(opt['url'], strip_text = '\n', pages = pid, split_text = True)
  # for index, table in enumerate(tables):

  stateOutputFile = open(opt['state_code'].lower() + '.csv', 'w')
  # csvWriter = csv.writer(stateOutputFile)
  # arrayToWrite = []

  startedReadingDistricts = False
  for index, table in enumerate(tables):
    tables[index].to_csv(opt['state_code'].lower() + str(index) + '.pdf.txt')
    with open(opt['state_code'].lower() + str(index) + '.pdf.txt', newline='') as stateCSVFile:
      rowReader = csv.reader(stateCSVFile, delimiter=',', quotechar='"')
      for row in rowReader:
        line = "|".join(row)
        line = re.sub("\|+", '|', line)
        if opt['config']['start_key'] in line:
          startedReadingDistricts = True
        if len(opt['config']['end_key']) > 0 and opt['config']['end_key'] in line:
          startedReadingDistricts = False
          continue
        if startedReadingDistricts == False:
          continue
        line = eval(opt['state_code'].lower() + "_format_line")(line.split('|'))
        if line == "\n":
          continue
        print(line, file = stateOutputFile, end = "")

  stateOutputFile.close()

## ------------------------ <STATE_CODE>_get_data functions START HERE
def ap_get_data(opt):
  print('fetching AP data', opt)
  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('table', {'class': 'table'}).find_all('tr')
  districts_data = []

  for row in table[1:]:
    # Ignoring 1st row containing table headers
    d = row.find_all('td')
    districts_data.append({
      'district_name': d[0].get_text(),
      'confirmed': int(d[1].get_text().strip()),
      'recovered': int(d[2].get_text().strip()),
      'deceased': int(d[3].get_text().strip())
    })

  return districts_data

def ar_get_data(opt):
  print('Fetching AR data', opt)

def as_get_data(opt):
  print('Fetching AS data', opt)

def br_get_data(opt):
  print('Fetching BR data', opt)

def ch_get_data(opt):
  print('Fetching CH data', opt)

def ct_get_data(opt):
  print('Fetching CT data', opt)

def dd_get_data(opt):
  print('Fetching DD data', opt)

def dh_get_data(opt):
  print('Fetching DH data', opt)

def dn_get_data(opt):
  print('Fetching DN data', opt)

def ga_get_data(opt):
  print('Fetching GA data', opt)

def gj_get_data(opt):
  print('fetching GJ data', opt)

  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('table', {'id': 'tbl'}).find_all('tr')
  districts_data = []

  for row in table[1:]:
    # Ignoring 1st row containing table headers
    d = row.find_all('td')
    districts_data.append({
      'district_name': d[0].get_text(),
      'confirmed': int(d[1].get_text().strip()),
      'recovered': int(d[3].get_text().strip()),
      'deceased': int(d[5].get_text().strip())
    })

  return districts_data

def hp_get_data(opt):
  print('Fetching HP data', opt)

def hr_get_data(opt):
  print('fetching HR data', opt)

  # always get for T - 1 day
  today = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
  opt['url'] = opt['url'] + today + '.' + opt['type']
  opt['config']['page'] = str(opt['config']['page'])

  read_pdf_from_url(opt)

  # once the csv file is genered, read it
  linesArray = []
  districtDictionary = {}
  districtArray = []
  with open("hr.csv", "r") as upFile:
    for line in upFile:
      linesArray = line.split(',')
      if len(linesArray) != 4:
        print("--> Issue with {}".format(linesArray))
        continue

      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[1])
      districtDictionary['recovered'] = int(linesArray[2])
      districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
      districtArray.append(districtDictionary)
  upFile.close()
  return districtArray

# TODO - Post request not running
def jh_get_data(opt):
  url = "https://covid19dashboard.jharkhand.gov.in/Bulletin/GetTestCaseData?date=2021-03-25"

  payload="date=" + (datetime.date.today() - datetime.timedelta(days = 0)).strftime("%Y-%m-%d")
  headers = {
    'Host': 'covid19dashboard.jharkhand.gov.in',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Content-Length': '15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cookie': 'ci_session=i6qt39o41i7gsopt23ipm083hla6994c'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  soup = BeautifulSoup(response.content, 'html.parser')
  districts = soup.find("table").find_all("tr")

  districtArray = []

  districtStart = False
  for district in districts:

    if "Bokaro" in district.get_text() and districtStart == False:
      districtStart = True

    if districtStart == False:
      continue

    data = district.find_all("td")

    if int(data[3].get_text()) != 0:
      print("{},Jharkhand,JH,{},Hospitalized".format(data[1].get_text(), data[3].get_text()))
    if int(data[4].get_text()) != 0:
      print("{},Jharkhand,JH,{},Recovered".format(data[1].get_text(), data[4].get_text()))
    if int(data[6].get_text()) != 0:
      print("{},Jharkhand,JH,{},Deceased".format(data[1].get_text(), data[6].get_text()))

def jk_get_data(opt):
  print('Fetching JK data', opt)

def ka_get_data(opt):
  print('fetching KA data', opt)
  opt['config']['page'] = str(opt['config']['page'])

  # read the pdf.txt files and generate
  linesArray = []
  districtDictionary = {}
  districts_data = []
  runDeceased = False
  startId = 0
  endId = 0
  fileId = opt['config']['file_id']

  if ',' in opt['config']['page']:
    startId = opt['config']['page'].split(',')[1]
    endId = opt['config']['page'].split(',')[2]
    opt['config']['page'] = opt['config']['page'].split(',')[0]
    runDeceased = True

  if len(opt['url']) != 0:
    urlArray = opt['url'].split('/')
    for index, parts in enumerate(urlArray):
      if parts == "file":
        if urlArray[index + 1] == "d":
          fileId = urlArray[index + 2]
          break
    opt['url'] += fileId
    print("--> Downloading using: {}".format(opt['url']))

  # read & generate pdf.txt file for the given url
  read_pdf_from_url(opt)

  try:
    with open("{}.csv".format(opt['state_code']), "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with {}".format(linesArray))
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districts_data.append(districtDictionary)

    upFile.close()

    if runDeceased == True:
      os.system("python3 kaautomation.py d " + str(startId) + " " + str(endId))

  except FileNotFoundError:
    print("ka.txt missing. Generate through pdf or ocr and rerun.")

  return districts_data

def kl_get_data(opt):
  # if opt['type'] == 'html':
  #   opt['url'] = 'https://dashboard.kerala.gov.in/index.php'
  #   print('Fetching KL data', opt)
  #   response = requests.request("GET", opt['url'])

  #   # sessionId = (response.headers['Set-Cookie']).split(';')[0].split('=')[1]

  #   cookies = {
  #     '_ga': 'GA1.3.594771251.1592531338',
  #     '_gid': 'GA1.3.674470591.1592531338',
  #     # 'PHPSESSID': sessionId,
  #     '_gat_gtag_UA_162482846_1': '1'
  #   }

  #   headers = {
  #     'Connection': 'keep-alive',
  #     'Accept': 'application/json, text/javascript, */*; q=0.01',
  #     'X-Requested-With': 'XMLHttpRequest',
  #     'Sec-Fetch-Site': 'same-origin',
  #     'Sec-Fetch-Mode': 'cors',
  #     'Sec-Fetch-Dest': 'empty',
  #     'Referer': 'https://dashboard.kerala.gov.in/index.php',
  #     'Accept-Language': 'en-US,en;q=0.9'
  #   }
  #   stateDashboard = requests.get(opt['url'], headers=headers).json()

  #   districtArray = []
  #   for districtDetails in stateDashboard['features']:
  #     districtDictionary = {}
  #     districtDictionary['districtName'] = districtDetails['properties']['District']
  #     districtDictionary['confirmed'] = districtDetails['properties']['covid_stat']
  #     districtDictionary['recovered'] = districtDetails['properties']['covid_statcured']
  #     districtDictionary['deceased'] = districtDetails['properties']['covid_statdeath']
  #     districtArray.append(districtDictionary)
  #   # deltaCalculator.getStateDataFromSite("Kerala", districtArray, option)
  #   return districtArray

  if opt['type'] == 'pdf':
    # TODO - run script to generate the csv

    linesArray = []
    districtDictionary = {}
    districts_data = []
    read_pdf_from_url(opt)
    with open("{}.csv".format(opt['state_code'].lower()), "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 3:
          print("--> Issue with {}".format(linesArray))
          continue

        print("{},Kerala,KL,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[1].strip()))
        print("{},Kerala,KL,{},Recovered".format(linesArray[0].strip().title(), linesArray[2].strip()))
        # TODO - append to districts_data
    upFile.close()
    return districts_data

def la_get_data(opt):
  print('fetching LA data', opt)

  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('table', id='tableCovidData2').find_all('tr')

  district_data = []
  district_dictionary = {}
  confirmed = table[9].find_all('td')[1]
  discharged = table[11].find_all('td')[1]
  confirmed_array = re.sub('\\r', '',
    re.sub(':', '',
      re.sub(' +', ' ',
        re.sub('\n', ' ',
          confirmed.get_text().strip()
        )
      )
    )
  ).split(' ')

  discharged_array = re.sub('\\r', '',
    re.sub(':', '',
      re.sub(' +', ' ',
        re.sub("\n", " ",
          discharged.get_text().strip()
        )
      )
    )
  ).split(' ')

  district_dictionary['district_name'] = confirmed_array[0]
  district_dictionary['confirmed'] = int(confirmed_array[1])
  district_dictionary['recovered'] = int(discharged_array[1])
  district_dictionary['deceased'] = -999
  district_data.append(district_dictionary)

  district_dictionary = {
    'district_name': confirmed_array[2],
    'confirmed': int(confirmed_array[3]),
    'recovered': int(discharged_array[3]),
    'deceased': -999
  }
  district_data.append(district_dictionary)

  return district_data

def mh_get_data(opt):
  print('fetching MH data', opt)
  stateDashboard = requests.request('GET', opt['url']).json()

  district_data = []
  for details in stateDashboard:
    district_data.append({
      'districtName': details['District'],
      'confirmed': details['Positive Cases'],
      'recovered': details['Recovered'],
      'deceased': details['Deceased']
    })

  return district_data

def ml_get_data(opt):
  print('Fetching ML data', opt)

  run_for_ocr(opt)

  districts_data = []
  with open(OUTPUT_FILE, "r") as mlFile:
    for line in mlFile:
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 8:
        print("--> Issue with {}".format(linesArray))
        continue

      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[5].strip())
      districtDictionary['recovered'] = int(linesArray[6].strip())
      districtDictionary['deceased'] = int(linesArray[7]) if len(re.sub('\n', '', linesArray[7])) != 0 else 0
      districts_data.append(districtDictionary)
  return districts_data

def mn_get_data(opt):
  print('Fetching MN data', opt)

def mp_get_data(opt):
  print('Fetching MP data', opt)

def mz_get_data(opt):
  print('Fetching MZ data', opt)

def nl_get_data(opt):
  print('Fetching NL data', opt)

def or_get_data(opt):
  temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'or.csv')
  cmd = ' | '.join([
    "curl -sk {}".format(opt['url']),
    "grep -i string | grep -v legend",
    "sed 's/var result = JSON.stringify(//' |sed 's/);//' | head -1 > {}".format(temp_file)
  ])
  os.system(cmd)

  district_data = []
  fetched_data = []
  with open(temp_file, 'r', encoding='utf-8') as meta_file:
    for line in meta_file:
      fetched_data = json.loads(line)

  for d in fetched_data:
    district_data.append({
      'district_name': d['vchDistrictName'],
      'confirmed': int(d['intConfirmed']),
      'recovered': int(d['intRecovered']),
      'deceased': int(d['intDeceased']) + int(d['intOthDeceased'])
    })

  # delete temp file after printed
  os.system('rm -f {}'.format(temp_file))
  return district_data

def pb_get_data(opt):
  print('Fetching PB data', opt)
  linesArray = []
  districtDictionary = {}
  districts_data = []
  read_pdf_from_url(opt)

  with open("{}.csv".format(opt['state_code'].lower()), "r") as upFile:
    for line in upFile:
      linesArray = line.split(',')
      if len(linesArray) != 5:
        print("--> Issue with {}".format(linesArray))
        continue
      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[1])
      districtDictionary['recovered'] = int(linesArray[3])
      districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
      districts_data.append(districtDictionary)

  upFile.close()
  return districts_data

def py_get_data(opt):
  print('fetching PY data', opt)
  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find_all('tbody')[1].find_all('tr')

  district_data = []
  for index, row in enumerate(table):
    data_points = row.find_all('td')

    district_dictionary = {
      'district_name': data_points[0].get_text().strip(),
      'confirmed': int(data_points[1].get_text().strip()),
      'recovered': int(data_points[2].get_text().strip()),
      'deceased': int(data_points[4].get_text().strip())
    }
    district_data.append(district_dictionary)

  return district_data

def rj_get_data(opt):
  print('Fetching RJ data', opt)

  # run all bash scripts, ocr_vision.py & googlevision.py
  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districtArray = []
  skipValues = False
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        if 'Other' in line:
          skipValues = True
          continue
        if skipValues == True:
          continue

        linesArray = line.split('|')[0].split(',')

        if len(linesArray) != 9:
          print("--> Issue with {}".format(linesArray))
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip().title()
        districtDictionary['confirmed'] = int(linesArray[3])
        districtDictionary['recovered'] = int(linesArray[7])
        districtDictionary['deceased'] = int(linesArray[5])
        districtArray.append(districtDictionary)

    upFile.close()
    # deltaCalculator.getStateDataFromSite("Rajasthan", districtArray, option)
  except FileNotFoundError:
    print("rj.txt missing. Generate through pdf or ocr and rerun.")

  return districtArray

def sk_get_data(opt):
  print('Fetching SK data', opt)

def tn_get_data(opt):
  print('Fetching TN data', opt)

  # ..........
  linesArray = []
  districtDictionary = {}
  district_data = []
  with open("tn.csv", "r") as upFile:
    for line in upFile:
      linesArray = line.split(',')
      if len(linesArray) != 4:
        print("--> Issue with {}".format(linesArray))
        continue
      linesArray[3] = linesArray[3].replace('$', '')
      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[1])
      districtDictionary['recovered'] = int(linesArray[2])
      districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
      district_data.append(districtDictionary)

  upFile.close()
  return district_data

def tg_get_data(opt):
  print('Fetching TG data', opt)

def tr_get_data(opt):
  print('fetching TR data', opt)
  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('tbody').find_all('tr')
  district_data = []
  for index, row in enumerate(table):
    data_points = row.find_all("td")
    district_dictionary = {
      'district_name': data_points[1].get_text().strip(),
      'confirmed': int(data_points[8].get_text().strip()),
      'recovered': int(data_points[10].get_text().strip()),
      'deceased': int(data_points[12].get_text().strip())
    }
    district_data.append(district_dictionary)

  return district_data

def up_get_data(opt):
  print('Fetching UP data', opt)

def ut_get_data(opt):
  print('Fetching UT data', opt)

def wb_get_data(opt):
  print('Fetching WB data', opt)

## ------------------------ <STATE_CODE>_get_data functions END HERE


def fetch_data(st_obj):
  '''
  for a given state object, fetch the details from url

  :state:  object as contained in automation.yaml
    {
      name: ...
      state_code: ...
      url: ...
    }
  '''
  fn_map = {
    'ap': ap_get_data,
    'ar': ar_get_data,
    'as': as_get_data,
    'br': br_get_data,
    'ch': ch_get_data,
    'ct': ct_get_data,
    'dd': dd_get_data,
    'dh': dh_get_data,
    'dn': dn_get_data,
    'ga': ga_get_data,
    'gj': gj_get_data,
    'hp': hp_get_data,
    'hr': hr_get_data,
    'jh': jh_get_data,
    'jk': jk_get_data,
    'ka': ka_get_data,
    'kl': kl_get_data,
    'la': la_get_data,
    'mh': mh_get_data,
    'ml': ml_get_data,
    'mn': mn_get_data,
    'mp': mp_get_data,
    'mz': mz_get_data,
    'nl': nl_get_data,
    'or': or_get_data,
    'pb': pb_get_data,
    'py': py_get_data,
    'rj': rj_get_data,
    'sk': sk_get_data,
    'tn': tn_get_data,
    'tg': tg_get_data,
    'tr': tr_get_data,
    'up': up_get_data,
    'ut': ut_get_data,
    'wb': wb_get_data
  }

  try:
    return fn_map[st_obj['state_code'].lower()](st_obj)
  except KeyError:
    print('no function definition in fn_map for state code {}'.format(st_obj['state_code']))


if __name__ == '__main__':
  '''
  Example to extract from html dashboard (the url will be taken from automation.yaml file by default)
    $python automation.py --state_code GJ

  Example to overwrite settings already provided in yaml file:
    $python automation.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
  '''
  parser = argparse.ArgumentParser()
  parser.add_argument('--state_code', type=str, nargs='?', default='all', help='provide 2 letter state code, defaults to all')
  parser.add_argument('--type', type=str, choices=['pdf', 'image', 'html'], help='type of url to be specified [pdf, ocr, html]')
  parser.add_argument('--url', type=str, help='url to the image or pdf to be parsed')

  args = parser.parse_args()
  state_code = args.state_code.lower()
  url = args.url
  url_type = args.type

  # execute for all states, if state_code not mentioned
  if state_code == 'all':
    for sc in states_all:
      if states_all[sc]['url']:
        print('running {}_get_data'.format(sc))
        fetch_data(states_all[sc])
  else:
    if url_type is not None and url is not None:
      # if there's a url & type provided as args, use that
      states_all[state_code].update({
        'url': url,
        'type': url_type
      })
    # always use default url & type from yaml file
    live_data = fetch_data(states_all[state_code])
    print(live_data)

  # TODO - get delta for states
  # delta = delta_calculator.get_state_data_from_site(
  #   states_all[state_code]['name'],
  #   live_data,
  #   states_all[state_code]['type']
  # )


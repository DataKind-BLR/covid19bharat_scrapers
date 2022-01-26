import os
import re
import json
import requests
import datetime
import pandas as pd

from bs4 import BeautifulSoup
from rich.pretty import pprint
from rich.console import Console
from read_ocr import run_for_ocr
from read_pdf import read_pdf_from_url

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs')
OUTPUT_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'output.txt')

def _get_mohfw_data(name):
  '''Fetch state-wise data from MOHFW website.
  
  Inputs:
    name: state name, eg: Ladakh

  Returns:
    dict: [{
      'districtName': '',
      'confirmed': 12345,
      ...
    }]
  '''
  MOHFW_URL = 'https://www.mohfw.gov.in/data/datanew.json'
  
  datum = (pd.read_json(MOHFW_URL)
             .set_index('state_name')
             .loc[name])

  return [{
    'districtName': name,
    'confirmed': datum['new_positive'],
    'recovered': datum['new_cured'],
    'deceased':  datum['new_death']
  }] 

## ------------------------ <STATE_CODE>_get_data functions START HERE
def ap_get_data(opt):
  print('Fetching AP data')
  pprint(opt)

  if opt['type'] == 'html':
    if opt['skip_output'] == False:
      response = requests.request('GET', opt['url'], verify=False)
      soup = BeautifulSoup(response.content, 'html.parser')
      table = soup.find('table', {'class': 'table'}).find_all('tr')
      districts_data = []

      for row in table[1:]:
        # Ignoring 1st row containing table headers
        d = row.find_all('td')
        districts_data.append({
          'districtName': d[0].get_text(),
          'confirmed': int(d[1].get_text().strip()),
          'recovered': int(d[2].get_text().strip()),
          'deceased': int(d[3].get_text().strip())
        })

  elif opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districts_data.append(districtDictionary)

    upFile.close()
    #return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    secondRunArray = []
    masterColumnList = ""
    masterColumnArray = []
    splitArray = []
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')
          if len(linesArray) != 6:
            print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
            print('--------------------------------------------------------------------------------')
            continue
          if linesArray[0].strip() == "Total":
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[2].strip())
          districtDictionary['recovered'] = int(linesArray[4].strip())
          districtDictionary['deceased'] = int(linesArray[5].strip())
          districts_data.append(districtDictionary)

      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")

  return districts_data

def an_get_data(opt):
  print('Fetching AN data')
  pprint(opt)
  pprint('You\'ve got to do this manually looking at the tweet/image')
  return []

def ar_get_data(opt):
  print('Fetching AR data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  districts_data = []
  additionalDistrictInfo = {}
  additionalDistrictInfo['districtName'] = 'Papum Pare'
  additionalDistrictInfo['confirmed'] = 0
  additionalDistrictInfo['recovered'] = 0
  additionalDistrictInfo['deceased'] = 0

  with open(OUTPUT_TXT, "r") as upFile:
    for line in upFile:
      if 'Total' in line:
        continue

      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 14:
        print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
        print('--------------------------------------------------------------------------------')
        continue

      # take total of `Papum Pare` & `Capital Complex` under a single district called `Papum Pare`
      # Anjaw , 4 , 21079 , 20891 , 19823 , 1068 , 0 , 0 , 0 , 0 , 0 , 0 , 1065, 3
      if linesArray[0].strip() == "Capital Complex" or linesArray[0].strip() == "Papum Pare":
        additionalDistrictInfo['confirmed'] += int(linesArray[5])
        additionalDistrictInfo['recovered'] += int(linesArray[12])
        additionalDistrictInfo['deceased'] += int(linesArray[13]) if len(re.sub('\n', '', linesArray[13])) != 0 else 0
        continue

      districtDictionary = {}
      districtName = linesArray[0].strip()
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[5])
      districtDictionary['recovered'] = int(linesArray[12])
      districtDictionary['deceased'] = int(linesArray[13]) if len(re.sub('\n', '', linesArray[13])) != 0 else 0
      districts_data.append(districtDictionary)

  upFile.close()

  # lastly, add the additional district calculated for `Papum Pare`
  districts_data.append(additionalDistrictInfo)

  return districts_data

def as_get_data(opt):
  print('Fetching AS data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districtArray = []
  splitArray = []
  districts_data = []
  print('\n*** Do Manual entry of Recovered and Deaths\nDistrictwise Hospitalized \n')
  try:
    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        splitArray = re.sub('\n', '', line.strip()).split('|')
        linesArray = splitArray[0].split(',')
        if int(linesArray[len(linesArray) - 1]) > 0:
          if linesArray[0].strip() == 'Kamrup Metro':
            print("Kamrup Metropolitan,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
          elif linesArray[0].strip() == 'Kamrup Rural':
            print("Kamrup,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
          elif linesArray[0].strip() == 'South Salmara':
            print("South Salmara Mankachar,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
          else:
            print("{},Assam,AS,{},Hospitalized".format(linesArray[0].strip(), linesArray[len(linesArray) - 1].strip()))

  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")
  print('\nRecovery & Deaths available at state level in Image-1')
  return districts_data

def br_get_data(opt):
  print('Fetching BR data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  try:
    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        #use this when backlog released
        #if len(linesArray) != 7: 
        if len(linesArray) != 5:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0]
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3])
        #when death backlog comes use
        #districtDictionary['deceased'] = int(linesArray[5])
        districts_data.append(districtDictionary)

    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")
  return districts_data

def ch_get_data(opt):
  print('Fetching CH data')
  pprint(opt)
  response = requests.request("GET", opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  divs = soup.find("div", {"class": "col-lg-8 col-md-9 form-group pt-10"}).find_all("div", {"class": "col-md-3"})

  districtDictionary = {}
  districts_data = []
  districtDictionary['districtName'] = 'Chandigarh'

  for index, row in enumerate(divs):

    if index > 2:
      continue

    dataPoints = row.find("div", {"class": "card-body"}).get_text()

    if index == 0:
      districtDictionary['confirmed'] = int(dataPoints)
    if index == 1:
      districtDictionary['recovered'] = int(dataPoints)
    if index == 2:
      districtDictionary['deceased'] = int(dataPoints)

  districts_data.append(districtDictionary)
  return districts_data

def ct_get_data(opt):
  print('Fetching CT data')
  pprint(opt)
  '''
  if opt['skip_output'] == False:
    run_for_ocr(opt)

  districts_data = []
  with open(OUTPUT_TXT, "r") as upFile:
    for line in upFile:
      linesArray = line.split('|')[0].split(',')
      availableColumns = line.split('|')[1].split(',')

      districtDictionary = {}
      districtDictionary['deceased'] = 0
      # confirmedFound = False
      # recoveredFound = False
      # deceasedFound = False
      # for ind, line in enumerate(linesArray):
      #   if ind == 0:
      #     districtDictionary['districtName'] = linesArray[ind].strip()
      #   elif ind == 3:
      #     districtDictionary['confirmed'] = int(linesArray[ind].strip())
      #     confirmedFound = True
      #   elif ind == 5:
      #     districtDictionary['recovered'] = int(linesArray[ind].strip())
      #     recoveredFound = True
      #   elif ind == 10:
      #     districtDictionary['deceased'] = int(linesArray[ind].strip())
      #     deceasedFound = True

      for index, data in enumerate(linesArray):
        if availableColumns[index].strip() == "2":
          districtDictionary['districtName'] = data.strip()
        if availableColumns[index].strip() == "4":
          districtDictionary['confirmed'] = int(data.strip())
          confirmedFound = True
        if availableColumns[index].strip() == "9":
          districtDictionary['recovered'] = int(data.strip())
          recoveredFound = True
        if availableColumns[index].strip() == "12":
          districtDictionary['deceased'] += int(data.strip())
          deceasedFound = True

      if recoveredFound == False or confirmedFound == False:
        print("--> Issue with {}".format(linesArray))
        continue
      districts_data.append(districtDictionary)

  upFile.close()
  return districts_data
  '''
  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districts_data.append(districtDictionary)

    upFile.close()
    #return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    secondRunArray = []
    masterColumnList = ""
    masterColumnArray = []
    splitArray = []
    #columns reduced to remove dD & D
    nColRef = 9
    print('\nDeaths today column is not scraped if empty. \n last two columns should be clipped for file submission\n')
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')
          if len(linesArray) != nColRef:
            print("--> Issue with Columns: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
            print('--------------------------------------------------------------------------------')
            continue
          if linesArray[0].strip() == "Total":
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[2].strip())
          districtDictionary['recovered'] = int(linesArray[7].strip())
          #districtDictionary['deceased'] = int(linesArray[10].strip())
          districtDictionary['deceased'] = int(linesArray[2].strip()) - (int(linesArray[7].strip()) + int(linesArray[8].strip()))
          districts_data.append(districtDictionary)

      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")

  return districts_data

# Daman & Diu is merged with Dadra & Nagar Haveli
def dd_get_data(opt):
  print('Fetching DD data')
  pprint(opt)
  pprint('You\'ve got to do this manually looking at the tweet/image')

def dh_get_data(opt):
  print('Fetching DH data')
  pprint(opt)
  pprint('You\'ve got to do this manually looking at the tweet/image')

def dn_get_data(opt):
  print('Fetching DN data')
  pprint(opt)

  return _get_mohfw_data(opt['name'])

  # pprint('You\'ve got to do this manually looking at the tweet/image')

def ga_get_data(opt):
  print('Fetching GA data')
  pprint(opt)

  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find_all("div", {"class": "vc_col-md-2"})

  districts_data = []
  for index, row in enumerate(table):
    print(row.get_text())

    districtDictionary = {}
    districts_data.append(districtDictionary)

  return districts_data

def gj_get_data(opt):
  print('fetching GJ data')
  pprint(opt)

  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('table', {'id': 'tbl'}).find_all('tr')
  districts_data = []

  for row in table[1:]:
    # Ignoring 1st row containing table headers
    d = row.find_all('td')
    districts_data.append({
      'districtName': d[0].get_text(),
      'confirmed': int(d[1].get_text().strip()),
      'recovered': int(d[3].get_text().strip()),
      'deceased': int(d[5].get_text().strip())
    })

  return districts_data

def hp_get_data(opt):
  print('Fetching HP data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  districtTableBeingRead = False
  print('\n')
  #whats up HP?
  #keep changing columns....
  #now it is 12 (02-01-2022)
  nColRef = 12

  try:
    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        line = re.sub('\*', '', line)
        linesArray = line.split('|')[0].split(',')
        availableColumns = line.split('|')[1].split(',')

        districtDictionary = {}
        confirmedFound = False
        recoveredFound = False
        deceasedFound = False

        if len(linesArray) != nColRef:
          print("--> Issue with Columns: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        # if reached the last item, break
        if linesArray[0].strip().title() == 'Total':
          break
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1].strip())
        
        #if columns are 11
        districtDictionary['recovered'] = int(linesArray[8].strip())
        districtDictionary['deceased'] = int(re.sub('\*', '', linesArray[10].strip()).strip())
        #districtDictionary['migrated'] = int(linesArray[11].strip())        
        #if columns are 9
        #districtDictionary['recovered'] = int(linesArray[6].strip())
        #districtDictionary['deceased'] = int(re.sub('\*', '', linesArray[7].strip()).strip())

        #districtDictionary['migrated'] = int(linesArray[10].strip())
        districts_data.append(districtDictionary)

    pprint('Migrated for HP is not calculated. Always check active and  do manual entry for Migrated')
    print('\n')
    upFile.close()
    return districts_data

  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")


def hr_get_data(opt):
  print('fetching HR data')
  pprint(opt)

  if not opt['url'].endswith('.pdf'):
    today = datetime.date.today().strftime("%d-%m-%Y")
    print(f'Downloading HR pdf file for {today}')
    opt['url'] = opt['url'] + today + '.' + opt['type']

  opt['config']['page'] = str(opt['config']['page'])

  if opt['skip_output'] == False:
    read_pdf_from_url(opt)

  # once the csv file is genered, read it
  linesArray = []
  districtDictionary = {}
  districts_data = []
  nColRef = 4

  csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
  with open(csv_file, "r") as upFile:
    for line in upFile:
      linesArray = line.split(',')
      if len(linesArray) != nColRef:
        print("--> Issue with Columns: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
        print('--------------------------------------------------------------------------------')
        continue

      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[1])
      districtDictionary['recovered'] = int(linesArray[2])
      districtDictionary['deceased'] = int(linesArray[3])
      districts_data.append(districtDictionary)
  upFile.close()
  return districts_data

def jh_get_data(opt):
  print('fetching JH data')
  pprint(opt)

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    nColRef = 8

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != nColRef:
          print("--> Issue with Columns: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
          print('--------------------------------------------------------------------------------')
          continue
          districtDictionary = {}
        if (linesArray[2].isdigit() and linesArray[3].isdigit() and linesArray[4].isdigit() \
            and linesArray[5].isdigit() and linesArray[6].isdigit() and (linesArray[7].replace('\n','')).isdigit()):
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[4]) + int(linesArray[5])
          districtDictionary['recovered'] = int(linesArray[2]) + int(linesArray[6])
          districtDictionary['deceased'] = int(linesArray[3]) + int(linesArray[7])
          districts_data.append(districtDictionary)
        else:
          print("--> Non-numeric issue: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
          print('--------------------------------------------------------------------------------')
          continue

    upFile.close()
    return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')
          availableColumns = line.split('|')[1].split(',')

          if len(linesArray) != 8:
            print("--> Confirm for {}".format(linesArray))
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[4]) + int(linesArray[5])
          districtDictionary['recovered'] = int(linesArray[2]) + int(linesArray[6])
          districtDictionary['deceased'] = int(linesArray[3]) + int(linesArray[7])

          districts_data.append(districtDictionary)
      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")
    return districts_data

def jk_get_data(opt):
  print('Fetching JK data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  print('\n')  

  try:
    with open(OUTPUT_TXT, "r") as upFile:
      isIgnoreFlagSet = False
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 11:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        try:
          if type(linesArray[0].strip()) == int:
            print("--> Check District Name for: {}".format(linesArray))
            continue
          if 'Division' in linesArray[0].strip():
            continue
          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[6])
          districtDictionary['recovered'] = int(linesArray[9])
          districtDictionary['deceased'] = int(linesArray[10])
          districts_data.append(districtDictionary)
        except ValueError:
          print("--> Please validate and calculate manually for: {}".format(linesArray))
          continue

    print('\n')
    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")
  return districts_data

def ka_get_data(opt):
  print('fetching KA data')
  pprint(opt)
  # TODO - have a check for whether a url has been provided, if so, don't download file
  # if not opt['url']:

  # read the pdf.txt files and generate
  #   if ',' in opt['config']['page']:
  #     startId = opt['config']['page'].split(',')[1]
  #     endId = opt['config']['page'].split(',')[2]
  #     opt['config']['page'] = opt['config']['page'].split(',')[0]
  #     runDeceased = True

  #   if len(opt['url']) != 0:
  #     urlArray = opt['url'].split('/')
  #     for index, parts in enumerate(urlArray):
  #       if parts == "file":
  #         if urlArray[index + 1] == "d":
  #           fileId = urlArray[index + 2]
  #           break
  #     opt['url'] += fileId
  #     print("--> Downloading using: {}".format(opt['url']))

  # read & generate .pdf.txt file for the given url
  if opt['type'] == 'image':
    pass
    # scan the image (_inputs/ka.jpeg)

  if opt['type'] == 'pdf':
    linesArray = []
    districtDictionary = {}
    districts_data = []
    runDeceased = False
    startId = 0
    endId = 0
    # fileId = opt['config']['file_id']
    opt['config']['page'] = str(opt['config']['page'])

    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    try:
      csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')
          if len(linesArray) != 4:
            print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
            print('--------------------------------------------------------------------------------')
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
          districts_data.append(districtDictionary)

      upFile.close()

      if runDeceased == True:
        os.system("python3 automation/kaautomation.py d " + str(startId) + " " + str(endId))

    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")

    return districts_data

def kl_get_data(opt):
  if opt['type'] == 'html':
    response = requests.request('GET', opt['url'])
    soup = BeautifulSoup(response.content, 'html.parser')
    #table = soup.find('table', {'id': 'wrapper2'}).find_all('tr')
    table = soup.find("table", {"class": "sortable"})#.find_all('tr')
    #table = soup.find_all('table')[3]
    print(table)
    districts_data = []

    for row in table[1:]:
      # Ignoring 1st row containing table headers
      d = row.find_all('td')
      districts_data.append({
        'districtName': d[0].get_text(),
        'confirmed': int(d[1].get_text().strip()),
        'recovered': int(d[3].get_text().strip()),
        'deceased': int(d[5].get_text().strip())
      })

    return districts_data

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

    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    print("\n***Caution Kerala scrap will always show deltas for that day.\n It is not compared to previous day data in our API. \nEnsure that you are scrapping correct file ;))\n")

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 3:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        if "District" not in linesArray:
          print("{},Kerala,KL,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[1].strip()))
          print("{},Kerala,KL,{},Recovered".format(linesArray[0].strip().title(), linesArray[2].strip()))
          # TODO - append to districts_data
    print('\n')
    #print("\n===>Scrapping Deaths reported\n")
    #os.system("python scrapers.py --state_code KLD --type pdf -u %s"%opt['url'])
    #print("\n===>Scrapping BACKLOG Deaths reported\n")
    #os.system("python scrapers.py --state_code KLDBL --type pdf -u %s"%opt['url'])
    upFile.close()
    #quit()
    return districts_data

def kld_get_data(opt):
  if opt['type'] == 'pdf':
    # TODO - run script to generate the csv

    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    print("\n")

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:

      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 3:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        if linesArray[0].strip() == "District":
          continue
        if "Cumulative" in linesArray[0].strip():
          break
        gender = "M" if linesArray[2].strip() == "Male" else "F"
        print("{},{},,{},Kerala,KL,1,Deceased".format(linesArray[1], gender, linesArray[0].strip().title()))

    print('\n---------------------------------------------------------------------\n')

    upFile.close()
    #quit()
    #return districts_data

def kldbl_get_data(opt):
  if opt['type'] == 'pdf':
    # TODO - run script to generate the csv
    linecnt=0

    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    print("---------------------------------------------------------------------\n")

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:

      for line in upFile:
        linecnt=linecnt+1
        linesArray = line.split(',')
        if len(linesArray) != 3:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        if linecnt !=1:
           if int(linesArray[1].strip()) != 0:
              print("{},Kerala,KL,{},Deceased,,cat_B (G.O.(Rt) No.2110/2021/H and FWD)".format(linesArray[0].strip().title(), linesArray[1].strip()))
           if int(linesArray[2].strip()) != 0:
              print("{},Kerala,KL,{},Deceased,,cat_C (G.O.(Rt) No.2219/2021/H and FWD)".format(linesArray[0].strip().title(), linesArray[2].strip()))
    print('\n---------------------------------------------------------------------\n')
    upFile.close()
    #quit()
    #return districts_data

def la_get_data(opt):
  print('fetching LA data')
  pprint(opt)

  return _get_mohfw_data(opt['name'])

  ## Code to pull from website: https://covid.ladakh.gov.in/#dataInsights which is no more updated as of: 30-10-2021 
  # response = requests.request('GET', opt['url'])
  # soup = BeautifulSoup(response.content, 'html.parser')
  # table = soup.find('table', id='tableCovidData2').find_all('tr')

  # district_data = []
  # district_dictionary = {}
  # confirmed = table[9].find_all('td')[1]
  # discharged = table[11].find_all('td')[1]
  # confirmed_array = re.sub('\\r', '',
  #   re.sub(':', '',
  #     re.sub(' +', ' ',
  #       re.sub('\n', ' ',
  #         confirmed.get_text().strip()
  #       )
  #     )
  #   )
  # ).split(' ')

  # discharged_array = re.sub('\\r', '',
  #   re.sub(':', '',
  #     re.sub(' +', ' ',
  #       re.sub("\n", " ",
  #         discharged.get_text().strip()
  #       )
  #     )
  #   )
  # ).split(' ')

  # district_dictionary['districtName'] = confirmed_array[0]
  # district_dictionary['confirmed'] = int(confirmed_array[1])
  # district_dictionary['recovered'] = int(discharged_array[1])
  # district_dictionary['deceased'] = -999
  # district_data.append(district_dictionary)

  # district_dictionary = {
  #   'districtName': confirmed_array[2],
  #   'confirmed': int(confirmed_array[3]),
  #   'recovered': int(discharged_array[3]),
  #   'deceased': -999
  # }
  # district_data.append(district_dictionary)

  # return district_data

def ld_get_data(opt):
  print('fetching LD data')
  pprint(opt)

  return _get_mohfw_data(opt['name'])

def mh_get_data(opt):
  print('fetching MH data')
  pprint(opt)
  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    districts_data = []
    print('\n')
    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 6:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1].strip())
        districtDictionary['recovered'] = int(linesArray[2].strip())
        districtDictionary['deceased'] = int(linesArray[3].strip())
        districtDictionary['migrated'] = int(linesArray[4].strip())
        districts_data.append(districtDictionary)
    return districts_data
    
    print('\n')
  elif opt['type'] == 'html':
    stateDashboard = requests.request('GET', opt['url']).json()

    district_data = []
    for details in stateDashboard:
      datems= details['Date'],
      district_data.append({
        'districtName': details['District'],
        'confirmed': details['Positive Cases'],
        'recovered': details['Recovered'],
        'deceased': details['Deceased']

      })
    datems = datems[0]
    datems=int(datems)
    datestamp=datetime.datetime.fromtimestamp(datems/1000)
    print("\nReported Date : ",datestamp,"\n")
    return district_data

def ml_get_data(opt):
  print('Fetching ML data')
  pprint(opt)

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    districts_data = []
    with open(OUTPUT_TXT, "r") as mlFile:
      for line in mlFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 8:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[5].strip())
        districtDictionary['recovered'] = int(linesArray[6].strip())
        districtDictionary['deceased'] = int(linesArray[7]) if len(re.sub('\n', '', linesArray[7])) != 0 else 0
        districts_data.append(districtDictionary)
    return districts_data

  elif opt['type'] == 'html':
    response = requests.request("GET", opt['url'])
    authKey = json.loads(response.text)['key']

    url = "https://mbdasankalp.in/api/elasticsearch/aggregation/or/db/merge?access_token=" + authKey

    payload = "{\"aggregation\":{\"XAxisHeaders\":[{\"TagId\":\"5dd151b22fc63e490ca55ad6\",\"Header\":false,\"dbId\":\"5f395a260deffa1bd752be4e\"}],\"IsXaxisParallel\":false,\"YAxisHeaders\":[{\"Operator\":\"COUNT_DISTINCT\",\"isHousehold\":true,\"Header\":false,\"dbId\":\"5f395a260deffa1bd752be4e\"}],\"IsYaxisParallel\":true,\"YAxisFormulae\":[{\"isHousehold\":false,\"Instance\":\"\",\"axisId\":\"9100b461-5d86-47f9-b11c-6d48f90f9cf9\",\"isFormulaAxis\":true,\"formulaId\":\"5f395d6f0deffa1bd752bee8\",\"dbIds\":[\"5f395a260deffa1bd752be4e\"]},{\"isHousehold\":false,\"Instance\":\"\",\"axisId\":\"5b94c49f-7c8e-4bdf-9c8b-e7af4e53e14d\",\"isFormulaAxis\":true,\"formulaId\":\"5f395dba0deffa1bd752bef2\",\"dbIds\":[\"5f395a260deffa1bd752be4e\"]},{\"isHousehold\":false,\"Instance\":\"\",\"axisId\":\"3a36866c-956d-48b2-a47c-1149a0334f29\",\"isFormulaAxis\":true,\"formulaId\":\"5f395dd80deffa1bd752bef5\",\"dbIds\":[\"5f395a260deffa1bd752be4e\"]},{\"isHousehold\":false,\"Instance\":\"\",\"axisId\":\"a714425e-e78f-4dd7-833a-636a3bb850ca\",\"isFormulaAxis\":true,\"formulaId\":\"5f395d9a0deffa1bd752beef\",\"dbIds\":[\"5f395a260deffa1bd752be4e\"]}]},\"dbId\":\"5f395a260deffa1bd752be4e\",\"tagFilters\":[],\"sorting\":{\"axis\":{\"id\":\"5f395d6f0deffa1bd752bee8\",\"axisId\":\"9100b461-5d86-47f9-b11c-6d48f90f9cf9\",\"operator\":\"rowcount\"},\"sort\":{\"orderBy\":\"count\",\"order\":\"desc\"},\"size\":9999,\"enabled\":true,\"histogram\":false,\"timeseries\":false},\"customBins\":[],\"tagStatus\":true,\"boxplot\":false,\"requestedDbs\":{\"5f395a260deffa1bd752be4e\":{}}}"
    headers = {
      'Origin': 'https://mbdasankalp.in',
      'Referer': 'https://mbdasankalp.in/render/chart/5f4a8e961dbba63b625ff002?c=f7f7f7&bc=121212&key=' + authKey,
      'Host': 'mbdasankalp.in',
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/plain, */*',
      'Content-Length': '1399'
    }

    response = requests.request("POST", url, headers=headers, data = payload)
    stateDashboard = json.loads(response.text.encode('utf8'))
    #pprint(stateDashboard)

    districts_data = []
    for data in stateDashboard[0]:
      districtDictionary = {}
      districtDictionary['districtName'] = data["name"]
      for value in data["value"]:
        try:
          if value["formulaId"] == "5f395d6f0deffa1bd752bee8":
            districtDictionary['confirmed'] = int(value["value"])
          if value["formulaId"] == "5f395dba0deffa1bd752bef2":
            districtDictionary['recovered'] = int(value["value"])
          if value["formulaId"] == "5f395dd80deffa1bd752bef5":
            districtDictionary['deceased'] = int(value["value"])
        except KeyError:
          continue
      districts_data.append(districtDictionary)
      
    #pprint(districts_data)
    return districts_data

def mn_get_data(opt):
  print('Fetching MN data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  linesArray = []
  districts_data = []
  #clip from Districts to daily deaths
  nColRef = 5

  with open(OUTPUT_TXT) as mnFile:
    for line in mnFile:
      districtDictionary = {}
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != nColRef:
        print("--> Issue with Columns: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
        print('--------------------------------------------------------------------------------')
        continue

      # districtDictionary['districtName'] = linesArray[0].strip()
      # districtDictionary['confirmed'] = int(re.sub('[^0-9]+', '', linesArray[2])) + int(re.sub('[^0-9]+', '', linesArray[6]))
      # districtDictionary['recovered'] = 0
      # districtDictionary['deceased'] = int(re.sub('[^0-9]+', '', linesArray[4])) + int(re.sub('[^0-9]+', '', linesArray[7]))
      # districts_data.append(districtDictionary)

      if (linesArray[2].strip()) != "0":
        print("{},Manipur,MN,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[2].strip()))
      if (linesArray[4].strip()) != "0":
        print("{},Manipur,MN,{},Deceased".format(linesArray[0].strip().title(), linesArray[4].strip()))

  print('DONT COPY & PASTE `Recovered` cases for this state')
  # return districts_data

def mp_get_data(opt):
  print('Fetching MP data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  nColRef = 8
  print('\n')
  
  try:
    with open(OUTPUT_TXT, "r") as upFile:
      isIgnoreFlagSet = False
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if 'Total' in line or isIgnoreFlagSet == True:
          isIgnoreFlagSet = True
          print("--> Ignoring {} ".format(line))
        if len(linesArray) != nColRef:
          print("--> Issue with Columns: nCol={} nColref=({}) : {}".format(len(linesArray), nColRef, linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        try:
          #if is_number(linesArray[0].strip()):
          #  print("--> Ignoring: {}".format(linesArray))
          #  continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[2])
          districtDictionary['recovered'] = int(linesArray[6])
          districtDictionary['deceased'] = int(linesArray[4])
          districts_data.append(districtDictionary)
        except ValueError:
          print("--> Ignoring: {}".format(linesArray))
          continue
    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")

  return districts_data

def mz_get_data(opt):
  print('Fetching MZ data')
  pprint(opt)

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  districts_data = []
  with open(OUTPUT_TXT) as mzFile:
    for line in mzFile:
      line = line.replace('Nil', '0')
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 5:
        print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
        print('--------------------------------------------------------------------------------')
        continue

      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[4]) #+ int(linesArray[2]) + int(linesArray[3])
      districtDictionary['recovered'] = int(linesArray[2])
      districtDictionary['deceased'] = int(linesArray[3]) #if len(re.sub('\n', '', linesArray[3])) != 0 else 0
      districts_data.append(districtDictionary)

    mzFile.close()
  return districts_data

def nl_get_data(opt):
  print('Fetching NL data')
  pprint(opt)
  districts_data = []

  if opt['skip_output'] == False:
    run_for_ocr(opt)

  try:
    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 13:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[12])
        districtDictionary['recovered'] = int(linesArray[7])
        districtDictionary['migrated'] = int(linesArray[11])
        #Nagaland has detahs due to other causes as additional column
        districtDictionary['deceased'] = int(linesArray[8]) + int(linesArray[9]) 
        districts_data.append(districtDictionary)

    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")
  return districts_data

def or_get_data(opt):
  temp_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
  # temp_file = "./_cache/{}.csv".format(opt['state_code'].lower())
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
      'districtName': d['vchDistrictName'],
      'confirmed': int(d['intConfirmed']),
      'recovered': int(d['intRecovered']),
      'deceased': int(d['intDeceased']) + int(d['intOthDeceased'])
    })
  return district_data

def pb_get_data(opt):
  print('Fetching PB data')
  pprint(opt)

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 5:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[3])
        districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districts_data.append(districtDictionary)

    upFile.close()
    return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    secondRunArray = []
    masterColumnList = ""
    masterColumnArray = []
    splitArray = []
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')
          if len(linesArray) != 5:
            print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
            print('--------------------------------------------------------------------------------')
            continue
          if linesArray[0].strip() == "Total":
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[3])
          districtDictionary['deceased'] = int(linesArray[4])
          districts_data.append(districtDictionary)

      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")
    return districts_data

def py_get_data(opt):
  print('fetching PY data')
  pprint(opt)

  return _get_mohfw_data(opt['name'])

  # Code to parse data from website: that stopped updating as of:
  # response = requests.request('GET', opt['url'])
  # soup = BeautifulSoup(response.content, 'html.parser')
  # table = soup.find_all('tbody')[1].find_all('tr')

  # district_data = []
  # for index, row in enumerate(table):
  #   data_points = row.find_all('td')

  #   district_dictionary = {
  #     'districtName': data_points[0].get_text().strip(),
  #     'confirmed': int(data_points[1].get_text().strip()),
  #     'recovered': int(data_points[2].get_text().strip()),
  #     'deceased': int(data_points[4].get_text().strip())
  #   }
  #   district_data.append(district_dictionary)

  # return district_data

def rj_get_data(opt):
  print('Fetching RJ data')
  pprint(opt)

  linesArray = []
  districtDictionary = {}
  district_data = []

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    skipValues = False
    edge_case = False
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          if 'Other' in line:
            skipValues = True
            continue
          if skipValues == True:
            continue

          linesArray = line.split('|')[0].split(',')

          if len(linesArray) != 9:
            print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
            print('--------------------------------------------------------------------------------')
            continue

          districtDictionary = {}

          if 'Other' in linesArray[0].strip().title():
            print('Ignoring Other States/Countries',linesArray[0].strip())
            continue

          if linesArray[0].strip().title() != 'Ganganagar':
            districtDictionary['districtName'] = linesArray[0].strip().title()
            edge_case = False
          else:
            edge_case = True

          if edge_case:
            # only for Ganaganagar
            cf = re.sub(r'[a-z]+', '', linesArray[4])
            dt = re.sub(r'\)', '', linesArray[6])
            rc = re.sub(r'[a-z]+', '', linesArray[7])
            districtDictionary['confirmed'] = int(cf.strip())
            districtDictionary['recovered'] = int(rc.strip())
            districtDictionary['deceased'] = int(dt.strip())
          else:
            rc = re.sub(r'[a-z]+', '', linesArray[7])
            districtDictionary['confirmed'] = int(linesArray[3].strip())
            districtDictionary['recovered'] = int(linesArray[7].strip())
            districtDictionary['deceased'] = int(linesArray[5].strip())

          district_data.append(districtDictionary)

      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 8:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        if 'Other' in linesArray[0].strip().title():
          print('Ignoring Other States/Countries',linesArray[0].strip())
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip().title()
        districtDictionary['confirmed'] = int(linesArray[2])
        districtDictionary['recovered'] = int(linesArray[6])
        districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
        district_data.append(districtDictionary)
    upFile.close()

  return district_data

def sk_get_data(opt):
  print('Fetching SK data')
  pprint(opt)

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 8:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        if 'Other' in linesArray[0].strip().title():
          print('Ignoring Other States/Countries',linesArray[0].strip())
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip().title()
        districtDictionary['confirmed'] = int(linesArray[2])
        districtDictionary['recovered'] = int(linesArray[6])
        districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
        district_data.append(districtDictionary)
    upFile.close()

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    district_data = []
    with open(OUTPUT_TXT, "r") as mlFile:
      for line in mlFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 8:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[5].strip())
        districtDictionary['recovered'] = int(linesArray[6].strip())
        districtDictionary['deceased'] = int(linesArray[7]) if len(re.sub('\n', '', linesArray[7])) != 0 else 0
        district_data.append(districtDictionary)
  return district_data

def tn_get_data(opt):
  print('Fetching TN data')
  pprint(opt)

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)
    
    linesArray = []
    districtDictionary = {}
    district_data = []

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:

      airportConfirmedCount =0
      airportRecoveredCount =0
      airportDeceasedCount =0
      airportRun =1

      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 5:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        linesArray[4] = linesArray[4].replace('$', '')

        #check for airport and railway
        if 'Airport' in line:
          airportConfirmedCount += int(linesArray[1])
          airportRecoveredCount += int(linesArray[2])
          airportDeceasedCount += int(linesArray[4])
          if airportRun == 1:
            airportRun += 1
            continue
          else:
            #print("{}, {}, {}, {}\n".format('Airport Quarantine', airportConfirmedCount, airportRecoveredCount, airportDeceasedCount), file = tnOutputFile)
            linesArray[1]=airportConfirmedCount
            linesArray[2]=airportRecoveredCount
            linesArray[4]=airportDeceasedCount
            districtDictionary = {}
            districtDictionary['districtName'] = 'Airport Quarantine'
            districtDictionary['confirmed'] = int(linesArray[1])
            districtDictionary['recovered'] = int(linesArray[2])
            districtDictionary['deceased'] = int(linesArray[4]) #if len(re.sub('\n', '', linesArray[4])) != 0 else 0
            district_data.append(districtDictionary)
            continue
        if 'Railway' in line:
          #print("{}, {}, {}, {}".format('Railway Quarantine', linesArray[1], linesArray[2], linesArray[4]), file = tnOutputFile)
          districtDictionary = {}
          districtDictionary['districtName'] = 'Railway Quarantine'
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[4]) #if len(re.sub('\n', '', linesArray[4])) != 0 else 0
          district_data.append(districtDictionary)
          continue


        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
        district_data.append(districtDictionary)

    upFile.close()
    return district_data

def tg_get_data(opt):
  print('Fetching TG data')
  pprint(opt)

  district_data = []
  if opt['skip_output'] == False:
    run_for_ocr(opt)
  print('\n')
  linesArray = []
  districtDictionary = {}

  with open(OUTPUT_TXT, "r") as upFile:
    for line in upFile:
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 2:
        print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
        print('--------------------------------------------------------------------------------')
        continue
      if linesArray[0].strip().capitalize() == "Ghmc":
        linesArray[0] = "Hyderabad"

      districtDictionary['districtName'] = linesArray[0].strip().title()
      districtDictionary['confirmed'] = int(linesArray[1].strip())
      districtDictionary['recovered'] = 0
      districtDictionary['deceased'] = 0
      district_data.append(districtDictionary)
      if linesArray[1].strip() != '0':
        print("{},Telangana,TG,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[1].strip()))
      
  print('\n')
  upFile.close()
  #quit()
  # return district_data

def tr_get_data(opt):
  print('fetching TR data')
  pprint(opt)
  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('tbody').find_all('tr')
  district_data = []
  for index, row in enumerate(table):
    data_points = row.find_all("td")
    district_dictionary = {
      'districtName': data_points[1].get_text().strip(),
      'confirmed': int(data_points[8].get_text().strip()),
      'recovered': int(data_points[10].get_text().strip()),
      'deceased': int(data_points[12].get_text().strip())
    }
    district_data.append(district_dictionary)

  return district_data

def up_get_data(opt):
  print('Fetching UP data')
  pprint(opt)

  if opt['skip_output'] == False:
    read_pdf_from_url(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  ignoreLines = False
  try:
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        if ignoreLines == True:
          continue

        if 'Total' in line:
          ignoreLines = True
          continue

        linesArray = line.split(',')
        if len(linesArray) != 7:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[3]) + int(linesArray[5]) + int(linesArray[6])
        districtDictionary['recovered'] = int(linesArray[3])
        districtDictionary['deceased'] = int(linesArray[5])
        # districtDictionary['migrated'] = int(re.sub('\n', '', linesArray[5].strip()))
        districts_data.append(districtDictionary)

    upFile.close()
  except FileNotFoundError:
    print("_outputs/output.txt missing. Generate through pdf or ocr and rerun.")
  return districts_data

def ut_get_data(opt):
  print('Fetching UT data')
  pprint(opt)

  linesArray = []
  districts_data = []
  splitArray = []

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    ignoreLines = False
    try:
      csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
      with open(csv_file, "r") as upFile:
        for line in upFile:
          if ignoreLines == True:
            continue

          if 'Total' in line:
            ignoreLines = True
            continue

          linesArray = line.split(',')
          if len(linesArray) != 6:
            print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
            print('--------------------------------------------------------------------------------')
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(re.sub('[^A-Za-z0-9]+', '', linesArray[1]))
          districtDictionary['recovered'] = int(re.sub('[^A-Za-z0-9]+', '', linesArray[2]))
          districtDictionary['deceased'] = int(re.sub('[^A-Za-z0-9]+', '', linesArray[4]))
          districtDictionary['migrated'] = int(re.sub('\n', '', linesArray[5].strip()))
          districts_data.append(districtDictionary)

      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")
    return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        splitArray = re.sub('\n', '', line.strip()).split('|')
        linesArray = splitArray[0].split(',')

        if len(linesArray) != 6:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip().title()
        districtDictionary['confirmed'] = int(linesArray[1].strip())
        districtDictionary['recovered'] = int(linesArray[2].strip())
        districtDictionary['deceased'] = int(linesArray[4].strip())
        districtDictionary['migrated'] = int(linesArray[5].strip())
        districts_data.append(districtDictionary)

    return districts_data

def wb_get_data(opt):
  print('Fetching WB data')
  pprint(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []

  if opt['skip_output'] == False:
    read_pdf_from_url(opt)

  try:
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districts_data.append(districtDictionary)

    upFile.close()
  except FileNotFoundError:
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    print(f"{csv_file} missing. Generate through pdf or ocr and rerun.")
  return districts_data

## ------------------------ <STATE_CODE>_get_data functions END HERE

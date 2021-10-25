#!/usr/bin/python3
import os
import re
import sys
import csv
import yaml
import json
import logging
import camelot
import argparse
import html5lib
import requests
import datetime
import pdftotext

from bs4 import BeautifulSoup
# from deltaCalculator import DeltaCalculator

# read the config file
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml'), 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

def hr_get_data(opt):
  print('fetching HR data', opt)

  # always get for T - 1 day
  today = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
  opt['url'] = opt['url'] + today + '.' + opt['type']
  opt['config']['page'] = str(opt['config']['page'])

  # util function for HR only
  def HRFormatLine(row):
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

  ## call the readFileFromURLV2 to generate the CSV file here...
  tables = camelot.read_pdf(opt['url'],
    strip_text = '\n',
    pages = opt['config']['page'],
    split_text = True
  )

  # create an empty csv file first
  stateOutputFile = open(opt['state_code'].lower() + '.csv', 'w')
  startedReadingDistricts = False

  for index, table in enumerate(tables):
    # create .pdf.txt file for every page
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

        line = eval(opt['state_code'] + "FormatLine")(line.split('|'))
        if line == "\n":
          continue
        print(line, file = stateOutputFile, end = "")
    stateOutputFile.close()

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

# TODO - can't read POST request
def jh_get_data(opt):
  today = (datetime.date.today() - datetime.timedelta(days=0)).strftime("%Y-%m-%d")
  # complete url with the today's date
  opt['url'] += today

  headers = {
    'Host': 'covid19dashboard.jharkhand.gov.in',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Content-Length': '15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cookie': 'ci_session=i6qt39o41i7gsopt23ipm083hla6994c'
  }

  # TODO - request fails here....
  response = requests.post(opt['url'], headers=headers, data=today)
  soup = BeautifulSoup(response.content, 'html.parser')
  districts = soup.find('table').find_all('tr')

  district_start = False
  for district in districts:

    if "Bokaro" in district.get_text() and district_start is False:
      district_start = True

    if district_start is False:
      continue

    data = district.find_all("td")

    if int(data[3].get_text()) != 0:
      print(f"{data[1].get_text()},Jharkhand,JH,{data[3].get_text()},Hospitalized")
    if int(data[4].get_text()) != 0:
      print(f"{data[1].get_text()},Jharkhand,JH,{data[4].get_text()},Recovered")
    if int(data[6].get_text()) != 0:
      print(f"{data[1].get_text()},Jharkhand,JH,{data[6].get_text()},Deceased")

def or_get_data(opt):
  temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orsite.csv')
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

def ga_get_data(opt):
  print('fetching GA data', opt)

def rj_get_data(opt):
  print('fetching RJ data', opt)

def nl_get_data(opt):
  print('fetching NL data', opt)

def mz_get_data(opt):
  print('fetching MZ data', opt)

def as_get_data(opt):
  print('fetching AS data', opt)

def ch_get_data(opt):
  print('fetching CH data', opt)

def kl_get_data(opt):
  print('fetching KL data', opt)
  # if opt['type'] == 'pdf':
    # call pdf scanner, get page number

def ml_get_data(opt):
  print('fetching ML data', opt)

def ka_get_data(opt):
  print('fetching KA data', opt)
  opt['config']['page'] = str(opt['config']['page'])

  def read_pdf_from_url(opt):

    def KAFormatLine(row):
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

    if len(opt['url']) > 0:
      url = opt['url']
    if len(url) > 0:
      #print("--> Requesting download from {} ".format(url))
      r = requests.get(url, allow_redirects=True, verify=False)
      open(opt['state_code'] + ".pdf", 'wb').write(r.content)
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
    tables = camelot.read_pdf(opt['state_code'] + ".pdf", strip_text = '\n', pages = pid, split_text = True)
    # for index, table in enumerate(tables):

    stateOutputFile = open(opt['state_code'].lower() + '.csv', 'w')
    # csvWriter = csv.writer(stateOutputFile)
    # arrayToWrite = []

    startedReadingDistricts = False
    for index, table in enumerate(tables):
      tables[index].to_csv(opt['state_code'] + str(index) + '.pdf.txt')
      with open(opt['state_code'] + str(index) + '.pdf.txt', newline='') as stateCSVFile:
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

          line = eval(opt['state_code'] + "FormatLine")(line.split('|'))
          if line == "\n":
            continue
          print(line, file = stateOutputFile, end = "")

    stateOutputFile.close()

  # read the pdf.txt files and generate
  linesArray = []
  districtDictionary = {}
  districtArray = []
  runDeceased = False
  startId = 0
  endId = 0
  fileId = '1CaKq55BuKucINTV8C-IhUtck5_VO2hdg'

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
        districtArray.append(districtDictionary)

    upFile.close()

    if runDeceased == True:
      os.system("python3 kaautomation.py d " + str(startId) + " " + str(endId))

  except FileNotFoundError:
    print("ka.txt missing. Generate through pdf or ocr and rerun.")

  return districtArray

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
    'ga': ga_get_data,
    'or': or_get_data,
    'rj': rj_get_data,
    'mh': mh_get_data,
    'gj': gj_get_data,
    'nl': nl_get_data,
    'mz': mz_get_data,
    'as': as_get_data,
    'tr': tr_get_data,
    'py': py_get_data,
    'ch': ch_get_data,
    'kl': kl_get_data,
    'la': la_get_data,
    'ml': ml_get_data,
    'jh': jh_get_data,
    'hr': hr_get_data,
    'ka': ka_get_data
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
  parser.add_argument('--url', type=str, help='url to the ocr image or pdf to be parsed')
  parser.add_argument('--type', type=str, choices=['pdf', 'ocr', 'html'], help='type of url to be specified [pdf, ocr, html]')

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
    if url is not None or url_type is not None:
      # if there's a url & type provided as args, use that
      states_all[state_code].update({
        'type': url_type,
        'url': url
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


import re
import json
import requests
import datetime

from bs4 import BeautifulSoup
from rich.pretty import pprint

from read_ocr import run_for_ocr
from read_pdf import read_pdf_from_url

OUTPUT_FILE = "output.txt"

## ------------------------ <STATE_CODE>_get_data functions START HERE
def ap_get_data(opt):
  print('Fetching AP data')
  pprint(opt)
  response = requests.request('GET', opt['url'])
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

  return districts_data

def an_get_data(opt):
  print('Fetching AN data')
  pprint(opt)
  pprint('You\'ve got to do this manually looking at the tweet/image')

def ar_get_data(opt):
  print('Fetching AR data')
  pprint(opt)

  run_for_ocr(opt)

  districts_data = []
  additionalDistrictInfo = {}
  additionalDistrictInfo['districtName'] = 'Papum Pare'
  additionalDistrictInfo['confirmed'] = 0
  additionalDistrictInfo['recovered'] = 0
  additionalDistrictInfo['deceased'] = 0

  with open(OUTPUT_FILE, "r") as upFile:
    for line in upFile:
      if 'Total' in line:
        continue

      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 14:
        print("--> Issue with {}".format(linesArray))
        continue

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
  districts_data.append(additionalDistrictInfo)

  return districts_data

def as_get_data(opt):
  print('Fetching AS data')
  pprint(opt)

  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districtArray = []
  splitArray = []
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        splitArray = re.sub('\n', '', line.strip()).split('|')
        linesArray = splitArray[0].split(',')
        if int(linesArray[len(linesArray) - 1]) > 0:
          print("{},Assam,AS,{},Hospitalized".format(linesArray[0].strip(), linesArray[len(linesArray) - 1].strip()))

  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")

def br_get_data(opt):
  print('Fetching BR data')
  pprint(opt)

  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 5:
          print("--> Issue with {}".format(linesArray))
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0]
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3])
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

  run_for_ocr(opt)

  districts_data = []
  with open(OUTPUT_FILE, "r") as upFile:
    for line in upFile:
      linesArray = line.split('|')[0].split(',')
      availableColumns = line.split('|')[1].split(',')

      districtDictionary = {}
      districtDictionary['deceased'] = 0
      confirmedFound = False
      recoveredFound = False
      deceasedFound = False
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
        print(linesArray[index])
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
  pprint('You\'ve got to do this manually looking at the tweet/image')

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

  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  districtTableBeingRead = False
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        line = re.sub('\*', '', line)
        linesArray = line.split('|')[0].split(',')
        availableColumns = line.split('|')[1].split(',')

        districtDictionary = {}
        confirmedFound = False
        recoveredFound = False
        deceasedFound = False

        if len(linesArray) != 11:
          print("--> Issue with {}".format(linesArray))
          print("try cropping the image to only show the case details part of the image")
          continue

        # if reached the last item, break
        if linesArray[0].strip().title() == 'Una':
          break
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1].strip())
        districtDictionary['recovered'] = int(linesArray[8].strip())
        districtDictionary['deceased'] = int(re.sub('\*', '', linesArray[9].strip()).strip())
        #districtDictionary['migrated'] = int(linesArray[10].strip())
        districts_data.append(districtDictionary)

    upFile.close()
    return districts_data

  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")

def hr_get_data(opt):
  print('fetching HR data')
  pprint(opt)

  if not opt['url'].endswith('.pdf'):
    # always get for T - 1 day
    today = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    opt['url'] = opt['url'] + today + '.' + opt['type']

  opt['config']['page'] = str(opt['config']['page'])

  read_pdf_from_url(opt)

  # once the csv file is genered, read it
  linesArray = []
  districtDictionary = {}
  districts_data = []
  with open('{}.csv'.format(opt['state_code'].lower()), "r") as upFile:
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
  return districts_data

def jh_get_data(opt):

  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        availableColumns = line.split('|')[1].split(',')

        if len(linesArray) != 8:
          pass
          # print("--> Confirm for {}".format(linesArray))
          # continue

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

  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      isIgnoreFlagSet = False
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 11:
          print("--> Please validate and calculate manually for: {}".format(linesArray))
          continue
        districtDictionary = {}
        try:
          if type(linesArray[0].strip()) == int:
            print("--> Please validate and calculate manually for: {}".format(linesArray))
            continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[6])
          districtDictionary['recovered'] = int(linesArray[9])
          districtDictionary['deceased'] = int(linesArray[10])
          districts_data.append(districtDictionary)
        except ValueError:
          print("--> Please validate and calculate manually for: {}".format(linesArray))
          continue
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
        os.system("python3 automation/kaautomation.py d " + str(startId) + " " + str(endId))

    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")

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
  print('fetching LA data')
  pprint(opt)

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

  district_dictionary['districtName'] = confirmed_array[0]
  district_dictionary['confirmed'] = int(confirmed_array[1])
  district_dictionary['recovered'] = int(discharged_array[1])
  district_dictionary['deceased'] = -999
  district_data.append(district_dictionary)

  district_dictionary = {
    'districtName': confirmed_array[2],
    'confirmed': int(confirmed_array[3]),
    'recovered': int(discharged_array[3]),
    'deceased': -999
  }
  district_data.append(district_dictionary)

  return district_data

def mh_get_data(opt):
  print('fetching MH data')
  pprint(opt)
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
  print('Fetching ML data')
  pprint(opt)

  if opt['type'] == 'image':
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
    # deltaCalculator.getStateDataFromSite("Meghalaya", districts_data, option)
    return districts_data

    # districts_data = []
    # for districtDetails in stateDashboard['features']:
    #   districtDictionary = {}
    #   districtDictionary['districtName'] = districtDetails['attributes']['Name']
    #   districtDictionary['confirmed'] = districtDetails['attributes']['Positive']
    #   districtDictionary['recovered'] = districtDetails['attributes']['Recovered']
    #   districtDictionary['deceased'] = districtDetails['attributes']['Deceasesd']
    #   districts_data.append(districtDictionary)

def mn_get_data(opt):
  print('Fetching MN data')
  pprint(opt)

  run_for_ocr(opt)

  districts_data = []
  with open(OUTPUT_FILE) as mnFile:
    for line in mnFile:
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 8:
        print("--> Issue with {}".format(linesArray))
        continue

      if (linesArray[2].strip()) != "0":
        print("{},Manipur,MN,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[2].strip()))
      if (linesArray[4].strip()) != "0":
        print("{},Manipur,MN,{},Deceased".format(linesArray[0].strip().title(), linesArray[4].strip()))

  mnFile.close()

def mp_get_data(opt):
  print('Fetching MP data')
  pprint(opt)

  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      isIgnoreFlagSet = False
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if 'Total' in line or isIgnoreFlagSet == True:
          isIgnoreFlagSet = True
          print("--> Ignoring {} ".format(line))
        if len(linesArray) != 8:
          print("--> Ignoring due to invalid length: {}".format(linesArray))
          continue
        districtDictionary = {}
        try:
          if is_number(linesArray[0].strip()):
            print("--> Ignoring: {}".format(linesArray))
            continue

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

  run_for_ocr(opt)

  districts_data = []
  with open(OUTPUT_FILE) as mzFile:
    for line in mzFile:
      line = line.replace('Nil', '0')
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 5:
        print("--> Issue with {}".format(linesArray))
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
  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 13:
          print("--> Issue with {}".format(linesArray))
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[12])
        districtDictionary['recovered'] = int(linesArray[7])
        districtDictionary['migrated'] = int(linesArray[11])
        districtDictionary['deceased'] = int(linesArray[8]) if len(re.sub('\n', '', linesArray[8])) != 0 else 0
        districts_data.append(districtDictionary)

    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")
  return districts_data

def or_get_data(opt):
  import os
  temp_file = "./_cache/{}.csv".format(opt['state_code'].lower())
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
    read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []

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

  elif opt['type'] == 'image':
    run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    secondRunArray = []
    masterColumnList = ""
    masterColumnArray = []
    splitArray = []
    try:
      with open(OUTPUT_FILE, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')
          if len(linesArray) != 6:
            print("--> Issue with {}".format(linesArray))
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
  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find_all('tbody')[1].find_all('tr')

  district_data = []
  for index, row in enumerate(table):
    data_points = row.find_all('td')

    district_dictionary = {
      'districtName': data_points[0].get_text().strip(),
      'confirmed': int(data_points[1].get_text().strip()),
      'recovered': int(data_points[2].get_text().strip()),
      'deceased': int(data_points[4].get_text().strip())
    }
    district_data.append(district_dictionary)

  return district_data

def rj_get_data(opt):
  print('Fetching RJ data')
  pprint(opt)

  # run all bash scripts, ocr_vision.py & googlevision.py
  run_for_ocr(opt)

  linesArray = []
  districtDictionary = {}
  districtArray = []
  skipValues = False
  edge_case = False
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

        districtArray.append(districtDictionary)

    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")

  return districtArray

def sk_get_data(opt):
  print('Fetching SK data')
  pprint(opt)
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

def tn_get_data(opt):
  print('Fetching TN data')
  pprint(opt)

  if opt['type'] == 'pdf':
    read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    district_data = []
    with open('{}.csv'.format(opt['state_code'].lower()), "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 5:
          print("--> Issue with {}".format(linesArray))
          continue
        linesArray[4] = linesArray[4].replace('$', '')
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

  run_for_ocr(opt)

  linesArray = []
  with open(OUTPUT_FILE, "r") as tgFile:
    for line in tgFile:
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 2:
        print("--> Issue with {}".format(linesArray))
        continue
      if linesArray[0].strip().capitalize() == "Ghmc":
        linesArray[0] = "Hyderabad"
      print("{},Telangana,TG,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[1].strip()))

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

# TODO - make this run
def up_get_data(opt):
  print('Fetching UP data')
  pprint(opt)
  errorCount = 0
  linesArray = []
  districtDictionary = {}
  districts_data = []
  masterColumnArray = []
  splitArray = []
  lengthOfArray = 7
  activeIndex = 6
  recoveredIndex = 3
  deceasedIndex = 5
  typeOfAutomation = 'ocr1'

  if typeOfAutomation == "ocr1":
    lengthOfArray = 7
    activeIndex = 6
    recoveredIndex = 3
    deceasedIndex = 5
  else:
    typeOfAutomation = "ocr2"
    lengthOfArray = 8
    activeIndex = 7
    recoveredIndex = 4
    deceasedIndex = 6
  print("--> Using format {}".format(typeOfAutomation))

  try:
    with open(OUTPUT_FILE, "r") as upFile:
      for line in upFile:
        splitArray = re.sub('\n', '', line.strip()).split('|')
        linesArray = splitArray[0].split(',')

        if errorCount > 10:
          errorCount = 0
          if typeOfAutomation == "ocr1":
            typeOfAutomation = "ocr2"
          else:
            typeOfAutomation = "ocr1"
          print("--> Switching to version {}. Error count breached.".format(typeOfAutomation))
          up_get_data()
          return

        if len(linesArray) != lengthOfArray:
          print("--> Issue with {}".format(linesArray))
          errorCount += 1
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[recoveredIndex]) + int(linesArray[deceasedIndex]) + int(linesArray[activeIndex])
        districtDictionary['recovered'] = int(linesArray[recoveredIndex])
        districtDictionary['deceased'] = int(linesArray[deceasedIndex])
        #districtDictionary['active'] = int(linesArray[activeIndex])
        """

        districtDictionary['confirmed'] = int(linesArray[2])
        districtDictionary['recovered'] = int(linesArray[4])
        districtDictionary['deceased'] = int(linesArray[6])
        """

        districts_data.append(districtDictionary)
    upFile.close()
  except FileNotFoundError:
    print("output.txt missing. Generate through pdf or ocr and rerun.")
  return districts_data

def ut_get_data(opt):
  print('Fetching UT data')
  pprint(opt)

  if opt['type'] == 'pdf':
    read_pdf_from_url(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    ignoreLines = False
    try:
      with open('{}.csv'.format(opt['state_code'].lower()), "r") as upFile:
        for line in upFile:
          if ignoreLines == True:
            continue

          if 'Total' in line:
            ignoreLines = True
            continue

          linesArray = line.split(',')
          if len(linesArray) != 6:
            print("--> Issue with {}".format(linesArray))
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[4])
          districtDictionary['migrated'] = int(re.sub('\n', '', linesArray[5].strip()))
          districts_data.append(districtDictionary)

      upFile.close()
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")
    return districts_data

  elif opt['type'] == 'image':
    run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    districts_data = []
    splitArray = []
    try:
      with open(OUTPUT_FILE, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')

          if len(linesArray) != 6:
            print('---> Issue with {}'.format(linesArray))
            continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[1].strip())
          districtDictionary['recovered'] = int(linesArray[2].strip())
          districtDictionary['deceased'] = int(linesArray[4].strip())
          districtDictionary['migrated'] = int(linesArray[5].strip())
          districts_data.append(districtDictionary)

    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")
    return districts_data

def wb_get_data(opt):
  print('Fetching WB data')
  pprint(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []

  read_pdf_from_url(opt)

  try:
    with open("{}.csv".format(opt['state_code'].lower()), "r") as upFile:
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
  except FileNotFoundError:
    print("wb.csv missing. Generate through pdf or ocr and rerun.")
  return districts_data

## ------------------------ <STATE_CODE>_get_data functions END HERE


def vaccination_data(opt):
  ## TODO - looks like this is vaccination data, not cases
  print("Date, State, First Dose, Second Dose, Total Doses")

  lookback = int(opt['config']['page']) if len(opt['config']['page']) != 0 else 0
  for day in range(lookback, -1, -1):
    today = (datetime.date.today() - datetime.timedelta(days = day)).strftime("%Y-%m-%d")
    fileName=today+"-at-07-00-AM.pdf"

    read_pdf(opt)

    dadra = {'firstDose': 0, 'secondDose': 0, 'totalDose': 0}

    try:
      with open("vcm.csv", "r") as upFile:
        for line in upFile:
          if "Dadra" in line or "Daman" in line:
            dadra['firstDose'] += int(line.split(',')[1])
            dadra['secondDose'] += int(line.split(',')[2])
            dadra['totalDose'] += int(line.split(',')[3])
            continue
          print(today + "," + line, end = "")

      print("{}, DnH, {}, {}, {}".format(today, dadra['firstDose'], dadra['secondDose'], dadra['totalDose']))
    except FileNotFoundError:
      print("output.txt missing. Generate through pdf or ocr and rerun.")
    return dadra

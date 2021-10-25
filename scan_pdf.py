import requests
import camelot
import csv
import re

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

def ka_get_data(opt):
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
      os.system("python3 kaautomation.py d " + str(startId) + " " + str(endId) + " && cat kaconfirmed.csv")

  except FileNotFoundError:
    print("ka.txt missing. Generate through pdf or ocr and rerun.")



ka_get_data({
  'name': 'Karnataka',
  'state_code': 'KA',
  'automatic': 'False',
  # test it against locally saved file
  # url: file:///Users/i536332/Documents/DK/covid19bharat_scrapers/automation/.tmp/KA.pdf
  # append the google drive file's id to the below url to download PDF
  'url': 'https://docs.google.com/uc?export=download&id=',
  'type': 'pdf',
  'config': {
    'page': '5',
    'start_key': 'Bagalakote',
    'end_key': 'Total'
  }
})

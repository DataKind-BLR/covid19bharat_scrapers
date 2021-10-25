import camelot
import csv
import re

def hr_get_data(optt):
  ## constants
  opt = {}
  opt['name'] = 'Haryana'
  opt['state_code'] = 'HR'
  opt['url'] = 'http://nhmharyana.gov.in/WriteReadData/userfiles/file/CoronaVirus/Daily%20Bulletin%20of%20COVID%2019%20as%20on%2024-10-2021.pdf'
  opt['type'] = 'pdf'
  opt['config'] = {}
  opt['config']['page'] = '2'
  opt['config']['start_key'] = 'Gurugram'
  opt['config']['end_key'] = 'Total'

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

  for pg_no, table in enumerate(tables):
    tables[pg_no].to_csv(opt['state_code'] + str(pg_no) + '.pdf.txt')

  # create an empty csv file first
  stateOutputFile = open(opt['state_code'].lower() + '.csv', 'w')
  startedReadingDistricts = False

  for index, table in enumerate(tables):
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
  ##
  # try:
  #   with open(".tmp/hr.csv", "r") as upFile:
  #     for line in upFile:
  #       linesArray = line.split(',')
  #       if len(linesArray) != 4:
  #         print("--> Issue with {}".format(linesArray))
  #         continue

  #       districtDictionary = {}
  #       districtDictionary['districtName'] = linesArray[0].strip()
  #       districtDictionary['confirmed'] = int(linesArray[1])
  #       districtDictionary['recovered'] = int(linesArray[2])
  #       districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
  #       districtArray.append(districtDictionary)

  #   upFile.close()
  #   deltaCalculator.getStateDataFromSite("Haryana", districtArray, option)
  # except FileNotFoundError:
  #   print("hr.csv missing. Generate through pdf or ocr and rerun.")

hr_get_data({})


def readFileFromURLV2(url, stateName, startKey, endKey):
  '''
  Given a filename & page number, scan and extract tables
  '''


  global pdfUrl
  global pageId
  stateFileName = metaDictionary[stateName].stateCode

  if len(pdfUrl) > 0:
    url = pdfUrl
  if len(url) > 0:
    #print("--> Requesting download from {} ".format(url))
    r = requests.get(url, allow_redirects=True, verify=False)
    open(".tmp/" + stateFileName + ".pdf", 'wb').write(r.content)
  if len(pageId) > 0:
    pid = ""
    if ',' in pageId:
      startPage = int(pageId.split(',')[0])
      endPage = int(pageId.split(',')[1])
      for pages in range(startPage, endPage + 1, 1):
        print(pages)
        pid = pid + "," + str(pages) if len(pid) > 0 else str(pages)
        print(pid)
    else:
      pid = pageId
  else:
    pid = input("Enter district page:")
  print("Running for {} pages".format(pid))
  tables = camelot.read_pdf(".tmp/" + stateFileName + ".pdf", strip_text = '\n', pages = pid, split_text = True)
  for index, table in enumerate(tables):
    tables[index].to_csv('.tmp/' + stateFileName + str(index) + '.pdf.txt')

  stateOutputFile = open('.tmp/' + stateFileName.lower() + '.csv', 'w')
  csvWriter = csv.writer(stateOutputFile)
  arrayToWrite = []

  startedReadingDistricts = False
  for index, table in enumerate(tables):
    with open('.tmp/' + stateFileName + str(index) + '.pdf.txt', newline='') as stateCSVFile:
      rowReader = csv.reader(stateCSVFile, delimiter=',', quotechar='"')
      for row in rowReader:
        line = "|".join(row)
        line = re.sub("\|+", '|', line)
        if startKey in line:
          startedReadingDistricts = True
        if len(endKey) > 0 and endKey in line:
          startedReadingDistricts = False
          continue
        if startedReadingDistricts == False:
          continue

        line = eval(stateFileName + "FormatLine")(line.split('|'))
        if line == "\n":
          continue
        print(line, file = stateOutputFile, end = "")

  stateOutputFile.close()

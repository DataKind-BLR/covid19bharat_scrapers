import os
import re
import csv
import urllib
import camelot
import requests
import pdftotext

INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_inputs')
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs')

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

  if urllib.parse.urlparse(opt['url']).scheme != '':
    r = requests.get(opt['url'], allow_redirects=True, verify=False)
    DOWNLOADED_PDF = os.path.join(INPUTS_DIR, opt['state_code'].lower() + '.pdf')
    open(DOWNLOADED_PDF, 'wb').write(r.content)
    opt['url'] = DOWNLOADED_PDF

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
  OUTPUT_CSV = os.path.join(OUTPUTS_DIR, opt['state_code'].lower() + '.csv')
  stateOutputFile = open(OUTPUT_CSV, 'w')
  startedReadingDistricts = False

  if opt['config']['translation'] == True:
    # read translation file
    translation_dict = read_translation(opt['state_code'].lower())

  for index, table in enumerate(tables):
    OUTPUT_PDF = os.path.join(OUTPUTS_DIR, opt['state_code'].lower() + str(index) + '.pdf.txt')
    tables[index].to_csv(OUTPUT_PDF)

    with open(OUTPUT_PDF, newline='') as stateCSVFile:
      rowReader = csv.reader(stateCSVFile, delimiter=',', quotechar='"')
      for row in rowReader:
        line = "|".join(row)
        line = re.sub("\|+", '|', line)
        if opt['state_code'] == 'UP':
          formatted_line = up_custom(opt, line.split('|'), translation_dict)
          print(formatted_line, file=stateOutputFile, end="")
          continue

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

## ------------------------ Custom format line functions for specific states START
def up_custom(opt, row, translation_dict):
  if row[1] in translation_dict:
    dist_eng = translation_dict[row[1]]
    #             dist_name,     confirmed,     discharged, cum discharged,   deceased,     cum deceased,    active
    modifiedRow = dist_eng + ',' + row[2] + ',' + row[3] + ',' + row[4] + ',' + row[5] + ',' + row[6] + ',' + row[7] + '\n'
    return modifiedRow
  else:
    return ''

def ut_format_line(row):
  if len(row) == 6 and row[0] != 'Districts':
    to_print = ','.join(row) + '\n'
    return to_print
  else:
    return ''

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

def tn_format_line(row):
  row[1] = re.sub('"', '', re.sub('\+.*', '', row[1]))
  row[2] = re.sub('"', '', re.sub('\+.*', '', row[2]))
  # line = row.replace('"', '').replace('*', '').replace('#', '').replace(',', '').replace('$', '')
  line = row[1] + "," + row[2] + "," + row[3] + "," + row[4] +  "," + row[5] + "\n"
  return line

## ------------------------ Custom format line functions for specific states END

def read_translation(state_code):
  translated_dict = {}
  meta_file = os.path.join(os.path.dirname(__file__), 'automation', state_code.lower() + '_districts.meta')
  try:
    with open(meta_file, "r") as metaFile:
      for line in metaFile:
        if line.startswith('#'):
          continue
        lineArray = line.strip().split(',')
        translated_dict[lineArray[0].strip()] = lineArray[1].strip()
  except:
    pass
  return translated_dict

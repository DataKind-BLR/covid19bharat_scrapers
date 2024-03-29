import os
import re
import json
from numpy import False_
import requests
import datetime
import pandas as pd

from bs4 import BeautifulSoup
from read_ocr import run_for_ocr
from read_pdf import read_pdf_from_url

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs')
OUTPUT_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'output.txt')

MOHFW_URL = 'https://www.mohfw.gov.in/data/datanew.json'
api_state_wise = 'https://data.covid19bharat.org/csv/latest/state_wise.csv'

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
  
  datum = (pd.read_json(MOHFW_URL))
  #           .set_index('state_name'))
  #           .loc[name])
  #print(datum)
  datum['state_name'] = datum['state_name'].str.replace('[^a-zA-Z\s]', '', regex=True)
  datum = datum.replace('', 0, regex=True)
  datum['death_reconsille'] = datum['death_reconsille'].astype(int)
  datum['total'] = datum['total'].astype(int)
  datum = datum.loc[datum['state_name'] == name]
  #print(datum.head(2).to_string(index=False))
  #print(datum.dtypes)
  #print(datum['death_reconsille'],datum['new_death'],datum['death'])

  if str(datum['death_reconsille']) != 0:
    #print(datum['death_reconsille'],datum['new_death'],datum['death'])
    dDno = datum['new_death'] - datum['death'] + datum['death_reconsille']
  else:
    dDno = datum['new_death'] - datum['death']
  #print('dD = ',dDno.to_string(index=False))

  return [{
    'districtName': name,
    'confirmed': datum['new_positive'].to_string(index=False),
    'recovered': datum['new_cured'].to_string(index=False),
    'deceased':  datum['new_death'].to_string(index=False),
    'active':  datum['new_active'].to_string(index=False),
    'dC': (datum['new_positive'] - datum['positive']).to_string(index=False),
    'dR': (datum['new_cured'] - datum['cured']).to_string(index=False),
    'dD': dDno.to_string(index=False)
  }] 

def _get_api_statewise_data(name):
  '''Fetch state-wise data from MOHFW website.
  
  Inputs:
    name: state name, eg: Ladakh

  Returns:
    dict: [{
      'StateName': '',
      'confirmed': 12345,
      ...
    }]
  '''
  
  datum = (pd.read_csv(api_state_wise)
             .set_index('State')
             .loc[name])

  return [{
    'stateName': name,
    'api_C': datum['Confirmed'],
    'api_R': datum['Recovered'],
    'api_D':  datum['Deaths'],
    'api_A':  datum['Active']
  }]

def ap_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data


    #if opt['skip_output'] == False:
    #  response = requests.request('GET', opt['url'], verify=False)
    #  soup = BeautifulSoup(response.content, 'html.parser')
    #  table = soup.find('table', {'class': 'table'}).find_all('tr')
    #  districts_data = []

    #  for row in table[1:]:
        # Ignoring 1st row containing table headers
    #    d = row.find_all('td')
    #    districts_data.append({
    #      'districtName': d[0].get_text(),
    #      'confirmed': int(d[1].get_text().strip()),
    #      'recovered': int(d[2].get_text().strip()),
    #      'deceased': int(d[3].get_text().strip())
    #    })
  '''
  elif opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    to_correct = []
    needs_correction = False
    linesArray = []
    districtDictionary = {}
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          if len(linesArray) != 4:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    to_correct = []
    needs_correction = False
    linesArray = []
    districtDictionary = {}
    districts_data = []
    splitArray = []

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')

          if len(linesArray) != 6:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          if linesArray[0].strip() == "Total":
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[2].strip())
          districtDictionary['recovered'] = int(linesArray[4].strip())
          districtDictionary['deceased'] = int(linesArray[5].strip())
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'output': OUTPUT_TXT,
        'to_correct': e
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'output': OUTPUT_TXT,
        'to_correct': to_correct
      }
  '''
  #return districts_data


def an_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data


def ar_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  '''
  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    to_correct = []
    needs_correction = False
    districts_data = []
    additionalDistrictInfo = {}
    additionalDistrictInfo['districtName'] = 'Papum Pare'
    additionalDistrictInfo['confirmed'] = 0
    additionalDistrictInfo['recovered'] = 0
    additionalDistrictInfo['deceased'] = 0

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          if 'Total' in line:
            continue

          linesArray = line.split('|')[0].split(',')

          NcolReq = 14
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(', '.join(linesArray))
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
    except Exception as e:
      return {
        'needs_correction': True,
        'output': OUTPUT_TXT,
        'to_correct': e
      }

    # lastly, add the additional district calculated for `Papum Pare`
    districts_data.append(additionalDistrictInfo)

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'output': OUTPUT_TXT,
        'to_correct': to_correct
      }
  return districts_data
  '''


def as_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    splitArray = []
    print('\n*** Do Manual entry of Recovered and Deaths\nDistrictwise Hospitalized \n')

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')

          NcolReq = 4
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          ## Why is this not fixed in `as_districts.meta` ??
          if int(linesArray[len(linesArray) - 1]) > 0:
            if ((linesArray[0].strip() == 'Kamrup Metro') or (linesArray[0].strip() == 'Metro')):
              print("Kamrup Metropolitan,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
            elif linesArray[0].strip() == 'Kamrup Rural':
              print("Kamrup,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
            elif linesArray[0].strip() == 'South Salmara':
              print("South Salmara Mankachar,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
            elif linesArray[0].strip() == 'Hasao':
              print("Dima Hasao,Assam,AS,{},Hospitalized".format(linesArray[len(linesArray) - 1].strip()))
            else:
              print("{},Assam,AS,{},Hospitalized".format(linesArray[0].strip(), linesArray[len(linesArray) - 1].strip()))
            # districtDictionary['districtName'] = linesArray[0].strip()
            # districtDictionary['confirmed'] = linesArray[len(linesArray) - 1].strip()
            # districts_data.append(districtDictionary)

    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def br_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    to_correct = []
    needs_correction = False
    linesArray = []
    districtDictionary = {}
    districts_data = []
    Dno=0

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 5
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0]
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3])
          #districtDictionary['deceased'] = int(linesArray[5])
          districts_data.append(districtDictionary)
          Dno = Dno + 1

    except Exception as e:
      return {
        'needs_correction': True,
        'output': OUTPUT_TXT,
        'to_correct': e
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'output': OUTPUT_TXT,
        'to_correct': to_correct
      }

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Districts scraped = ',Dno)
    print('+++++++++++++++++++++++++++++++++++++++++++++++') 
    return districts_data


def ch_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  '''
  import urllib
  #file download
  htm_string_1 = 'http://chdpr.gov.in/cadmin/uploads/downloads/Media_Bulletin_on_'
  htm_string_3 = '.docx'
  upstring = ''

  #bull_date_string = '06-07-2022'
  bull_date_string = datetime.datetime.today().strftime('%d-%m-%Y')
  bull_date_print = datetime.datetime.today().strftime('%d/%m/%Y')

  htm_string= htm_string_1+bull_date_string+htm_string_3
  churl=htm_string
  #print(htm_string)

  filename = '_inputs/'+opt['state_code']+'.docx'
  try:
    urllib.request.urlretrieve(htm_string, filename)

    #extract text from DOCX
    #http://etienned.github.io/posts/extract-text-from-word-docx-simply/
    try:
        from xml.etree.cElementTree import XML
    except ImportError:
        from xml.etree.ElementTree import XML
    import zipfile


    """
    Module that extract text from MS XML Word document (.docx).
    (Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
    """

    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'


    def get_docx_text(path):
        """
        Take the path of a docx file as argument, return the text in unicode.
        """
        document = zipfile.ZipFile(path)
        xml_content = document.read('word/document.xml')
        document.close()
        tree = XML(xml_content)

        paragraphs = []
        for paragraph in tree.getiterator(PARA):
            texts = [node.text
                    for node in paragraph.getiterator(TEXT)
                    if node.text]
            if texts:
                paragraphs.append(''.join(texts))

        return '|'.join(paragraphs)

    #use above sub to Get the txt from docx
    text = get_docx_text(filename)

    text = text.replace(' ','')
    #print(text)
    #extract dC dR dD Tests

    newcasespat = re.compile(r'newpositivecases\|(\d+)\|')
    newcases = re.search(newcasespat, text)
    newcases = newcases[1]
    newcases = str(int(newcases))

    recpat = re.compile(r'Today(\d+)patients')
    rec = re.search(recpat, text)
    rec = rec[1]
    rec = str(int(rec))

    #deathpat = re.compile(r'death(\d+)')
    #death = re.search(deathpat, text)
    #death = death[1]
    #death = str(int(death))

    testpat = re.compile(r'SamplesTested\|(\d+)')
    testno = re.search(testpat, text)
    testno = testno[1]

    #print(testdate,newcases,rec,testno)

    if newcases != '0':
      upstring += opt['name']+','+opt['state_code']+','+newcases+',Hospitalized,,,'+churl+'\n'
    if rec != '0':
      upstring += opt['name']+','+opt['state_code']+','+rec+',Recovered,,,'+churl+'\n'
    #if death != '0':
    #  upstring += opt['name']+','+opt['state_code']+','+death+',Deceased,,,'+churl+'\n'
    
    teststring = bull_date_print+','+opt['name']+',,,,'+testno+',Tested,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'+churl+'\n'

    print('\n On '+bull_date_print+' Cases data for copy & paste \n')
    print(upstring,'\n')

    print('\n TESTs data for copy & paste \n')
    print(teststring,'\n')

  except:
    print("Todays Bulletin yet to come. check website")

  return {
    'needs_correction': False
  }

  
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
  '''

def ct_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          NcolReq = 4
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    to_correct = []
    needs_correction = False
    linesArray = []
    districtDictionary = {}
    districts_data = []
    splitArray = []

    #columns reduced to remove dD & D
    # nColRef = 9
    # print('\nDeaths today column is not scraped if empty. \n last two columns should be clipped for file submission\n')
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')

          NcolReq = 9
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
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
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }

  return districts_data


def dd_get_data(opt):
  pass


def dl_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data




def dn_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data


def ga_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  '''
  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find_all("div", {"class": "vc_col-md-2"})
  districts_data = []

  for index, row in enumerate(table):
    # print(row.get_text())
    districtDictionary = {}
    districts_data.append(districtDictionary)

  return districts_data
  '''

def gj_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'html':
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

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Current Deltas directly from bulletin\nEnsure current data is not entered already')
    print('+++++++++++++++++++++++++++++++++++++++++++++++\n') 

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          NcolReq = 4
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          #Directly printout current deltas given in bulletin
          if 'Surat' in linesArray[0].strip(): 
            dt_name = 'Surat'
          elif 'Vadodara' in linesArray[0].strip(): 
            dt_name = 'Vadodara'
          elif 'Rajkot' in linesArray[0].strip(): 
            dt_name = 'Rajkot'
          elif 'Bhavnagar' in linesArray[0].strip(): 
            dt_name = 'Bhavnagar'
          elif 'Jamnagar' in linesArray[0].strip(): 
            dt_name = 'Jamnagar'
          #elif 'Gir' in linesArray[0].strip(): 
          #  dt_name = 'Gir'
          elif 'Junagadh' in linesArray[0].strip(): 
            dt_name = 'Junagadh'
          elif 'Aanand' in linesArray[0].strip(): 
            dt_name = 'Anand'
          elif 'Aravali' in linesArray[0].strip(): 
            dt_name = 'Aravalli'
          elif 'Devbhuvam Dwarka' in linesArray[0].strip(): 
            dt_name = 'Devbhumi Dwarka'
          elif 'Gandhinagar' in linesArray[0].strip(): 
            dt_name = 'Gandhinagar'
          elif 'Kachchh' in linesArray[0].strip(): 
            dt_name = 'Kutch'
          elif 'Namjada' in linesArray[0].strip(): 
            dt_name = 'Narmada'
          elif 'Fifth' in linesArray[0].strip(): 
            dt_name = 'Panchmahal'
          elif 'Chhota' in linesArray[0].strip(): 
            dt_name = 'Chhota Udaipur'
          else:
            dt_name =  linesArray[0].strip()

          #print("{},{},{},{},Hospitalized".format(dt_name, opt['name'], opt['state_code'], int(re.sub('[^0-9]+', '', linesArray[1].strip()).strip())))
          if int(re.sub('[^0-9]+', '', linesArray[1].strip()).strip()) != 0:
            print("{},{},{},{},Hospitalized".format(dt_name, opt['name'], opt['state_code'], int(re.sub('[^0-9]+', '', linesArray[1].strip()).strip())))
          if int(re.sub('[^0-9]+', '', linesArray[3].strip()).strip()) != 0:
            print("{},{},{},{},Recovered".format(dt_name, opt['name'], opt['state_code'], int(re.sub('[^0-9]+', '', linesArray[3].strip()).strip())))
          if int(re.sub('[^0-9]+', '', linesArray[2].strip()).strip()) != 0:
            print("{},{},{},{},Deceased".format(dt_name, opt['name'], opt['state_code'], int(re.sub('[^0-9]+', '', linesArray[2].strip()).strip())))

    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    return {
      'needs_correction': False
    }
    return districts_data

def hp_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    to_correct = []
    needs_correction = False
    linesArray = []
    districtDictionary = {}
    districts_data = []
    districtTableBeingRead = False

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Current Deltas directly from bulletin\nEnsure current data is not entered already')
    print('+++++++++++++++++++++++++++++++++++++++++++++++\n') 

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          line = re.sub('\*', '', line)
          linesArray = line.split('|')[0].split(',')
          availableColumns = line.split('|')[1].split(',')
          districtDictionary = {}

          NcolReq = 10
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue
          if linesArray[0].strip().title() == 'Total':
            break

          districtDictionary = {}
          #subtract today's delta's and pass to calc to estimate yesterday's deltas
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(re.sub('[^0-9]+', '', linesArray[1].strip()).strip()) - int(re.sub('[^0-9]+', '', linesArray[3].strip()).strip())
          districtDictionary['recovered'] = int(re.sub('[^0-9]+', '', linesArray[6].strip()).strip()) - int(re.sub('[^0-9]+', '', linesArray[4].strip()).strip())
          districtDictionary['deceased'] = int(re.sub('[^0-9]+', '', linesArray[8].strip()).strip()) - int(re.sub('[^0-9]+', '', linesArray[7].strip()).strip())
          districts_data.append(districtDictionary)

          #Directly printout current deltas given in bulletin
          if '& Spiti' in linesArray[0].strip() or 'Spiti' in linesArray[0].strip(): 
            dt_name = 'Lahaul and Spiti'
          else:
            dt_name =  linesArray[0].strip()

          if int(linesArray[3]) != 0:
            print("{},{},{},{},Hospitalized".format(dt_name, opt['name'], opt['state_code'], int(linesArray[3])))
          if int(linesArray[4]) != 0:
            print("{},{},{},{},Recovered".format(dt_name, opt['name'], opt['state_code'], int(linesArray[4])))
          if int(linesArray[7]) != 0:
            print("{},{},{},{},Deceased".format(dt_name, opt['name'], opt['state_code'], int(linesArray[7])))

    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Previous Day Deltas give below. \nNo deltas: we got bulletin previous day too. \nNegative Deltas: Current data already entered')
    print('+++++++++++++++++++++++++++++++++++++++++++++++') 

    return districts_data

def hr_get_data(opt):

  if not opt['url'].endswith('.pdf'):
    today = datetime.date.today().strftime("%d-%m-%Y")
    print(f'Downloading HR pdf file for {today}')
    opt['url'] = opt['url'] + today + '.' + opt['type']

  opt['config']['page'] = str(opt['config']['page'])

  if opt['skip_output'] == False:
    read_pdf_from_url(opt)

  needs_correction = False
  to_correct = []
  linesArray = []
  districtDictionary = {}
  districts_data = []
  csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

  try:
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')

        NcolReq = 4
        if len(linesArray) != NcolReq:
          NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
          needs_correction = True
          linesArray.insert(0, NcolErr)
          to_correct.append(linesArray)
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3])
        districts_data.append(districtDictionary)
  except Exception as e:
    return {
      'needs_correction': True,
      'to_correct': e,
      'output': csv_file
    }

  upFile.close()
  if needs_correction:
    return {
      'needs_correction': True,
      'to_correct': to_correct,
      'output': csv_file
    }
  return districts_data


def jh_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          NcolReq = 8
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[4]) + int(linesArray[5])
          districtDictionary['recovered'] = int(linesArray[2]) + int(linesArray[6])
          districtDictionary['deceased'] = int(linesArray[3]) + int(linesArray[7])
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Current Deltas directly from bulletin\nEnsure current data is not entered already')
    print('+++++++++++++++++++++++++++++++++++++++++++++++') 

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')
          availableColumns = line.split('|')[1].split(',')

          NcolReq = 8
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          #districtDictionary['confirmed'] = int(linesArray[4]) + int(linesArray[5])
          #districtDictionary['recovered'] = int(linesArray[2]) + int(linesArray[6])
          #districtDictionary['deceased'] = int(linesArray[3]) + int(linesArray[7])

          #we pass totals of previous day for deltas of Previous day
          districtDictionary['confirmed'] = int(linesArray[4])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3])

          #Directly printout current deltas given in bulletin
          if 'Saralkela' in linesArray[0].strip() or 'Saraikela' in linesArray[0].strip(): 
            dt_name = 'Saraikela-Kharsawan'
          else:
            dt_name =  linesArray[0].strip()

          if int(linesArray[5]) != 0:
            print("{},Jharkhand,JH,{},Hospitalized".format(dt_name, int(linesArray[5])))
          if int(linesArray[6]) != 0:
            print("{},Jharkhand,JH,{},Recovered".format(dt_name, int(linesArray[6])))
          if int(linesArray[7]) != 0:
            print("{},Jharkhand,JH,{},Deceased".format(dt_name, int(linesArray[7])))

          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Previous Day Deltas give below. \nNo deltas: we got bulletin previous day too. \nNegative Deltas: Current data already entered')
    print('+++++++++++++++++++++++++++++++++++++++++++++++') 
    return districts_data


def jk_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        isIgnoreFlagSet = False
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 11
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          if type(linesArray[0].strip()) == int:
            needs_correction = True
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[6])
          districtDictionary['recovered'] = int(linesArray[9])
          districtDictionary['deceased'] = int(linesArray[10])
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def ka_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    runDeceased = False
    opt['config']['page'] = str(opt['config']['page'])

    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    try:
      csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          if len(linesArray) != 5:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3])
          districtDictionary['migrated'] = int(linesArray[4].strip()) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data


def kl_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data


def kld_get_data(opt):
  '''
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
    return districts_data
'''

def kldbl_get_data(opt):
  '''
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
        #if len(linesArray) != 3:
        if len(linesArray) != 2:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue
        if linecnt !=1:
           if int(linesArray[1].strip()) != 0:
              print("{},Kerala,KL,{},Deceased,,cat_B (G.O.(Rt) No.2110/2021/H and FWD)".format(linesArray[0].strip().title(), linesArray[1].strip()))
           #if int(linesArray[2].strip()) != 0:
           #   print("{},Kerala,KL,{},Deceased,,cat_C (G.O.(Rt) No.2219/2021/H and FWD)".format(linesArray[0].strip().title(), linesArray[2].strip()))
    print('\n---------------------------------------------------------------------\n')
    upFile.close()
    #quit()
    return districts_data
  '''

def la_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data


def ld_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'html':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])
    #print(api_data[0]['api_A'],data[0]['active'])

    if ((data[0]['active'] != api_data[0]['api_A']) and ((data[0]['dC'] != 0) or (data[0]['dR']) or (data[0]['dD']))):
      print('\nState level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD\n')
      if data[0]['dC'] != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if data[0]['dR'] != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if data[0]['dD'] != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')
      
    return {
      'needs_correction': False
    }

def mh_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          NcolReq = 4
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue
          if 'District' in linesArray[0].strip() or 'Other' in linesArray[0].strip():
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3])
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    districts_data = []

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 5
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1].strip())
          districtDictionary['recovered'] = int(linesArray[2].strip())
          districtDictionary['deceased'] = int(linesArray[3].strip())
          #districtDictionary['migrated'] = int(linesArray[4].strip())
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data
    
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
    datems = int(datems)
    datestamp = datetime.datetime.fromtimestamp(datems/1000)
    print("\nReported Date : ", datestamp, "\n")
    return district_data


def ml_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          NcolReq = 7
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          #districtDictionary['districtName'] = linesArray[0].strip()
          #districtDictionary['confirmed'] = int(linesArray[1])
          #districtDictionary['recovered'] = int(linesArray[1]) - (int(linesArray[2]) + int(linesArray[3]))
          #districtDictionary['deceased'] = int(linesArray[2])

          #Directly printout current deltas given in bulletin
          if 'Ri-Bhoi' in linesArray[0].strip(): 
            dt_name = 'RiBhoi'
          else:
            dt_name =  linesArray[0].strip()

          if 'Meghalaya' in linesArray[0].strip():
            print('\n','-*-'*20)
            print("Tests done during week = {}".format(int(linesArray[4])))
            print('-*-'*20,'\n')
            continue

          if int(linesArray[1]) != 0:
            print("{},{},{},{},Hospitalized".format(dt_name, opt['name'], opt['state_code'], int(linesArray[1])))
          if int(linesArray[2]) != 0:
            print("{},{},{},{},Recovered".format(dt_name, opt['name'], opt['state_code'], int(linesArray[2])))
          if int(linesArray[3]) != 0:
            print("{},{},{},{},Deceased".format(dt_name, opt['name'], opt['state_code'], int(linesArray[3])))


          districts_data.append(districtDictionary)
      return {
        'needs_correction': False
      }

    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    districts_data = []

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 8
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[4].strip())
          districtDictionary['recovered'] = int(linesArray[4].strip()) - (int(linesArray[5].strip()) + int(linesArray[6].strip()))
          districtDictionary['deceased'] = int(linesArray[5].strip())
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
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

    return districts_data


def mn_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districts_data = []

    try:
      with open(OUTPUT_TXT) as upFile:
        for line in upFile:
          districtDictionary = {}
          linesArray = line.split('|')[0].split(',')

          if len(linesArray) != 8:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          if linesArray[2].strip() != "0":
            districtDictionary['confirmed'] = linesArray[2].strip()
          if linesArray[4].strip() != "0":
            districtDictionary['deceased'] = linesArray[4].strip()
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def mp_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Current Deltas directly from bulletin\nEnsure current data is not entered already')
    print('+++++++++++++++++++++++++++++++++++++++++++++++\n') 

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 8
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          #subtract today's delta's and pass to calc to estimate yesterday's deltas
          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[2]) - int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[6]) - int(linesArray[5])
          districtDictionary['deceased'] = int(linesArray[4]) - int(linesArray[3])
          districts_data.append(districtDictionary)

          #Directly printout current deltas given in bulletin
          #if 'Saralkela' in linesArray[0].strip() or 'Saraikela' in linesArray[0].strip(): 
          #  dt_name = 'Saraikela-Kharsawan'
          #else:
          dt_name =  linesArray[0].strip()

          if int(linesArray[1]) != 0:
            print("{},{},{},{},Hospitalized".format(dt_name, opt['name'], opt['state_code'], int(linesArray[1])))
          if int(linesArray[5]) != 0:
            print("{},{},{},{},Recovered".format(dt_name, opt['name'], opt['state_code'], int(linesArray[5])))
          if int(linesArray[3]) != 0:
            print("{},{},{},{},Deceased".format(dt_name, opt['name'], opt['state_code'], int(linesArray[3])))

    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')    
    print('Previous Day Deltas give below. \nNo deltas: we got bulletin previous day too. \nNegative Deltas: Current data already entered')
    print('+++++++++++++++++++++++++++++++++++++++++++++++') 

    return districts_data


def mz_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    districts_data = []

    try:
      with open(OUTPUT_TXT) as upFile:
        for line in upFile:
          line = line.replace('Nil', '0')
          linesArray = line.split('|')[0].split(',')

          NcolReq = 5
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[4]) #+ int(linesArray[2]) + int(linesArray[3])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3]) #if len(re.sub('\n', '', linesArray[3])) != 0 else 0
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def nl_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    needs_correction = False
    to_correct = []
    districts_data = []

    if opt['skip_output'] == False:
      run_for_ocr(opt)

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 13
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[12])
          districtDictionary['recovered'] = int(linesArray[7])
          districtDictionary['migrated'] = int(linesArray[11])
          #Nagaland has detahs due to other causes as additional column
          districtDictionary['deceased'] = int(linesArray[8]) + int(linesArray[9])
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def or_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'html':
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

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          if len(linesArray) != 5:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3])
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []
    splitArray = []

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')

          if len(linesArray) != 5:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          if linesArray[0].strip() == "Total":
            continue
          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[3])
          districtDictionary['deceased'] = int(linesArray[4])
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def py_get_data(opt):
  
  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data


def rj_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  needs_correction = False
  to_correct = []
  linesArray = []
  districtDictionary = {}
  district_data = []

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')   
    print('Direct Deltas from bulletin. Pl check state totals')
    print('+++++++++++++++++++++++++++++++++++++++++++++++\n') 

    skipValues = False
    edge_case = False
    needs_correction = False
    to_correct = []      
    with open(OUTPUT_TXT, "r") as upFile:
      for line in upFile:
        if 'Other' in line:
          skipValues = True
          continue
        if skipValues == True:
          continue

        linesArray = line.split('|')[0].split(',')

        NcolReq = 6
        if len(linesArray) != NcolReq:
          NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
          needs_correction = True
          linesArray.insert(0, NcolErr)
          to_correct.append(linesArray)
          continue

        if 'Other' in linesArray[0].strip().title():
          print('\n+++++++++++++++++++++++++++++++++++++++++++++++')   
          print('Ignoring Other States/Countries',linesArray[0].strip())
          continue

        if 'Madhopur' in linesArray[0].strip().title():
          linesArray[0] = 'Sawai Madhopur'

        dC = int(re.sub('[^0-9]+', '', linesArray[2].strip()))
        dR = int(re.sub('[^0-9]+', '', linesArray[4].strip()))
        dD = int(re.sub('[^0-9]+', '', linesArray[3].strip()))
        if dC != 0:
          print("{},Rajasthan,RJ,{},Hospitalized".format(linesArray[0].strip().title(), dC))
        if dR != 0:
          print("{},Rajasthan,RJ,{},Recovered".format(linesArray[0].strip().title(), dR))          
        if dD != 0:
          print("{},Rajasthan,RJ,{},Deceased".format(linesArray[0].strip().title(), dD))

    upFile.close()
    return {
      'needs_correction': False,
    }

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++')   
    print('Direct Deltas from bulletin. Pl check state totals')
    print('+++++++++++++++++++++++++++++++++++++++++++++++\n') 

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))
    with open(csv_file, "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        '''
        if len(linesArray) != 8:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        if 'Other' in linesArray[0].strip().title():
          print('\n Ignoring Other States/Countries',linesArray[0].strip())
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip().title()
        districtDictionary['confirmed'] = int(linesArray[2])
        districtDictionary['recovered'] = int(linesArray[6])
        districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
        district_data.append(districtDictionary)
        '''
        if len(linesArray) != 5:
          print("--> Issue with Columns: Cno={} : {}".format(len(linesArray), linesArray))
          print('--------------------------------------------------------------------------------')
          continue

        if 'Other' in linesArray[0].strip().title():
          print('\n+++++++++++++++++++++++++++++++++++++++++++++++')   
          print('Ignoring Other States/Countries',linesArray[0].strip())
          continue

        if linesArray[1].strip() != '0':
          print("{},Rajasthan,RJ,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[1].strip()))
        if linesArray[3].strip() != '0':
          print("{},Rajasthan,RJ,{},Recovered".format(linesArray[0].strip().title(), linesArray[3].strip()))
        if linesArray[2].strip() != '0':
          print("{},Rajasthan,RJ,{},Deceased".format(linesArray[0].strip().title(), linesArray[2].strip()))

    upFile.close()
    return {
      'needs_correction': False,
    }

  #return district_data


def sk_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    needs_correction = False
    to_correct = []
    district_data = []

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          if len(linesArray) != 8:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[5].strip())
          districtDictionary['recovered'] = int(linesArray[6].strip())
          districtDictionary['deceased'] = int(linesArray[7]) if len(re.sub('\n', '', linesArray[7])) != 0 else 0
          district_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return district_data


def tn_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'pdf':
    if opt['skip_output'] == False:
      read_pdf_from_url(opt)
    
    linesArray = []
    districtDictionary = {}
    district_data = []
    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    with open(csv_file, "r") as upFile:
      airportConfirmedCount = 0
      airportRecoveredCount = 0
      airportDeceasedCount = 0
      airportRun = 1

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

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    district_data = []
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    linesArray = []
    districtDictionary = {}
    needs_correction = False
    to_correct = []
    print('\n-*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-')
    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          linesArray = line.split('|')[0].split(',')

          NcolReq = 8
          if len(linesArray) != NcolReq:
            NcolErr = '--> Ncol='+str(len(linesArray))+' (NcolReq='+str(NcolReq)+')'
            needs_correction = True
            linesArray.insert(0, NcolErr)
            to_correct.append(linesArray)
            continue

          if linesArray[0].strip().title() == "Ghmc":
            linesArray[0] = "Hyderabad"
          elif linesArray[0].strip().title() == "Jagityal":
            linesArray[0] = "Jagtial"
          elif linesArray[0].strip().title() == "Medchal Malkajigiri":
            linesArray[0] = "Medchal Malkajgiri"
          elif linesArray[0].strip().title() == "Rajanna Siricilla":
            linesArray[0] = "Rajanna Sircilla"
          elif linesArray[0].strip().title() == "Rangareddy":
            linesArray[0] = "Ranga Reddy"
          elif linesArray[0].strip().title() == "Hanumakonda":
            linesArray[0] = "Warangal Urban"
          elif linesArray[0].strip().title() == "Yadadri Bhonigir":
            linesArray[0] = "Yadadri Bhuvanagiri"

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[1].strip())
          districtDictionary['recovered'] = 0
          districtDictionary['deceased'] = 0
          district_data.append(districtDictionary)

          if linesArray[1].strip() != '0':
            print("{},Telangana,TG,{},Hospitalized".format(linesArray[0].strip().title(), linesArray[1].strip()))
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return district_data


def tr_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'html':
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

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  '''
  if opt['skip_output'] == False:
    read_pdf_from_url(opt)

  linesArray = []
  districtDictionary = {}
  districts_data = []
  ignoreLines = False
  needs_correction = False
  to_correct = []
  csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

  try:
    with open(csv_file, "r") as upFile:
      for line in upFile:
        if ignoreLines == True:
          continue

        if 'Total' in line:
          ignoreLines = True
          continue

        linesArray = line.split(',')

        if len(linesArray) != 7:
          needs_correction = True
          linesArray.insert(0, '--> Issue with')
          to_correct.append(linesArray)
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[3]) + int(linesArray[5]) + int(linesArray[6])
        districtDictionary['recovered'] = int(linesArray[3])
        districtDictionary['deceased'] = int(linesArray[5])
        # districtDictionary['migrated'] = int(re.sub('\n', '', linesArray[5].strip()))
        districts_data.append(districtDictionary)
  except Exception as e:
    return {
      'needs_correction': True,
      'to_correct': to_correct,
      'output': csv_file
    }

  upFile.close()
  if needs_correction:
    return {
      'needs_correction': True,
      'to_correct': to_correct,
      'output': csv_file
    }
  return districts_data
  '''

def ut_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  needs_correction = False
  to_correct = []
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
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(re.sub('[^A-Za-z0-9]+', '', linesArray[1]))
          districtDictionary['recovered'] = int(re.sub('[^A-Za-z0-9]+', '', linesArray[2]))
          districtDictionary['deceased'] = int(re.sub('[^A-Za-z0-9]+', '', linesArray[4]))
          districtDictionary['migrated'] = int(re.sub('\n', '', linesArray[5].strip()))
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data

  elif opt['type'] == 'image':
    if opt['skip_output'] == False:
      run_for_ocr(opt)

    try:
      with open(OUTPUT_TXT, "r") as upFile:
        for line in upFile:
          splitArray = re.sub('\n', '', line.strip()).split('|')
          linesArray = splitArray[0].split(',')

          if len(linesArray) != 6:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[1].strip())
          districtDictionary['recovered'] = int(linesArray[2].strip())
          districtDictionary['deceased'] = int(linesArray[4].strip())
          districtDictionary['migrated'] = int(linesArray[5].strip())
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': OUTPUT_TXT
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': OUTPUT_TXT
      }
    return districts_data


def wb_get_data(opt):

  districts_data = []
  if opt['type'] == 'mohfw':
    data=_get_mohfw_data(opt['name'])
    api_data=_get_api_statewise_data(opt['name'])

    #if (not (int(data[0]['dC']) == (int(data[0]['dR']) + int(data[0]['dD']))) and (((int(data[0]['active']) != api_data[0]['api_A'])) and (int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0)))):
    if ((int((data[0]['dC']) != 0) or (int(data[0]['dR']) != 0) or (int(data[0]['dD']) != 0))):
      print('\n***WARNING*** CHECK sheet for prior entry before pasting.')
      print('State level ('+opt['name']+' : '+opt['state_code']+') dC, dR, dD')
      print('-*-'*20,'\n')
      if int(data[0]['dC']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dC'])+',Hospitalized,,,'+MOHFW_URL)
      if int(data[0]['dR']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dR'])+',Recovered,,,'+MOHFW_URL)
      if int(data[0]['dD']) != 0:
        print(opt['name']+','+opt['state_code']+','+str(data[0]['dD'])+',Deceased,,,'+MOHFW_URL)
    else:
      print('\n NO DELTAS')
      print('1) No changes or 2) MOHFW yet to update data. Please try after sometime to verify')

    return {
      'needs_correction': False
    }
    return districts_data

  if opt['type'] == 'image':
    needs_correction = False
    to_correct = []
    linesArray = []
    districtDictionary = {}
    districts_data = []

    if opt['skip_output'] == False:
      read_pdf_from_url(opt)

    csv_file = os.path.join(OUTPUTS_DIR, '{}.csv'.format(opt['state_code'].lower()))

    try:
      with open(csv_file, "r") as upFile:
        for line in upFile:
          linesArray = line.split(',')

          if len(linesArray) != 4:
            needs_correction = True
            linesArray.insert(0, '--> Issue with')
            to_correct.append(linesArray)
            continue

          districtDictionary = {}
          districtDictionary['districtName'] = linesArray[0].strip()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
          districts_data.append(districtDictionary)
    except Exception as e:
      return {
        'needs_correction': True,
        'to_correct': e,
        'output': csv_file
      }

    upFile.close()
    if needs_correction:
      return {
        'needs_correction': True,
        'to_correct': to_correct,
        'output': csv_file
      }
    return districts_data

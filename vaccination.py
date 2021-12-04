import os
import re
import yaml
import datetime
import requests
import warnings
import pandas as pd

warnings.simplefilter(action='ignore')

VACC_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination.txt')
VCMBL_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vcmbl.csv')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')
DISTRICTS_DATA_SHEET = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTrt_V4yW0jd91chhz9BJZOgJtFrsaZEa_gPlrFfQToBuuNDDkn01w0K0GdnjCdklyzFz84A1hFbSUN/pub?gid=382746758&single=true&output=csv'

with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)


def get_vaccination():
    """
        Gets state and district-wise vaccination data from CoWIN API.
    """
    today = (datetime.date.today() - datetime.timedelta(days = 1))
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'

    district_rows = []
    # run for every state
    for state_code in states_all:
        params = {
            's_id': states_all[state_code].get('cowin_code'),
            'd_id': '',
            'd': today.strftime("%Y-%m-%d")
        }
        state_url = base_url.format(**params)
        print(state_url)
        resp = requests.request('GET', state_url)
        state_data = resp.json()
        age_groups = state_data['vaccinationByAge'] if 'vaccinationByAge' in state_data else state_data['topBlock'].get('vaccination')

        print('printing for ', states_all[state_code].get('name'), '---> all districts')
        with open(VACC_TXT, 'a') as file:
            datum = [
                today.strftime('%d-%m-%Y'), \
                states_all[state_code].get('name'), \
                'TEST_districtName', \
                state_data['topBlock'].get('vaccination')['total'], \
                state_data['topBlock']['sessions']['total'], \
                state_data['topBlock']['sites']['total'], \
                state_data['topBlock']['vaccination']['tot_dose_1'], \
                state_data['topBlock']['vaccination']['tot_dose_2'], \
                state_data['topBlock']['vaccination']['male'], \
                state_data['topBlock']['vaccination']['female'], \
                state_data['topBlock']['vaccination']['others'], \
                state_data['topBlock']['vaccination']['covaxin'], \
                state_data['topBlock']['vaccination']['covishield'], \
                state_data['topBlock']['vaccination'].get('sputnik'), \
                state_data['topBlock']['vaccination'].get('aefi'), \
                state_data['vaccinationByAge'].get('vac_18_45'), \
                state_data['vaccinationByAge'].get('vac_45_60'), \
                state_data['vaccinationByAge'].get('above_60')
            ]

            datum = ','.join(map(str, datum))
            print(datum, file=file)

        # run for every district within each state
        for district in state_data['getBeneficiariesGroupBy']:
            params = {
                's_id': states_all[state_code].get('cowin_code'),
                'd_id': district['district_id'],
                'd': today.strftime("%Y-%m-%d")
            }
            district_url = base_url.format(**params)
            resp = requests.request('GET', district_url)
            district_data = resp.json()
            print('printing for ', states_all[state_code].get('name'), '--->', district['title'])
            with open(VACC_TXT, 'a') as file:
                datum = {
                    'updated_at': today.strftime('%d-%m-%Y'), \
                    'State': states_all[state_code].get('name'), \
                    'District': district['title'], \
                    'Total Doses Administered': district_data['topBlock'].get('vaccination').get('total'), \
                    'Sessions': district_data['topBlock'].get('sessions').get('total'), \
                    'Sites': district_data['topBlock'].get('sites').get('total'), \
                    'First Dose Administered': district_data['topBlock'].get('vaccination').get('tot_dose_1'), \
                    'Second Dose Administered': district_data['topBlock'].get('vaccination').get('tot_dose_2'), \
                    'Male(Doses Administered)': district_data['topBlock'].get('vaccination').get('male'), \
                    'Female(Doses Administered)': district_data['topBlock'].get('vaccination').get('female'), \
                    'Transgender(Doses Administered)': district_data['topBlock'].get('vaccination').get('others'), \
                    'Covaxin (Doses Administered)': district_data['topBlock'].get('vaccination').get('covaxin'), \
                    'Covishield (Doses Administered)': district_data['topBlock'].get('vaccination').get('covishield'), \
                    # Enable these if necessary
                    # 'Sputnik (Doses Administered)': district_data['topBlock'].get('vaccination').get('sputnik'), \
                    # 'Aefi': district_data['topBlock'].get('vaccination').get('aefi'), \
                    # '18-45 (Doses administered)': district_data['vaccinationByAge'].get('vac_18_45'), \
                    # '45-60 (Doses administered)': district_data['vaccinationByAge'].get('vac_45_60'), \
                    # 'Above 60 (Doses administered)': district_data['vaccinationByAge'].get('above_60')
                }

                district_rows.append(datum)
                datum = [str(v) for k, v in datum.items()]
                datum = ','.join(datum)
                print(datum, file=file)
        
    print("Making districts data file")
    district_data = pd.DataFrame(district_rows).drop('updated_at', 1)
    district_data.to_csv(os.path.join('_outputs', 'district_data_vaccines.csv'), index=False)
    
    print("Getting district data from google sheet")
    public_data = pd.read_csv(DISTRICTS_DATA_SHEET)
    temp = public_data[['State_Code', 'State', 'District']].drop(0, axis=0)
    merged_data = pd.merge(temp, district_data, on=['State', 'District'])
    merged_data.columns = pd.MultiIndex.from_tuples([('' if k in ('State_Code', 'State', 'District') else '2020-12-03', k) for k in merged_data.columns])
    merged_data.to_csv(os.path.join('_outputs', 'merged_district_data.csv'), index=False)

get_vaccination()




def download_pdf(url, save_as):
    '''
    :param: url         - to download from
    :param: save_as     - filename to save it as
    '''
    r = requests.get(url, allow_redirects=True, verify=False)
    DOWNLOADED_PDF = os.path.join(INPUTS_DIR, save_as + '.pdf')
    open(DOWNLOADED_PDF, 'wb').write(r.content)
    url = DOWNLOADED_PDF

### -- Rajaram's code

'''
opt = {
    'name': 'Vaccination MOHFW',
    'type': 'pdf',
    'url': 'https://raw.githubusercontent.com/datameet/covid19/master/downloads/mohfw-backup/cumulative_vaccination_coverage/',
    'config': {
        'page': 1,
        'lookback': 25,
        'start_key': 'auto',
        'end_key': 'auto'
    }
}
'''

def VCMGetData(pageId):
    print("Date, State, First Dose, Second Dose, Total Doses\n")

    #new file for backlog storage
    text_file = open(VCMBL_CSV, 'w')
    row=''

    lookback = int(pageId) if len(pageId) != 0 else 0
    #forced loops for number of days
    #lookback=25

    for day in range(lookback, -1, -1):
        today = (datetime.date.today() - datetime.timedelta(days = day)).strftime("%Y-%m-%d")
        fileName = today+"-at-07-00-AM.pdf"

        pageId = "1"

        # downloading pdf file from url (use requests)
        readFileFromURLV2(metaDictionary['VCMohfw'].url + fileName, "VCMohfw", "A & N Islands", "")
        # Example of url: https://raw.githubusercontent.com/datameet/covid19/master/downloads/mohfw-backup/cumulative_vaccination_coverage/2021-11-11-at-07-00-AM.pdf
        # Another url: https://www.mohfw.gov.in/pdf/CummulativeCovidVaccinationReport04november2021.pdf
        dadra = {'firstDose': 0, 'secondDose': 0, 'totalDose': 0}

        #have date format match with our sheet
        todayp = (datetime.date.today() - datetime.timedelta(days = day)).strftime("%d/%m/%Y")

        #initialize for Inida total
        IndiaFirstDose=0
        IndiaSecondDose=0
        IndiaTotalDose=0

        try:
            with open(".tmp/vcm.csv", "r") as upFile:
                for line in upFile:
                    #Check if some pdf files end Misc total split to additional lines
                    if len(line.split(',')) != 1:
                        if "Miscellaneous" in line:
                            #trap & rework Misc
                            miscline=line
                            continue

                    IndiaFirstDose += int(line.split(',')[1])
                    IndiaSecondDose += int(line.split(',')[2])
                    IndiaTotalDose += int(line.split(',')[3])

                    if "Dadra" in line or "Daman" in line:
                        dadra['firstDose'] += int(line.split(',')[1])
                        dadra['secondDose'] += int(line.split(',')[2])
                        dadra['totalDose'] += int(line.split(',')[3])
                        continue

                    #A & N name mapping
                    if "A & N Islands" in line:
                        row += str("{},Andaman and Nicobar Islands,{},{},{}\n".format(todayp, int(line.split(',')[1]), int(line.split(',')[2]), int(line.split(',')[3])))
                        #print(row)
                    else:
                        #print(todayp + "," + line, end = "")
                        row += str(todayp + "," + line)
                    else:
                        #trap & club all misc lines at end
                        miscline += line

                #add clubbed Dadra Daman last
                row += str("{},Dadra and Nagar Haveli and Daman and Diu,{},{},{}\n".format(todayp, dadra['firstDose'], dadra['secondDose'], dadra['totalDose']))

            #rework on Misc line issue to sortout
            miscline=miscline.replace ('\n', '')
            print(miscline)

            if miscline != '':
                miscFirstDose = int(miscline.split(',')[1])
                miscSecondDose = int(miscline.split(',')[2])
                miscTotalDose = int(miscline.split(',')[3].lstrip('0'))
                IndiaFirstDose += miscFirstDose
                IndiaSecondDose += miscSecondDose
                IndiaTotalDose += miscTotalDose
                row += str("{},Miscellaneous,{},{},{}\n".format(todayp, miscFirstDose, miscSecondDose, miscTotalDose))
            row += str("{},Total,{},{},{}\n".format(todayp, IndiaFirstDose, IndiaSecondDose, IndiaTotalDose))
            print(row)

        except FileNotFoundError:
            print("br.txt missing. Generate through pdf or ocr and rerun.")

    #File write
    n = text_file.write(row)

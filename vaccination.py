import os
import re
import yaml
import datetime
import requests

VACC_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination.txt')
VCMBL_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vcmbl.csv')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')

with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)


def get_vaccination():
    today = (datetime.date.today() - datetime.timedelta(days = 1))
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'

    # run for every state
    for state_code in states_all:
        params = {
            's_id': states_all[state_code]['cowin_code'],
            'd_id': '',
            'd': today.strftime("%Y-%m-%d")
        }
        state_url = base_url.format(**params)
        resp = requests.request('GET', state_url)
        state_data = resp.json()
        age_groups = state_data['vaccinationByAge'] if 'vaccinationByAge' in state_data else state_data['topBlock']['vaccination']

        print('printing for ', states_all[state_code]['name'], '---> all districts')
        with open(VACC_TXT,'a') as file:
            print("{}, {}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
            format(today.strftime('%d-%m-%Y'), \
                states_all[state_code]['name'], \
                'TEST_districtName', \
                state_data['topBlock']['vaccination']['today'], \
                state_data['topBlock']['vaccination']['total'], \
                state_data['topBlock']['sessions']['total'], \
                state_data['topBlock']['sites']['total'], \
                state_data['topBlock']['vaccination']['tot_dose_1'], \
                state_data['topBlock']['vaccination']['tot_dose_2'], \
                state_data['topBlock']['vaccination']['male'], \
                state_data['topBlock']['vaccination']['female'], \
                state_data['topBlock']['vaccination']['others'], \
                state_data['topBlock']['vaccination']['covaxin'], \
                state_data['topBlock']['vaccination']['covishield'], \
            ), file = file)

        # run for every district within each state
        for district in state_data['getBeneficiariesGroupBy']:
            params = {
                's_id': states_all[state_code]['cowin_code'],
                'd_id': district['district_id'],
                'd': today.strftime("%Y-%m-%d")
            }
            district_url = base_url.format(**params)
            resp = requests.request('GET', district_url)
            district_data = resp.json()
            print('printing for ', states_all[state_code]['name'], '--->', district['title'])
            with open(VACC_TXT,'a') as file:
                print("{}, {}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
                format(today.strftime('%d-%m-%Y'), \
                    states_all[state_code]['name'], \
                    district['title'], \
                    district_data['topBlock']['vaccination']['today'], \
                    district_data['topBlock']['vaccination']['total'], \
                    district_data['topBlock']['sessions']['total'], \
                    district_data['topBlock']['sites']['total'], \
                    district_data['topBlock']['vaccination']['tot_dose_1'], \
                    district_data['topBlock']['vaccination']['tot_dose_2'], \
                    district_data['topBlock']['vaccination']['male'], \
                    district_data['topBlock']['vaccination']['female'], \
                    district_data['topBlock']['vaccination']['others'], \
                    district_data['topBlock']['vaccination']['covaxin'], \
                    district_data['topBlock']['vaccination']['covishield'], \
                ), file = file)

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
    'state_code': 'VCMBL',
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
        # read_pdf(opt) ## this will write into `vcmbl0.pdf.txt` and `vcmbl.csv`
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

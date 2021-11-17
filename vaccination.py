import os
import re
import yaml
import datetime
import requests

VACC_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination.txt')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')

with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

# for state_code in states_all:
#     print(states_all[state_code]['name'], states_all[state_code]['cowin_code'])

def new_function():
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id=@@state_id@@&district_id=@@district_id@@&date=@@date@@'
    today = (datetime.date.today() - datetime.timedelta(days = 1))

    # run for India
    url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'

    # run for every state
    for state_code in states_all:
        params = {
            's_id': states_all[state_code]['cowin_code'],
            'd_id': '',
            'd': today.strftime("%Y-%m-%d")
        }
        state_url = url.format(**params)
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

        for district in state_data['getBeneficiariesGroupBy']:
            params = {
                's_id': states_all[state_code]['cowin_code'],
                'd_id': district['district_id'],
                'd': today.strftime("%Y-%m-%d")
            }
            district_url = url.format(**params)
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

            # url_district = re.sub('@@district_id@@', str(district['district_id']), re.sub('@@state_id@@', str(state_code), url))
            # if option == "V2":
                # getAndPrintVaccineDataV2(url_district, state_code, todayStr, stateKeys, district['district_name'])
            # else:
                # getAndPrintVaccineDataV1(url_district, state_code, todayStr, stateKeys, district['district_name'])


# --------
def getAndPrintVaccineDataV2(url, state_code, todayStr, stateKeys, districtName):

    vaccineDashboard = requests.request("get", url)
    if vaccineDashboard.status_code != 200:
        while True:
            vaccineDashboard = requests.request("get", url)
            if vaccineDashboard.status_code == 200:
                break
    vaccineDashboard = vaccineDashboard.json()

    if not vaccineDashboard:
        return

    category = vaccineDashboard['topBlock']['vaccination']
    if 'vaccinationByAge' in vaccineDashboard.keys():
        category = vaccineDashboard['vaccinationByAge']

    print("{}, {}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
        format(todayStr, \
            stateKeys[str(state_code)], \
            districtName, \
            vaccineDashboard['topBlock']['vaccination']['today'], \
            vaccineDashboard['topBlock']['vaccination']['total'], \
            vaccineDashboard['topBlock']['sessions']['total'], \
            vaccineDashboard['topBlock']['sites']['total'], \
            vaccineDashboard['topBlock']['vaccination']['tot_dose_1'], \
            vaccineDashboard['topBlock']['vaccination']['tot_dose_2'], \
            vaccineDashboard['topBlock']['vaccination']['male'], \
            vaccineDashboard['topBlock']['vaccination']['female'], \
            vaccineDashboard['topBlock']['vaccination']['others'], \
            vaccineDashboard['topBlock']['vaccination']['covaxin'], \
            vaccineDashboard['topBlock']['vaccination']['covishield'], \
            vaccineDashboard['topBlock']['vaccination']['sputnik'], \
            vaccineDashboard['topBlock']['vaccination']['aefi'], \
            category['vac_18_45'], \
            category['vac_45_60'], \
            category['above_60']
        )
    )


    with open('output2.out','a') as file:
        print("{}, {}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
            format(todayStr, \
                stateKeys[str(state_code)], \
                districtName, \
                vaccineDashboard['topBlock']['vaccination']['today'], \
                vaccineDashboard['topBlock']['vaccination']['total'], \
                vaccineDashboard['topBlock']['sessions']['total'], \
                vaccineDashboard['topBlock']['sites']['total'], \
                vaccineDashboard['topBlock']['vaccination']['tot_dose_1'], \
                vaccineDashboard['topBlock']['vaccination']['tot_dose_2'], \
                vaccineDashboard['topBlock']['vaccination']['male'], \
                vaccineDashboard['topBlock']['vaccination']['female'], \
                vaccineDashboard['topBlock']['vaccination']['others'], \
                vaccineDashboard['topBlock']['vaccination']['covaxin'], \
                vaccineDashboard['topBlock']['vaccination']['covishield'], \
            ), file = file)
        return vaccineDashboard['getBeneficiariesGroupBy']


# def VCMGetData():
#   print("Date, State, First Dose, Second Dose, Total Doses")

#   # lookback = int(pageId) if len(pageId) != 0 else 0
#   lookback = 0
#   for day in range(lookback, -1, -1):
#     today = (datetime.date.today() - datetime.timedelta(days = day)).strftime("%Y-%m-%d")
#     fileName=today+"-at-07-00-AM.pdf"

#     pageId = "1"

#     readFileFromURLV2(metaDictionary['VCMohfw'].url + fileName, "VCMohfw", "A & N Islands", "")
#     dadra = {'firstDose': 0, 'secondDose': 0, 'totalDose': 0}

#     try:
#       with open(".tmp/vcm.csv", "r") as upFile:
#         for line in upFile:
#           if "Dadra" in line or "Daman" in line:
#             dadra['firstDose'] += int(line.split(',')[1])
#             dadra['secondDose'] += int(line.split(',')[2])
#             dadra['totalDose'] += int(line.split(',')[3])
#             continue
#           print(today + "," + line, end = "")

#       print("{}, DnH, {}, {}, {}".format(today, dadra['firstDose'], dadra['secondDose'], dadra['totalDose']))
#     except FileNotFoundError:
#       print("br.txt missing. Generate through pdf or ocr and rerun.")

def VCGetData():
  today = (datetime.date.today() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
  #proxy = {"https":"http://159.65.153.14:8080"}
  #vaccineDashboardNation = requests.request("get", "https://api.cowin.gov.in/api/v1/reports/getPublicReports?state_id=&district_id=&date=2021-03-01").json()
  stateKeys = {
    '36': 'West Bengal',
    '7': 'Chhattisgarh',
    '31': 'Tamil Nadu',
    '20': 'Madhya Pradesh',
    '13': 'Himachal Pradesh',
    '4': 'Assam',
    '15': 'Jharkhand',
    '11': 'Gujarat',
    '28': 'Punjab',
    '17': 'Kerala',
    '32': 'Telangana',
    '33': 'Tripura',
    '10': 'Goa',
    '14': 'Jammu and Kashmir',
    '34': 'Uttar Pradesh',
    '29': 'Rajasthan',
    '5': 'Bihar',
    '21': 'Maharashtra',
    '2': 'Andhra Pradesh',
    '16': 'Karnataka',
    '35': 'Uttarakhand',
    '26': 'Odisha',
    '12': 'Haryana',
    '3': 'Arunachal Pradesh',
    '9': 'Delhi',
    '1': 'Andaman and Nicobar Islands',
    '24': 'Mizoram',
    '23': 'Meghalaya',
    '27': 'Puducherry',
    '18': 'Ladakh',
    '30': 'Sikkim',
    '25': 'Nagaland',
    '37': 'Daman and Diu',
    '22': 'Manipur',
    '39': 'Himachal',
    '6': 'Chandigarh',
    '8': 'Dadra and Nagar Haveli',
    '19': 'Lakshadweep',
    '0': 'India'
  }

  lookback = 0
  option = 'V2'

  # lookback = int(pageId) if len(pageId) != 0 else 0
  lookbackMaxDate = datetime.date(2021, 5, 21)
  if datetime.date.today() - datetime.timedelta(days = lookback) < lookbackMaxDate:
    lookback = (datetime.date.today() - lookbackMaxDate).days
    print("------------ Data beyond 21st May has different data ranges hence defaulting max lookback to max {} days--------- ".format(lookback))
  print("date, state, district, daily vaccine count, beneficiaries, sessions, sites, vaccines given, vaccines given dose two, male, female, others, covaxin, covishield, sputnik, aefi, 18-45, 45-60, 60+")

  for day in range (lookback, -1, -1):
    today = (datetime.date.today() - datetime.timedelta(days = day)).strftime("%Y-%m-%d")
    todayStr = (datetime.date.today() - datetime.timedelta(days = day)).strftime("%d-%m-%Y")
    if option == "V2":
      metaDictionary['Vaccine'].url = "https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id=@@state_id@@&district_id=@@district_id@@&date=@@date@@"
    url = re.sub('@@date@@', today, metaDictionary['Vaccine'].url)
    url_nation = re.sub('@@district_id@@', '', re.sub('@@state_id@@', '', url))

    if option == "V2":
      districtArray = getAndPrintVaccineDataV2(url_nation, '0', todayStr, stateKeys, '')
    else:
      districtArray = getAndPrintVaccineDataV1(url_nation, '0', todayStr, stateKeys, '')


    for state_code in range(1, 38, 1):
      url_state = re.sub('@@district_id@@', '', re.sub('@@state_id@@', str(state_code), url))
      districtArray = []

      if option == "V2":
        districtArray = getAndPrintVaccineDataV2(url_state, state_code, todayStr, stateKeys, '')
      else:
        districtArray = getAndPrintVaccineDataV1(url_state, state_code, todayStr, stateKeys, '')

      if not districtArray:
        continue
      for district in districtArray:
        url_district = re.sub('@@district_id@@', str(district['district_id']), re.sub('@@state_id@@', str(state_code), url))
        if option == "V2":
          getAndPrintVaccineDataV2(url_district, state_code, todayStr, stateKeys, district['district_name'])
        else:
          getAndPrintVaccineDataV1(url_district, state_code, todayStr, stateKeys, district['district_name'])

# def getAndPrintVaccineDataV1(url, state_code, todayStr, stateKeys, districtName):

#   vaccineDashboard = requests.request("get", url)
#   if vaccineDashboard.status_code != 200:
#     while True:
#       vaccineDashboard = requests.request("get", url)
#       if vaccineDashboard.status_code == 200:
#         break
#   vaccineDashboard = vaccineDashboard.json()
#   if not vaccineDashboard:
#     return
#   gender = {'male': 0, 'female': 0, 'others': 0}
#   #print(vaccineDashboard)
#   for i in range (0, 3, 1):
#     if vaccineDashboard['vaccinatedBeneficiaryByGender'][i]['gender_label'].lower() == 'male':
#       gender['male'] = vaccineDashboard['vaccinatedBeneficiaryByGender'][i]['count']
#     if vaccineDashboard['vaccinatedBeneficiaryByGender'][i]['gender_label'].lower() == 'female':
#       gender['female'] = vaccineDashboard['vaccinatedBeneficiaryByGender'][i]['count']
#     if vaccineDashboard['vaccinatedBeneficiaryByGender'][i]['gender_label'].lower() == 'others':
#       gender['others'] = vaccineDashboard['vaccinatedBeneficiaryByGender'][i]['count']

#   typeOfVaccine = {'covaxin': 0, 'covishield': 0}
#   for i in range (0, 2, 1):
#     if vaccineDashboard['vaccinatedBeneficiaryByMaterial'][i]['material_name'].lower() == 'covaxin':
#       typeOfVaccine['covaxin'] = vaccineDashboard['vaccinatedBeneficiaryByMaterial'][i]['count']
#     if vaccineDashboard['vaccinatedBeneficiaryByMaterial'][i]['material_name'].lower() == 'covishield':
#       typeOfVaccine['covishield'] = vaccineDashboard['vaccinatedBeneficiaryByMaterial'][i]['count']

#   print("{}, {}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
#       format(todayStr, \
#         stateKeys[str(state_code)], \
#         districtName, \
#         vaccineDashboard['dailyVaccineData']['vaccine_given'], \
#         vaccineDashboard['overAllReports']['Beneficiaries'], \
#         vaccineDashboard['overAllReports']['Sessions'], \
#         vaccineDashboard['overAllReports']['Sites'], \
#         vaccineDashboard['overAllReports']['Vaccine Given'], \
#         vaccineDashboard['overAllReports']['Vaccine Given Dose Two'], \
#         gender['male'], \
#         gender['female'], \
#         gender['others'], \
#         typeOfVaccine['covaxin'], \
#         typeOfVaccine['covishield']
#         ))
#   with open('output.out','a') as file:
#     print("{}, {}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
#     format(todayStr, \
#       stateKeys[str(state_code)], \
#       districtName, \
#       vaccineDashboard['dailyVaccineData']['vaccine_given'], \
#       vaccineDashboard['overAllReports']['Beneficiaries'], \
#       vaccineDashboard['overAllReports']['Sessions'], \
#       vaccineDashboard['overAllReports']['Sites'], \
#       vaccineDashboard['overAllReports']['Vaccine Given'], \
#       vaccineDashboard['overAllReports']['Vaccine Given Dose Two'], \
#       gender['male'], \
#       gender['female'], \
#       gender['others'], \
#       typeOfVaccine['covaxin'], \
#       typeOfVaccine['covishield']
#       ), file = file)
#   return vaccineDashboard['getBeneficiariesGroupBy']


#   category = vaccineDashboard['topBlock']['vaccination']
#   if 'vaccinationByAge' in vaccineDashboard.keys():
#     category = vaccineDashboard['vaccinationByAge']

#   print("{}, {}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
#     format(todayStr, \
#       stateKeys[str(state_code)], \
#       districtName, \
#       vaccineDashboard['topBlock']['vaccination']['today'], \
#       vaccineDashboard['topBlock']['vaccination']['total'], \
#       vaccineDashboard['topBlock']['sessions']['total'], \
#       vaccineDashboard['topBlock']['sites']['total'], \
#       vaccineDashboard['topBlock']['vaccination']['tot_dose_1'], \
#       vaccineDashboard['topBlock']['vaccination']['tot_dose_2'], \
#       vaccineDashboard['topBlock']['vaccination']['male'], \
#       vaccineDashboard['topBlock']['vaccination']['female'], \
#       vaccineDashboard['topBlock']['vaccination']['others'], \
#       vaccineDashboard['topBlock']['vaccination']['covaxin'], \
#       vaccineDashboard['topBlock']['vaccination']['covishield'], \
#       vaccineDashboard['topBlock']['vaccination']['sputnik'], \
#       vaccineDashboard['topBlock']['vaccination']['aefi'], \
#       category['vac_18_45'], \
#       category['vac_45_60'], \
#       category['above_60']
#     )
#   )


#   with open('output2.out','a') as file:
#     print("{}, {}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ". \
#     format(todayStr, \
#       stateKeys[str(state_code)], \
#       districtName, \
#       vaccineDashboard['topBlock']['vaccination']['today'], \
#       vaccineDashboard['topBlock']['vaccination']['total'], \
#       vaccineDashboard['topBlock']['sessions']['total'], \
#       vaccineDashboard['topBlock']['sites']['total'], \
#       vaccineDashboard['topBlock']['vaccination']['tot_dose_1'], \
#       vaccineDashboard['topBlock']['vaccination']['tot_dose_2'], \
#       vaccineDashboard['topBlock']['vaccination']['male'], \
#       vaccineDashboard['topBlock']['vaccination']['female'], \
#       vaccineDashboard['topBlock']['vaccination']['others'], \
#       vaccineDashboard['topBlock']['vaccination']['covaxin'], \
#       vaccineDashboard['topBlock']['vaccination']['covishield'], \
#       ), file = file)
#   return vaccineDashboard['getBeneficiariesGroupBy']

def loadMetaData():
  with open("automation.meta", "r") as metaFile:
    for line in metaFile:
      if line.startswith('#'):
        continue
      lineArray = line.strip().split(',')
      metaObject = AutomationMeta(lineArray[0].strip(), lineArray[1].strip(), lineArray[2].strip())
      metaDictionary[lineArray[0].strip()] = metaObject
  metaFile.close()

new_function()

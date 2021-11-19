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

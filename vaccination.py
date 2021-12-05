import os
import re
import yaml
import datetime
import requests
import warnings
import pandas as pd

warnings.simplefilter(action='ignore')

VACC_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination.txt')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')
DISTRICTS_DATA_SHEET = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTrt_V4yW0jd91chhz9BJZOgJtFrsaZEa_gPlrFfQToBuuNDDkn01w0K0GdnjCdklyzFz84A1hFbSUN/pub?gid=382746758&single=true&output=csv'

with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)


def get_vaccination(lookback=1):
    '''
    For a given number of days, gets state and district-wise vaccination data from CoWIN API

    :param: `lookback` <int> - The number of days to pull back from

    :returns: None - Writes the output to following files
        vaccination state level -> `_outputs/vaccination.txt`
        vaccination distr level -> `_outputs/...`
    '''
    today = (datetime.date.today() - datetime.timedelta(days=lookback))
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
            try:
                resp = requests.request('GET', district_url)
                district_data = resp.json()
            except:
                print(district_url)
                print(resp)
                import pdb
                pdb.set_trace()

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
    merged_data = pd.merge(temp, district_data, on=['State', 'District'], how='left')
    merged_data.columns = pd.MultiIndex.from_tuples([('' if k in ('State_Code', 'State', 'District') else '2020-12-03', k) for k in merged_data.columns])
    merged_data.to_csv(os.path.join('_outputs', 'merged_district_data.csv'), index=False)

get_vaccination()

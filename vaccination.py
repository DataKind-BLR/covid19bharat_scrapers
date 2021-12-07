import os
import re
import yaml
import datetime
import requests
import warnings
import pandas as pd

warnings.simplefilter(action='ignore')

VACC_STA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_state_level.txt')
VACC_DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_district_level.csv')
VACC_DST_COWIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_cowin_district_level.csv')

STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')
DISTRICTS_DATA_SHEET = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTrt_V4yW0jd91chhz9BJZOgJtFrsaZEa_gPlrFfQToBuuNDDkn01w0K0GdnjCdklyzFz84A1hFbSUN/pub?gid=382746758&single=true&output=csv'

with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)


def get_vaccination_state_level(lookback=0):
    '''
    For a given number of days, gets state vaccination data from CoWIN API

    :param: `lookback` <int> - The number of days to pull back from. If 0, then will only take current date

    :returns: None - Writes the output to following files
        vaccination state level -> `_outputs/vaccination_state_level.txt`
        vaccination distr level -> `_outputs/vaccination_district_level.csv`
    '''
    today = datetime.date.today()
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'

    # append code for cases at nation level
    states_all['in'] = {
        'cowin_code': '',
        'name': 'India'
    }

    for day in range (lookback, -1, -1):
        curr_date = today - datetime.timedelta(days=day)
        curr_date_str = curr_date.strftime('%d-%m-%Y')
        # print('Fetching for {}'.format(curr_date_str))
        district_rows = []

        # run for every state
        for state_code in states_all:
            params = {
                's_id': states_all[state_code].get('cowin_code'),
                'd_id': '',
                'd': curr_date.strftime("%Y-%m-%d")
            }
            state_url = base_url.format(**params)
            resp = requests.request('GET', state_url)
            state_data = resp.json()
            age_groups = state_data['vaccinationByAge'] if 'vaccinationByAge' in state_data else state_data['topBlock'].get('vaccination')

            print('printing for ', states_all[state_code].get('name'), '---> all districts', state_url)
            with open(VACC_STA, 'a') as file:
                datum = [
                    curr_date_str, \
                    states_all[state_code].get('name'), \
                    # 'TEST_districtName', \
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

def get_vaccination(lookback=0):
    '''
    For a given number of days, gets state and district-wise vaccination data from CoWIN API

    :param: `lookback` <int> - The number of days to pull back from. If 0, then will only take current date

    :returns: None - Writes the output to following files
        vaccination state level -> `_outputs/vaccination_state_level.txt`
        vaccination distr level -> `_outputs/vaccination_district_level.csv`
    '''
    today = datetime.date.today()
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'
    states_all['in'] = {
        'cowin_code': '',
        'name': 'India'
    }

    for day in range (lookback, -1, -1):
        # curr_date = today - datetime.timedelta(days=day)
        curr_date = datetime.datetime(2021, 10, 31)
        curr_date_str = curr_date.strftime('%d-%m-%Y')
        print('Fetching for {}'.format(curr_date_str))
        district_rows = []

        # run for every state
        for state_code in states_all:
            params = {
                's_id': states_all[state_code].get('cowin_code'),
                'd_id': '',
                'd': curr_date.strftime("%Y-%m-%d")
            }
            state_url = base_url.format(**params)
            print(state_url)
            resp = requests.request('GET', state_url)
            state_data = resp.json()
            age_groups = state_data['vaccinationByAge'] if 'vaccinationByAge' in state_data else state_data['topBlock'].get('vaccination')

            print('printing for ', states_all[state_code].get('name'), '---> all districts')
            with open(VACC_STA, 'a') as file:
                datum = [
                    curr_date_str, \
                    states_all[state_code].get('name'), \
                    # 'TEST_districtName', \
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
                    'd': curr_date.strftime("%Y-%m-%d")
                }
                district_url = base_url.format(**params)
                try:
                    resp = requests.request('GET', district_url)
                    district_data = resp.json()
                except:
                    print(district_url)
                    print(resp)

                print('printing for ', states_all[state_code].get('name'), '--->', district['title'])
                with open(VACC_STA, 'a') as file:
                    datum = {
                        'updated_at': curr_date_str, \
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
    district_data.to_csv(VACC_DST_COWIN, index=False)

    print("Getting state-district mapping from google sheet")
    public_data = pd.read_csv(DISTRICTS_DATA_SHEET)
    state_dist_mapping = public_data[['State_Code', 'State', 'District']].drop(0, axis=0)
    merged_data = pd.merge(state_dist_mapping, district_data, on=['State', 'District'], how='left')
    merged_data.columns = pd.MultiIndex.from_tuples([('' if k in ('State_Code', 'State', 'District') else curr_date_str, k) for k in merged_data.columns])

    merged_data.to_csv(VACC_DST, index=False)
    print("District data is saved to: ", VACC_DST)

get_vaccination_state_level(lookback=1)

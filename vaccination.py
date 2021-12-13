import os
import re
import yaml
import argparse
import datetime
import requests
import warnings
import pandas as pd
from rich.console import Console
from read_pdf import read_pdf_from_url

console = Console(record=True)
warnings.simplefilter(action='ignore')

VACC_STA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_state_level.txt')
VACC_DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_district_level.csv')
VACC_OUTPUT_MOHFW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_mohfw.csv')

STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')
DISTRICTS_DATA_SHEET = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTrt_V4yW0jd91chhz9BJZOgJtFrsaZEa_gPlrFfQToBuuNDDkn01w0K0GdnjCdklyzFz84A1hFbSUN/pub?gid=382746758&single=true&output=csv'
TODAY = datetime.date.today()

with open(STATES_YAML, 'r') as stream:
    try:
        states_all = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def get_mohfw_state(data_for=TODAY - datetime.timedelta(days=1)):
    '''
    Given a specific date (PDF date), download the pdf for the specified date. Contains data at state level & national level
    NOTE: data in the PDF for current day (T) contains the values for the previous day (T-1)

    :param: - `data_for` (datetime object). Defaults to T-1 day (today)
    '''
    base_url = "https://www.mohfw.gov.in/pdf/CummulativeCovidVaccinationReport{}.pdf"
    date_mohfw_str = data_for.strftime("%d%B%Y")
    date_sheet_str = data_for.strftime("%d/%m/%Y")
    url = base_url.format(date_mohfw_str.lower())
    print(f" ---------> Downloading PDF from: {url}")

    # if you change this variable value, you'll have to change the function name inside `read_pdf.py` file too
    vacc_mohfw_code = 'vaccination_mohfw'

    opt = {
        'state_code': vacc_mohfw_code,
        'url': url,
        'type': 'pdf',
        'config': {
            'page': 1,
            'start_key': 'A & N Islands',
            'end_key': ''
        }
    }
    name_mapping = {
        'A & N Islands': 'Andaman and Nicobar Islands'
    }

    # read pdf file and extract text
    read_pdf_from_url(opt)

    # read the csv output produced by previous function
    mohfw_data = []
    total_fd, total_sd, total_td = 0, 0, 0
    with open(VACC_OUTPUT_MOHFW, "r") as output_csv:
        for line in output_csv:
            lines_arr = line.split(',')
            if len(lines_arr) != 4:
                print("--> Issue with {}".format(lines_arr))
                continue

            data = {}
            data['state_name'] = lines_arr[0].strip()
            if lines_arr[0].strip() == 'A & N Islands':
                data['state_name'] = 'Andaman and Nicobar Islands'
            data['firstDose'] = int(lines_arr[1])
            total_fd += data['firstDose']
            data['secondDose'] = int(lines_arr[2])
            total_sd += data['secondDose']
            data['totalDose'] = int(lines_arr[3].strip('\n'))
            total_td += data['totalDose']

            # print on console for copy-paste purpose
            console.print(f"{date_sheet_str},{data['state_name']},{data['firstDose']},{data['secondDose']},{data['totalDose']}")

            mohfw_data.append(data)
    # print totals for India
    console.print(f"{date_sheet_str},Total,{total_fd},{total_sd},{total_td}")
    return mohfw_data


def get_cowin_state(date_for=TODAY):
    '''
    For a given number of days, gets state vaccination data from CoWIN API

    :param: `lookback` <int> - The number of days to pull back from. If 0, then will only take current date

    :returns: None - Appends the output to following files
        vaccination state level -> `_outputs/vaccination_state_level.txt`
    '''
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'

    # append code for cases at nation level
    states_all['in'] = {
        'cowin_code': '',
        'name': 'India'
    }

    # for day in range (lookback, -1, -1):
    # TODAY - datetime.timedelta(days=day)
    curr_date = date_for
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


def get_cowin_district(data_for=TODAY):
    '''
    For a given number of days, gets state and district-wise vaccination data from CoWIN API

    :param: `lookback` <int> - The number of days to pull back from. If 0, then will only take current date

    :returns: None - Writes the output to following files
        vaccination state level -> `_outputs/vaccination_state_level.txt`
        vaccination distr level -> `_outputs/vaccination_district_level.csv`
    '''
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'
    states_all['in'] = {
        'cowin_code': '',
        'name': 'India'
    }

    # for day in range (lookback, -1, -1):
    # curr_date = TODAY - datetime.timedelta(days=day)
    curr_date = data_for
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

        # run for every district within each state
        for district in state_data['getBeneficiariesGroupBy']:
            if states_all[state_code].get('name') != 'India':
                params = {
                    's_id': states_all[state_code].get('cowin_code'),
                    'd_id': district.get('district_id'),
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
                        'State': states_all[state_code].get('name', '').strip(), \
                        'District': district['title'].strip(), \
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
    VACC_DST_COWIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'vaccination_cowin_district_level.csv')
    district_data.to_csv(VACC_DST_COWIN, index=False)

    print("Getting state-district mapping from google sheet")
    public_data = pd.read_csv(DISTRICTS_DATA_SHEET)
    state_dist_mapping = public_data[['State_Code', 'State', 'Cowin Key', 'District']].drop(0, axis=0)
    merged_data = pd.merge(state_dist_mapping, district_data, left_on=['State', 'Cowin Key'], right_on=['State', 'District'], how='left', suffixes=('', '_cowin'))
    # we are keeping district names from Covid19Bharat's google sheet and ignoring the API ones.
    merged_data = merged_data.drop(['Cowin Key', 'District_cowin'], 1)
    merged_data.columns = pd.MultiIndex.from_tuples([('' if k in ('State_Code', 'State', 'District') else curr_date_str, k) for k in merged_data.columns])

    merged_data.to_csv(VACC_DST, index=False)
    print("District data is saved to: ", VACC_DST)


def util_date(str_date, frmt='%d-%m-%Y'):
    '''
    given a date in dd-mm-yyyy format, create and return a datetime object
    '''
    arr_date = str_date.split('-')
    return datetime.datetime(arr_date[0], arr_date[1], arr_date[2])

if __name__ == '__main__':
    fn_map = {
        'cowin_state': get_cowin_state,
        'cowin_district': get_cowin_district,
        'mohfw_state': get_mohfw_state
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str, nargs='?', default='cowin_state', help='cowin or mohfw', choices=['cowin_state', 'cowin_district', 'mohfw_state'])
    # parser.add_argument('-d', '--date', type=str, help='please provide date in dd-mm-yyyy format only', default=datetime.date.today())

    args = parser.parse_args()
    vacc_src = args.source.lower()

    if vacc_src not in fn_map.keys():
        parser.print_help()
        sys.exit(0)

    fn_map[vacc_src]()

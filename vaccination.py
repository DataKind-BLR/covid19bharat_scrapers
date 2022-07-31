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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VACC_STA = os.path.join(ROOT_DIR, '_outputs', 'vaccination_state_level.txt')
VACC_DST = os.path.join(ROOT_DIR, '_outputs', 'vaccination_district_level.csv')
VACC_OUTPUT_MOHFW = os.path.join(ROOT_DIR, '_outputs', 'vaccination_mohfw.csv')
COWIN_META = os.path.join(ROOT_DIR, '_meta', 'cowin_district_mapping.csv')
COWIN_DIST_LIVE = os.path.join(ROOT_DIR, '_outputs', 'cowin_downloaded_district_data.csv')
STATES_YAML = os.path.join(ROOT_DIR, 'states.yaml')
IGNORE_STATE_CODES = ['KLD', 'KLDBL']

with open(STATES_YAML, 'r') as stream:
    try:
        states_all = yaml.safe_load(stream)
        # append code for cases at nation level
        states_all['in'] = {
            'cowin_code': '',
            'name': 'India'
        }
    except yaml.YAMLError as exc:
        print(exc)


def get_district_mapping(sheet_url='https://docs.google.com/spreadsheets/d/e/2PACX-1vTrt_V4yW0jd91chhz9BJZOgJtFrsaZEa_gPlrFfQToBuuNDDkn01w0K0GdnjCdklyzFz84A1hFbSUN/pub?gid=382746758&single=true&output=csv'):
    '''
    From the published google sheets url, extract district names to map against
    cowin's data

    :param: `sheet_url` <str> - the published url sheet to pull the district names from

    :returns: <os.path> - returns the path to the updated csv file
    '''
    published_df = pd.read_csv(sheet_url)
    state_dist_mapping = published_df[['State_Code', 'State', 'Cowin Key', 'District']]
    state_dist_mapping.to_csv(COWIN_META, index=False, encoding='utf-8')
    return COWIN_META

def get_mohfw_state(from_date, to_date, state_codes):
    '''
    Given a specific date (PDF date), download the pdf for the specified date. Contains data at state level & national level
    NOTE: data in the PDF for current day (T) contains the values for the previous day (T-1)

    :param: `from_date` <datetime> - The date to start extracting data from
    :param: `to_date` <datetime> - The date to until when you want extract data (inclusive)
    '''
    base_url = 'https://www.mohfw.gov.in/pdf/CummulativeCovidVaccinationReport{}.pdf'
    if from_date == datetime.date.today():
        #from_date = from_date - datetime.timedelta(days=1)
        day_count = datetime.timedelta(days=1)
    else:
        day_count = (to_date - from_date) + datetime.timedelta(days=1)
    # if you change this variable value, you'll have to change the function name inside `read_pdf.py` file too
    vacc_mohfw_code = 'vaccination_mohfw'
    name_mapping = {
        'A & N Islands': 'Andaman and Nicobar Islands',
        'Jammu & Kashmir': 'Jammu and Kashmir'
    }

    for curr_date in (from_date + datetime.timedelta(n) for n in range(day_count.days)):
        date_mohfw_str = curr_date.strftime("%d%b%Y")
        sheet_date = curr_date + datetime.timedelta(days=-1)
        date_sheet_str = sheet_date.strftime("%d/%m/%Y")
        #date_sheet_str = curr_date.strftime("%d/%m/%Y")
        #url = base_url.format(date_mohfw_str.lower())
        #MOHFW changed month capitalise
        url = base_url.format(date_mohfw_str)
        print(f" ---------> Downloading PDF from: {url}")
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
        #MOHFW added below 18 and above 18 as two categories along with precautionary dose
        # we read 2 dose-1, 2 dose-2, precautionary dose, total dose
        # read pdf file and extract text
        read_pdf_from_url(opt)

        # read the csv output produced by previous function
        mohfw_data = []
        total_fd, total_sd, total_pd, total_td = 0, 0, 0, 0
        dadra_firstDose, dadra_secondDose, dadra_PrecautDose, dadra_totalDose = 0, 0, 0, 0

        with open(VACC_OUTPUT_MOHFW, "r") as output_csv:
            for line in output_csv:
                lines_arr = line.split(',')
                if len(lines_arr) != 10:
                    print("--> Issue with {}".format(lines_arr))
                    continue

                data = {}
                data['vaccinated_as_of'] = date_sheet_str
                data['state_name'] = lines_arr[0].strip()

                #we need to combine Dadra and Daman
                if "Dadra" in line or "Daman" in line:
                  dadra_firstDose += int(lines_arr[1]) + int(lines_arr[3]) + int(lines_arr[5])
                  dadra_secondDose += int(lines_arr[2]) + int(lines_arr[4]) + int(lines_arr[6])
                  dadra_PrecautDose += int(lines_arr[7]) + int(lines_arr[8])
                  dadra_totalDose += int(lines_arr[9].strip('\n'))
                  continue

                if lines_arr[0].strip() in name_mapping.keys():
                    data['state_name'] = name_mapping[lines_arr[0].strip()]
                data['firstDose'] = int(lines_arr[1]) + int(lines_arr[3]) + int(lines_arr[5])
                total_fd += data['firstDose']
                data['secondDose'] = int(lines_arr[2]) + int(lines_arr[4]) + int(lines_arr[6])
                total_sd += data['secondDose']
                data['PrecautDose'] = int(lines_arr[7]) + int(lines_arr[8])
                total_pd += data['PrecautDose']
                data['totalDose'] = int(lines_arr[9].strip('\n'))
                total_td += data['totalDose']

                # print on console for copy-paste purpose
                console.print(f"{date_sheet_str},{data['state_name']},{data['firstDose']},{data['secondDose']},{data['totalDose']},{data['PrecautDose']}")

                mohfw_data.append(data)
        #add dadra to Total
        total_fd += dadra_firstDose
        total_sd += dadra_secondDose
        total_pd += dadra_PrecautDose
        total_td += dadra_totalDose
        #print dadra
        console.print(f"{date_sheet_str},Dadra and Nagar Haveli and Daman and Diu,{dadra_firstDose},{dadra_secondDose},{dadra_totalDose},{dadra_PrecautDose}")
        # print totals for India
        console.print(f"{date_sheet_str},Total,{total_fd},{total_sd},{total_td},{total_pd}")
    return mohfw_data


def get_cowin_state(from_date, to_date, state_codes):
    '''
    :param: `from_date` <datetime> - The date to start extracting data from
    :param: `to_date` <datetime> - The date to until when you want extract data (inclusive)
    :param: `state_codes` <list> - List of state codes to extract data for

    :returns: None - Appends the output to following files
        vaccination state level -> `_outputs/vaccination_state_level.txt`
    '''
    if state_codes == None:
        state_codes = states_all
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'

    day_count = (to_date - from_date) + datetime.timedelta(days=1)

    for curr_date in (from_date + datetime.timedelta(n) for n in range(day_count.days)):
        curr_date_str = curr_date.strftime('%d/%m/%Y')

        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        if curr_date >= today:
            print('Extract Cowin data only upto previous day')
            break

        print('Fetching for {}'.format(curr_date_str))
        district_rows = []

        # run for every state
        for state_code in state_codes:
          if states_all[state_code].get('state_code') in IGNORE_STATE_CODES:
            print('Skipping: ', states_all[state_code].get('state_code'))
            continue
          else:
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
                    state_data['topBlock'].get('vaccination')['total'], \
                    state_data['topBlock']['sessions']['total'], \
                    state_data['topBlock']['sites']['total'], \
                    state_data['topBlock']['vaccination']['tot_dose_1'], \
                    state_data['topBlock']['vaccination']['tot_dose_2'], \
                    state_data['topBlock']['vaccination'].get('tot_pd'), \
                    state_data['topBlock']['vaccination']['male'], \
                    state_data['topBlock']['vaccination']['female'], \
                    state_data['topBlock']['vaccination']['others'], \
                    state_data['topBlock']['vaccination']['covaxin'], \
                    state_data['topBlock']['vaccination']['covishield'], \
                    state_data['topBlock']['vaccination'].get('sputnik'), \
                    state_data['topBlock']['vaccination'].get('aefi'), \
                    # state_data['topBlock']['vaccination'].get('zycov'), \
                    state_data['vaccinationByAge'].get('vac_18_45'), \
                    state_data['vaccinationByAge'].get('vac_45_60'), \
                    state_data['vaccinationByAge'].get('above_60')
                ]

                datum = ','.join(map(str, datum))
                print(datum, file=file)


def get_cowin_district(from_date, to_date, state_codes):
    '''
    Get COWIN district level data for a given date

    :param: `from_date` <datetime> - the date for which data needs to be extracted for
    :param: `to_date` <datetime> - the date for which data needs to be extracted for
    :param: `state_codes` <list> - list of state codes to extract data for

    :returns: None - Writes the output to following files
        vaccination distr level -> `_outputs/vaccination_district_level.csv`
    '''
    if state_codes == None:
        state_codes = states_all
    base_url = 'https://api.cowin.gov.in/api/v1/reports/v2/getPublicReports?state_id={s_id}&district_id={d_id}&date={d}'
    day_count = (to_date - from_date) + datetime.timedelta(days=1)
    multi_dfs = []
    multi_dwnld_dfs = []
    published_df = pd.read_csv(COWIN_META) # keep district names from c19b googlesheet & ignore API names

    for curr_date in (from_date + datetime.timedelta(n) for n in range(day_count.days)):
        curr_date_str = curr_date.strftime('%d/%m/%Y')

        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        if curr_date >= today:
            print('Extract Cowin data only upto previous day')
            break

        print('Fetching for {}'.format(curr_date_str))

        district_rows = []
        # run for every state
        for state_code in state_codes:
          if ((states_all[state_code].get('state_code') == 'KLD') or (states_all[state_code].get('state_code') == 'KLDBL')):
            print('Not repeating for: ', states_all[state_code].get('state_code'))
            continue
          else:
            params = {
                's_id': states_all[state_code].get('cowin_code'),
                'd_id': '',
                'd': curr_date.strftime("%Y-%m-%d")
            }
            state_url = base_url.format(**params)
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
                        print('SKIPPED --->', resp, district_url)
                        continue
                    district['title'] = district['title'].replace(',','')
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
                            'Precautionary Dose Administered': district_data['topBlock'].get('vaccination').get('tot_pd'), \
                            'Male(Doses Administered)': district_data['topBlock'].get('vaccination').get('male'), \
                            'Female(Doses Administered)': district_data['topBlock'].get('vaccination').get('female'), \
                            'Transgender(Doses Administered)': district_data['topBlock'].get('vaccination').get('others'), \
                            'Covaxin (Doses Administered)': district_data['topBlock'].get('vaccination').get('covaxin'), \
                            'Covishield (Doses Administered)': district_data['topBlock'].get('vaccination').get('covishield'), \
                            # Enable these if necessary
                            # 'Zycov (Doses Administered)': district_data['topBlock'].get('vaccination').get('zycov'), \
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

        cowin_df = pd.DataFrame(district_rows).drop('updated_at', 1)
        multi_dwnld_dfs.append(cowin_df)
        state_dist_mapping = published_df[['State_Code', 'State', 'Cowin Key', 'District']].drop(0, axis=0)
        merged_data = pd.merge(state_dist_mapping, cowin_df, left_on=['State', 'Cowin Key'], right_on=['State', 'District'], how='left', suffixes=('', '_cowin'))
        merged_data = merged_data.drop(['Cowin Key', 'District_cowin'], 1)
        merged_data.columns = pd.MultiIndex.from_tuples([('' if k in ('State_Code', 'State', 'District') else curr_date_str, k) for k in merged_data.columns])
        multi_dfs.append(merged_data)

    final_df = pd.concat(multi_dfs, axis=1)
    final_dwnld_df = pd.concat(multi_dwnld_dfs, axis=1)

    #Removing first 3 columns (state_code, state_name, district_name)
    final_df.drop(final_df.iloc[:,0:3], inplace=True, axis=1)

    final_df.to_csv(VACC_DST, index=False)
    final_dwnld_df.to_csv(COWIN_DIST_LIVE, index=False)
    print("District data is saved to: ", VACC_DST)

if __name__ == '__main__':
    fn_map = {
        'cowin_state': get_cowin_state,
        'cowin_district': get_cowin_district,
        'mohfw_state': get_mohfw_state
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str, nargs='?', default='cowin_state', help='cowin or mohfw', choices=['cowin_state', 'cowin_district', 'mohfw_state'])
    parser.add_argument('-st', '--state_codes', required=False, type=str, default=None, help='comma separated state codes to extract for. Defaults to all')
    parser.add_argument('-f', '--from_date', required=False, type=lambda d: datetime.datetime.strptime(d, '%d-%m-%Y'), default=datetime.date.today(), help='please provide date in dd-mm-yyyy format only')
    parser.add_argument('-t', '--to_date', required=False, type=lambda d: datetime.datetime.strptime(d, '%d-%m-%Y'), help='please provide date in dd-mm-yyyy format only')

    args = parser.parse_args()
    vacc_src = args.source.lower()
    if args.state_codes is not None:
        state_codes = list(map(lambda sc: sc.lower(), args.state_codes.split(',')))
    else:
        state_codes = None
    from_date = args.from_date
    to_date = args.to_date

    if to_date is None or to_date <= from_date:
        to_date = from_date #+ datetime.timedelta(1)

    if vacc_src not in fn_map.keys():
        parser.print_help()
        sys.exit(0)

    fn_map[vacc_src](from_date, to_date, state_codes)

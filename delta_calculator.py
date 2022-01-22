import os
import datetime
import pandas as pd

API_DIST_CUM = 'https://data.covid19bharat.org/csv/latest/district_wise.csv'
API_DIST_TS = 'https://data.covid19bharat.org/csv/latest/districts.csv'
DELTA_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'delta.txt')
DELTA_MAPPING = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_meta', 'delta_mapping.meta')


def sheet_print(opt, df):
    '''
    Given dataframe, format print as example shown as below

    ---
    Example: Lower Siang,    Arunachal Pradesh, AR          , -17    , Recovered
    Format:  <districtname>, <state name>     , <state_code>, <delta>, <[Hospitalised, Recovered, Deceased, Migrated]>
    ---

    :param: <dict> - state config
    :param: <pd.DataFrame> - delta dataframe

    :returns: <str> - string format required by sheets
    '''
    hosp_df = reco_df = dece_df = migr_df = pd.DataFrame(columns=[
        'district_name',
        'state_name',
        'state_code',
        'delta',
        'delta_type'
    ])
    # df = df.rename(columns={'Confirmed': 'Hospitalized'})
    hosp_df['district_name'] = df['District']
    hosp_df['delta'] = df['Confirmed']
    hosp_df['delta_type'] = 'Hospitalized'
    hosp_df['state_name'] = opt['name']
    hosp_df['state_code'] = opt['state_code']

    reco_df['district_name'] = df['District']
    reco_df['delta'] = df['Recovered']
    reco_df['delta_type'] = 'Recovered'
    reco_df['state_name'] = opt['name']
    reco_df['state_code'] = opt['state_code']

    dece_df['district_name'] = df['District']
    dece_df['delta'] = df['Deceased']
    dece_df['delta_type'] = 'Deceased'
    dece_df['state_name'] = opt['name']
    dece_df['state_code'] = opt['state_code']

    migr_df['district_name'] = df['District']
    migr_df['delta'] = df['Migrated_Other']
    migr_df['delta_type'] = 'Migrated_Other'
    migr_df['state_name'] = opt['name']
    migr_df['state_code'] = opt['state_code']

    str_hosp = hosp_df.to_string(header=False, index=False, index_names=False).split('\n')
    print_hosp = '\n'.join([','.join(ele.split()) for ele in str_hosp])

    str_reco = reco_df.to_string(header=False, index=False, index_names=False).split('\n')
    print_reco = '\n'.join([','.join(ele.split()) for ele in str_reco])

    str_dece = dece_df.to_string(header=False, index=False, index_names=False).split('\n')
    print_dece = '\n'.join([','.join(ele.split()) for ele in str_dece])

    str_migr = migr_df.to_string(header=False, index=False, index_names=False).split('\n')
    print_migr = '\n'.join([','.join(ele.split()) for ele in str_migr])

    print(print_hosp, print_reco, print_dece, print_migr)


def calculate_deltas(opt, live_data):
    '''
    Calculate difference b/w current data vs API/latest data and return deltas

    :param: <dict> - `opt` as selected state's config
    :param: <dict> - currently read data from input
    :param: <pd.DataFrame> - dataframe for a particular date

    :returns: <pd.DataFrame> - calculated difference dataframe
    '''

    # 1. get updated API data & filter for selected state & sort
    api_df = pd.read_csv(API_DIST_CUM)
    state_df = api_df[api_df['State'] == opt['name']]
    state_df = state_df[[
        'District',
        'Confirmed',
        'Recovered',
        'Deceased',
        'Migrated_Other'
    ]].set_index('District').sort_index(ascending=True)

    # 2. read meta file to map district names
    meta_df = pd.read_csv(DELTA_MAPPING, sep=',', encoding='utf-8', header=None, names=['state_name', 'from_dist', 'to_dist'])
    state_meta_df = meta_df[meta_df['state_name'] == opt['name']][[
        'from_dist',
        'to_dist'
    ]].apply(lambda x: x.str.strip()) # strip whitespaces
    dist_to_rename = state_meta_df.set_index('from_dist').to_dict().get('to_dist')

    # 3. structure the live_data, rename districts & sort
    live_df = pd.DataFrame.from_dict(live_data)
    live_df.rename(columns={
        'confirmed': 'Confirmed',
        'recovered': 'Recovered',
        'deceased' : 'Deceased'
    }, inplace=True)
    live_df.replace(dist_to_rename, inplace=True)
    live_df = live_df.set_index('districtName').sort_index(ascending=True)

    # 4. calculate deltas, fill NA = 0, convert to int, structure it & return
    delta_df = live_df - state_df
    delta_df.fillna(0, inplace=True)
    delta_df = delta_df.astype(int).reset_index().rename(columns={
        'index': 'District'
    })

    # 5. drop rows with no deltas
    delta_df = delta_df.drop(delta_df[delta_df['District'].str.contains('Total')].index)

    return {
        'delta_totals': {
            'confirmed': delta_df['Confirmed'].sum(),
            'recovered': delta_df['Recovered'].sum(),
            'deceased': delta_df['Deceased'].sum(),
            'migrated': delta_df['Migrated_Other'].sum()
        },
        'deltas': delta_df,
        'api_state_data': state_df.reset_index()
        # 'for_sheets': sheet_print(opt, delta_df)
    }

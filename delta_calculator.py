import os
import datetime
import pandas as pd

API_DIST_CUM = 'https://data.covid19bharat.org/csv/latest/district_wise.csv'
API_DIST_TS = 'https://data.covid19bharat.org/csv/latest/districts.csv'
DELTA_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'delta.txt')
DELTA_MAPPING = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_meta', 'delta_mapping.meta')


def format_df(opt, df):
    '''
    Given dataframe, format print as example shown as below

    ---
    Example: Lower Siang   , Arunachal Pradesh, AR          , -17    , Recovered
    Format:  <districtname>, <state name>     , <state_code>, <delta>, <[Hospitalised, Recovered, Deceased, Migrated_Other]>
    ---

    :param: <dict> - state config
    :param: <pd.DataFrame> - delta dataframe

    :returns: <dict> - deltas, other info and formatted data for printing
    '''
    cols = [
        'district_name',
        'state_name',
        'state_code',
        'delta',
        'delta_type'
    ]
    frmts = {
        'Confirmed': 'Hospitalized',
        'Recovered': 'Recovered',
        'Deceased': 'Deceased',
        'Migrated_Other': 'Migrated_Other'
    }
    dfs = []

    for f in frmts:
        frmt_df = pd.DataFrame(columns=cols)
        frmt_df['district_name'] = df['District']
        frmt_df['delta'] = df[f]
        frmt_df['delta_type'] = frmts[f]
        frmt_df['state_name'] = opt['name']
        frmt_df['state_code'] = opt['state_code']
        dfs.append(frmt_df)

    result_df = pd.concat(dfs)
    result_df = result_df[result_df['delta'] != 0]  # drop rows with no deltas

    return result_df


def calculate_deltas(opt, live_data, dt=datetime.date.today()):
    '''
    Calculate difference b/w current data vs API/latest data and return deltas

    :param: <dict> - `opt` as selected state's config
    :param: <dict> - currently read data from input
    :param: <pd.DataFrame> - dataframe for a particular date
    :param: <datetime> - date to calculate deltas against

    :returns: <pd.DataFrame> - calculated difference dataframe
    '''

    # 1. get updated API data & filter for selected state & sort
    if dt != datetime.date.today():
        api_df = pd.read_csv(API_DIST_TS)
        dt_str = dt.strftime('%Y-%m-%d')
        state_df = api_df[
            (api_df['State'] == opt['name']) &
            (api_df['Date'] == dt_str)
        ].rename(columns={'Other': 'Migrated_Other'})
    else:
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
        'deceased' : 'Deceased',
        'migrated':  'Migrated_Other'
    }, inplace=True)
    live_df.replace(dist_to_rename, inplace=True)
    live_df = live_df.set_index('districtName').sort_index(ascending=True)

    # 4. calculate deltas, fill NA = 0, convert to int, structure it & return
    delta_df = live_df - state_df
    delta_df.fillna(0, inplace=True)
    delta_df = delta_df.astype(int).reset_index()
    delta_df.rename(columns={
        'districtName': 'District',
        'index': 'District'
    }, inplace=True)

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
        'api_state_data': state_df.reset_index(),
        'for_sheets': format_df(opt, delta_df)
    }

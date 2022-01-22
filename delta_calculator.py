import os
import pandas as pd

DELTA_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'delta.txt')
DELTA_MAPPING = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_meta', 'delta_mapping.meta')
API_DATA_CSV = 'https://data.covid19bharat.org/csv/latest/district_wise.csv'


def calculate_deltas(opt, live_data):
    '''
    Calculate difference b/w current data vs API/latest data and return deltas

    :param: <dict> - `opt` as selected state's config
    :param: <dict> - currently read data from input

    :returns: <pd.DataFrame> - calculated difference dataframe
    '''

    # 1. get updated API data & filter for selected state & sort
    all_states_df = pd.read_csv(API_DATA_CSV)
    state_df = all_states_df[all_states_df['State'] == opt['name']]
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
    delta_df = delta_df.astype(int).reset_index().rename({
        'index': 'District'
    })
    return delta_df

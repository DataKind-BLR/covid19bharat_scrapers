import os
import yaml
import logging
import datetime
import argparse
import tabulate

from rich.pretty import pprint
from statewise_get_data import *
from delta_calculator import calculate_deltas

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs')
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_inputs')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')

# read the config file first
with open(STATES_YAML, 'r') as stream:
    try:
        states_all = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)



def fetch_data(st_obj):
    '''
    for a given state object, fetch the details from url

    :state: <dict> - object as contained in states.yaml
        `{
          name: ...
          state_code: ...
          url: ...
        }`
    '''
    logging.info(f"Fetching data for {st_obj}")
    fn_map = {
        'ap': ap_get_data,
        'an': an_get_data,
        'ar': ar_get_data,
        'as': as_get_data,
        'br': br_get_data,
        'ch': ch_get_data,
        'ct': ct_get_data,
        'dd': dd_get_data,
        'dl': dl_get_data,
        'dn': dn_get_data,
        'ga': ga_get_data,
        'gj': gj_get_data,
        'hp': hp_get_data,
        'hr': hr_get_data,
        'jh': jh_get_data,
        'jk': jk_get_data,
        'ka': ka_get_data,
        'kl': kl_get_data,
        'kld': kld_get_data,
        'kldbl': kldbl_get_data,
        'ld': ld_get_data,
        'la': la_get_data,
        'mh': mh_get_data,
        'ml': ml_get_data,
        'mn': mn_get_data,
        'mp': mp_get_data,
        'mz': mz_get_data,
        'nl': nl_get_data,
        'or': or_get_data,
        'pb': pb_get_data,
        'py': py_get_data,
        'rj': rj_get_data,
        'sk': sk_get_data,
        'tn': tn_get_data,
        'tg': tg_get_data,
        'tr': tr_get_data,
        'up': up_get_data,
        'ut': ut_get_data,
        'wb': wb_get_data
    }

    try:
        return fn_map[st_obj['state_code'].lower()](st_obj)
    except KeyError:
        print('no function definition in fn_map for state code {}'.format(st_obj['state_code']))


def run(args):
    '''
    Based on set of configuration dictionary, trigger appropriate scraper for a state

    :param: <dict> - dictionary of configurations (see structure in `states.yaml`)
    '''
    state_code  = args.get('state_code').lower()
    url         = args.get('url')
    url_type    = args.get('type')
    page        = args.get('page', None)
    skip_output = args.get('skip_output', False)
    verbose     = args.get('verbose', False)
    delta_date  = args.get('delta_date', datetime.date.today())

    # default update skip_output key value
    states_all[state_code].update({ 'skip_output': skip_output })
    states_all[state_code].update({ 'verbose': verbose })

    # overwrite `page` provided by cmd
    if page:
        states_all[state_code]['config'].update({
            'page': page
        })

    # overwrite `type` provided by cmd
    if url_type is not None:
        states_all[state_code].update({
            'type': url_type
        })
    # overwrite `url` provided by cmd
    if url is not None:
        states_all[state_code].update({
            'url': url
        })
    # set delta_calc=false for MOHFW scrap
    if states_all[state_code]['type'] == 'mohfw':
        states_all[state_code]['config'].update({
            'delta_calc': False
        })
    #GJ html/pdf mixed requirement
    if states_all[state_code]['type'] == 'pdf' and (state_code == 'gj'):
        states_all[state_code]['config'].update({
            'delta_calc': False
        })
    #Remove start_key and end_key for processing image of RJ & MH
    if url_type == 'image' and (state_code == 'rj' or state_code == 'mh' or state_code == 'ml'):
      keys_to_remove = ['key_not_exist', 'start_key','end_key']
      k = list(map( states_all[state_code]['config'].pop, keys_to_remove, keys_to_remove))

    live_data = fetch_data(states_all[state_code])

    if 'needs_correction' in live_data and live_data['needs_correction'] == True:
        print('\n\n', '-*-'*20)
        print('Corrections required')
        pprint(live_data)
        print('-*-'*20, '\n\n')
        return live_data

    if 'config' in states_all[state_code] and\
        'delta_calc' in states_all[state_code]['config'] and\
        states_all[state_code]['config']['delta_calc'] == False:
        print('\n\n', '-*-'*20)
        print('Data from input provided as deltas - no calculations required')
        print('\n\n', '-*-'*20)
        return 'Data from input provided as deltas - no calculations required'

    dc = calculate_deltas(
        states_all[state_code],
        live_data,
        delta_date
    )

    if verbose:
        print('\n\n')

        pprint(states_all[state_code])

        print('Current input data')
        print(tabulate.tabulate(live_data, headers='keys', tablefmt='github', showindex=False))
        print('\n\n', '-*-'*20)

        print('API state data as on', delta_date.strftime('%d-%m-%Y'))
        print(tabulate.tabulate(dc['api_state_data'], headers='keys', tablefmt='github', showindex=False))
        print('\n\n', '-*-'*20)

        print('Calculated deltas against', delta_date.strftime('%d-%m-%Y'), 'data')
        print(tabulate.tabulate(dc['deltas'], headers='keys', tablefmt='github', showindex=False))
        print('\n\n', '-*-'*20)

        print('Delta Totals')
        print(dc['delta_totals'])
        print('\n\n', '-*-'*20)
        return {
            'live_data': tabulate.tabulate(live_data, headers='keys', tablefmt='github', showindex=False),
            'api_state_data': tabulate.tabulate(dc['api_state_data'], headers='keys', tablefmt='github', showindex=False),
            'deltas': tabulate.tabulate(dc['deltas'], headers='keys', tablefmt='github', showindex=False),
            'delta_totals': dc['delta_totals']
        }

    print('\n\n')
    if dc['for_sheets'].empty:
        print('No deltas')
        return 'No deltas'
    else:
        to_print = []
        for ind, row in dc['for_sheets'].iterrows():
            to_print.append('{},{},{},{},{}'.format(
                row['district_name'],
                row['state_name'],
                row['state_code'],
                row['delta'],
                row['delta_type']
            ))
        print('--> DELTAS CALCULATED AGAINST:', delta_date.strftime('%d-%m-%Y'), '\n\n')
        print('\n'.join(to_print))
        return '\n'.join(to_print)
    print('\n\n')


if __name__ == '__main__':
    '''
    Example to extract from html dashboard (the url will be taken from states.yaml file by default)
    $python scrapers.py --state_code GJ

    Example to overwrite settings already provided in yaml file:
    $python scrapers.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
    '''
    # console = Console(record=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--state_code', type=str, nargs='?', required=True, help=f'provide 2 letter state code. Possible options = {states_all.keys()}')
    parser.add_argument('-t', '--type', type=str, choices=['pdf', 'image', 'html', 'mohfw'], help='type of url to be specified [pdf, image, html, mohfw]')
    parser.add_argument('-u', '--url', type=str, help='url/path to the image or pdf to be parsed')
    parser.add_argument('-p', '--page', type=str, help='page numbers to read in case of PDFs')
    parser.add_argument('-o', '--skip_output', action='store_true', help='when you add this flag, it will not generate or update existing output files. Ideally use this when you manually want to update outputs and re-run statewise function')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose will print out all the details in a tabular format')
    parser.add_argument('-d', '--delta_date', required=False, type=lambda d: datetime.datetime.strptime(d, '%d-%m-%Y'), default=datetime.date.today(), help='date in dd-mm-yyyy format to calculate deltas against')

    args = parser.parse_args()
    run(vars(args))

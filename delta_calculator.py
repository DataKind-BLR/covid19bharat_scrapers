"""
This class provides a way to get delta per district
based on passed values and website numbers
"""
import os
import re
import csv
import requests
import pandas as pd
from rich.pretty import pprint
from rich.console import Console
from rich.table import Table

DELTA_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'delta.txt')

def draw_table(data, info, console):
  table = Table(title=f"{info['name']} last updated data from <data.covid19bharat.org>", title_justify="left", style="bold")

  table.add_column('district', style='white')
  table.add_column('confirmed', style='red', justify='right')
  table.add_column('recovered', style='green', justify='right')
  table.add_column('deceased', style='grey39', justify='right')
  table.add_column('migrated_other', style='white', justify='right')
  table.add_column('active', style='white', justify='right')

  for k,v in data.items():
    table.add_row(k, 
                  str(v['confirmed']), 
                  str(v['recovered']), 
                  str(v['deceased']),
                  str(v['migrated_other']),
                  str(v['active']))
  
  console.print(table, justify="left")


def state_level_delta(name, live_data, console):
    DASHBOARD_URL = 'https://data.covid19bharat.org/csv/latest/state_wise.csv'
    state_data = pd.read_csv(DASHBOARD_URL).set_index('State').loc[name]
    state_data.index = state_data.index.str.lower()
    state_code = state_data['state_code']
    state_data['deceased']  = state_data['deaths']
    
    draw_table(state_data.to_frame(), {'name': name}, console)
    
    delta = {
      'Hospitalized': live_data[0]['confirmed'] - state_data['confirmed'],
      'Recovered':    live_data[0]['recovered'] - state_data['recovered'],
      'Deceased':     live_data[0]['deceased']  - state_data['deceased']
    }
    
    if list(delta.values()) == [0,0,0]:
        console.print('\nDelta Unchanged.')
    else:
        for k,v in delta.items():
            console.print(f"{name},{state_code},{str(v)},{k}")
            
        console.print('\nDelta Processing complete.')


class DeltaCalculator:
    """ This class is used to calculate delta between website and bulletin """

    def __init__(self, console):
        self.covid_dashboard_data = {}
        self.build_json()
        self.name_mapping = {}
        self.load_meta_data()
        self.delta_changed = 0
        self.console = console

    # TODO - there are unassigned states in the JSON being built here...
    def build_json(self):
        """
        :rtype: object
        """
        decoded_content = requests.request("get", 'https://data.covid19bharat.org/csv/latest/district_wise.csv').content.decode('utf-8')
        csv_reader = csv.reader(decoded_content.splitlines(), delimiter=',')
        rows = list(csv_reader)
        for index, row in enumerate(rows):
            if index == 0:
                continue
            if row[2] not in self.covid_dashboard_data:
                self.covid_dashboard_data[row[2]] = {}

            if 'state_code' not in self.covid_dashboard_data[row[2]]:
                self.covid_dashboard_data[row[2]]['state_code'] = row[1]

            if 'district_data' not in self.covid_dashboard_data[row[2]]:
                self.covid_dashboard_data[row[2]]['district_data'] = {}

            if row[4] not in self.covid_dashboard_data[row[2]]['district_data']:
                self.covid_dashboard_data[row[2]]['district_data'][row[4]] = {}

            self.covid_dashboard_data[row[2]]['district_data'][row[4]]['confirmed'] = int(row[5])
            self.covid_dashboard_data[row[2]]['district_data'][row[4]]['confirmed'] = int(row[5])
            self.covid_dashboard_data[row[2]]['district_data'][row[4]]['recovered'] = int(row[7])
            self.covid_dashboard_data[row[2]]['district_data'][row[4]]['migrated_other'] = int(row[9])
            self.covid_dashboard_data[row[2]]['district_data'][row[4]]['deceased'] = int(row[8])
            self.covid_dashboard_data[row[2]]['district_data'][row[4]]['active'] = int(row[6])

    def load_meta_data(self):
        """
        :return: load data into name_mapping dict
        """
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "delta_mapping.meta"), "r", encoding="utf-8") as meta_file:
            for line in meta_file:
                line_array = line.split(',')
                if line_array[0] not in self.name_mapping:
                    self.name_mapping[line_array[0]] = {}

                current_dictionary = self.name_mapping[line_array[0]]
                current_dictionary[line_array[1].strip()] = re.sub('\n', '', line_array[2].strip())
                self.name_mapping[line_array[0]] = current_dictionary

    def get_state_data_from_site(self, state_name, live_data, options='full'):
        """
        Eg: deltaCalculator.getStateDataFromSite("Arunachal Pradesh", districtArray, option). The value for options are: full/detailed/<empty>. These values are passed via command line.
        :param state_name:
        :param live_data:
        :param options:
        :return: print all deltas
        """

        state_data = self.covid_dashboard_data[state_name]['district_data']
        state_code = self.covid_dashboard_data[state_name]['state_code']

        draw_table(state_data, {'name': state_name}, self.console)

        self.console.print("\n" + '*' * 10 + " Computing Delta for [bold]"+ state_name + '[/] ' + '*' * 10, style="cyan")
        try:
            name_mapping = self.name_mapping[state_name]
        except KeyError:
            name_mapping = {}

        confirmed_delta_array = []
        recovered_delta_array = []
        deceased_delta_array = []
        active_delta_array = []
        migrated_delta_array = []
        districts = []
        error_array = []

        # ---->>>> TODO - take diff using dataframes
        # import pdb
        # pdb.set_trace()
        # -----
        # import pandas as pd
        # df_live = pd.DataFrame(live_data)
        # df_live['districtName'].replace(name_mapping, inplace=True).sort_values(by='districtName')
        # df_dashboard = pd.DataFrame(state_data).T.reset_index().rename(columns={'index': 'districtName'}).sort_values(by='districtName')
        #
        # Do a check if the order of the districts in both dataframes are the same, then take a diff
        self.console.print(f'\nMapping for district names')
        for (_name,name) in name_mapping.items():
            self.console.print(f"[dim cyan]{_name}[/] -> [b u cyan]{name}[/]")

        for district_details in live_data:
            district_name = ""
            try:
                if 'districtName' not in district_details:
                    continue
                district_name = name_mapping[district_details['districtName']] \
                    if district_details['districtName'] in name_mapping \
                    else district_details['districtName']

                if "Total" in district_name:
                    continue

                confirmed_delta = \
                    district_details['confirmed'] - state_data[district_name]['confirmed'] \
                        if district_details['confirmed'] != -999 else "NA"
                recovered_delta = \
                    district_details['recovered'] - state_data[district_name]['recovered'] \
                        if district_details['recovered'] != -999 else "NA"
                deceased_delta = \
                    district_details['deceased'] - state_data[district_name]['deceased'] \
                        if district_details['deceased'] != -999 else "NA"
                active_delta = 0
                migrated_delta = 0

                if 'migrated' in district_details.keys():
                    migrated_delta = \
                        district_details['migrated'] - state_data[district_name]['migrated_other']

            except KeyError:
                error_array.append(
                    f"[dim red]--> ERROR: Failed to find key mapping for district"
                    f": [bold]{district_name}[/], state: {state_name}[/]")
                continue

            if options in ("detailed", "full"):
                districts.append(district_name)
                confirmed_delta_array.append(confirmed_delta)
                recovered_delta_array.append(recovered_delta)
                deceased_delta_array.append(deceased_delta)
                active_delta_array.append(active_delta)
                migrated_delta_array.append(migrated_delta)

        if options == "full":
            self.clear_delta_file(DELTA_TXT)
            self.console.print('\nDelta statistics\n', style="bold cyan")
            self.print_full_details(
                confirmed_delta_array, "Hospitalized", state_name, state_code, districts, color='red')
            self.print_full_details(
                recovered_delta_array, "Recovered", state_name, state_code, districts, color='green')
            self.print_full_details(
                deceased_delta_array, "Deceased", state_name, state_code, districts, color='grey39')
            self.print_full_details(
                migrated_delta_array, "Migrated_Other", state_name, state_code, districts, color='yellow')
            print('\n')

        if len(error_array) > 0:
            for error in error_array:
                self.console.print(error)

        return self.delta_changed


    @staticmethod
    def clear_delta_file(file):
        if os.path.isfile(file):
            os.remove(file)

    def print_full_details(self, delta_array, category, state_name, state_code, districts, color='white'):
        """
        :param delta_array:
        :param category:
        :param state_name:
        :param state_code:
        :param districts:
        :return: Print in proper format
        """
        try:
            with open(DELTA_TXT, "a", encoding="utf-8") as file:
                for index, data in enumerate(delta_array):
                    if str(data) not in ("0", "NA"):
                        self.delta_changed = 1
                        print(f"{districts[index]},{state_name},{state_code},{str(data)},{category}", file=file)
                        self.console.print(f"[bold cyan]{districts[index]}[/],[no bold]{state_name},{state_code}[/],[green bold]{str(data)}[/],[{color}]{category}[/]")
        except Exception as e:
            self.console.print(f"[red]Error in writing to delta file {e}[/]")

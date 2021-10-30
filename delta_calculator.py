"""
This class provides a way to get delta per district
based on passed values and website numbers

To scan PDFs
  ./automation.py "statename" full pdf=<urlOfThepdf>=<pageNumber>
  ./automation.py "stateName" full pdf==<pageNumber> (this in case you manually place the pdf as .tmp/stateCode.pdf)

"""
import os
import re
import csv
import requests


class DeltaCalculator:
    """ This class is used to calculate delta between website and bulletin """

    def __init__(self):
        self.covid_dashboard_data = {}
        self.build_json()
        self.name_mapping = {}
        self.load_meta_data()
        self.delta_changed = 0

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

        print("\n" + '*' * 10 + "Computing Delta for "+state_name + '*' * 10)
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
                    f"--> ERROR: Failed to find key mapping for district"
                    f": {district_name}, state: {state_name}")
                continue

            if options in ("detailed", "full"):
                districts.append(district_name)
                confirmed_delta_array.append(confirmed_delta)
                recovered_delta_array.append(recovered_delta)
                deceased_delta_array.append(deceased_delta)
                active_delta_array.append(active_delta)
                migrated_delta_array.append(migrated_delta)

        if options == "full":
            self.clear_delta_file("_cache/delta.txt")
            self.print_full_details(
                confirmed_delta_array, "Hospitalized", state_name, state_code, districts)
            self.print_full_details(
                recovered_delta_array, "Recovered", state_name, state_code, districts)
            self.print_full_details(
                deceased_delta_array, "Deceased", state_name, state_code, districts)
            self.print_full_details(
                migrated_delta_array, "Migrated_Other", state_name, state_code, districts)

        if len(error_array) > 0:
            for error in error_array:
                print(error)

        return self.delta_changed


    @staticmethod
    def clear_delta_file(file):
        if os.path.isfile(file):
            os.remove(file)

    def print_full_details(self, delta_array, category, state_name, state_code, districts):
        """
        :param delta_array:
        :param category:
        :param state_name:
        :param state_code:
        :param districts:
        :return: Print in proper format
        """
        try:
            with open("_cache/delta.txt", "a", encoding="utf-8") as file:
                for index, data in enumerate(delta_array):
                    if str(data) not in ("0", "NA"):
                        self.delta_changed = 1
                        print(f"{districts[index]},{state_name},{state_code},{str(data)},{category}", file=file)
                        print(f"{districts[index]},{state_name},{state_code},{str(data)},{category}")
        except Exception as e:
            print(f"Error in writing to delta file {e}")

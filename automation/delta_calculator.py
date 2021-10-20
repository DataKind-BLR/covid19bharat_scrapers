"""
    This class provides a way to get delta per district
    based on passed values and website numbers
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

    def build_json(self):
        """
        :rtype: object
        """
        decoded_content = requests.request("get",
                                           "https://data.covid19india.org/csv/latest/district_wise.csv").content.decode(
            'utf-8')

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
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "name_mapping.meta"), "r", encoding="utf-8") as meta_file:
            for line in meta_file:
                line_array = line.split(',')
                if line_array[0] not in self.name_mapping:
                    self.name_mapping[line_array[0]] = {}

                current_dictionary = self.name_mapping[line_array[0]]
                current_dictionary[line_array[1].strip()] = re.sub('\n', '', line_array[2].strip())
                self.name_mapping[line_array[0]] = current_dictionary

    def get_state_data_from_site(self, state_name, state_date_from_state_dashboard, options):
        """
        :param state_name:
        :param state_date_from_state_dashboard:
        :param options:
        :return: print all deltas
        """

        state_data = self.covid_dashboard_data[state_name]['district_data']
        state_code = self.covid_dashboard_data[state_name]['state_code']
        print("\n" + '*' * 20 + state_name + '*' * 20)
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

        for district_details in state_date_from_state_dashboard:
            district_name = ""
            try:
                district_name = name_mapping[district_details['district_name']] \
                    if district_details['district_name'] in name_mapping \
                    else district_details['district_name']

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

    @staticmethod
    def print_full_details(delta_array, category, state_name, state_code, districts):
        """
        :param delta_array:
        :param category:
        :param state_name:
        :param state_code:
        :param districts:
        :return: Print in proper format
        """
        with open("output2.txt", "w+", encoding="utf-8") as file:
            for index, data in enumerate(delta_array):
                if data not in (0, "NA"):
                    print(f"{districts[index]},{state_name},{state_code},{data},{category}", file=file)
                    print(f"{districts[index]},{state_name},{state_code},{data},{category}")

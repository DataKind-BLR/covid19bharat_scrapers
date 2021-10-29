def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

states_map = {
  'Andhra Pradesh': 'AP',
  'Andaman and Nicobar Islands': 'AN',
  'Arunachal Pradesh': 'AR',
  'Assam': 'AS',
  'Bihar': 'BR',
  'Chandigarh': 'CH',
  'Chhattisgarh': 'CT',
  'Daman and Diu': 'DD',
  'Delhi': 'DH',
  'Dadra and Nagar Haveli': 'DN',
  'Goa': 'GA',
  'Gujarat': 'GJ',
  'Himachal Pradesh': 'HP',
  'Haryana': 'HR',
  'Jharkhand': 'JH',
  'Jammu and Kashmir': 'JK',
  'Karnataka': 'KA',
  'Kerala': 'KL',
  'Ladakh': 'LA',
  'Maharashtra': 'MH',
  'Meghalaya': 'ML',
  'Manipur': 'MN',
  'Madhya Pradesh': 'MP',
  'Mizoram': 'MZ',
  'Nagaland': 'NL',
  'Odisha': 'OR',
  'Punjab': 'PB',
  'Puducherry': 'PY',
  'Rajasthan': 'RJ',
  'Sikkim': 'SK',
  'Tamil Nadu': 'TN',
  'Telangana': 'TG',
  'Tripura': 'TR',
  'Uttar Pradesh': 'UP',
  'Uttarakhand': 'UT',
  'West Bengal': 'WB'
}

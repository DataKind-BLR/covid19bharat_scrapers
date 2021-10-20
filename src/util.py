def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


ocr_dict = {
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CT": "Chhattisgarh",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "UP": "Uttar Pradesh",
    "UT": "Uttarakhand",
    "TG": "Telangana",
    "TN": "Tamil Nadu",
}


pdf_dict = {
    "HR": "Haryana",
    "KA": "Karnataka",
    "PB": "Punjab",
    "TN": "Tamil Nadu",
    "WB": "West Bengal",
    "AP": "Andhra Pradesh",
    "KL": "Kerala"
}

dash_dict = {
    "GJ": "Gujarat",
    "KL": "Kerala",
    "LA": "Ladakh",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "OR": "Odisha",
    "PY": "Puducherry",
    "TR": "Tripura",
    "VC": "Vaccine"
}


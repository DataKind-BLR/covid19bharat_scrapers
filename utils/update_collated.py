# pip install gspread_pandas
# pip install gspread
# pip install oauth2client
# cp google-api-secret.json /home/<user>/.config/gspread_pandas/google_secret.json

import pandas as pd
from gspread_pandas import Spread, Client

client = Client()
state_wise_data = client.open('DKind_States_7th_Nov')
spread = Spread('Collated_DK')

mydata = state_wise_data.worksheets
for i in mydata():
    data = i.get_values()

df = pd.DataFrame(data)
df.rename(columns=df.iloc[0], inplace = True)
df = df.drop(df.index[[0]])

df_mega = pd.DataFrame(columns=df.columns)
spread.df_to_sheet(df=df_mega, sheet="Sheet1",index=False,replace=True)

for i in mydata():
    data = i.get_values()
    df_temp = pd.DataFrame(data)
    df_temp.rename(columns=df_temp.iloc[0], inplace = True)
    df_temp = df_temp.drop(df_temp.index[[0]])
    df_mega = df_mega.append(df_temp, ignore_index=True)

df_mega = df_mega.sort_values(["Date Announced", "Detected State","Current Status"])

spread.df_to_sheet(df=df_mega, sheet="Sheet1",index=False,replace=True)

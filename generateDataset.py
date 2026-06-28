import pandas as pd
import numpy as np
import os

import random
from datetime import date, timedelta


def readCSV(file_path, separator=',', columns=None):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep=separator, usecols=columns)
        return df
    else:
        print(f"File {file_path} does not exist.")
        return None

def random_dates(start, end, n):
    start = date(1950, 1, 1)
    end = date.today()
    delta = (end - start).days
    return [start + timedelta(days=random.randint(0, delta)) for _ in range(n)]

def main():
    #read the csvFiles
    bse_df = readCSV(os.path.join(os.getcwd(),  'rawdata',  'bse_combined.csv'), separator=',', columns=['Date', 'Close'])
    gold_df = readCSV(os.path.join(os.getcwd(),  'rawdata',  'gold.csv'), separator=',', columns=['Date', 'Price'])
    #We want to keep only the rows in the gold_df that are on or after 1950-01-01
    gold_df = gold_df[gold_df['Date'] >= '1950-01-01']
    dji_df = readCSV(os.path.join(os.getcwd(),  'rawdata',  'dji.csv'), separator=',', columns=['Date', 'Close'])
    inr_usd_df = readCSV(os.path.join(os.getcwd(),  'rawdata',  'usdinr.csv'), separator=',', columns=['Date', 'INR_per_USD'])

    # Use datetimes so we can match the exact date or the next available date.
    bse_df['Date'] = pd.to_datetime(bse_df['Date'])
    gold_df['Date'] = pd.to_datetime(gold_df['Date'])
    dji_df['Date'] = pd.to_datetime(dji_df['Date'])
    inr_usd_df['Date'] = pd.to_datetime(inr_usd_df['Date'])

    #add an index on the Date column for faster lookups
    bse_df.set_index('Date', inplace=True)
    gold_df.set_index('Date', inplace=True)
    dji_df.set_index('Date', inplace=True)
    inr_usd_df.set_index('Date', inplace=True)

    bse_df.sort_index(inplace=True)
    gold_df.sort_index(inplace=True)
    dji_df.sort_index(inplace=True)
    inr_usd_df.sort_index(inplace=True)


    # Generate random dates
    n = 5000  # Number of random dates to generate
    dates = random_dates(date(1950, 1, 1), date.today(), n)

    df = pd.DataFrame(dates, columns=['Date'])
    df['Date'] = pd.to_datetime(df['Date']).astype('datetime64[ns]')
    
    #add a column to indicate that this date is after 1979-04-03 or not
    df['has_bse'] = df['Date'].apply(lambda x: 1 if x >= pd.to_datetime('1979-04-03') else 0)
    
    # Find the exact match or the next available date in each source table.
    bse_lookup = bse_df[['Close']].reset_index()
    bse_lookup['Date'] = pd.to_datetime(bse_lookup['Date']).astype('datetime64[ns]')
    df = pd.merge_asof(df.sort_values('Date'), bse_lookup.sort_values('Date'), on='Date', direction='forward')
    df.rename(columns={'Close': 'BSE_Close'}, inplace=True)     
    df['BSE_Close'] = df['BSE_Close'].where(df['has_bse'].eq(1), 0)

    gold_lookup = gold_df[['Price']].reset_index()
    gold_lookup['Date'] = pd.to_datetime(gold_lookup['Date']).astype('datetime64[ns]')
    df = pd.merge_asof(df, gold_lookup.sort_values('Date'), on='Date', direction='forward')
    df.rename(columns={'Price': 'Gold_Price'}, inplace=True)

    dji_lookup = dji_df[['Close']].reset_index()
    dji_lookup['Date'] = pd.to_datetime(dji_lookup['Date']).astype('datetime64[ns]')
    df = pd.merge_asof(df, dji_lookup.sort_values('Date'), on='Date', direction='forward')
    df.rename(columns={'Close': 'DJI_Close'}, inplace=True)

    inr_lookup = inr_usd_df[['INR_per_USD']].reset_index()
    inr_lookup['Date'] = pd.to_datetime(inr_lookup['Date']).astype('datetime64[ns]')
    df = pd.merge_asof(df, inr_lookup.sort_values('Date'), on='Date', direction='forward')
    df.rename(columns={'INR_per_USD': 'INR_per_USD'}, inplace=True)
    print(df.head())
    

    df['DJI_INR'] = df['DJI_Close'] * df['INR_per_USD']
    df['Gold_INR'] = df['Gold_Price'] * df['INR_per_USD']

    #Save the final dataframe to a CSV file
    outputFile = os.path.join(os.getcwd(), 'final_dataset.csv')
    df.to_csv(outputFile, index=False)
    


if __name__ == "__main__":
    main()
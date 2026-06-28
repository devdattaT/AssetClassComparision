import pandas as pd
import numpy as np
import os
from itertools import combinations

def cagr(start_val, end_val, years):
    """Returns CAGR as a percentage. Returns NaN if not computable."""
    if years <= 0 or start_val <= 0 or end_val <= 0:
        return np.nan
    return ((end_val / start_val) ** (1 / years) - 1) * 100

def getCalulculatedValues(r1, r2):
    days = (r2['Date'] - r1['Date']).days
    years = days / 365.25

    # CAGR for DJI_INR and Gold_INR
    dji_inr_cagr  = cagr(r1['DJI_INR'],  r2['DJI_INR'],  years)
    gold_inr_cagr = cagr(r1['Gold_INR'], r2['Gold_INR'], years)

    # BSE CAGR only if both rows have has_bse == 1
    if r1['has_bse'] == 1 and r2['has_bse'] == 1:
        bse_cagr = cagr(r1['BSE_Close'], r2['BSE_Close'], years)
    else:
        bse_cagr = np.nan

    return {
        'start_date':     r1['Date'].date(),
        'end_date':       r2['Date'].date(),
        'days':           days,
        'years':          round(years, 4),
        'DJI_INR_CAGR':  round(dji_inr_cagr,  4) if not np.isnan(dji_inr_cagr)  else np.nan,
        'Gold_INR_CAGR':  round(gold_inr_cagr,  4) if not np.isnan(gold_inr_cagr)  else np.nan,
        'BSE_CAGR':       round(bse_cagr, 4)        if not np.isnan(bse_cagr)        else np.nan,
    }

def main():
    #read the final dataset
    df = pd.read_csv(os.path.join(os.getcwd(), 'final_dataset.csv'))
    #add an index on the Date column for faster lookups
    df['Date'] = pd.to_datetime(df['Date'])
    #Drop all rows where DJI_INR or GOLD_INR is NaN
    df.dropna(subset=['DJI_INR', 'Gold_INR'], inplace=True)

    #Get a Random sample of 2000 rows from the dataframe
    df = df.sample(n=2000, random_state=29).sort_values('Date').reset_index(drop=True)

    records = []

    #Lets get all Pairs
    for i, j in combinations(df.index, 2):
        r1, r2 = df.loc[i], df.loc[j]

        # Ensure r1 is the earlier date
        if r1['Date'] > r2['Date']:
            r1, r2 = r2, r1
        
        records.append(getCalulculatedValues(r1, r2))

    # Convert records to DataFrame and save to CSV
    result_df = pd.DataFrame(records)
    print("Pairs found: ", len(result_df))
    result_df.to_csv('calculated_values.csv', index=False)

if __name__ == "__main__":
    main()
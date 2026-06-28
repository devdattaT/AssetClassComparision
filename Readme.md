# Graphing Returns across Gold, Dow Jones & BSE Sensex 30

I have been saying for a long time that gold is a bad investment, but with the huge rise in the value of Gold in the recent past, is this statement still valid ?

## Thought Process

 - Let's take the historical values of Gold, Dow Jones Industrial Average, and the BSE Sensex 30. 
 - Let's run a simulation using random start points and random end points at least 90 days away.
 - Since I would be investing from India, I need to convert Gold & DJI values from USD to INR.
 - Then calculate the returns we would get if we had invested on those dates, or the next available date, in Gold, DJI, and Sensex (after 1979).
 - Let's graph the CAGR returns by aggregating across 3 parameters:
     - Holding Duration
     - Starting half decade
     - Ending half decade


## Data Required

 - DJI Values from https://stooq.com/q/d/?s=%5Edji
 - Gold Values from https://freegoldapi.com/
 - Historical Sensex values from https://www.kaggle.com/datasets/raghunandanbalasub/bse-historical-indices
 - New Sensex Values from Yahoo Finance
 - INR USD Values from RBI & Yahoo Finance


## Output of Analysis

Looking at the average returns from a duration point of view, Gold is better only when you look at a short holding period
![ DJI & Gold Holding Period](charts\01b_year_buckets_all_avg.png)

Even when we take BSE investing into consideration, the same results hold
![BSE, DJI & Gold Holding Period](charts\02b_year_buckets_bse_filter_avg.png)

If we look at the returns in every half decade, the volatile nature of investments becomes clear
![Bucketing by half decades End](charts\04b_halfdecade_end_bse_filter_avg.png)

You can clearly see the effect of the bull run in Gold prices when you look at this graph. The value of Gold returns is so high because the investments started in this half decade have seen huge returns due to the exponential rise.
![Bucketing by half decades start](charts\06b_halfdecade_start_bse_filter_avg.png)


# Conclusion.

It is not guaranteed that Gold always provides a high rate of returns, and you should invest in it only if you are comfortable with its volatility.
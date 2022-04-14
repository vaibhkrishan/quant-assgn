# Crypto Project #
Here is the code for reading data from the exchanges, storing it in csv files, replaying the data from csv files, finding the alpha from the replayed data and plotting the profits from those opportunities. The code is written as per Python 3.7.13, although future versions should work fine as well.

The code has been broken into the following parts:

1. Data readers (in the directory ExchDataReaders)
2. Data replayer (in the directory Replayer)
3. Alpha Finder (in the file FindAlpha.py)

## ExchDataReaders ##
The files in this folder can be imported as libraries but they also contain their own main functions. Currently the code was run using their own main functions. The folder contains three files:

1. **BtcAudReader.py**. This is for reading BTCAUD data from BTC Markets API.
2. **BtcSgdReader.py**. This is for reading BTCSGD data from Independent Reserve API. This file has two second sleep between successive API calls so as to not hit the rate limit of the exchange.
3. **AudSgdReader.py**. This is for reading AUDSGD data from OANDA API. This file has a 6 minute sleep between successive API calls as there are a very limited number of API calls that could be made. This limit has been exhausted now.

## Replayer ##
This contains only one file and can also be imported as a library, but doesn't contain it's own main function. The file it contains is:

**DataReplayer.py**. This reads a csv file, loads it into a pandas dataframe and replays it as requested.

## FindAlpha.py ##
This contains the code for calculating the alpha and finding the profitable opportunities. It replays the data, calculates the profit for each value of slippage considered as well as the tier of trading fees considered, and plots the profit onto a graph.

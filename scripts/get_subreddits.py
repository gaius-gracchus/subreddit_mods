# -*- coding: UTF-8 -*-

"""Create a list of the 10000 most popular subreddits
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
import ssl

import pandas as pd

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# set HTTPS context, otherwise Pandas gets mad
ssl._create_default_https_context = ssl._create_unverified_context

# string formatter of URL
URL = 'https://redditmetrics.com/top/offset/{}'

# number of subreddits to look at
N = 10000

# filename of pickled Pandas DataFrame
OUTPUT_FILE = '../data/subreddits.df'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

dfl = [ ]

for offset in range( 0, N, 100 ):

  print( f'[{offset} / {N}]')
  df = pd.read_html( URL.format( offset ) )
  dfl.extend( df )

df = pd.concat( dfl )
df = df.reset_index( )

os.makedirs( os.path.dirname( OUTPUT_FILE ), exist_ok = True )

df.to_pickle( OUTPUT_FILE )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
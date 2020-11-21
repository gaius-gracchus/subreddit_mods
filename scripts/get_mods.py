# -*- coding: UTF-8 -*-

"""Create a dict of every mod for a list of subreddits
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
import pickle

import praw
from prawcore.exceptions import Forbidden
import pandas as pd

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

CLIENT_ID = os.getenv( 'PRAW_CLIENT_ID' )
CLIENT_SECRET = os.getenv( 'PRAW_CLIENT_SECRET' )

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'

INPUT_SUBREDDIT_DF = '../data/subreddits.df'

OUTPUT_MOD_DICT = '../data/mod_dict.pkl'

OUTPUT_BLACKLIST = '../data/subreddit_blacklist.txt'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_subreddit_moderators( subreddit ):

  """Extract list of moderator users for a given subreddit.

  Parameters
  ----------
  subreddit : str
    Name of subreddit

  Returns
  -------
  list<str>
    List of moderator usernames
  """

  _subreddit = str( subreddit )
  _subreddit = reddit.subreddit( _subreddit )

  mods = _subreddit.moderator( )

  names = [ user.name for user in mods ]

  return names

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

reddit = praw.Reddit(
  client_id = CLIENT_ID,
  client_secret = CLIENT_SECRET,
  user_agent = USER_AGENT )

df = pd.read_pickle( INPUT_SUBREDDIT_DF )

subreddit_list = [ str( s[ 3: ] ) for s in df[ 'Reddit' ] ]

mod_dict = dict( )
blacklist = list( )

#-----------------------------------------------------------------------------#

for i, subreddit in enumerate( subreddit_list ):
  if ( ( subreddit not in mod_dict.keys( ) ) and ( subreddit not in blacklist ) ):
    try:
      mod_dict[ subreddit ] = get_subreddit_moderators( subreddit )
      print( f'[{i} / {len( subreddit_list)}] : {subreddit}')

    except:
      blacklist.append( subreddit )
      print( f'FAILED [{i} / {len( subreddit_list)}] : {subreddit}' )

#-----------------------------------------------------------------------------#

with open( OUTPUT_MOD_DICT, 'wb' ) as f:
  pickle.dump( mod_dict, f )

with open( OUTPUT_BLACKLIST, 'w' ) as f:
  for s in blacklist:
    f.write( s + '\n' )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# -*- coding: UTF-8 -*-

"""Create a GEXF graph file in which the nodes are subreddits and the edges are the
number of mods the two subreddits share.
"""

###############################################################################

from collections import Counter
import itertools
import pickle

import pandas as pd
import numpy as np

import networkx as nx

###############################################################################

# input pickle file containing dict where the keys are subreddits and the
# values are a list of mods for that subreddit
INPUT_MOD_DICT = '../data/mod_dict.pkl'

# filename of GEXF file to save graph to
OUTPUT_GEXF_FULL = '../data/subreddits_full.gexf'

# filename of GEXF file to save graph to
OUTPUT_GEXF_FILTERED = '../data/subreddits_filtered.gexf'

# pickled DataFrame containing subreddit information
INPUT_SUBREDDIT_DF = '../data/subreddits.df'

# subreddits connected by fewer than this many mods are removed from the graph
WEIGHT_THRESHOLD = 2

# subreddits with fewer than this many connections are removed from the graph
NEIGHBOR_THRESHOLD = 10

# list of
BOT_LIST = [
  'AutoModerator',
  'MAGIC_EYE_BOT',
  'AssistantBOT',
  'BotDefense',
  'BotTerminator',
  'rarchives',
  'SFWPornNetworkBot',
  'RepostSleuthBot',
  'PornOverlord',
  'publicmodlogs',
  'BotBust',
  'ModeratelyHelpfulBot',
  'SEO_Nuke',
  'USLBot' ]

###############################################################################

with open( INPUT_MOD_DICT, 'rb' ) as f:
  mod_dict = pickle.load( f )

# invert dictionary of lists to create a dict in which the keys are mods and
# the values are the subreddits the mod moderates.
# (https://stackoverflow.com/a/35491335/13026442)
subreddit_dict = { }
for k, v in mod_dict.items( ):
  for x in v:
    subreddit_dict.setdefault( x, [ ] ).append( k )

# remove bot moderators
for mod in BOT_LIST:
  subreddit_dict.pop( mod, None )

subreddit_df = pd.read_pickle( INPUT_SUBREDDIT_DF )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

mod_connection_list = [ ]

for mod, subreddit_list in subreddit_dict.items( ):

  combo_list = list( itertools.combinations( subreddit_list, 2 ) )
  combo_list = [ tuple( sorted( combo ) ) for combo in combo_list ]

  mod_connection_list.extend( combo_list )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

c = Counter( mod_connection_list )

edge_list = [ ]

for ( source, target ), weight in c.items( ):
  edge = ( source, target, { 'weight' : weight } )
  edge_list.append( edge )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

G = nx.Graph( )
G.add_edges_from( edge_list )

nx.write_gexf( G, OUTPUT_GEXF_FULL )

weights = nx.get_edge_attributes( G, 'weight' )
edges_to_remove = [ k for k, v in weights.items( ) if v < WEIGHT_THRESHOLD ]

G.remove_edges_from( edges_to_remove )
G.remove_nodes_from( list( nx.isolates( G ) ) )

nodes_to_remove = [ ]
for node in G:
  if len( list( nx.neighbors( G, node ) ) ) < NEIGHBOR_THRESHOLD:
    nodes_to_remove.append( node )

G.remove_nodes_from( nodes_to_remove )
G.remove_nodes_from( list( nx.isolates( G ) ) )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

nx.write_gexf( G, OUTPUT_GEXF_FILTERED )

###############################################################################
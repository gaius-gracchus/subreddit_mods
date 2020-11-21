# -*- coding: UTF-8 -*-

"""Create a GEXF graph file in which the nodes are mods and the edges are the
number of subreddits two mods share.
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
OUTPUT_GEXF_FULL = '../data/mods_full.gexf'

# filename of GEXF file to save graph to
OUTPUT_GEXF_FILTERED = '../data/mods_filtered.gexf'

# mods connected by this many or fewer subreddits are removed from the graph
WEIGHT_THRESHOLD = 2

# mods with fewer than this many connections are removed from the graph
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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

subreddit_connection_list = [ ]

for subreddit, mod_list in mod_dict.items( ):

  combo_list = list( itertools.combinations( mod_list, 2 ) )
  combo_list = [ tuple( sorted( combo ) ) for combo in combo_list ]

  subreddit_connection_list.extend( combo_list )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

c = Counter( subreddit_connection_list )

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
G.remove_nodes_from( BOT_LIST )
G.remove_nodes_from( list( nx.isolates( G ) ) )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

nx.write_gexf( G, OUTPUT_GEXF_FILTERED )

###############################################################################
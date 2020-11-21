# -*- coding: UTF-8 -*-

"""Create an HTML interactive visualization of the reddit moderator network,
where the nodes are subreddits, and the edges between nodes  are the number of
mutual moderators between the two subreddits
"""

###############################################################################

import os
import pickle
from collections import Counter

import pandas as pd
import networkx as nx
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import rgb2hex, hex2color

import holoviews as hv
from bokeh.models import HoverTool
hv.extension('bokeh')
renderer = hv.renderer('bokeh')

CMAP = get_cmap( 'tab20' )

###############################################################################

INPUT_GEXF = '../data/subreddits_filtered_pos.gexf'

INPUT_SUBREDDIT_DF = '../data/subreddits.df'

OUTPUT_HTML = '../data/subreddits_filtered_script'

GRAPH_EXTENTS = ( -6000, -2500, 3000, 3500 )

EDGE_SCALING = 0.5
NODE_SCALING = 0.5

###############################################################################

def get_edge_color( row ):

  source_rgb = np.asarray( hex2color( node_color_dict[ row[ 'source' ] ] ) )
  target_rgb = np.asarray( hex2color( node_color_dict[ row[ 'target' ] ] ) )

  rgb = 0.5 * ( source_rgb + target_rgb )

  return rgb2hex( rgb )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_color( mod_class ):

  mod_priority = mod_priorities[ mod_class ]
  color = rgb2hex( colors[ mod_priority % len( colors ) ] )

  return color

###############################################################################

with open(INPUT_GEXF, 'r') as f:
  data = f.read()

soup = BeautifulSoup( data, 'xml' )

# Extract node data and parameters from GEXF file, store as DataFrame
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

_nodes = soup.find('nodes')
nodes = _nodes.find_all('node')

node_list = list( )

for node in nodes:

  _node_dict = {
    'x' : float( node.find( 'viz:position' )[ 'x' ] ),
    'y' : float( node.find( 'viz:position' )[ 'y' ] ),
    'index' : str( node[ 'id' ] ),
    'name' : str( node[ 'id' ] ),
    'size' : float( node.find( 'viz:size' )[ 'value' ] ) * NODE_SCALING,
    'mod_class' :  int( node.find( 'attvalue', { 'for' : 'modularity_class' } )[ 'value' ] ), }

  node_list.append( _node_dict )

nodes_df = pd.DataFrame( node_list )

# Incorporate subscriber data into node DataFrame
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

subreddit_df = pd.read_pickle( INPUT_SUBREDDIT_DF )
subreddit_df[ 'Reddit' ] = subreddit_df[ 'Reddit' ].apply( lambda s : s[ 3 :])
subscriber_dict = dict( zip( subreddit_df[ 'Reddit'], subreddit_df[ 'Subscribers' ] ) )

nodes_df[ 'subscribers' ] = nodes_df[ 'index' ].apply( subscriber_dict.get )

# Extract edge data from GEXF file, store as DataFrame
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

_edges = soup.find( 'edges' )
edges = _edges.find_all( 'edge' )

edge_list = [ ]
for edge in edges:

  _edge_dict = {
    'source' : str( edge[ 'source' ] ),
    'target' : str( edge[ 'target' ] ),
    'weight' : float( edge[ 'weight' ] ) * EDGE_SCALING }

  edge_list.append( _edge_dict )

edges_df = pd.DataFrame( edge_list )

# Apply specified colormap to nodes and edges
###############################################################################

# Create mapping that sorts modularity classes by total number of subscribers,
mod_classes = sorted( list( set( nodes_df[ 'mod_class' ] ) ) )
partition_weights = { mod_class : np.sum( nodes_df[ nodes_df[ 'mod_class' ] == mod_class ][ 'subscribers' ] ) for mod_class in mod_classes }

mod_priorities = dict( zip(
  mod_classes,
  np.asarray( list( partition_weights.keys( ) ) )[ np.argsort( list( partition_weights.values( ) ) )[ ::-1 ] ] ) )

colors = CMAP.colors

# insert column for hex colors in node DataFrame
nodes_df['color'] = nodes_df['mod_class'].apply(get_color)

# node_colors = nodes_df['mod_class'].apply( CMAP ).apply( np.asarray )
# nodes_df[ 'color' ] = node_colors.apply( rgb2hex )

node_color_dict = dict( zip(
  nodes_df[ 'name' ],
  nodes_df[ 'color' ] ) )

edges_df[ 'color' ] = edges_df.apply( get_edge_color, axis = 1 )

###############################################################################

# convert node DataFrame to HoloViews object
hv_nodes = hv.Nodes(nodes_df).sort()

# create HoloViews Graph object from nodes and edges, with x and y limits
# bounded by `GRAPH_EXTENTS`
hv_graph = hv.Graph(
  (edges_df, hv_nodes),
  extents = GRAPH_EXTENTS )

# define custom hover tooltip
hover = HoverTool(tooltips=[
  ("subreddit", "@name"),
  ("subscribers", "@subscribers"),])

# specify parameters for visualization
hv_graph.opts(
  node_radius='size',
  edge_color = 'color',
  node_color = 'color',
  node_hover_fill_color = '#EF4E02',
  edge_alpha = 0.2,
  edge_line_width='weight',
  edge_hover_line_color = '#DF0000',
  responsive=True,
  aspect = 1,
  bgcolor = 'black',
  tools = [hover],
  xticks = 0,
  yticks = 0,
  xlabel = '',
  ylabel = '', )

# save visualization to HTML file
renderer.save(hv_graph, OUTPUT_HTML)

###############################################################################
# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import networkx as nx
import numpy as np
from dwave.system import LeapHybridSampler
from dimod import AdjVectorBQM

import matplotlib
matplotlib.use("agg")    # must select backend before importing pyplot
import matplotlib.pyplot as plt

# Build large grid graph for city (default to square, provide options for triangular, hexagonal)
G = nx.grid_2d_graph(14, 15)
nodes = G.nodes()

# Tunable parameters
gamma1 = len(G.nodes()) * 2
gamma2 = len(G.nodes()) / 3
gamma3 = len(G.nodes()) / 3
gamma4 = len(G.nodes()) ** 2

# Identify a fixed set of points of interest
num_poi = 3
pois = random.sample(nodes, k=num_poi)

# Identify a fixed set of current charging locations
num_cs = 4
charging_stations = random.sample(nodes, k=num_cs)

# Number of new charging stations to place
num_new_cs = 2

poi_cs_list = set(pois) - (set(pois)-set(charging_stations))
poi_cs_graph = G.subgraph(poi_cs_list)
poi_graph = G.subgraph(pois)
cs_graph = G.subgraph(charging_stations)


# Identify potential new charging locations
potential_new_cs_nodes = list(nodes - charging_stations)

# Build BQM using adjVectors to find best new charging location s.t. min distance to POIs and max distance to existing charging locations
linear = np.zeros(len(potential_new_cs_nodes))
quadratic = np.zeros((len(potential_new_cs_nodes), len(potential_new_cs_nodes)))
vartype = 'BINARY'

# Constraint 1: Min average distance to POIs
for i in range(len(potential_new_cs_nodes)):
    # Compute average distance to POIs from this node
    ave_dist = 0
    cand_loc = potential_new_cs_nodes[i]
    for loc in pois:
        manhattan_dist = (cand_loc[0]**2 - 2*cand_loc[0]*loc[0] + loc[0]**2 
                            + cand_loc[1]**2 - 2*cand_loc[1]*loc[1] + loc[1]**2)
        ave_dist += manhattan_dist / num_cs
    linear[i] += ave_dist * gamma1

# Constraint 2: Max distance to existing chargers
for i in range(len(potential_new_cs_nodes)):
    # Compute average distance to POIs from this node
    ave_dist = 0
    cand_loc = potential_new_cs_nodes[i]
    for loc in charging_stations:
        manhattan_dist = (-1*cand_loc[0]**2 + 2*cand_loc[0]*loc[0] - loc[0]**2
                            - cand_loc[1]**2 + 2*cand_loc[1]*loc[1] - loc[1]**2)
        ave_dist += manhattan_dist / num_poi
    linear[i] += ave_dist * gamma2

# Constraint 3: Max distance to other new charging location
for i in range(len(potential_new_cs_nodes)):
    for j in range(i+1, len(potential_new_cs_nodes)):
        ai = potential_new_cs_nodes[i]
        aj = potential_new_cs_nodes[j]
        dist = (-1*ai[0]**2 + 2*ai[0]*aj[0] - aj[0]**2 - ai[1]**2 
                + 2*ai[1]*aj[1] - aj[1]**2*gamma3)
        quadratic[i,j] += dist

# Constraint 4: Choose exactly E new charging locations
for i in range(len(potential_new_cs_nodes)):
    linear[i] += (1-2*num_new_cs) * gamma4
    for j in range(i+1, len(potential_new_cs_nodes)):
        quadratic[i,j] += 2 * gamma4

# Run BQM on HSS
bqm = AdjVectorBQM(linear, quadratic, vartype)
sampler = LeapHybridSampler()
sampleset = sampler.sample(bqm)

ss = sampleset.first.sample
new_charging_nodes = [potential_new_cs_nodes[k] for k, v in ss.items() if v == 1]
print("\nNew charging locations:", new_charging_nodes)
new_cs_graph = G.subgraph(new_charging_nodes)

# Display image of results for user
#   - Black nodes: available space
#   - Red nodes: current charger location
#   - Nodes marked 'P': POI locations
#   - Blue nodes: new charger locations

poi_labels = {x: 'P' for x in poi_graph.nodes()}
poi_cs_labels = {x: 'P' for x in poi_graph.nodes()}
pos = {x: [x[0],x[1]] for x in G.nodes()}

fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('New EV Charger Locations')

# Draw existing set up (left image)
nx.draw_networkx(G, ax=ax1, pos=pos, with_labels=False, node_color='k', font_color='w')
nx.draw_networkx(poi_graph, ax=ax1, pos=pos, with_labels=True, 
                    labels=poi_labels, node_color='k', font_color='w')
nx.draw_networkx(cs_graph, ax=ax1, pos=pos, with_labels=False, node_color='r',
                    font_color='k')
nx.draw_networkx(poi_cs_graph, ax=ax1, pos=pos, with_labels=True, 
                    labels=poi_cs_labels, node_color='r', font_color='w')

# Draw new set up (right image)
nx.draw_networkx(G, ax=ax2, pos=pos, with_labels=False, node_color='k', 
                    font_color='w')
nx.draw_networkx(poi_graph, ax=ax2, pos=pos, with_labels=True, 
                    labels=poi_labels,node_color='k', font_color='w')
nx.draw_networkx(cs_graph, ax=ax2, pos=pos, with_labels=False, node_color='r',
                    font_color='k')
nx.draw_networkx(poi_cs_graph, ax=ax2, pos=pos, with_labels=True, 
                    labels=poi_cs_labels,  node_color='r', font_color='w')
nx.draw_networkx(new_cs_graph, ax=ax2, pos=pos, with_labels=False, 
                    node_color='#00b4d9', font_color='w')

# Save image
plt.savefig("map.png")

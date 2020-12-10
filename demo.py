import random
import networkx as nx
from collections import defaultdict
from dwave.system import LeapHybridSampler

# import matplotlib
# matplotlib.use("agg")    # must select backend before importing pyplot
import matplotlib.pyplot as plt

# Build large grid graph for city (default to square, provide options for triangular, hexagonal)
G = nx.grid_2d_graph(14,15)
nodes = G.nodes()

# Tunable parameters
gamma1 = len(G.nodes())
gamma2 = 5
gamma2a= len(G.nodes())/2
gamma3 = len(G.nodes())**2

# Identify a fixed set of points of interest
num_POI = 3
POIs = random.sample(nodes, k=num_POI)

# Identify a fixed set of current charging locations
num_cs = 4
charging_stations = random.sample(nodes, k=num_cs)

# Number of new charging stations to place
num_new_cs = 2

poi_cs_list = set(POIs)-(set(POIs) - set(charging_stations))
poi_cs_graph = G.subgraph(poi_cs_list)
poi_graph = G.subgraph(POIs)
cs_graph = G.subgraph(charging_stations)


# Identify potential new charging locations
potential_new_cs_nodes = list(nodes - charging_stations)

# Build BQM using adjVectors to find best new charging location s.t. min distance to POIs and max distance to existing charging locations
Q = defaultdict(int)

# Constraint 1: Min average distance to POIs
for i in range(len(potential_new_cs_nodes)):
    # Compute average distance to POIs from this node
    ave_dist = 0
    cand_loc = potential_new_cs_nodes[i]
    for loc in POIs:
        manhattan_dist = cand_loc[0]**2-2*cand_loc[0]*loc[0]+loc[0]**2+cand_loc[1]**2-2*cand_loc[1]*loc[1]+loc[1]**2
        ave_dist += manhattan_dist/num_cs
    Q[(i,i)] += ave_dist*gamma1

# Constraint 2: Max distance to existing chargers
for i in range(len(potential_new_cs_nodes)):
    # Compute average distance to POIs from this node
    ave_dist = 0
    cand_loc = potential_new_cs_nodes[i]
    for loc in charging_stations:
        manhattan_dist = -1*cand_loc[0]**2+2*cand_loc[0]*loc[0]-loc[0]**2-cand_loc[1]**2+2*cand_loc[1]*loc[1]-loc[1]**2
        ave_dist += manhattan_dist/num_POI
    Q[(i,i)] += ave_dist*gamma2

for i in range(len(potential_new_cs_nodes)):
    for j in range(i+1, len(potential_new_cs_nodes)):
        ai = potential_new_cs_nodes[i]
        aj = potential_new_cs_nodes[j]
        Q[(i,j)] += -1*ai[0]**2 + 2*ai[0]*aj[0] - aj[0]**2 - ai[1]**2 + 2*ai[1]*aj[1] - aj[1]**2*gamma2a

# Constraint 3: Choose exactly E new charging locations
for i in range(len(potential_new_cs_nodes)):
    Q[(i,i)] += (1-2*num_new_cs)*gamma3
    for j in range(i+1, len(potential_new_cs_nodes)):
        Q[(i,j)] += 2*gamma3

# Run BQM on HSS
sampler = LeapHybridSampler()
sampleset = sampler.sample_qubo(Q)
ss = sampleset.first.sample
new_charging_nodes = [potential_new_cs_nodes[k] for k,v in ss.items() if v == 1]
print("\nNew charging locations:", new_charging_nodes)
new_cs_graph = G.subgraph(new_charging_nodes)

# Display image of results for user
#   - Black nodes: available space
#   - Red nodes: current charger location
#   - Nodes marked 'P': POI locations
#   - Blue nodes: new charger locations

POI_labels = {x: 'P' for x in poi_graph.nodes()}
poi_cs_labels = {x: 'P' for x in poi_graph.nodes()}

fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('New EV Charger Locations')

pos = {x: [x[0],x[1]] for x in G.nodes()}
nx.draw_networkx(G, ax=ax1, pos=pos, with_labels=False, node_color='k', font_color='w')
nx.draw_networkx(poi_graph, ax=ax1, pos=pos, with_labels=True, labels=POI_labels, node_color='k', font_color='w')
nx.draw_networkx(cs_graph, ax=ax1, pos=pos, with_labels=False, node_color='r', font_color='k')
nx.draw_networkx(poi_cs_graph, ax=ax1, pos=pos, with_labels=True, labels=poi_cs_labels, node_color='r', font_color='w')

nx.draw_networkx(G, ax=ax2, pos=pos, with_labels=False, node_color='k', font_color='w')
nx.draw_networkx(poi_graph, ax=ax2, pos=pos, with_labels=True, labels=POI_labels,node_color='k', font_color='w')
nx.draw_networkx(cs_graph, ax=ax2, pos=pos, with_labels=False, node_color='r', font_color='k')
nx.draw_networkx(poi_cs_graph, ax=ax2, pos=pos, with_labels=True, labels=poi_cs_labels,  node_color='r', font_color='w')
nx.draw_networkx(new_cs_graph, ax=ax2, pos=pos, with_labels=False, node_color='#00b4d9', font_color='w')
plt.show()
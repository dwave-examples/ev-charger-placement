# Copyright 2021 D-Wave Systems Inc.
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

import numpy as np
import dimod
from dwave.system import LeapHybridSampler

import demo

def build_bqm(potential_new_cs_nodes, num_poi, pois, num_cs, charging_stations, num_new_cs):
    """Build bqm that models our problem scenario using NumPy. 

    Args:
        potential_new_cs_nodes (list of tuples of ints):
            Potential new charging locations
        num_poi (int):
            Number of points of interest
        pois (list of tuples of ints):
            A fixed set of points of interest
        num_cs (int):
            Number of existing charging stations
        charging_stations (list of tuples of ints):
            A fixed set of current charging locations
        num_new_cs (int):
            Number of new charging stations desired
    Returns:
        bqm_np (BinaryQuadraticModel):
            QUBO model for the input scenario
    """

    # Tunable parameters
    gamma1 = len(potential_new_cs_nodes) * 4.
    gamma2 = len(potential_new_cs_nodes) / 3.
    gamma3 = len(potential_new_cs_nodes) * 1.7
    gamma4 = len(potential_new_cs_nodes) ** 3

    # Build BQM using adjVectors to find best new charging location s.t. min
    # distance to POIs and max distance to existing charging locations
    linear = np.zeros(len(potential_new_cs_nodes))

    nodes_array = np.asarray(potential_new_cs_nodes)
    pois_array = np.asarray(pois)
    cs_array = np.asarray(charging_stations)

    # Constraint 1: Min average distance to POIs
    if num_poi > 0:

        ct_matrix = np.matmul(nodes_array, pois_array.T)*(-2.) + np.sum(np.square(pois_array), axis=1).astype(float) + np.sum(np.square(nodes_array), axis=1).reshape(-1,1).astype(float)

        linear += np.sum(ct_matrix, axis=1) / num_poi * gamma1

    # Constraint 2: Max distance to existing chargers
    if num_cs > 0:    

        dist_mat = np.matmul(nodes_array, cs_array.T)*(-2.) + np.sum(np.square(cs_array), axis=1).astype(float) + np.sum(np.square(nodes_array), axis=1).reshape(-1,1).astype(float)

        linear += -1 * np.sum(dist_mat, axis=1) / num_cs * gamma2 

    # Constraint 3: Max distance to other new charging locations
    if num_new_cs > 1:

        dist_mat = ((np.matmul(nodes_array, nodes_array.T)*(-2.) + np.sum(np.square(nodes_array), axis=1)).astype(float) + np.sum(np.square(nodes_array), axis=1).reshape(-1,1).astype(float)) * -gamma3

    # Constraint 4: Choose exactly num_new_cs new charging locations
    linear += (1-2*num_new_cs)*gamma4
    dist_mat += 2*gamma4
    dist_mat = np.triu(dist_mat, k=1).flatten()

    quad_col = np.tile(np.arange(len(potential_new_cs_nodes)), len(potential_new_cs_nodes))
    quad_row = np.tile(np.arange(len(potential_new_cs_nodes)), (len(potential_new_cs_nodes),1)).flatten('F')

    q2 = quad_col[dist_mat != 0]
    q1 = quad_row[dist_mat != 0]
    q3 = dist_mat[dist_mat != 0]
    
    bqm_np = dimod.BinaryQuadraticModel.from_numpy_vectors(linear=linear, quadratic=(q1, q2, q3), offset=0, vartype=dimod.BINARY)

    return bqm_np

if __name__ == '__main__':

    # Collect user inputs
    args = demo.read_in_args()

    # Build large grid graph for city
    G, pois, charging_stations, potential_new_cs_nodes = demo.set_up_scenario(args.width, args.height, args.poi, args.chargers)

    # Build BQM
    bqm = build_bqm(potential_new_cs_nodes, args.poi, pois, args.chargers, charging_stations, args.new_chargers)

    # Run BQM on HSS
    sampler = LeapHybridSampler()
    print("\nRunning scenario on", sampler.solver.id, "solver...")

    new_charging_nodes = demo.run_bqm_and_collect_solutions(bqm, sampler, potential_new_cs_nodes)

    # Print results to commnand-line for user
    demo.printout_solution_to_cmdline(pois, args.poi, charging_stations, args.chargers, new_charging_nodes, args.new_chargers)

    # Create scenario output image
    demo.save_output_image(G, pois, charging_stations, new_charging_nodes)
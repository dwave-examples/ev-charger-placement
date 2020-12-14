# Placement of Charging Stations

Determining optimal locations to build new electric vehicle charging stations
is a complex optimization problem.  Many factors should be taken into
consideration, like existing charger locations, points of interest (POIs),
quantity to build, etc. In this example, we take a look at how we might
formulate this optimization problem and solve it using D-Wave's binary
quadratic model (BQM) hybrid solver.

## Usage

To run the demo, type the command:

```python demo.py```

The program will construct a 14x15 grid representation of a city, and randomly
place 3 POIs and 4 current charging station locations. Using the BQM hybrid
solver, locations for 2 new charging stations will be selected.

After the new charging station locations have been selected, an image is
created. This image shows the current map with existing charging locations
shown in red and POIs denoted by P (left figure), as well as a future map with
the future charging station locations colored in blue (right figure). This
image is saved as ```map.png```.

Finally, the new charging locations within the grid are printed on the command
line for the user.

## Building the BQM

This problem can be considered as a set of 4 independent constraints (or
objectives) with binary variables that represent each potential new charging
station location.

### Minimize distance to POIs

For each potential new charging station location, we compute the average
distance to all POIs on the map. Using this value as a linear bias on each
binary variable, our program will prefer locations that are (on average) close
to the POIs.

### Maximize distance to existing charging stations

For each potential new charging station location, we compute the average
distance to all existing charging locations on the map. Using the negative of
this value as a linear bias on each binary variable, our program will prefer
locations that are (on average) far from existing chargers.

### Maximize distance to other new charging stations

For the pair of new charging station locations, we would like to maximize the
distance between them. To do this, we consider all possible pairs of locations
and compute the distance between them.  Using the negative of this value as a
quadratic bias on the product of the corresponding binary variables, our
program will prefer locations that are far from the other new charging
location.

### Build exactly two new charging stations

Using a value of -3 as a linear bias for each binary variable and a value of 2
as a quadratic bias on each product of binary variables, we can encode a
constraint to select exactly two new charging station locations.

### Parameter tuning

Each of these constraints is built into our BQM object with a coefficient
(names all start with `gamma`).  This term gamma is known as a Lagrange
parameter and can be used to weight the constraints against each other to
accurately reflect the requirements of the problem. You may wish to adjust this
parameter depending on your problem requirements and size. The value set here
in this program was chosen to empirically work well as a starting point for
problems of a wide-variety of sizes. For more information on setting this
parameter, see D-Wave's [Problem Formulation
Guide](https://www.dwavesys.com/practical-quantum-computing-developers).

## Ocean Features

This code example utilizes Ocean's ```AdjVectorBQM``` functionality. For
smaller problems we can use Python dictionaries to store a BQM. However, for
large, real-world sized problems, using dictionaries to store the BQM biases
can become quite slow. Using NumPy arrays instead allows Python to run quickly,
and is much more efficient on large problems. The Ocean ```AdjVectorBQM```
functions allow the user to store biases as numpy arrays and load them quickly
to build a BQM object, suitable for both quantum and hybrid solvers.

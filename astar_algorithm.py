"""
Implementation of A* algorithm connected to GUI.

Module prints shortest path, that is calculated with A* algorithm.
Parameters used to run algorithm are taken from GUI module.
Instances of start, end, obstacles are given as input.
Additional option for presenting principle of operation can be chosen.
"""

from math import sqrt
import time


class Node:
    """Create nodes that will be considered in calculations."""

    def __init__(self, coord):
        self.coord = coord
        self.g_value = 0
        self.h_value = 0
        self.f_value = 0
        self.parent = None


def g_cost(new_node, current_node):
    """
    G-cost of a node is a distance from start to current node.
    Distance is 10 when moving horizontal/vertical, and sqrt(2)*10~=14 when diagonal.
    """
    adjacent_nodes_diagonal = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    temp = (
        new_node.coord[0] - current_node.coord[0],
        new_node.coord[1] - current_node.coord[1],
    )
    return (
        current_node.g_value + 14
        if temp in adjacent_nodes_diagonal
        else current_node.g_value + 10
    )


def heuristic(current_node, end_node):
    """H-cost of a node is its distance in straight line to end node."""
    x1 = current_node[0]
    y1 = current_node[1]
    x2 = end_node[0]
    y2 = end_node[1]
    # Euclid's method
    return int(
        sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2)) * 10
    )  # * 10 to fit g_cost scale


def check_neighbour(neighbour_node, wall, closed, number_of_cells):
    """Check if adjacent nodes are passable."""
    if (
        neighbour_node.coord[0] < 0
        or neighbour_node.coord[1] < 0
        or neighbour_node.coord[0] > number_of_cells - 1
        or neighbour_node.coord[1] > number_of_cells - 1
    ):
        return True  # out of grid
    if neighbour_node.coord in closed:
        return True  # closed set of nodes
    if neighbour_node.coord in wall:
        return True  # obstacle
    return False  # passable node


def to_coord(start_id, end_id, wall_id, normal_id, number_cells, can, draw_flag):
    """Change ID of nodes to coordinates and run algorithm."""
    global time_start
    time_start = time.time()
    global start
    global end
    global wall
    global normal
    start = []
    end = []
    wall = []
    normal = []
    for cell_s in start_id:
        y = cell_s.find("y")
        coord_s = (int(cell_s[1:y]), int(cell_s[y + 1 :]))
        start.append(Node(coord_s))
    for cell_e in end_id:
        y = cell_e.find("y")
        coord_e = (int(cell_e[1:y]), int(cell_e[y + 1 :]))
        end.append(Node(coord_e))
    for cell_w in wall_id:
        y = cell_w.find("y")
        coord_w = (int(cell_w[1:y]), int(cell_w[y + 1 :]))
        wall.append(Node(coord_w))
    for cell_n in normal_id:
        y = cell_n.find("y")
        coord_n = (int(cell_n[1:y]), int(cell_n[y + 1 :]))
        normal.append(Node(coord_n))

    astar(start, end, wall, number_cells, can, draw_flag)
    return None


def astar(start, end, wall, number_of_cells, can, draw):
    """
    Run algorithm with parameters taken from GUI.
    Can be set to color nodes with every iteration or just color the path in the end.
    """
    adjacent_nodes = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]
    temp_node = Node((0, 0))
    open_nodes = set()
    closed_nodes = set()
    open_coord = set()  # set of only the coordinates of open nodes
    closed_coord = set()
    wall_coord = set()

    for item in wall:  # create set of coordinates of obstacles
        wall_coord.add(item.coord)

    path = []

    open_nodes.add(start[0])
    start[0].parent = None

    while open_nodes:
        current = next(iter(open_nodes))

        for node in open_nodes:
            if node.f_value < current.f_value:
                current = node  # firstly consider node with the lowest f value

        open_nodes.remove(current)
        closed_nodes.add(current)
        for item in open_nodes:  # accordingly to set add coordinates of nodes
            open_coord.add(item.coord)
        for item in closed_nodes:
            closed_coord.add(item.coord)

        if draw:  # color closed nodes on GUI
            tag = f"x{current.coord[0]}y{current.coord[1]}"
            can.itemconfig(tag, fill="red")
            can.update()

        if current.coord == end[0].coord:  # path found
            node = current
            while node is not None:
                path.append(node.coord)
                node = node.parent
            path_rev = path[::-1]
            print("path:", path_rev)
            for step in path_rev:
                tag = f"x{step[0]}y{step[1]}"
                can.itemconfig(tag, fill="blue")
                if draw:
                    can.update()
            can.update()
            time_stop = time.time()
            print("run time =", time_stop - time_start)
            break

        valid_neighbours = []
        # check every neighbour
        for adjacent in adjacent_nodes:
            neighbour = Node(adjacent)
            neighbour.coord = (
                current.coord[0] + adjacent[0],
                current.coord[1] + adjacent[1],
            )

            if check_neighbour(neighbour, wall_coord, closed_coord, number_of_cells):
                continue  # change to next neighbour if current is not traversable

            valid_neighbours.append(neighbour)
            if draw:  # color open nodes on GUI
                tag = f"x{neighbour.coord[0]}y{neighbour.coord[1]}"
                can.itemconfig(tag, fill="yellow")
        can.update()

        for (
            node
        ) in (
            valid_neighbours
        ):  # set or change path cost values and parents according to lowest f_value

            if node.coord in closed_coord:
                continue

            if node.coord not in open_coord:
                node.g_value = g_cost(node, current)
                node.h_value = heuristic(node.coord, end[0].coord)
                node.f_value = node.g_value + node.h_value
                node.parent = current
                open_nodes.add(node)
            else:
                temp_node.g_value = g_cost(node, current)
                temp_node.h_value = heuristic(node.coord, end[0].coord)
                temp_node.f_value = temp_node.g_value + temp_node.h_value
                temp_node.parent = current
                if temp_node.f_value < node.f_value:
                    node.g_value = temp_node.g_value
                    node.h_value = temp_node.h_value
                    node.f_value = temp_node.f_value
                    node.parent = temp_node.parent

    if not path:  # if it's impossible to get from start to end
        print("No path!")
        time_stop = time.time()
        print("run time =", time_stop - time_start)
    return None

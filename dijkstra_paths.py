import networkx as nx
import matplotlib.pyplot as plt
from network import Network

def find_path_bellman_ford(self, start_node_name, end_node_name):
    """
    Finds the shortest path from start_node_name to end_node_name using the Bellman-Ford algorithm.

    Parameters:
    -----------
    start_node_name : str
        The name of the start node.
    end_node_name : str
        The name of the end node.

    Returns:
    --------
    list
        The shortest path from start_node_name to end_node_name as a list of node names.
    None
        If there is no path or a negative weight cycle is detected.
    """
    distances = {node: float('inf') for node in self.graph.nodes()}
    predecessors = {node: None for node in self.graph.nodes()}
    distances[start_node_name] = 0

    for _ in range(len(self.graph.nodes) - 1):
        for u, v, data in self.graph.edges(data=True):
            weight = data['weight']
            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                predecessors[v] = u

    for u, v, data in self.graph.edges(data=True):
        if distances[u] + data['weight'] < distances[v]:
            print("Graph contains negative weight cycle")
            return None

    path = []
    step = end_node_name
    if distances[end_node_name] == float('inf'):
        print(f"No path exists from {start_node_name} to {end_node_name}")
        return None
    while step is not None:
        path.append(step)
        step = predecessors[step]
    path.reverse()

    return path

def compute_shortest_paths_bellman_ford(network):
    """
    Computes the shortest paths from all nodes to all other nodes using the Bellman-Ford algorithm.

    Parameters:
    -----------
    network : Network
        The network object containing nodes and links.

    Returns:
    --------
    dict
        A dictionary of shortest paths from each node to all other nodes.
    None
        If a negative weight cycle is detected.
    """
    shortest_paths = {}

    for source_node in network.nodes.values():
        source_paths = {}

        distances = {node.name: float('inf') for node in network.nodes.values()}
        predecessors = {node.name: None for node in network.nodes.values()}

        distances[source_node.name] = 0

        for _ in range(len(network.nodes) - 1):
            for u, v, data in network.graph.edges(data=True):
                weight = data['weight']
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u

                if distances[v] != float('inf') and distances[v] + weight < distances[u]:
                    distances[u] = distances[v] + weight
                    predecessors[u] = v

        for u, v, data in network.graph.edges(data=True):
            if distances[u] != float('inf') and distances[u] + data['weight'] < distances[v]:
                print("The graph contains a negative weight cycle")
                return None

        for target_node in network.nodes.values():
            if source_node.name == target_node.name:
                source_paths[target_node.name] = [source_node.name]
            else:
                path = []
                step = target_node.name
                while step is not None:
                    path.append(step)
                    step = predecessors[step]
                path.reverse()
                if path[0] == source_node.name:
                    source_paths[target_node.name] = path
                else:
                    source_paths[target_node.name] = None

        shortest_paths[source_node.name] = source_paths

    return shortest_paths

def find_shortest_path_dijks(network, source_name, destination_name, weight='weight'):
    """
    Finds the shortest path from source_name to destination_name using Dijkstra's algorithm.

    Parameters:
    -----------
    network : Network
        The network object containing nodes and links.
    source_name : str
        The name of the source node.
    destination_name : str
        The name of the destination node.
    weight : str, optional
        The edge attribute to be used as weight (default is 'weight').

    Returns:
    --------
    list
        The shortest path from source_name to destination_name as a list of node names.
    None
        If no path exists or the source/destination node is not found.
    """
    try:
        path = nx.dijkstra_path(network.graph, source=source_name, target=destination_name, weight=weight)
        print(f"Shortest path from {source_name} to {destination_name}: {path}")
        return path
    except nx.NetworkXNoPath:
        print(f"No path exists between {source_name} and {destination_name}.")
        return None
    except KeyError as e:
        print(f"Node {e} not found in the network.")
        return None

def compute_all_shortest_paths(network):
    """
    Computes the shortest paths between all pairs of nodes using Dijkstra's algorithm.

    Parameters:
    -----------
    network : Network
        The network object containing nodes and links.
    """
    all_paths = dict(nx.all_pairs_dijkstra_path(network.graph))
    for source, destinations in all_paths.items():
        for destination, path in destinations.items():
            print(f"Shortest path from {source} to {destination}: {path}")

def visualize_path(path, network):
    """
    Visualizes the network graph with the specified path highlighted.

    Parameters:
    -----------
    path : list
        The list of node names representing the path to be highlighted.
    network : Network
        The network object containing nodes and links.
    """
    pos = nx.spring_layout(network.graph)
    nx.draw(network.graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold')
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_nodes(network.graph, pos, nodelist=path, node_color='red')
    nx.draw_networkx_edges(network.graph, pos, edgelist=path_edges, edge_color='red', width=2)
    plt.show()

# Example usage:
network_nsf = Network()
network_nsf.add_node(1, 'A')
network_nsf.add_node(2, 'B')
network_nsf.add_node(3, 'C')
network_nsf.add_node(4, 'D')

network_nsf.add_link(2, 3, 1)
network_nsf.add_link(2, 1, 1)
network_nsf.add_link(3, 1, 3)
network_nsf.add_link(3, 4, 2)
network_nsf.add_link(1, 4, 2)

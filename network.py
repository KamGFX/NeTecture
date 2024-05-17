import networkx as nx
import matplotlib.pyplot as plt
from node import Node
from link import Link

class Network:
    """
    A class to represent a network consisting of nodes and links.

    Attributes:
    -----------
    nodes : dict
        A dictionary to store nodes with node IDs as keys and Node objects as values.
    links : list
        A list to store Link objects representing the links between nodes.
    graph : networkx.Graph
        A graph to represent the network topology.

    Methods:
    --------
    __init__():
        Initializes the Network object with empty nodes, links, and a graph.

    add_node(node_id, name, node_type='router'):
        Adds a node to the network.

    add_link(source_id, destination_id, bandwidth):
        Adds a link between two nodes in the network.

    remove_node(node_name):
        Removes a node and its associated links from the network.

    remove_link(source_id, destination_id):
        Removes a link between two nodes in the network.

    display_network():
        Prints the nodes and links in the network.

    visualize_network():
        Visualizes the network graph.
    """

    def __init__(self):
        """
        Initializes the Network object with empty nodes, links, and a graph.
        """
        self.nodes = {}
        self.links = []
        self.graph = nx.Graph()

    def add_node(self, node_id, name, node_type='router'):
        """
        Adds a node to the network.

        Parameters:
        -----------
        node_id : str
            The unique identifier for the node.
        name : str
            The name of the node.
        node_type : str, optional
            The type of the node (default is 'router').
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, name, node_type)
            self.graph.add_node(name, node_type=node_type)

    def add_link(self, source_id, destination_id, bandwidth):
        """
        Adds a link between two nodes in the network.

        Parameters:
        -----------
        source_id : str
            The unique identifier for the source node.
        destination_id : str
            The unique identifier for the destination node.
        bandwidth : float
            The bandwidth of the link in Gbps.
        """
        if source_id in self.nodes and destination_id in self.nodes:
            source_node = self.nodes[source_id]
            destination_node = self.nodes[destination_id]
            self.links.append(Link(source_node, destination_node, bandwidth))
            self.graph.add_edge(source_node.name, destination_node.name, weight=1/bandwidth)
        else:
            print(f"Error: Nodes {source_id} and/or {destination_id} not found in the network")

    def remove_node(self, node_name):
        """
        Removes a node and its associated links from the network.

        Parameters:
        -----------
        node_name : str
            The name of the node to be removed.
        """
        for node_id, node in self.nodes.items():
            if node.name == node_name:
                del self.nodes[node_id]
                self.graph.remove_node(node_name)
                self.links = [link for link in self.links if
                              link.source.name != node_name and link.destination.name != node_name]
                return
        print(f"Error: Node with name {node_name} not found")

    def remove_link(self, source_id, destination_id):
        """
        Removes a link between two nodes in the network.

        Parameters:
        -----------
        source_id : str
            The unique identifier for the source node.
        destination_id : str
            The unique identifier for the destination node.
        """
        if source_id in self.nodes and destination_id in self.nodes:
            self.graph.remove_edge(self.nodes[source_id].name, self.nodes[destination_id].name)
            self.links = [link for link in self.links if
                          link.source != self.nodes[source_id] or link.destination != self.nodes[destination_id]]
        else:
            print("Error: Source or destination node not found")

    def display_network(self):
        """
        Prints the nodes and links in the network.
        """
        print("Nodes in the network:")
        for node in self.nodes.values():
            print(node)
        print("\nLinks in the network:")
        for link in self.links:
            print(link)

    def visualize_network(self):
        """
        Visualizes the network graph.
        """
        pos = nx.spring_layout(self.graph)  # positions for all nodes
        nx.draw(self.graph, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10,
                font_weight="bold")
        labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels, font_size=7)
        plt.show()





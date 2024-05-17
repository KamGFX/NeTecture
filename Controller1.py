import socket
import threading
import json
import networkx as nx
import rsa
import pickle
from network import Network

# Cargar claves RSA desde archivos
with open('pri_key.txt', 'rb') as file_pri:
    private_key = pickle.load(file_pri)

with open('pub_key.txt', 'rb') as file_pub:
    public_key = pickle.load(file_pub)

#Create Network

network = Network()

network.add_node(1, '10.0.0.1')
network.add_node(2, '10.0.0.2')
network.add_node(3, '10.0.0.3')
network.add_node(4, '10.0.0.4')
network.add_node(5, '10.0.0.5')
network.add_node(6, '10.0.0.6')
network.add_node(7, '10.0.0.7')
network.add_node(8, '10.0.0.8')
network.add_node(9, '10.0.0.9')
network.add_node(10, '10.0.0.10')
network.add_node(11, '10.0.0.11')
network.add_node(12, '10.0.0.12')
network.add_node(13, '10.0.0.13')
network.add_node(14, '10.0.0.14')

network.add_link(1, 2, 2100)
network.add_link(1, 8, 4800)
network.add_link(1, 3, 3000)
network.add_link(2, 4, 1500)
network.add_link(2, 3, 1200)
network.add_link(3, 6, 3600)
network.add_link(4, 5, 1200)
network.add_link(4, 11, 3900)
network.add_link(5, 7, 1200)
network.add_link(5, 6, 2400)
network.add_link(6, 10, 2100)
network.add_link(6, 14, 3600)
network.add_link(7, 10, 2700)
network.add_link(7, 8, 1500)
network.add_link(8, 9, 1500)
network.add_link(9, 10, 1500)
network.add_link(9, 12, 600)
network.add_link(9, 13, 600)
network.add_link(11, 12, 1200)
network.add_link(11, 13, 1500)
network.add_link(12, 14, 600)
network.add_link(13, 14, 300)

class TCPServer:
    """
    Class to implement a TCP server for routing in a network.

    Attributes:
        host (str): The host address for the server.
        port (int): The port number for the server.
        server_socket (socket): The server socket object.
        node_timers (dict): A dictionary to store node timers.
        algorithm (str): The routing algorithm used by the server.
    """

    def __init__(self, host, port, algorithm):
        """
        Initializes the TCPServer with given parameters.

        Args:
            host (str): The host address for the server.
            port (int): The port number for the server.
            algorithm (str): The routing algorithm used by the server.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.node_timers = {}
        self.algorithm = None

    def start(self):
        """
        Starts the TCP server, binds it to the specified host and port, and listens for incoming connections.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}...")
        threading.Timer(30, self.update_routing_tables).start()
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection established with {client_address}")
                client_handler_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler_thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket):
        """
        Handles the incoming client connections.

        Args:
            client_socket (socket): The client socket object.
        """
        try:
            encrypted_node_name = client_socket.recv(1024)
            node_name_bytes = rsa.decrypt(encrypted_node_name, private_key)
            node_name = node_name_bytes.decode()

            print(f"Received request from node: {node_name}")
            if node_name in self.node_timers:
                self.node_timers[node_name].cancel()
            self.node_timers[node_name] = threading.Timer(30, self.remove_node, args=(node_name,))
            self.node_timers[node_name].start()
            with open("routing_tables.json", "r") as file:
                routing_tables = json.load(file)
                if node_name in routing_tables:
                    routing_table_json = json.dumps(routing_tables[node_name], indent=4)
                    client_socket.sendall(routing_table_json.encode())
                    print(f"Routing table sent to {node_name}.")
                else:
                    print(f"No routing table found for node {node_name}.")
                    node_id = node_name[-1]
                    self.add_node_to_network(node_name, node_id)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def compute_routing_tables(self):
        """
        Computes the routing tables based on the selected routing algorithm.
        """
        if algorithm == '2':
            all_paths = dict(nx.all_pairs_dijkstra_path(network.graph))
        elif algorithm == '1':
            all_paths = dict(nx.all_pairs_bellman_ford_path(network.graph))
        else:
            raise ValueError(
                "Invalid algorithm specified. Choose dijkstra ('1') or bellman_ford ('2').")
        routing_tables = {}
        for node, paths in all_paths.items():
            routing_tables[node] = {}
            for destination, path in paths.items():
                routing_tables[node][destination] = path
        with open("routing_tables.json", "w") as file:
            json.dump(routing_tables, file, indent=4)
        print("Routing tables written to routing_tables.json.")
        threading.Timer(30, self.update_routing_tables).start()

    def update_routing_tables(self):
        """
        Updates the routing tables periodically.
        """
        threading.Thread(target=self.compute_routing_tables).start()

    def remove_node(self, node_name):
        """
        Removes the specified node from the network topology.

        Args:
            node_name (str): The name of the node to be removed.
        """
        print(f"Removing node {node_name} from topology.")
        network.remove_node(node_name)

    def add_node_to_network(self, node_name, node_id):
        """
        Reconnects the specified node and adds it back to the network.

        Args:
            node_name (str): The name of the node to be reconnected.
            node_id (int): The ID of the node to be reconnected.
        """
        print(f"Node {node_name} reconnected. Adding it back to the network.")
        network.add_node(node_id, node_name)
        network.display_network()

def menu():
    """
    Displays the initialization menu for selecting the routing algorithm.

    Returns:
        str: The selected routing algorithm.
    """
    print("=== INITIALIZATION ====")
    print("  1. Bellman-Ford")
    print("  2. Dijkstra")
    while True:
        try:
            choice = int(input("Enter an option to adjust your algorithm: "))
            if choice == 1:
                return "1"
            elif choice == 2:
                return "2"
            else:
                print("Invalid option. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 2).")

# Example usage
if __name__ == "__main__":
    algorithm = menu()
    server = TCPServer("localhost", 1000, algorithm)
    server.start()

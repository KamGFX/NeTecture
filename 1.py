import socket
import json
import threading
import time
import pickle
import rsa

# Load RSA keys from files
with open('pri_key.txt', 'rb') as file_pri:
    private_key = pickle.load(file_pri)

with open('pub_key.txt', 'rb') as file_pub:
    public_key = pickle.load(file_pub)

class TCPNode:
    def __init__(self, node_name, server_host, server_port, listen_port, outgoing_ports):
        """
        Initializes a TCP node.

        Parameters:
        node_name (str): Name of the node.
        server_host (str): Hostname or IP address of the server.
        server_port (int): Port number of the server.
        listen_port (int): Port number to listen for incoming connections.
        outgoing_ports (list): List of outgoing ports for connecting to other nodes.
        """
        self.node_name = node_name
        self.server_host = server_host
        self.server_port = server_port
        self.listen_port = listen_port
        self.outgoing_ports = outgoing_ports
        self.routing_table = None

        # Load port mapping from file
        with open("port_mapping.json", "r") as file:
            self.port_mapping = json.load(file)

    def start(self):
        """
        Starts the TCP node by initializing the server for incoming connections and connecting to the controller server.
        """
        # Start server for incoming connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", self.listen_port))
        self.server_socket.listen(5)
        print(f"Node {self.node_name} listening on port {self.listen_port}...")

        # Connect to the controller server to get the routing table
        self.connect_to_server()

        # Listen for incoming connections from other nodes in a separate thread
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def stop(self):
        """
        Stops the TCP node by closing the server socket.
        """
        self.server_socket.close()

    def connect_to_server(self):
        """
        Connects to the controller server to obtain the routing table.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_host, self.server_port))
                encrypted_node_name = rsa.encrypt(self.node_name.encode(), public_key)
                client_socket.sendall(encrypted_node_name)
                routing_table_json = client_socket.recv(4096).decode()
                self.routing_table = json.loads(routing_table_json)  # Assign the received routing table
                print(f"ACK received from controller: {self.routing_table}")
        except Exception as e:
            print(f"Error while connecting to server: {e}")

    def accept_connections(self):
        """
        Accepts incoming connections from other nodes.
        """
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Node {self.node_name} accepted connection from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket):
        """
        Handles messages received from other nodes.

        Parameters:
        client_socket (socket.socket): Client socket for communication.
        """
        try:
            data = client_socket.recv(1024)
            message_data = pickle.loads(data)
            message_type = message_data.get("type")
            origin_node = message_data.get("origin")
            destination_node = message_data.get("destination")
            user_message = message_data.get("message")

            # Call the method to handle the user message
            self.handle_user_message(message_type, origin_node, destination_node, user_message)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def connect_to_node(self, destination_node_name, position, message):
        """
        Connects to a destination node and sends a message.

        Parameters:
        destination_node_name (str): Name of the destination node.
        position (int): Index of the outgoing port to use.
        message (str): Message to send.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(("localhost", self.outgoing_ports[position]))
                client_socket.sendall(destination_node_name.encode())
                print(f"Node {self.node_name} connected to {destination_node_name} on port {self.outgoing_ports[position]}")
                client_socket.sendall(message.encode())  # Send a message to the destination node
        except Exception as e:
            print(f"Error while connecting to node {destination_node_name} on port {self.outgoing_ports[position]}: {e}")

    def handle_user_message(self, message_type, origin_node, destination_node, user_message):
        """
        Handles a user message received from another node.

        Parameters:
        message_type (str): Type of the message.
        origin_node (str): Name of the origin node.
        destination_node (str): Name of the destination node.
        user_message (str): User message content.
        """
        print(f"Received user message from {origin_node} to {destination_node}: {user_message}")

        # Forward the user message using route_message
        self.route_message(destination_node, {
            "type": message_type,
            "origin": origin_node,
            "destination": destination_node,
            "message": user_message
        })

    def route_message(self, destination_node_name, message):
        """
        Routes a message to a destination node.

        Parameters:
        destination_node_name (str): Name of the destination node.
        message (dict): Message to be routed.
        """
        # Check if the destination is in the routing table
        if destination_node_name in self.routing_table:
            # Get the shortest path to the destination node
            path_to_destination = self.routing_table[destination_node_name]

            # Check if the path is valid (must contain at least two nodes: source and next hop)
            if len(path_to_destination) > 1:
                # Get the next hop (second node in the path)
                next_hop = path_to_destination[1]

                # Get the outgoing port for the next hop from the port_mapping dictionary
                next_hop_port = self.port_mapping[next_hop]

                if next_hop_port is not None:
                    # Establish connection with the next hop
                    self.connect_to_node(destination_node_name, next_hop_port, pickle.dumps(message))
                    print(f"Node {self.node_name} routed message to {destination_node_name} via {next_hop}")
                else:
                    print(f"No outgoing port found for next hop {next_hop}.")
            else:
                # If the current node is the destination node, send the message back to the receiving client
                print(f"Node {self.node_name} is the destination node. Sending message back to client.")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect(("localhost", client_port))  # Connect to the client's listening port
                    client_socket.sendall(pickle.dumps(message))
        else:
            print(f"No route found to {destination_node_name}")


# Ejemplo de uso
if __name__ == "__main__":
    node_name = "10.0.0.1"
    server_host = "localhost"
    client_port = 2001
    server_port = 1000
    listen_port = 1001
    outgoing_ports = [1002, 1003, 1004]  # Definir los puertos de salida
    node = TCPNode(node_name, server_host, server_port, listen_port, outgoing_ports)
    node.start()

    while True:
        node.connect_to_server()
        time.sleep(15)

import socket
import json
import threading
import time
import pickle
import rsa

# Cargar claves RSA desde archivos
with open('pri_key.txt', 'rb') as file_pri:
    private_key = pickle.load(file_pri)

with open('pub_key.txt', 'rb') as file_pub:
    public_key = pickle.load(file_pub)

class TCPNode:
    def __init__(self, node_name, server_host, server_port, listen_port, outgoing_ports):
        self.node_name = node_name
        self.server_host = server_host
        self.server_port = server_port
        self.listen_port = listen_port
        self.outgoing_ports = outgoing_ports
        self.routing_table = None

        # Cargar el mapeo de puertos desde el archivo
        with open("port_mapping.json", "r") as file:
            self.port_mapping = json.load(file)

    def start(self):
        # Iniciar servidor para conexiones entrantes
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", self.listen_port))
        self.server_socket.listen(5)
        print(f"Node {self.node_name} listening on port {self.listen_port}...")

        # Conectar al servidor para obtener tabla de enrutamiento
        self.connect_to_server()

        # Escuchar conexiones entrantes de otros nodos en un hilo separado
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def stop(self):
        # Detener el servidor y cerrar conexiones
        self.server_socket.close()

    def connect_to_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_host, self.server_port))
                encrypted_node_name = rsa.encrypt(self.node_name.encode(), public_key)
                client_socket.sendall(encrypted_node_name)
                routing_table_json = client_socket.recv(4096).decode()
                self.routing_table = json.loads(routing_table_json)  # Asignar la tabla de enrutamiento recibida
                print(f"ACK received from controller: {self.routing_table}")
        except Exception as e:
            print(f"Error while connecting to server: {e}")

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Node {self.node_name} accepted connection from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024)
            message_data = pickle.loads(data)
            message_type = message_data.get("tipo")
            origin_node = message_data.get("origen")
            destination_node = message_data.get("destino")
            user_message = message_data.get("mensaje")

            # Llamar al método que maneja el mensaje de usuario
            self.handle_user_message(message_type, origin_node, destination_node, user_message)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def connect_to_node(self, destination_node_name, position, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(("localhost", self.outgoing_ports[position]))
                client_socket.sendall(destination_node_name.encode())
                print(f"Node {self.node_name} connected to {destination_node_name} on port {self.outgoing_ports[position]}")
                client_socket.sendall(message.encode())  # Envía un mensaje al nodo destino
        except Exception as e:
            print(f"Error while connecting to node {destination_node_name} on port {self.outgoing_ports[position]}: {e}")

    def handle_user_message(self, message_type, origin_node, destination_node, user_message):
        print(f"Received user message from {origin_node} to {destination_node}: {user_message}")

        # Reenviar el mensaje de usuario utilizando route_message
        self.route_message(destination_node, {
            "tipo": message_type,
            "origen": origin_node,
            "destino": destination_node,
            "mensaje": user_message
        })

    def route_message(self, destination_node_name, message):
        # Verificar si el destino está en la tabla de enrutamiento
        if destination_node_name in self.routing_table:
            # Obtener el camino más corto al nodo destino
            path_to_destination = self.routing_table[destination_node_name]

            # Verificar si el camino es válido (debe contener al menos dos nodos: origen y siguiente salto)
            if len(path_to_destination) > 1:
                # Obtener el siguiente salto (segundo nodo en el camino)
                next_hop = path_to_destination[1]

                # Obtener el puerto de salida para el siguiente salto del diccionario port_mapping
                next_hop_port = self.port_mapping[next_hop]

                if next_hop_port is not None:
                    # Establecer conexión con el siguiente salto
                    self.connect_to_node(destination_node_name, next_hop_port, pickle.dumps(message))
                    print(f"Node {self.node_name} routed message to {destination_node_name} via {next_hop}")
                else:
                    print(f"No outgoing port found for next hop {next_hop}.")
            else:
                # Si el nodo actual es el nodo destino, enviar el mensaje de vuelta al cliente receptor
                print(f"Node {self.node_name} is the destination node. Sending message back to client.")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect(("localhost", client_port))  # Conectarse al puerto de escucha del cliente
                    client_socket.sendall(pickle.dumps(message))
        else:
            print(f"No route found to {destination_node_name}")


# Ejemplo de uso
if __name__ == "__main__":
    node_name = "10.0.0.14"
    server_host = "localhost"
    client_port = 2014
    server_port = 1000
    listen_port = 1014
    outgoing_ports = [1001, 1002, 1004]  # Definir los puertos de salida
    node = TCPNode(node_name, server_host, server_port, listen_port, outgoing_ports)
    node.start()

    while True:
        node.connect_to_server()
        time.sleep(15)
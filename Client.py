import dijkstra_paths
import json
import pickle
import rsa
import socket
import threading
from Controller1 import network

CHUNK = 1024

# Load RSA keys from files
with open('pri_key.txt', 'rb') as file_pri:
    private_key = pickle.load(file_pri)

with open('pub_key.txt', 'rb') as file_pub:
    public_key = pickle.load(file_pub)

def encrypt_message(message, public_key):
    """
    Encrypts a message using an RSA public key.

    Parameters:
    message (bytes): Message to encrypt.
    public_key (rsa.PublicKey): RSA public key.

    Returns:
    bytes: Encrypted message.
    """
    return rsa.encrypt(message, public_key)

def decrypt_message(encrypted_message, private_key):
    """
    Decrypts a message using an RSA private key.

    Parameters:
    encrypted_message (bytes): Encrypted message.
    private_key (rsa.PrivateKey): RSA private key.

    Returns:
    bytes: Decrypted message.
    """
    return rsa.decrypt(encrypted_message, private_key)

def load_port_mapping():
    """
    Loads port mapping from a JSON file.

    Returns:
    dict: Port mapping.
    """
    with open('port_mapping.json', 'r') as file:
        port_mapping = json.load(file)
    return port_mapping

def send_message(origin_node, destination_node, message, public_key, origin_port, message_type="user_message", audio_file=None):
    """
    Sends a message to a destination node.

    Parameters:
    origin_node (str): Origin node.
    destination_node (str): Destination node.
    message (str): Message to send.
    public_key (rsa.PublicKey): Recipient's RSA public key.
    origin_port (int): Origin port.
    message_type (str): Type of message ("user_message" or "audio_message"). Default is "user_message".
    audio_file (str, optional): Name of the audio file to send. Required if message_type is "audio_message".
    """
    try:
        # Establish connection to the target node
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", origin_port))  # Connect to the node's listening port
        with open("routing_tables.json", "r") as file:
            routing_tables = json.load(file)
            if origin_node in routing_tables:
                routing_table_json = routing_tables[origin_node]
                path = routing_table_json[destination_node]

        # If it is an audio message, attach the file to the message.
        if message_type == "audio_message":
            # Read audio file and send in chunks
            with open(audio_file, 'rb') as f:
                i = 0
                while i < 10:
                    i += 1
                    chunk = f.read(53)
                    if not chunk:
                        break
                    encrypted_chunk = encrypt_message(chunk, public_key)
                    data = {
                        "type": "audio_message",
                        "origin": origin_node,
                        "destination": destination_node,
                        "message": encrypted_chunk
                    }
                    # Establish a new connection to send current chunk
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect(("localhost", origin_port))  # Connect to the node listening port
                    client_socket.sendall(pickle.dumps(data))
                    client_socket.close()  # Close connection after sending chunk

        if message_type == "user_message":
            # Encrypt message only
            encrypted_message = encrypt_message(message.encode(), public_key)  # Convert to bytes before encryption

            # Construct the complete message with the data information
            data = {
                "type": message_type,
                "origin": origin_node,
                "destination": destination_node,
                "message": encrypted_message
            }

            # Send complete message to the node
            client_socket.sendall(pickle.dumps(data))

        # Confirmation send message
        print("Message sent successfully!")

        # Close connection
        dijkstra_paths.visualize_path(path, network)
        client_socket.close()

    except Exception as e:
        print(f"Error sending message: {e}")

def handle_client(client_socket, private_key):
    """
    Handles incoming messages from a client.

    Parameters:
    client_socket (socket.socket): Client socket.
    private_key (rsa.PrivateKey): RSA private key to decrypt the message.
    """
    try:
        audio_chunks = b''
        # Receive message from node
        data = pickle.loads(client_socket.recv(1024))
        message_type = data.get("type")
        message = data.get("message")

        # Decrypt message
        decrypted_message = decrypt_message(message, private_key)

        # Process message as required
        if message_type == "2":
            print(f"Message received from {data['origin']}: {decrypted_message}")
            # Process text message as required

        elif message_type == "1":
            print(f"Audio message received from {data['origin']}")
            # Concatenate audio packets
            audio_chunks += decrypted_message
            print("Audio chunk received.")

        else:
            print("Unknown message type")

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Close connection to the node
        client_socket.close()

def listen_for_messages(private_key):
    """
    Listens for incoming messages on a specific port and handles them in a separate thread.

    Parameters:
    private_key (rsa.PrivateKey): RSA private key to decrypt messages.
    """
    server_socket = None
    try:
        # Set socket to listen to incoming messages
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", 7001))  # Client listening port
        server_socket.listen(5)
        # print("Client listening for incoming messages...")

        while True:
            # Accept incoming connections
            client_socket, client_address = server_socket.accept()
            print(f"Client accepted connection from {client_address}")

            # Process message as required
            threading.Thread(target=handle_client, args=(client_socket, private_key)).start()

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Closing server socket...")
        if server_socket:
            server_socket.close()
    except Exception as e:
        print(f"Error listening for messages: {e}")
        if server_socket:
            server_socket.close()

def menu():
    """
    Displays the menu for sending messages and exiting the program.
    """
    while True:
        print("\n===== MENU =====")
        print("1. Send User message")
        print("2. Send Audio Message")
        print("3. Exit")
        choice = input("Enter your Option: ")

        if choice == "1":
            origin_node = input("Enter Origin Node (IP): ")
            destination_node = input("Enter Destination Node (IP): ")
            message = input("Enter message: ")
            origin_port = int(port_mapping.get(origin_node))
            if origin_port is None:
                print(f"No Port Found for IP Address {origin_node}")
            else:
                send_message(origin_node, destination_node, message, public_key, origin_port)

        elif choice == "2":
            origin_node = input("Enter Origin Node (IP): ")
            destination_node = input("Enter Destination Node (IP): ")
            audio_file = input("Enter Audio File Name: ")
            origin_port = int(port_mapping.get(origin_node))
            if origin_port is None:
                print(f"No Port Found for IP Address {origin_node}")
            else:
                send_message(origin_node, destination_node, audio_file, public_key, origin_port, "audio_message", audio_file)

        elif choice == "3":
            print("Exiting the Program...")
            break
        else:
            print("Invalid Option. Please Enter a Valid Option.")

if __name__ == "__main__":
    server_socket = None
    try:
        # Start a thread to listen to incoming messages
        threading.Thread(target=listen_for_messages, args=(private_key,)).start()

        # Load the mapping of IP to Port
        port_mapping = load_port_mapping()

        # Show Menu
        menu()
    except KeyboardInterrupt:
        print("Keyboard Interrupt Received. Exiting Program...")
        if server_socket:
            server_socket.close()


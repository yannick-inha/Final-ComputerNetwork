import socket
import threading
import csv
import base64
import json
from pprint import pprint
import PIL.Image
from csv import reader
from tabulate import tabulate

def printCSV(csvFile, delimiter=',', quotechar=''):
    print("type", type(csvFile))
    csvReader = list(reader(csvFile.split('\n'), delimiter=delimiter))
    print(tabulate(csvReader, headers='firstrow'))

def pixel_to_ascii(data):
    img_flag = True
    path = "received_image.png"
    with open(path, 'wb') as file:
            file.write(data)
    try:
        img = PIL.Image.open(path)
        img_flag = True
    except:
        print(path, "Unable to find image ");
    
    width, height = img.size
    aspect_ratio = height/width
    new_width = 120
    new_height = aspect_ratio * new_width * 0.55
    img = img.resize((new_width, int(new_height)))
    
    img = img.convert('L')
    
    chars = ["@", "J", "D", "%", "*", "P", "+", "Y", "$", ",", "."]
    
    pixels = img.getdata()
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
    ascii_image = "\n".join(ascii_image)
    print(ascii_image)


def printJSON(jsonString):
    jsonData = json.loads(jsonString)
    pprint(jsonData)

def send_json_data(index):
    file_path = input("Enter the path to the json file: ")
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        json_data = json.dumps(data)
        extension_size = len("json").to_bytes(1, byteorder='big')
        list_connected_clients[index].sendall(extension_size)
        list_connected_clients[index].sendall("json".encode('utf-8'))
        file_size = len(json_data).to_bytes(4, byteorder='big')
        list_connected_clients[index].sendall(file_size)
        list_connected_clients[index].sendall(json_data.encode('utf-8'))

def send_png_data(index):
    image_path = input("Enter the path to the image: max 3mo")
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    extension_size = len("png").to_bytes(1, byteorder='big')
    list_connected_clients[index].sendall(extension_size)
    list_connected_clients[index].sendall("png".encode('utf-8'))
    file_size = len(image_data).to_bytes(4, byteorder='big')
    list_connected_clients[index].sendall(file_size)
    list_connected_clients[index].sendall(image_data)

def receive_png_data(client_socket, save_path):
    image_data = client_socket.recv(1024)
    with open(save_path, 'wb') as image_file:
        image_file.write(base64.b64decode(image_data))

def send_csv_data(index):
    csv_path = input("Enter the path to the csv file: ")
    with open(csv_path, 'r') as csv_file:
        data = csv.reader(csv_file)
        csv_data = ""
        print(data)
        for row in data:
            csv_data += ','.join(map(str, row)) + '\n'
        extension_size = len("csv").to_bytes(1, byteorder='big')
        list_connected_clients[index].sendall(extension_size)
        list_connected_clients[index].sendall("csv".encode('utf-8'))
        file_size = len(csv_data).to_bytes(4, byteorder='big')
        list_connected_clients[index].sendall(file_size)
        list_connected_clients[index].sendall(csv_data.encode('utf-8'))

list_connected_clients = []
new_client_lock = threading.Lock()
new_client = None

def receive_messages(client_socket):
    while True:
        try:
            print("Waiting for message...")
            # Receive and deserialize the message
            extension_size_byte = client_socket.recv(1)
            extension_size = int.from_bytes(extension_size_byte, byteorder='big')
            file_type = client_socket.recv(extension_size).decode('utf-8')
            file_size_bytes = client_socket.recv(4)
            file_size = int.from_bytes(file_size_bytes, byteorder='big')
            data = client_socket.recv(file_size)

            print("File type: " + file_type)
            # Receive the first message
            # Extract file type and data from the message
            if file_type == "json":
                printJSON(data)
                return
            elif file_type == "csv":
                printCSV(data.decode('utf-8'))
                return
            elif file_type == "png":
                pixel_to_ascii(data)
                return

        except (socket.error, ConnectionResetError):
            print("Connection closed.")
            break


def main_menu(server_socket, ip, port):
    while True:
        print("\nMain Menu:")
        print("1. wait")
        print("2. connect")
        print("4. Exit")
        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                server_socket.listen()
                print(f"Listening for connections on {ip}:{port}")
                client_socket, client_address = server_socket.accept()
                print(f"Received connection from {client_address[0]}:{client_address[1]}")
                return client_socket
            elif choice == 2:
                # peer_ip = input("Enter peer's IP address: ")
                peer_ip = "0.0.0.0"
                peer_port = int(input("Enter peer's port number: "))
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    # Connect to the peer
                    client_socket.connect((peer_ip, peer_port))
                    print(f"Connected to peer at {peer_ip}:{peer_port}")
                except (socket.error, ConnectionRefusedError):
                    print(f"Failed to connect to peer at {peer_ip}:{peer_port}")
                    exit()
                print(f"Connected to {peer_ip}:{peer_port}")
                return client_socket
        except ValueError:
            print("Invalid input. Please enter a number.")

def wait_for_connection(server_socket, ip, port):
    global new_client
    with new_client_lock:
        server_socket.listen(len(list_connected_clients) + 1)
        print(f"Listening for connections on {ip}:{port}")
        client_socket, client_address = server_socket.accept()
        print(f"Received connection from {client_address[0]}:{client_address[1]}")
        new_client = client_socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ip = "0.0.0.0"
    port = int(input("Enter your port: "))
    server_socket.bind((ip, port))
    first_client = main_menu(server_socket, ip, port)
    receive_thread = threading.Thread(target=receive_messages, args=(first_client,))
    receive_thread.start()
    list_connected_clients.append(first_client)

    while True:
        print("1. Send a message")
        print("2. List connected clients")
        print("3. Wait for a connection")
        print("4. Share all sockets")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            print("Choose a client to send the message")
            for elem in list_connected_clients:
                print(list_connected_clients.index(elem))
                print(elem.getpeername())
            index = int(input("Enter the index of the client: "))
            print("Choose a file type to send")
            print("1. CSV")
            print("2. PNG")
            print("3. JSON")
            file_type = input("Enter your choice: ")            
            # Serialize and send the data based on file type
            if file_type == '1':
                send_csv_data(index)
            elif file_type == '2':
                send_png_data(index)
            elif file_type == '3':
                send_json_data(index)
        elif choice == "2":
            for element in list_connected_clients:
                print(element.getpeername())
        elif choice == "3":
            thread_client = threading.Thread(target=wait_for_connection, args=(server_socket, ip, port))
            thread_client.start()
            thread_client.join()  # Wait for the new client thread to finish
            with new_client_lock:
                if new_client and new_client not in list_connected_clients:
                    receive_thread = threading.Thread(target=receive_messages, args=(new_client,))
                    receive_thread.start()
                    list_connected_clients.append(new_client)
        elif choice == "5":
            print("Exiting...")
            # Close all connections and exit
            for client_socket in list_connected_clients:
                client_socket.close()
            exit()
        else:
            print("Invalid choice. Please enter a valid option.")


if __name__ == "__main__":
    start_server()

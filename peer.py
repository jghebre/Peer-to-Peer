import multiprocessing
from socket import *

from collections import deque
from multiprocessing import Manager, Process
from datetime import datetime

import platform
import traceback

import os


# Define the server's IP address and port
SERVER_IP = '127.0.0.1'  # Use the server's IP address (use 'localhost' or '127.0.0.1' if running on the same machine)
SERVER_PORT = 7734  # The port number used by the server

# Maximum number of connections the peer can handle
max_connects = 5



# Create a global linked list variable for holding all current client RFCs
# client_rfc_list = deque()

def colored_text(text, color, bold=False):
    color_codes = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
    }
    color_code = color_codes.get(color.lower(), 37)  # Default to white if the color is not found
    bold_code = "1;" if bold else ""
    print(f"\033[{bold_code}{color_code}m{text}\033[0m")

def separator() :
    colored_text("-" * 80, "magenta")


def download_rfc_locally(local_rfc_list):

    rfc_number = input("Enter number of RFC to be downloaded: ")
    
    rfc_exists = False

    for rfc in local_rfc_list:
        if rfc['rfc_number'] == rfc_number:
            rfc_exists = True
            rfc_title = rfc['title']
            rfc_content = rfc['data']

    if(not rfc_exists) :
        colored_text(f"No RFC with that number", "red")

    try:
        # Create the downloaded_rfcs folder if it doesn't exist
        if not os.path.exists("downloaded_rfcs"):
            os.makedirs("downloaded_rfcs")

        # Save the RFC content to a new text file
        with open(f"downloaded_rfcs/RFC_{rfc_number}-{rfc_title}.txt", 'w') as file:
            file.write(rfc_content)

            colored_text("RFC downloaded successfully:", "green", True)
    except Exception as e:
        print(f"Error downloading RFC {rfc_number}: {e}")


def add_method(client_ip, client_port, local_rfc_list):
    if not local_rfc_list:
        colored_text("No RFCs to add. Please add an RFC first.", "red")
        return None

    rfc_number = input("Enter the RFC number to add: ")
    for rfc in local_rfc_list:
        if rfc['rfc_number'] == rfc_number:
            request = f"ADD RFC {rfc_number} P2P-CI/1.0\r\nHost: {client_ip}\r\nPort: {client_port}\r\nTitle: {rfc['title']}\r\n"
            return request
    else:
        colored_text("RFC not found in local list.", "red")
        return None


def list_method(client_ip, client_port):
    request = f"LIST ALL P2P-CI/1.0\r\nHost: {client_ip}\r\nPort: {client_port}\r\n"
    return request


def lookup_method(client_ip, client_port):
    rfc_number = input("Enter the RFC number to look up: ")
    title = input("Enter the title of the RFC: ")
    request = f"LOOKUP RFC {rfc_number} P2P-CI/1.0\r\nHost: {client_ip}\r\nPort: {client_port}\r\nTitle: {title}\r\n"
    return request


def connect_to_server(client_ip, client_port, client_rfc_list, local_rfc_list):
   # Create a socket object (TCP)
    peer_socket = socket(AF_INET, SOCK_STREAM)


    try:
        # Connect to the server
        peer_socket.connect((SERVER_IP, SERVER_PORT))

        # Receive the welcome message from the server
        welcome_message = peer_socket.recv(1024).decode()
        print(welcome_message)

        while True:
            separator()
            colored_text("Please choose a method to send to the server:", "green", True)
            print("1. Add RFC to server")
            print("2. List server RFCs")
            print("3. Lookup specific RFC on server")
            print("4. Close the connection to server")
            print("\n")
            colored_text("You may also choose an operation to be performed locally :", "cyan")
            print("5. Add an RFC locally")
            print("6. Print local Current RFCs")
            print("7. Get RFCs from Peers")
            print("8. Download local RFCs")

            command = input("Enter the command number: ")

            if command == "1":
                request = add_method(client_ip, client_port, local_rfc_list)
            elif command == "2":
                request = list_method(client_ip, client_port)
            elif command == "3":
                request = lookup_method(client_ip, client_port)
            elif command == "4":
                colored_text("Closing the connection...", "yellow")
                peer_socket.send(f"CLOSE {gethostbyaddr(client_ip)[0]} {client_port}".encode())
                break
            elif command == "5":
                add_rfc(local_rfc_list)
                continue
            elif command == "6":
                print_rfcs(local_rfc_list) 
                continue
            elif command == "7":
                get_rfc_from_peers(client_rfc_list, local_rfc_list)
                continue
            elif command == "8":
                download_rfc_locally(local_rfc_list)
                continue
            else:
                colored_text("Invalid command. Please try again.", "red")
                continue

            if request:
                colored_text("Sending: ", "white", True)
                colored_text(request, "blue")
                colored_text("....", "white")
                peer_socket.send(request.encode())
                response = peer_socket.recv(1024).decode()
                colored_text("Server says: ", "cyan", True)
                print(response)

              

            if command in ("2", "3"):

                # if (command == "3") :
                #     client_rfc_list.clear()     
                    
                # Update client_rfc_list based on the server's response
                lines = response.split('\r\n')
                data_lines = lines[1:]
                for line in data_lines:
                    if not line:
                        continue

                    parts = line.split(" ")
                    rfc_number = parts[1]
                    title = parts[2]
                    hostname = parts[3]
                    port = int(parts[4])

                    
                    # Add a new RFC entry to the client_rfc_list
                    client_rfc_list.append({"rfc_number": rfc_number, "title": title, "hostname": hostname, "port": port})


   
        

    except:
        # Close the connection
        peer_socket.close()
        raise

# Updated create_rfc_entry function with a data field
def create_rfc_entry(rfc_number, title, data):
    return {"rfc_number": rfc_number, "title": title, "data": data}

def add_rfc(local_rfc_list):
    colored_text("Enter the RFC information:", "yellow")

    # Prompt the user to enter the RFC number, title, and data
    rfc_number = input("RFC Number: ")
    title = input("Title: ")
    data = input("Data: ")

    # Create an RFC entry and add it to the global variable
    rfc_entry = create_rfc_entry(rfc_number, title, data)
    local_rfc_list.append(rfc_entry)

    colored_text(f"Added RFC {rfc_number} with title '{title}' and data '{data}' to the local RFC list.", "blue")



def print_rfcs(local_rfc_list) :
    if(len(local_rfc_list) == 0):
        colored_text("No RFCs currently in system", "red", True)
        separator()
    else :
        colored_text(f"Printing {len(local_rfc_list)} RFCs stored in system", "green", True)
        for rfc in local_rfc_list:
            separator()
            rfc_number = colored_text(f"RFC Number: {rfc['rfc_number']}", "yellow")
            title = colored_text(f"Title: {rfc['title']}", "green")
            data = colored_text(f"Data: {rfc['data']}", "blue")
        separator()

def parse_message(message):

    if(message == "CLOSE") :
        return message

    # Split the message by line breaks (<cr><lf>)    
    lines = message.split("\r\n")
    parts = lines[0].split(" ")
    method = parts[0]
    version = parts[-1]
    rfc_number = parts[2]

    if method != "GET":
        raise Exception("Incorrect Method, please use GET")


    # Parse the headers into key-value pairs    
    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        header_field_name, value = line.split(" ", 1)
        headers[header_field_name] = value

    # Extract the OS from the headers, if present
    os = headers.get("OS:", None)
    if(os == None) :
        raise Exception("Incorrect Header, please use OS:")
        

    # Extract the OS from the headers, if present
    host = headers.get("Host:", None)
    if(host == None) :
        raise Exception("Incorrect Header, please use Host:")

    return {
        "method": method,
        "rfc_number": rfc_number,
        "os": os,
        "host": host,
        
    }

def get_rfc(rfc_number, local_rfc_list):
    for rfc in local_rfc_list:
        if rfc['rfc_number'] == rfc_number:
            return rfc
    else:
        raise Exception(f"404 {rfc_number} Not Found")


def create_response(rfc, os):
    response = "P2P-CI/1.0 200 OK\r\n"
    response += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S')} GMT\r\n"
    response += f"OS: {os}\r\n"
    # response += f"Last-Modified: {rfc['last_modified'].strftime('%a, %d %b %Y %H:%M:%S')} GMT\r\n"
    response += f"Content-Length: {len(rfc['data'])}\r\n"
    response += f"Content-Type: text/text\r\n"
    response += f"\r\n{rfc['data']}"
    return response


def get_rfc_for_peers(connection_socket, addr, local_rfc_list) :

    
    
        try:
            res = connection_socket.recv(1024).decode()
            response = parse_message(res)

            if(response == "CLOSE") :
                connection_socket.send("Goodbye".encode())
                return

            rfc = get_rfc(response["rfc_number"], local_rfc_list)

            response_text = create_response(rfc, response["os"])
            connection_socket.send(response_text.encode())




        except Exception as e :
            connection_socket.send(str(e).encode())



def handle_peers(server_running, peering_socket, client_ip, client_port, client_rfc_list, local_rfc_list) :

    try:
         while server_running.value:
            try :
                # Accept incoming connections and store the socket info in "connectionSocket" and the IP/port info in "addr"
                connection_socket, addr = peering_socket.accept()

                # Create a new Process that calls the function with args from accept()
                process = Process(target=get_rfc_for_peers, args=(connection_socket, addr, local_rfc_list))
                process.start()
                connection_socket.close()
            except timeout:
                # If a timeout occurs, just continue with the loop without processing the connection
                continue
            except Exception as e:
                # If any other exception occurs, print it and continue with the loop
                # print(f"Error occurred while accepting connection: {e}")
                continue
            

    
    except KeyboardInterrupt:
        colored_text("\nClosing port dedicated to peer connections..", "yellow")

    except Exception as e:  # Catch any exception
        colored_text(f"An error occurred: {e}", "red")
        traceback.print_exc()

        colored_text("\nClosing port dedicated to peer connections..", "yellow")


    

    finally:
        # Close the server socket
        peering_socket.close()
        print("Server socket closed.")

def download(rfc, local_rfc_list):
    peer_socket = socket(AF_INET, SOCK_STREAM)

    peer_socket.connect((rfc["hostname"], rfc["port"]))

    

    request = f"GET RFC {rfc['rfc_number']} P2P-CI/1.0\r\n"
    request += f"Host: {gethostname()}\r\n"
    request += f"OS: {platform.system()} {platform.release()}\r\n"

    peer_socket.send(request.encode())

    response = peer_socket.recv(1024).decode()
    print(response)

    lines = response.split('\r\n')
    content_type_index = next(i for i, line in enumerate(lines) if line.startswith('Content-Type: text/text'))
    data_lines = lines[content_type_index + 1:]
    data = "\r\n".join(data_lines)
    
    new_rfc = {
        'rfc_number': rfc['rfc_number'],
        'title': rfc['title'],
        'data': data
    }

    local_rfc_list.append(new_rfc)

    peer_socket.close()



def get_rfc_from_peers(client_rfc_list,local_rfc_list) :

    if(len(client_rfc_list) == 0):
        colored_text("No Outside RFCs currently in system", "red", True)
        separator()
        return
    else :
        colored_text(f"Printing {len(client_rfc_list)} outside RFCs stored in system", "green", True)
        for rfc in client_rfc_list:
            separator()
            colored_text(f"RFC Number: {rfc['rfc_number']}", "yellow")
            colored_text(f"Title: {rfc['title']}", "green")
            colored_text(f"Hostname: {rfc['hostname']}", "blue")
            colored_text(f"Port: {rfc['port']}", "cyan")
        separator()

    rfc_number = input("Enter the RFC number you wish to download or type CLOSE to exit: ")
    while (rfc_number != "CLOSE") :
        for rfc in client_rfc_list:
            if rfc['rfc_number'] == rfc_number:
                download(rfc, local_rfc_list)
                return
        else:
            rfc_number = colored_text("Invalid RFC code please try again: ", "red", True)

    
        




def main():

    manager = Manager()

    local_rfc_list = manager.list()

    client_rfc_list = manager.list()

    peering_socket = socket(AF_INET, SOCK_STREAM)

    peering_socket.bind(('', 0))
    peering_socket.settimeout(5)

    hostname, client_port = peering_socket.getsockname()

    hostname = gethostname()
    client_ip = gethostbyname(hostname)
 

    
    # Get the client's port number after binding
    client_port = peering_socket.getsockname()[1]

    # Listen for incoming connections maximum of 5 at one time
    peering_socket.listen(max_connects)
    colored_text(f"Peer is listening on port {client_port} with a maximum of {max_connects} connections...", "green")
    separator()

    server_running = multiprocessing.Value('i', 1)
    p = multiprocessing.Process(target=handle_peers, args=(server_running,peering_socket, client_ip, client_port, client_rfc_list, local_rfc_list))
    p.start()
    
    # process = Process(target=handle_peers, args=(peering_socket, client_ip, client_port, client_rfc_list, local_rfc_list))
    # process.start()
    peering_socket.close()

    
    try :

       


        while True :
            colored_text("Welcome to the Peer-to-Peer Network!", "green")
            print("Please enter a command:")
            print("1. Add an RFC")
            print("2. Print Current RFCs")
            print("3. Talk to the server")
            print("4. Close the connection")

            command = input("Enter the command number: ")

            if command == "1":
                add_rfc(local_rfc_list)
            elif command == "2":
                print_rfcs(local_rfc_list) 
            elif command == "3":
                connect_to_server(client_ip, client_port, client_rfc_list, local_rfc_list)
            elif command == "4":
                colored_text("Closing the connection...", "yellow")
                server_running.value = 0
                p.join()
                break
            else:
                colored_text("Invalid command. Please try again.", "red")

    except KeyboardInterrupt:
        colored_text("\nKeyboardInterrupt detected. Closing the connection...", "yellow")
        server_running.value = 0

    except Exception as e:  # Catch any exception
        colored_text(f"An error occurred: {e}", "red")
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()

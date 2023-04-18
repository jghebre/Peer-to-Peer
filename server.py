from collections import deque

from socket import *



from multiprocessing import Process,Manager


# Servers port number
SERVER_PORT = 7734

# Maximum number of connections the server can handle
max_connects = 5

# # Create linked list of info of current peers
# currentPeers = deque()

# # Create linked list of rfc indexes
# rfcIndex = deque()




def colored_text(text, color, bold=False):
    # Define a dictionary of color codes
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
    # Look up the color code for the specified color
    color_code = color_codes.get(color.lower(), 37)  # Default to white if the color is not found
    # Set the bold code to 1 if bold is True, otherwise set it to an empty string
    bold_code = "1;" if bold else ""
    # Print the text with the color code and bold code
    print(f"\033[{bold_code}{color_code}m{text}\033[0m")

def separator() :
    colored_text("-" * 80, "magenta")


def parse_message(message):
    print(message)
    # Split the message by line breaks (<cr><lf>)    
    lines = message.split("\r\n")
    parts = lines[0].split(" ")
    method = parts[0]
    version = parts[-1]

    if method == "LIST":
        rfc_number = None
    else:
        rfc_number = parts[2]


    # Parse the headers into key-value pairs    
    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        header_field_name, value = line.split(" ", 1)
        headers[header_field_name] = value

    # Extract the title from the headers, if present
    title = headers.get("Title:", None)

    return {
        "method": method,
        "rfc_number": rfc_number,
        "title": title,
        "version": version,
        "headers": headers,
    }



def add(connection_socket, headers, client_hostname, rfc, rfcIndex):

    required_headers = {"Host:", "Port:", "Title:"}
    print(headers.keys())
    if not required_headers.issubset(headers.keys()):
        error_message = f"Missing required header fields"
        connection_socket.send(error_message.encode())
        return 400  # Bad Request

    rfc_entry = {
        "rfc_number": rfc,
        "title": headers["Title:"],
        "hostname": client_hostname,
        "port": headers["Port:"],
    }

    rfcIndex.append(rfc_entry)
    print(f"Added RFC {rfc} with title '{headers['Title:']}' from {client_hostname}:{headers['Port:']}")

    success_message = f"RFC {rfc} added successfully"
    connection_socket.send(success_message.encode())
    return 200  # OK

def list_items(connection_socket, headers, client_hostname, rfc, rfcIndex):
    required_headers = {"Host:", "Port:"}

    if not required_headers.issubset(headers.keys()):
        error_message = f"Missing required header fields"
        connection_socket.send(error_message.encode())
        return 400  # Bad Request

    # Iterate through the rfcIndex and build a string of rfc entry information
    response_lines = [
        f"RFC {entry['rfc_number']} {entry['title']} {entry['hostname']} {entry['port']}"
        # Use List comprehension to build list       
        for entry in rfcIndex
    ]

    version = "P2P-CI/1.0"
    status_code = 200
    phrase = "OK"

    # Create the first line of the response with the version, status code, and phrase
    first_line = f"{version} {status_code} {phrase}"

    # Combine the first line and the rest of the response lines, separated by <cr> <lf>
    response = first_line + "\r\n" + "\r\n".join(response_lines) + "\r\n"

    connection_socket.send(response.encode())
    return status_code

def lookup(connection_socket, headers, client_hostname, rfc, rfcIndex):
    required_headers = {"Host:", "Port:", "Title:"}

    if not required_headers.issubset(headers.keys()):
        error_message = f"Missing required header fields"
        connection_socket.send(error_message.encode())
        return 400  # Bad Request

    # Filter the rfcIndex entries matching the given rfc number and title
    matching_entries = [
        entry for entry in rfcIndex if entry["rfc_number"] == rfc and entry["title"] == headers["Title:"]
    ]

    if not matching_entries:
        status_code = 404
        phrase = "Not Found"
    else:
        status_code = 200
        phrase = "OK"

    version = "P2P-CI/1.0"

    # Create the first line of the response with the version, status code, and phrase
    first_line = f"{version} {status_code} {phrase}"

    # Generate the response lines for matching entries
    response_lines = [
        f"RFC {entry['rfc_number']} {entry['title']} {entry['hostname']} {entry['port']}"
        for entry in matching_entries
    ]

    # Combine the first line and the rest of the response lines, separated by <cr> <lf>
    response = first_line + "\r\n" + "\r\n".join(response_lines) + "\r\n"

    connection_socket.send(response.encode())
    return status_code


# Client sent invalid method name
def invalid( connection_socket):
    error_message = f"Invalid method name"
    connection_socket.send(error_message.encode())


# Route the client to the appropriate message handler
def handle_method(connection_socket, method, headers, client_hostname, rfc, rfcIndex):
    methods_dict = {
        "ADD": add,
        "LIST": list_items,
        "LOOKUP": lookup
    }

    method_func = methods_dict.get(method, invalid)
    return method_func(connection_socket, headers, client_hostname, rfc, rfcIndex)

def remove_peer_records(client_hostname, port, rfcIndex, currentPeers, rec_ip, rec_port):

    
    # Remove all records associated with the peer from rfcIndex
    colored_text(f"Removing {client_hostname} from port {port} indexes", "yellow", True)
    print(rfcIndex)
    print(rec_ip, rec_port)
    rfcIndex[:] = [entry for entry in rfcIndex if not (entry["hostname"] == str(rec_ip) and int(entry["port"]) == int(rec_port))]

    # Remove the peer from currentPeers
    currentPeers[:] = [(hostname, peer_port) for hostname, peer_port in currentPeers if not (hostname == client_hostname and peer_port == port)]    

    print(currentPeers, rfcIndex)

def handleClient(connection_socket, addr, rfcIndex, currentPeers) :
    print(f"Client at ip address: {addr[0]} and port number {addr[1]} has connected")
    
    # Attempt to get a clients hostname
    client_ip = addr[0]
    try:
        client_hostname = gethostbyaddr(client_ip)[0]
        print(f"Client hostname: {client_hostname}")
    except herror:
        print(f"Unable to resolve hostname for IP address: {client_ip}")

    # Add clients hostname and IP to current peers linked list
    currentPeers.append((client_hostname, addr[1]))

    # Send a welcome message to the client
    welcome_message = "Welcome to the Centralized Index, please enter a command:"
    # Encode the string to bytes so it can be sent over the network
    connection_socket.send(welcome_message.encode())

    # Wait for the reply, when received decode the bytes into a string and strip any whitespace
    command = connection_socket.recv(1024).decode().strip()
    # While the client has not entered the CLOSE command
    while command.split(" ")[0] != "CLOSE":

        # Use the parse_message function to return the message's method, rfc, version and headers        parsed_message = parse_message(command)
        parsed_message = parse_message(command)
        method = parsed_message["method"]
        rfc = parsed_message["rfc_number"]
        version = parsed_message["version"]
        headers = parsed_message["headers"]
        

        # Call the handle_method function on these parameters to choose which method gets serviced
        handle_method(connection_socket, method, headers, client_hostname, rfc, rfcIndex)

        # Wait for the next command
        command = connection_socket.recv(1024).decode().strip()



        
    # Remove records associated with the disconnected peer
    remove_peer_records(client_hostname, addr[1], rfcIndex, currentPeers, command.split(" ")[1], command.split(" ")[2])  
     
    # Close socket
    connection_socket.close()

def main():
    
    manager = Manager()
    rfcIndex = manager.list()
    currentPeers = manager.list()

    # Create TCP Socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


    # Bind server to server port and accept connections from everywhere
    serverSocket.bind(('', SERVER_PORT))

    # Listen for incoming connections maximum of 5 at one time
    serverSocket.listen(max_connects)
    colored_text(f"Server is listening on port {SERVER_PORT} with a maximum of {max_connects} connections...", "green")

    try:
        while True:
            # Accept incoming connections and store the socket info in "connectionSocket" and the IP/port info in "addr"
            connection_socket, addr = serverSocket.accept()

            # Create a new Process that calls the handleClient function with args from accept()
            process = Process(target=handleClient, args=(connection_socket, addr, rfcIndex, currentPeers))
            process.start()
            connection_socket.close()


    except KeyboardInterrupt: 
        print("\nServer is shutting down...")
    
    except Exception as e:  # Catch any exception
        colored_text(f"An error occurred: {e}", "red")


    

    finally:
        # Close the server socket
        serverSocket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    main()





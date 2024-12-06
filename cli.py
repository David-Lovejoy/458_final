import socket
import sys
import os
import subprocess

def client_program():
    # Get server domain and port from command-line arguments
    server_domain = sys.argv[1]
    server_port = int(sys.argv[2])

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((server_domain, server_port))
        print(f"Connected to {server_domain}:{server_port}")
        
        while True:
            authentication =  input("username and password please: ")
            client_socket.send(authentication.encode())
            response = client_socket.recv(1024).decode()
            if response == "yes":
                print("youre logged in!")
                break
            else:
                print("wrong credentials, try again please")
        while True:
            # Display the prompt and get the user input
            command = input("sftp > ").strip()

            # Send the command to the server
            client_socket.send(command.encode())

            if command == "bye":
                # Close connection if "bye" command is issued
                print("Exiting SFTP session.")
                break
            elif command.startswith("get "):
                # Handle file download
                response = client_socket.recv(1024).decode()
                response = client_socket.recv(1024).decode()
                print("response: ", response)
                if True:
                    # Receive SCP file transfer details from the server
                    transfer_details = client_socket.recv(1024).decode()
                    print(f"File transfer details received: {transfer_details}")

                    # Parse server file path
                    server_host, file_path = transfer_details.split(":")
                    local_filename = os.path.basename(file_path)

                    # Execute SCP command
                    scp_command = f"scp {server_host}:{file_path} {local_filename}"
                    print(f"Executing: {scp_command}")
                    try:
                        subprocess.run(scp_command, shell=True, check=True)
                        print(f"The file '{local_filename}' has been successfully downloaded.")
                    except subprocess.CalledProcessError as scp_error:
                        print(f"Error during file transfer: {scp_error}")
                else:
                    print("The file does not exist.")
            else:
                # Handle other commands and print server response
                response = client_socket.recv(1024).decode()
                print(f"Server response: {response}")

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        # Close the client socket
        client_socket.close()
        print("Connection closed.")

if __name__ == '__main__':
    client_program()

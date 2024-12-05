import os
import socket
import sys
import subprocess
import hashlib

def server_program():
    host = socket.gethostname()
    port = int(sys.argv[1])  

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    print(f"Server listening on {host}:{port}")

    conn, address = server_socket.accept()
    print(f"Connection from {address}")

    current_directory = os.getcwd()  
    user_pass = {}

    user_pass["john"] = hashlib.md5("1234".encode()).hexdigest()
    user_pass["tim"] = hashlib.md5("5678".encode()).hexdigest()
    user_pass["bob"] = hashlib.md5("4321".encode()).hexdigest()
    while True:
        data = conn.recv(1024).decode()
        data = data.split(" ")
        print("data: ", data)
        print(data[0] in user_pass)
        print( hashlib.md5( data[1].encode()).hexdigest() )
        print( user_pass[data[0]] )
        if  data[0] in user_pass and hashlib.md5(data[1].encode()).hexdigest() == user_pass[data[0]]:
            conn.send("yes".encode())
            print("correct password")
            break
        else:
            conn.send("no".encode())
            print("wrong credentials, please try again")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            print(f"Received: {data}")
            command = data.strip()
            if command.startswith("get "):
                print("HANDLING FILE TRANSFER")
                _, filename = command.split(" ", 1)
                file_path = os.path.join(current_directory, filename)
                
                if os.path.isfile(file_path):
                    conn.send(b"1")  # Signal file exists
                    print(f"File {filename} is ready for transfer.")

                    conn.send(f"{host}:{file_path}".encode())
                else:
                    conn.send(b"NO FILE")  # File does not exist
            elif command == "bye":
                conn.send(b"Goodbye!")
                print("Client requested to end the connection.")
                break

            elif command.startswith("cd "):
                _, dir_name = command.split(" ", 1)
                if dir_name == "..":
                    if current_directory != "/":
                        current_directory = os.path.dirname(current_directory)
                        conn.send(f"Changed directory to {current_directory}\n".encode())
                    else:
                        conn.send(b"You have reached the root directory (/).\n")
                else:
                    new_dir = os.path.join(current_directory, dir_name)
                    if os.path.isdir(new_dir):
                        current_directory = new_dir
                        conn.send(f"Changed directory to {current_directory}\n".encode())
                    else:
                        conn.send(b"The directory does not exist.\n")

            elif command == "pwd":
                conn.send(f"{current_directory}\n".encode())

            else:
                try:
                    result = subprocess.check_output(
                        command, shell=True, cwd=current_directory, text=True, stderr=subprocess.STDOUT
                    )
                    conn.send(result.encode())
                except subprocess.CalledProcessError as e:
                    conn.send(f"Error executing command: {e.output}".encode())

        except Exception as e:
            conn.send(f"Error: {str(e)}".encode())
            break

    conn.close()
    print("Connection closed.")

if __name__ == '__main__':
    server_program()

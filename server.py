import socket
import sys
import threading
import csv

HOST = '127.0.0.1'
PORT = 7200

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = [] # list of dictionaries of each connected client {'username': name, 'client_socket': socket} , {} , ...
users = [] # list of connected usernames

def establish_connection():
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is running on {HOST}:{PORT}")

# remove a client from the online users lists
def remove_client(username):
    user_to_remove = None
    for user in clients:
        if user['username'] == username:
            user_to_remove = user

    clients.remove(user_to_remove)
    users.remove(username)

# broadcast a message to all online clients.
def broadcast(message):
    for client in clients:
        send_single_client_msg(client['client_socket'], message)

# send a single client a message
def send_single_client_msg(client, message):
    client.sendall(message.encode('utf-8'))

# attempt to send a private message to a certain username.
# returns boolean success indication.
def send_private_msg(username, message):
    for client in clients:
        if client['username'].lower() == username.lower():
            send_single_client_msg(client['client_socket'], message)
            return True
    return False

# find the username of a client using their client socket.
def get_username_by_client(client):
    for user in clients:
        if user['client_socket'] == client:
            return user['username']
        
# find a client's socket by their username
def get_client_by_username(username):
    for user in clients:
        if user['username'] == username:
            return user['client_socket']


def display_active_users(client):
    users_msg = f"\n** Users Online: ({len(users)}) **\n-------------------------------------------------------------------------------------\n{users}\n"
    users_msg += "-------------------------------------------------------------------------------------\n"
    send_single_client_msg(client, users_msg)


def register_user(username, password):
    with open('users.csv', 'r', newline='', encoding='utf-8') as user_file:
        users_csv = csv.reader(user_file) 
        for user in users_csv:
            if user[0].lower() == username.lower():
                return False # username already taken
    # username not taken, so append it to the users file
    with open('users.csv', 'a', newline='', encoding='utf-8') as user_file:
        csv_writer = csv.writer(user_file)  
        csv_writer.writerow([username, password])
        print(f"new user registered: '{username}'!")
        return True
    

def verify_login(username, password):
    with open('users.csv', 'r') as user_file:
        users_csv = csv.reader(user_file) 
        for user in users_csv:
            if user[0].lower() == username.lower() and user[1] == password:
                return True # username and password matched
    return False; # no user and password match.



def receive_new_client():
    while True:
        try:
            client, address = server_socket.accept()
            print(f"New connection with {str(address)}")
            login_verified = False

            while not login_verified:
                client_msg = client.recv(4096).decode('utf-8')
                
                if client_msg.lower() == 'login':
                    response = client.recv(4096).decode('utf-8').split()
                    username = response[0]
                    password = response[1]
                    if verify_login(username, password):
                        login_verified = True
                        send_single_client_msg(client, 'login_success')
                        users.append(username)
                        clients.append({'username': username, 'client_socket': client})
                        print(f"New client online! Username: '{username}'!")
                        # start a thread to handle the client's chatroom interactions
                        threading.Thread(target=handle_client, args=(client,)).start()
                        broadcast(f"* '{username}' joined the server! *")
                    else:
                        send_single_client_msg(client, "login_fail")


                elif client_msg.lower() == 'registration':
                    response = client.recv(4096).decode('utf-8').split()
                    username = response[0]
                    password = response[1]
                    if (register_user(username, password)):
                        send_single_client_msg(client, "registration_success")
                    else:
                        send_single_client_msg(client, "registration_fail")
                        
        except Exception as error:
            print("error while handling client login/registration:", error)



# handle client interactions
def handle_client(client):
    while True:
        try:
            message = client.recv(4096).decode('utf-8')
            parsed_msg = message.split()

            if message.lower() == 'list':
                display_active_users(client)
            elif message.lower() == 'logout':
                username = get_username_by_client(client)
                send_single_client_msg(client, "logout_success")
                remove_client(username)
                broadcast(f"* '{username}' left the chat! *")
                print(f"* '{username}' logged out! *")
                break

            elif parsed_msg[0].lower() == 'privmsg':
                # format the private message and attempt to send it.
                msg_portion = " ".join(f"{word}" for word in parsed_msg[2:])
                priv_msg = f"(private) {get_username_by_client(client)}: {msg_portion}"
                success = send_private_msg(parsed_msg[1], priv_msg)
                if not success:
                    send_single_client_msg(client, f"Sorry, user: '{parsed_msg[1]}' was not found. Type 'list' to view all online users.")
                    
            else:
                broadcast(message)

        except: # exception or disconnect, remove the client and close connection.
            username = get_username_by_client(client)
            remove_client(username)
            print(f"* '{username}' disconnected! *")
            broadcast(f"* '{username}' disconnected! *")
            break



# ------------------ MAIN --------------------
def main():
    establish_connection()
    receive_new_client()
    

if __name__ == "__main__":
    main()
import socket
import threading
import csv

HOST = '127.0.0.1'
PORT = 7200

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients_online = [] # list of dictionaries of each connected client {'username': name, 'client_socket': socket} , {} , ...
users = [] # list of connected usernames

# initial connection establishment
def establish_connection():
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is running on {HOST}:{PORT}")

# remove a client from the online users lists
def remove_client(username):
    user_to_remove = None
    for user in clients_online:
        if user['username'] == username:
            user_to_remove = user

    clients_online.remove(user_to_remove)
    users.remove(username)

# broadcast a message to all online clients, but not the client who sent the message.
def broadcast(this_client, message):
    for client in clients_online:
        if client['client_socket'] != this_client: # avoid sending to the client who sent this msg
            send_single_client_msg(client['client_socket'], message)

# send a single client a message
def send_single_client_msg(client, message):
    client.sendall(message.encode('utf-8'))

# attempt to send a private message to a certain username.
# returns boolean success indication.
def send_private_msg(username, message):
    for client in clients_online:
        if client['username'].lower() == username.lower():
            send_single_client_msg(client['client_socket'], message)
            return True
    return False

# find the username of a client using their client socket.
def get_username_by_client(client):
    for user in clients_online:
        if user['client_socket'] == client:
            return user['username']
        
# find a client's socket by their username
def get_client_by_username(username):
    for user in clients_online:
        if user['username'] == username:
            return user['client_socket']

# used to display all active online users to the client who requested. 
def display_active_users(client):
    users_msg = f"\n** Users Online: ({len(users)}) **\n-------------------------------------------------------------------------------------\n{users}\n"
    users_msg += "-------------------------------------------------------------------------------------\n"
    send_single_client_msg(client, users_msg)

# register a new user.
# checks for unique username and if unique, adds the username/password to 'users.csv'
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
        print(f"New user registered: '{username}'!")
        return True
    
# method to verify a login request with 'users.csv'. returns boolean success indication.
def verify_login(username, password):
    with open('users.csv', 'r') as user_file:
        users_csv = csv.reader(user_file) 
        for user in users_csv:
            if user[0].lower() == username.lower() and user[1] == password:
                return True # username and password matched
    return False; # no user and password match.

# check that a client is not already online. returns true if they are not online, false if they are. 
def verify_not_online(username):
    for client in clients_online:
        if client['username'].lower() == username.lower():
            return False
    return True

# method to receive a new client and handle login/registration logic.
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
                    if not verify_not_online(username): # check if the user is logged in already
                        send_single_client_msg(client, 'login_duplicate') # duplicate login detected
                    elif verify_login(username, password):
                        login_verified = True
                        send_single_client_msg(client, 'login_success')
                        users.append(username)
                        clients_online.append({'username': username, 'client_socket': client})
                        print(f"New client online! Username: '{username}'!")
                        # start a thread to handle the client's chatroom interactions
                        threading.Thread(target=handle_client, args=(client,)).start()
                        broadcast(client, f"* '{username}' joined the server! *")
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



# handle all client interactions for a client in the chatroom. 
# runs on a thread created by receive_new_client on successful login.
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
                broadcast(client, f"* '{username}' left the chat! *")
                print(f"* '{username}' logged out! *")
                break

            elif parsed_msg[0].lower() == 'privmsg':
                # format the private message and attempt to send it.
                msg_portion = " ".join(f"{word}" for word in parsed_msg[2:])
                priv_msg = f"(private) {get_username_by_client(client)}: {msg_portion}"
                success = send_private_msg(parsed_msg[1], priv_msg)
                if not success:
                    send_single_client_msg(client, f"Sorry, user: '{parsed_msg[1]}' was not found. Type 'list' to view all online users.")
                    
            else: # only other option is broadcast msg, so we send it. 
                broadcast(client, message)

        except: # exception or disconnect, remove the client and close connection.
            username = get_username_by_client(client)
            remove_client(username)
            print(f"* '{username}' disconnected! *")
            broadcast(client, f"* '{username}' disconnected! *")
            break



# ------------------ MAIN --------------------
def main():
    establish_connection()
    receive_new_client()
    
if __name__ == "__main__":
    main()
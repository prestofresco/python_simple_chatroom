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


def remove_client(client, username):
    user_to_remove = None
    for user in clients:
        if user['username'] == username:
            user_to_remove = user

    clients.remove(user_to_remove)
    users.remove(username)


def broadcast(message):
    for client in clients:
        send_single_client_msg(client['client_socket'], message)


def send_single_client_msg(client, message):
    client.sendall(message.encode('utf-8'))


def get_username_by_client(client):
    for user in clients:
        if user['client_socket'] == client:
            return user['username']
        

def get_client_by_username(username):
    for user in clients:
        if user['username'] == username:
            return user['client_socket']


def display_active_users(client):
    users_msg = f"\nUsers online: \n-------------------------------------------------------------------------------------\n{users}\n"
    all_users_msg = {'chat': users_msg}
    # send_single_client_json(client, all_users_msg)


def register_user(username, password):
    with open('users.csv', 'r') as user_file:
        users_csv = csv.reader(user_file) 
        for user in users_csv:
            if user[0].lower() == username.lower():
                return False # username already taken
    # username not taken, so append it to the users file
    with open('users.csv', 'a') as user_file:
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
                    send_single_client_msg(client, "login_success")
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

            # if (verify_username(client_msg['username'])):
            #     login_verified = True
            #     users.append(client_msg['username'])
            #     # send_single_client_json(client, {'success': ""})
            #     clients.append({'username': client_msg['username'], 'client_socket': client})
            #     print(f"New client connected! Username: {client_msg['username']}!")
            #     # start a thread to handle the client interactions
            #     threading.Thread(target=handle_client, args=(client,)).start()
            #     send_chat_all(f"* '{client_msg['username']}' joined the server! *")
            # else:
            #     send_single_client_json(client, {'fail': ""})



def verify_username(username):
    if not users: 
        return True
    else:
        if username in users:
            return False
        return True


# handle client interactions
def handle_client(client):
    while True:
        try:
            message = client.recv(4096).decode('utf-8')
            broadcast(message)

        except: # exception or disconnect, remove the client and close connection.
            username = get_username_by_client(client)
            remove_client(client, username)
            broadcast(f"* '{username}' disconnected! *")
            break



# ------------------ MAIN --------------------
def main():
    establish_connection()
    receive_new_client()
    


if __name__ == "__main__":
    main()
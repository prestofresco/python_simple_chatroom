import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 7200

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user = None
help_menu = "\n--------------------------------- HELP MENU ----------------------------------------\n"
help_menu += "* Use the following options: *\n"
help_menu += "'msg' <your message> to send a chat to all online users.\n"
help_menu += "'help' To display the help menu in chat.\n"
help_menu += "'list' To display all online users in chat.\n"
help_menu += "'logout' To logout and exit the chat room.\n"
help_menu += "'privmsg' <username> <message>' To send a direct message to another user.\n"
help_menu += "------------------------------------------------------------------------------------\n"

login_help_menu = "\n--------------------------------- LOGIN HELP ----------------------------------------\n"
login_help_menu += "Type 'registration' to register a new account.\n"
login_help_menu += "Type 'login' to login to your account.\n"
login_help_menu += "--------------------------------------------------------------------------------------\n"

# initial method to establish connection with the server
# handles user login and registration logic
def establish_connection():
    login_success = False
    client_socket.connect((HOST, PORT))

    while not login_success:
        print(login_help_menu)
        message = input("Enter option: ")

        if message.lower() == 'login':
            send_server_msg("login")
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            send_server_msg(f"{username} {password}")
            response = client_socket.recv(4096).decode('utf-8')
            if response == 'login_success': # successfull login
                login_success = True
                global user
                user = username
                print(f"** Login success! Welcome to the chatroom {user}!")
                print(help_menu)
            elif response == 'login_duplicate': # duplicate login
                print("\n** This user is already logged in to the chatroom. Type 'login' to try again.")
            else: 
                print("\n** Login fail. Username or password was incorrect. Type 'login' to try again.")
        
        elif message.lower() == 'registration':
            send_server_msg("registration")
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            send_server_msg(f"{username} {password}")
            response = client_socket.recv(4096).decode('utf-8')
            if response == 'registration_success':
                print("\n** Registration success!\nYou may now attempt to login now by typing 'login'")
            else: 
                print(f"\n** Registration failed. Username: {username} was already taken.")
        
        else:
            print("** Command not recognized. Please try again.")


# send a message to the server
def send_server_msg(msg):
    client_socket.sendall(msg.encode('utf-8'))

# receive method handled by a thread. handles receiving messages from the server.
def receive():
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')

            if message.lower() == 'logout_success':
                print("\n** You have successfully been logged out and disconnected. goodbye!!\n")
                client_socket.close()
                os._exit(1)
            else:
                print(message) # just a chat message

        except Exception as error:
            print("An error occurred!", error)
            client_socket.close()
            break

# write method handled by a thread. will accept and handle user messages.
def write():
    while True:
        try: 
            message = input("") # get chat message input
            parsed_msg = message.split()

            if parsed_msg[0].lower() == 'help':
                print(help_menu)
            elif parsed_msg[0].lower() == 'list':
                send_server_msg('list')
            elif parsed_msg[0].lower() == 'logout':
                send_server_msg('logout')
            elif parsed_msg[0].lower() == 'privmsg':
                if len(parsed_msg) < 3: # check if we have the correct argument structure
                    print("\n** Incorrect usage of 'privmsg'\nUsage: 'privmsg' <username> <message>'\n")
                else: # correct number of args
                    send_server_msg(message)
            elif parsed_msg[0].lower() == 'msg':
                msg_portion = " ".join(f"{word}" for word in parsed_msg[1:]) # remove 'msg' from string and join the rest of the message on spaces
                send_server_msg(f"{user}: {msg_portion}")

            else: # incorrect arguments
                print("** Usage not recognized. Type 'msg' <your message> to message all users, or 'help' for the help menu.")

        except Exception as error:
            print("Sorry, an error occurred! :( please try again or type 'help' for the help menu.")


# ------------------ MAIN --------------------
def main():
    establish_connection()
    threading.Thread(target=receive).start() # start the receive thread
    threading.Thread(target=write).start() # start the write thread

if __name__ == "__main__":
    main()
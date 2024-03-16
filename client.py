import socket
import sys
import threading

HOST = '127.0.0.1'
PORT = 7200

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None
help_menu = "\n--------------------------------- HELP MENU ----------------------------------------\n"
help_menu += "Type a message to chat with other players.\n"
help_menu += "If you would like to start a game with another player type: 'play' in chat.\n"
help_menu += "To display the help menu type: 'help' in chat.\n"
help_menu += "To display active users type: 'users' in chat.\n"
help_menu += "------------------------------------------------------------------------------------\n"

login_help_menu = "\n--------------------------------- LOGIN HELP ----------------------------------------\n"
login_help_menu += "Type 'registration' to register a new account.\n"
login_help_menu += "Type 'login' to login to your account.\n"
login_help_menu += "--------------------------------------------------------------------------------------\n"


def establish_connection():
    login_success = False
    client_socket.connect((HOST, PORT))

    while not login_success:
        print(login_help_menu)
        message = input("")

        if message.lower() == 'login':
            send_server_msg("login")
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            send_server_msg(f"{username} {password}")
            response = client_socket.recv(4096).decode('utf-8')
            if response == 'login_success':
                login_success = True
                print("** Login success! Welcome to the chatroom!\n")
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
            print("Command not recognized. Please try again.")



def send_server_msg(msg):
    client_socket.sendall(msg.encode('utf-8'))


def receive():
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8')
            print(message)

        except Exception as error:
            print("An error occurred!", error)
            client_socket.close()
            break


def write():
    while True:
        message = input("") # get chat message input

        if message.lower() == 'register':
            print('got register')
        elif message.lower() == 'login':
            print('got login')

        else: # just a chat message
            print('got chat')
            send_server_msg(message)


# ------------------ MAIN --------------------
def main():
    establish_connection()
    global write_thread, receive_thread
    receive_thread = threading.Thread(target=receive)
    write_thread = threading.Thread(target=write)
    receive_thread.start() # start the receive thread
    write_thread.start() # start the write thread


if __name__ == "__main__":
    main()
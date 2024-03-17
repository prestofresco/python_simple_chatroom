Begin by running the server 'python3 server.py'
The server will then wait for new connections and attempt to accept them.

Connect to the server by running the client 'python3 client.py'
The user is then greeted with a login/registration option menu.

On successful registration and login, the user enters the chatroom and is greeted by a help menu, which can be called any time by typing 'help'.
The user may enter a chat message to message all other online users, or use one of the commands outlined in the help menu.

-------------------------------------------------------------------------------------------------------------------------------------
Connection Commands:
'login' - to attempt to login to the chatroom. The user is prompted for their username and password.
'registration' - to register for a new account. The user is notified if the chosen username is already taken. 

Chatroom Commands / Usage:
Type a message in chat to send a message to all other active users.
'help' - prints the help menu.
'list' - displays the usernames of all online users.
'logout' - logs the user out of the chatroom and exits the application.
'privmsg' <username> <message>' - attempts to send a private message to the specified user. The sender is notified if the user is not online or doesn't exist.

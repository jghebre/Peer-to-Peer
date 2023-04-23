# 401_project
# Authors: Jonah Ghebremichael & Anaica Grouver

# Set Up

Ensure that you have Python 3.7 or later installed on your system. You can download the latest version of Python from the official website: https://www.python.org/downloads/

As both the peer and server are python scripts there is no compilation and therefore no necessary makefile. 
All python packages needed are part of Pythons standard library

Run the server with python server.py

Run the peer with python peer.py

# Guide

When you start up a server it will run without anymore needed commands. It will display the peers connected to it as they connnect and the messages it receives.

When you start up a peer you will see the following menu:

Welcome to the Peer-to-Peer Network!

Please enter a command:
1. Add an RFC
2. Print Current RFCs
3. Talk to the server
4. Close the connection

From here you can perform local operations like seeing which RFCs you have saved in memory locally or adding a rfc to your local list.

Choose 3 the "Talk to the server" option from the menu. The peer should now be connected to the server and the following message will display:

--------------------------------------------------------------------------------

Welcome to the Centralized Index, please enter a command

--------------------------------------------------------------------------------

Please choose a method to send to the server:
1. Add RFC to server
2. List server RFCs
3. Lookup specific RFC on server
4. Close the connection to server


You may also choose an operation to be performed locally:
5. Add an RFC locally
6. Print local Current RFCs
7. Get RFCs from Peers
8. Download local RFCs


The menu here is split into two sections, operations for the server and operations for the peer to perform

First lets add a RFC locally, meaning it will be saved in the local list, we press 5 and get this message:

Enter the RFC information:

Now we can enter RFC Number, Title and Data. I will enter 123 for each for demo purposes.

We get the message "Added RFC 123 with title '123' and data '123' to the local RFC list." and return to the main menu.

Select 6 to see RFCs saved to the local list. We get the output

Printing 1 RFCs stored in system
--------------------------------------------------------------------------------
RFC Number: 123
Title: 123
Data: 123

--------------------------------------------------------------------------------

Now lets add this to the server by selecting 1 from the main menu. We get asked the RFC number to add, we choose 123.

We see:

Sending: 
ADD RFC 123 P2P-CLI/1.0
Host: 127.0.0.1
Port: 56782
Title: 123

....
Server says: 
P2P-CLI/1.0 200 OK 
 RFC 123 added successfully

--------------------------------------------------------------------------------

On the servers console we see:

--------------------------------------------------------------------------------
Client hostname: localhost
ADD RFC 123 P2P-CLI/1.0
Host: 127.0.0.1
Port: 56782
Title: 123
--------------------------------------------------------------------------------
Added RFC 123 with title '123' from localhost:56782
--------------------------------------------------------------------------------

Lets make another peer on another terminal to see our added RFC.

Make another peer and select the option 3 again. Now select option 2 when at the Servers main menu, the following is outputted:

Sending: 
LIST ALL P2P-CLI/1.0
Host: 127.0.0.1
Port: 56827

....
Server says: 
P2P-CLI/1.0 200 OK
RFC 123 123 localhost 56782


--------------------------------------------------------------------------------


Now this has been added to the peer second list, client_rfcs which represents rfcs we can get from peers.

We can see this with selecting 7 from the main menu we get:

Printing 1 outside RFCs stored in system
--------------------------------------------------------------------------------
RFC Number: 123
Title: 123
Hostname: localhost
Port: 56782
--------------------------------------------------------------------------------
Enter the RFC number you wish to retreive or type CLOSE to exit:

We get a list of RFCs we can request from peers with 123 being the one we just saw from the server.

Enter 123 and we get: 
Retreiving RFC from localhost on port 56782 ......


P2P-CLI/1.0 200 OK
Date: Sun, 23 Apr 2023 16:02:01 GMT
OS: Darwin 21.6.0
Content-Length: 3
Content-Type: text/text

123

--------------------------------------------------------------------------------



Now if we selct 6 we can see that it is on our system.

We can select 8 to download this to our directory. By selecting 8 we see :

Here are the RFCs you have stored ready to download:
Printing 1 RFCs stored in system
--------------------------------------------------------------------------------
RFC Number: 123
Title: 123
Data: 
123
--------------------------------------------------------------------------------

we can enter 123 to download that file, after we get:

RFC 123 downloaded successfully

The RFC is saved to a text file under a folder named downloaded_tfcs as a .txt
The title is RFC_{rfc_number}_{rfc_title.txt} 


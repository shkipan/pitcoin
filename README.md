Pitcoin
=========
My implementation of bitcoin basic functionality using Python

Preinstall
==========
Before installing pitcoin itself, you should do some precautions to make it work.
1. Make sure you have UNIX-like system computer to work on
2. Have a stable Internet connection
3. Install Python, Pip, Make and Git on your computer

Installation
============
1. You should clone repository using `git clone https://xteams-gitlab.unit.ua/xteams/module-4-dskrypny.git` command
2. Make sure, that repo is cloned - there must be a folder named **module-4-dskrypny**
3. Enter project's folder and go to **pitcoin** directory (`cd module-4-dskrypny/pitcoin`)
4. Execute installer with command `source launch.sh` and wait until all packages will be installed
5. Now you may get access to *wallet_cli* and *miners_cli*

Getting started
===============
Before launching CLIs make sure you are in Python virtual environment. Type `virtenv` to check it. If you are in it, there will be a prefix `(pitcoinenv)` in command line. After that you may execute interfaces by typing `./wallet_cli` or `./miner_cli`

Wallet_cli
==========
Wallet's allows you to perform next actions:
- **new/import** - generate or import private key (imported in a WIF);
- **send** - get two parameters recipient and amount, afterwards build, sign and serialize
transaction;
 - **broadcast** - should send request with serialized transaction data to
web API of full node;
 - **balance** - return balance of address, transmitted in parameter.

Miner_cli
=========
Miner's interface allows you to perform next actions:
- **add_node** - adding node to nodes list of Blockchain (based on received
parameter in URL format without scheme);
- **mine** - start mining process;
- **consensus** - connect to other nodes and get full chain, compare it and
resolve conflicts by choosing more longer chain and replace current

Web API
=======
Web API has several routes, that provide next information:
- */transaction/new* - getting serialized transactiona
 nd push it to pending pool (which validate it and save, if validation is ok)
- */transaction/pendings* - return all pending transactions from you node in
JSON
- */chain* - return full chain from your storage (file or DB) in JSON
- */nodes* - return full list of nodes from Blockchain in JSON
 - */chain/length* - return length of full chain from this node

To access it open your browser and type in address bar *localhost:5000/**route***

There is a web interface, which allows you to work with node in browser. 
To start it execute new_api.py file in new terminal window while main node is running by typing *./new_api.py*. You must have pitcoin vvirtual enviroment activated to do it
After starting the browser access address *localhost:4242*. Now you are able to select from some options:
- *Address info* - gets information about bitcoin testnet address (inputs, outputs);
- *Block by index* - gets information about block by it's height (nonce, timestamp, transactions);
- *Blockchain* - if no parameter passed, displays whole blocks in blockchain in hidden form, 
pass an integer into input field to get info about N last blocks;
- *UTXO* - displays all unspent outputs n blockchain. Specify address to get it's unspnt outputs;
- *Balance* - get balance of pitcoin address;
- *Transaction* - get info about transation by it's hash.

For developers
=============
If you would like to create pull requests to develop this project and import another libraries to code, don't forget to save the info about them on file requierments.txt. There is a useful makefile command for it `make backup`
 



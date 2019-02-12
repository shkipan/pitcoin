chmod a+x api.py
chmod a+x wallet_cli.py
chmod a+x miner_cli.py
BDIR=$(pwd)
echo $BDIR
mkdir .pitcoin
cd .pitcoin
python3 -m venv pitcoinenv
source pitcoinenv/bin/activate
pip install -r $BDIR/requierments.txt
echo "alias virtenv='source .pitcoin/pitcoinenv/bin/activate'" >> ~/.bashrc
cd $BDIR
echo ''

if [ $(uname) = "Darwin" ]
then
	echo '\033[38;5;82mExecute \033[38;5;27mwallet_cli.py \033[38;5;82mor \033[38;5;27mminer_cli.py \033[38;5;82mto be able to work with pitcoin network\033[0m'
else
	echo 'Execute wallet_cli.py or miner_cli.py to be able to work with pitcoin network'
fi
./api.py

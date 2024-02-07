pkill -9 -f server.py
(git pull && git log -n 1 --oneline) >> logfile.log
python3.9 server.py >> logfile.log &
disown
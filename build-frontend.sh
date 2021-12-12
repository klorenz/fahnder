#docker run --rm -v $(pwd)/frontend:/frontend node sh -c 'cd /frontend ; npm install ; npm run build'

docker run --rm -v $(pwd)/frontend:/frontend node sh -c 'apt-get update -y ; apt-get install -y inotify-tools ; cd /frontend ; npm install ; while true ; do inotifywait -e modify,create,delete,move -r . && npm run build ; sleep 1 ; done'

# Fahnder

This is a meta search engine with a pure Rest API for the backend and a svelte 
frontend.  It supports engines behind authentication systems.

For the start there are user/password authentication and OAuth (via loginpass) 
supported.

It is a quite early stage of this project.

## Development (Howto)

  Copy `fahnder-config-sample.yml` to `fahnder.yml`.

Edit the configfile and define auths and engines.

If you have Ubuntu, you may have an outdated nodejs version, so install newest LTS version:

```bash
wget -q -O- https://deb.nodesource.com/setup_14.x | sudo bash
apt-get install -y nodejs
```

Then install frontend requirements

```bash
cd frontend
npm install

For working around https://github.com/hperrin/svelte-material-ui/issues/375, run
```bash
bash fix
```


You need three terminals:

- one for automatic frontend build on changing a file:
  ```bash
  cd frontend
  node run dev
  ```

- one for elasticsearch server:
  ```bash
  docker run -p 127.0.0.1:9200:9200 -p 127.0.0.1:9300:9300 -e "discovery.type=single-node" -e "ES_JAVA_OPTS=-Xms2g -Xmx2g" docker.elastic.co/elasticsearch/elasticsearch:7.15.2
  ```

- one for backend:
  ```bash
  python3 -m venv venv
  . venv/bin/activate
  pip install wheel
  pip install -r requirements.txt
  python fahnder.py
  ```

- build the theme with
  ```bash
  cd frontend ; npm run prepare
  ```

If you have an older nodejs, you can workaround that with using a docker container
for automatically building the frontend on file change.

This is not so comfortable in debugging frontend code:

```bash
docker run --rm -v $(pwd)/frontend:/frontend node sh -c '
  apt-get update -y ; apt-get install -y inotify-tools ;
  cd /frontend ; npm install ;
  while true ; do
    inotifywait -e modify,create,delete,move -r . && npm run build ;
    sleep 1 ;
  done'
```
## Configuration

You can do configurations in a local .env file.

## Connecting to Gitlab OAuth

Go to your user's preferences page and find "Applications".  There create a new application with redirect URL to Root of this application.  For development this is usually 
`http://localhost:3000`.

Then copy client ID and store it in:

```
GITLAB_CLIENT_ID=<client ID>
```

And copy client secret to store it in:

```
GITLAB_CLIENT_SECRET=<client Secret>
```


### Confluence Engines

In development mode, you may want to simply create an access token and use it for testing. You can configure it with setting:

```
CONFLUENCE_ACCESS_TOKEN=<your very long Confluence access token>
```

### Jira Engines

In development mode, you may want to simply create an access token and use it for testing. You can configure it with setting:

```
JIRA_ACCESS_TOKEN=<your very long Jira access token>
```



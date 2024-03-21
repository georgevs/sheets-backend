# Google Spreadsheets
[Google: overview](https://developers.google.com/sheets/api)  
[Google: reference](https://developers.google.com/sheets/api/reference/rest)  
[Google: discovery](https://sheets.googleapis.com/$discovery/rest?version=v4)  

[Google: read/write vlaues](https://developers.google.com/sheets/api/guides/values)  

[Google: quickstart](https://developers.google.com/sheets/api/quickstart/python)  
[Google: samples](https://developers.google.com/sheets/api/samples)  
[Google: export](https://developers.google.com/drive/api/guides/manage-downloads#python)  

[Stackoverflow: export](https://stackoverflow.com/questions/33713084/download-link-for-google-spreadsheets-csv-export-with-multiple-sheets/33727897#33727897)  

### Model
[Spreadsheet](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets)  
- speadsheetId, spreadsheetUrl  
- properties { title }  
- sheets[]  

[Sheet](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets)  
- properties { sheetId, title, index, gridProperties }
- properties.gridProperties { rowCount, columnCount, frozenRowCount, frozenColumnCount }

[Cell](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells)  

### Ranges
- A1 notation (common): 
  - Sheet1
  - Sheet1!A1:B2
  - Sheet1!A:B
  - Sheet1!1:10
  - 'My sheet'
  - 'My sheet'!A1:B2

- R1C1 notation:
  - Sheet1!R1C1:R2C2
  - Sheet1!R[1]C[1]


### Manage secrets
Push secrets:
```
tar czv secrets | openssl enc -aes-128-cbc -pbkdf2 -salt -out ~/ws-archive/secrets.hacct-script.tar.gz.enc
```
Fetch secrets:
```
openssl enc -d -aes-128-cbc -pbkdf2 -salt -in ~/ws-archive/secrets.hacct-script.tar.gz.enc | tar xzv
```
### Run docker container
```bash
sudo apt install docker.io docker-buildx

DOCKER_BUILDKIT=1 \
PASSWD=$(read -s -p 'Password:' PASSWD ; echo "$USER:$PASSWD") \
docker image build --no-cache --secret id=PASSWD --tag dev-python - << EOF
  FROM ubuntu
  RUN --mount=type=secret,id=PASSWD \
    apt-get update && apt-get install -y sudo ssh tmux vim curl python3 python3-pip && \
    useradd -m -s /bin/bash -G sudo $USER && \
    cat /run/secrets/PASSWD | chpasswd
    USER $USER
    ENV PATH "\$PATH:/home/$USER/.local/bin"
EOF

docker network create \
  -d bridge \
  --subnet 172.20.0.0/16 \
  --gateway 172.20.0.1 \
  bridge-dev

docker container run -it \
  --name dev-jupyter \
  --network bridge-dev \
  --ip 172.20.0.220 \
  --publish 8080:8080 \
  --volume "/home/$USER/ws/DEV:/home/$USER/ws/DEV" \
  --volume "/home/$USER/ws/NOTES/wiki:/home/$USER/ws/NOTES/wiki" \
  -d dev-python

docker container start -ia --detach-keys='ctrl-x' dev-jupyter
docker container exec -it dev-jupyter bash -c 'sudo service ssh start'
```

### Run sheets-py script
The client machine where authentication runs in the browser must PROXY `8080:172.20.0.220:8080` into the machine where Docker runs `172.20.0.220` container
```bash
pip3 install -r requirements.txt 
python3 app/download_hacct.py --bind-addr 172.20.0.220
python3 app/groom_hacct.py
python3 app/upload_hacct.py --bind-addr 172.20.0.220
```

### Stage a demo
```bash
python3 app/groom_hacct.py --config-path ./secrets/config.demo.json --spreadsheet-groomed-name HACC-demo
python3 app/upload_hacct.py --bind-addr 172.20.0.220 --config-path ./secrets/config.demo.json --spreadsheet-name HACC-demo

curl -s https://content-sheets.googleapis.com/v4/spreadsheets/1dFa-QpbnFzd7JaP-G5XLvYbsoZ0FcWv_I7u5S5XAbCc/values/BAL -H "Authorization: Bearer $TOKEN" -o ./data/confidential/BAL.json

curl -s https://content-sheets.googleapis.com/v4/spreadsheets/1dFa-QpbnFzd7JaP-G5XLvYbsoZ0FcWv_I7u5S5XAbCc/values/CATX -H "Authorization: Bearer $TOKEN" -o ./data/confidential/CATX.json
```

### Load authorization token
```bash
sudo apt install jq
export TOKEN=$(jq -r .token secrets/credentials.json)
```
### List spreadsheets
[jq: manual](https://jqlang.github.io/jq/manual/)  
```bash
curl -s https://www.googleapis.com/drive/v3/files?q=mimeType=\'application/vnd.google-apps.spreadsheet\' -H "Authorization: Bearer $TOKEN" | jq -r '.files[] | .id,.name'
```
### Export spreadsheet
[Google: supported output mime types](https://developers.google.com/drive/api/guides/ref-export-formats)  
```bash
curl -s https://www.googleapis.com/drive/v3/files/1EwmYvXtwV63K___xZmjMXg8O_msnlHU5KTHUSkGblNc/export?mimeType=application/x-vnd.oasis.opendocument.spreadsheet -H "Authorization: Bearer $TOKEN" > spreadsheet.ods

curl -s https://www.googleapis.com/drive/v3/files/1EwmYvXtwV63K___xZmjMXg8O_msnlHU5KTHUSkGblNc/export?mimeType=text/csv -H "Authorization: Bearer $TOKEN" | less
```

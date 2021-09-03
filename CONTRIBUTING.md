## Install

```bash
apt install python3 python3-venv python3-pip ffmpeg
python -m venv ./venv/
source ./venv/bin/activate 
pip install -r app/dev-requirements.txt
```

## Run python tests

```bash
pytest
```


## Run deploy tests

```bash
molecule test
```

For debug may use separate steps

```bash
molecule create
molecule converge
# Enter to instance for debugging
docker exec -it webmtogif_deploy_test bash
```
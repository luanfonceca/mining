# mining
Python mining script to grap data from Github and Slack, save in mongodb and shows a Radar chart using hightchart.

# Before install
- MongoDB
- Python

# Install
1. Download the code
2. `easy_install pip`
2. `pip install -r requirements.txt``

# Configure
1. `cp config.py.sample config.py`
2. Fill the `config.py`
1. Create the Slack json files based on (Follow their names and formats):
  - `channeler.json.sample`
  - `links-shared.json.sample`
  - `setuper.json.sample`
  - `talker.json.sample`

# Running
1. `python mining.py`
2. `python app.py`
3. Open in a browser: `http://127.0.0.1:5000/`

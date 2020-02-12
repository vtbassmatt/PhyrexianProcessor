# Phyrexian Processor

A quick project to help swim through piles of old cards.

## To use

```bash
# one-time
python3 -m venv .env
. .env/bin/activate.sh
python get_sets.py

# each time
. .env/bin/activate.sh
python create_session.py

# when you want to see what you have
. .env/bin/activate.sh
python process_all_sessions.py
python value_of_cards.py
```
import datetime
import yaml
import scrython
import webbrowser
import urllib
import colorama

GARBAGE_THRESHOLD = 1.0
SLEEVE_THRESHOLD = 10.0
NOW_WERE_TALKING_REAL_MONEY = 50.0

RED_TEXT = colorama.Fore.RED
GREEN_TEXT = colorama.Fore.GREEN
YELLOW_TEXT = colorama.Fore.YELLOW
BRIGHT_TEXT = colorama.Style.BRIGHT
BLUE_BACK = colorama.Back.BLUE
WOWZA_TEXT = YELLOW_TEXT + BLUE_BACK + BRIGHT_TEXT
RESET_ALL = colorama.Style.RESET_ALL

# options that can be mutated during runtime - use caution
WRITE_SESSION = True
SEARCH_APPEND = ''

with open('data/set_index.yaml') as f:
    sets = yaml.full_load(f)

previous_data = {}
try:
    with open('data/cards.yaml') as f:
        previous_data = yaml.full_load(f)
        print('Found aggregated previous session data')
except FileNotFoundError:
    print('No aggregated session data found')
    previous_data = {
        'keeps': {},
        'garbage': {},
    }


def main():
    colorama.init()
    session_name = input("What will we call this session? ")
    session_file = datetime.datetime.utcnow().strftime('sessions/SESSION-%Y-%m-%d_%H-%M-%S.yaml')

    session = {
        'keep': [],
        'garbage': [],
    }

    try:
        while True:
            print()
            request = input("Card? ")
            if request[0] == '.':
                process_command(request, session)
            else:
                process_card(request, session)
    except KeyboardInterrupt:
        print()
        print("Finished with the session.")
    finally:
        if WRITE_SESSION:
            print("Recording session.")
            save_session(session_name, session, session_file)
            print(f'Wrote to {session_file}')
        colorama.deinit()


def save_session(session_name, session_data, filename):
    with open(filename, 'w') as f:
        yaml.dump({
            'name': session_name,
            'keep': session_data['keep'],
            'garbage': session_data['garbage'],
        }, f)


def process_command(cmd, session):
    global WRITE_SESSION, SEARCH_APPEND

    if cmd == '.help':
        print('== HELP ==')
        print()
        print('Ctrl-C to finish the session')
        print('.backup  - take a snapshot of the session as a backup')
        print('.nowrite - turn off writing the session [DANGER!]')
        print('.write   - turn session writes back on')
        print('.search  - append something to every search')

    elif cmd == '.backup':
        print('Backing up session')
        backup_file = datetime.datetime.utcnow().strftime('sessions/BACKUP-%Y-%m-%d_%H-%M-%S.yaml')
        save_session('User requested backup', session, backup_file)

    elif cmd == '.nowrite':
        print('Session WILL NOT be written. Hope you know what you\'re doing.')
        WRITE_SESSION = False

    elif cmd == '.write':
        print('Session will be written.')
        WRITE_SESSION = True

    elif cmd[0:7] == '.search':
        SEARCH_APPEND = cmd[8:]
        print(f'Searches will have "{SEARCH_APPEND}" appended.')

    else:
        print('Unknown command.')


def process_card(card, session):
    search_terms = f"{card} -is:digital {SEARCH_APPEND}"
    print(f"Searching: '{search_terms}'")

    # first get the card data from Scryfall
    try:
        search = scrython.cards.Search(q=search_terms, unique="prints")
    except Exception as e:
        # sigh. scrython throws Exception even for handled errors
        print(f"== exception =={RED_TEXT}")
        print(e)
        print(f"{RESET_ALL}===============")
        return
    data = search.data()

    # make sure we're dealing with exactly one card
    if len(data) < 1:
        print(f"{RED_TEXT}No results.{RESET_ALL}")
        return

    if len(data) > 1:
        unique_names = set([x['name'] for x in data])
        if len(unique_names) > 1:
            print("Multiple cards found:")
            for name in unique_names:
                print(f"  {name}")
            return

    card_name = data[0]['name']
    print(f"Found: {card_name}")
    print()

    # if at least one printing exceeds the garbage threshold, determine set
    printings = { x['set']: float_safe(x['prices']['usd']) for x in data}
    if any([val and val > GARBAGE_THRESHOLD for key, val in printings.items()]):
        print(f'At least one printing exceeds ${GARBAGE_THRESHOLD}')
        which_set = determine_set(card_name, printings, data)

        if which_set in previous_data['keeps']:
            if card_name in previous_data['keeps'][which_set]:
                print(f'You noted {previous_data["keeps"][which_set][card_name]["qty"]} of these in a previous session.')

        # if the exact card meets one of the thresholds, note that
        card_value = printings[which_set]
        print(f"Card value: {GREEN_TEXT}${card_value}{RESET_ALL}")
        if card_value >= NOW_WERE_TALKING_REAL_MONEY:
            print(f"{WOWZA_TEXT}!! NOW WE'RE TALKING REAL MONEY, it's over ${NOW_WERE_TALKING_REAL_MONEY}{RESET_ALL}")
        elif card_value >= SLEEVE_THRESHOLD:
            print(f"{YELLOW_TEXT}{BRIGHT_TEXT}!! Sleeve that up, it's over ${SLEEVE_THRESHOLD}{RESET_ALL}")
        elif card_value >= GARBAGE_THRESHOLD:
            print(f"{YELLOW_TEXT}Worth selling, that's over ${GARBAGE_THRESHOLD}{RESET_ALL}")
        else:
            print(f"Garbage, skipping it")

        if card_value >= GARBAGE_THRESHOLD:
            quantity = 0
            while quantity <= 0:
                quantity_in = input("How many of that printing do you have? ")
                try:
                    quantity = int(quantity_in)
                except ValueError:
                    print("Expected an integer")
            if quantity > 0:
                session['keep'].append({
                    'card': card_name,
                    'set': which_set,
                    'value_per_card': card_value,
                    'quantity': quantity,
                })
                print("Added to keeps.")
        else:
            session['garbage'].append({
                'card': card_name,
                'set': which_set,
                'value_per_card': card_value,
            })
            print("Added to garbage.")
    else:
        print(f"No edition of the card exceeds ${GARBAGE_THRESHOLD}")
        for set_, value in printings.items():
            session['garbage'].append({
                'card': card_name,
                'set': set_,
                'value_per_card': value,
            })
        print("Added all printings to garbage.")


def determine_set(card_name, printings, full_data):
    if len(printings) == 1:
        set_ = None
        for key in printings:
            set_ = key
        long_set_name = sets.get(set_, {'name': '??'})['name']
        print(f"There's only one printing: {set_} ({long_set_name})")
        return set_

    for set_, value in printings.items():
        long_set_name = sets.get(set_, {'name': '??'})['name']
        print(f"{YELLOW_TEXT}{set_}{RESET_ALL}: ${value}  ({long_set_name})")

    print("If you don't know which set, enter '?' to launch a browser search.")
    which_set = ''
    while which_set not in printings.keys():
        which_set = input("Which set? ")
        if which_set == '?':
            query_params = {
                'as': 'grid',
                'order': 'released',
                'unique': 'prints',
                'q': f'!"{card_name}"'
            }
            webbrowser.open(f'https://scryfall.com/search?{urllib.parse.urlencode(query_params)}')
    return which_set


def float_safe(maybe_float):
    if maybe_float is None:
        return 0.0
    else:
        return float(maybe_float)


if __name__ == "__main__":
    main()

import glob
import yaml

def process_sessions(verbose=True):
    keeps = {}
    garbage = {}

    for filename in glob.iglob('sessions/SESSION-*.yaml'):
        if verbose:
            print(filename)
        with open(filename) as f:
            session_data = yaml.full_load(f)

        for card in session_data['keep']:
            set_ = card['set']
            name = card['card']
            value = card['value_per_card']
            qty = card['quantity']

            if set_ not in keeps:
                keeps[set_] = {}

            if name not in keeps[set_]:
                keeps[set_][name] = {}

            if 'value' not in keeps[set_][name]:
                keeps[set_][name]['value'] = value

            if 'qty' in keeps[set_][name]:
                keeps[set_][name]['qty'] += qty
            else:
                keeps[set_][name]['qty'] = qty

        for card in session_data['garbage']:
            set_ = card['set']
            name = card['card']

            if set_ not in garbage:
                garbage[set_] = []

            if name not in garbage[set_]:
                garbage[set_].append(name)

    if verbose:
        print('Dumping to data/cards.yaml')
    with open('data/cards.yaml', 'w') as f:
        yaml.dump({
            'keeps': keeps,
            'garbage': garbage,
        }, f)

if __name__ == '__main__':
    process_sessions()

import yaml

def get_values():
    with open('data/set_index.yaml', 'r') as f:
        set_names = yaml.full_load(f)

    with open('data/cards.yaml', 'r') as f:
        cards = yaml.full_load(f)

    total = 0.0
    for set_name, cards in cards['keeps'].items():
        print(f'-- {set_names[set_name]["name"]} --')
        for name, data in cards.items():
            value = data["qty"] * data["value"]
            total += value
            print(f'{name}: ${value} ({data["qty"]} x ${data["value"]})')
        print()

    print(f"Total: ${total}")

if __name__ == '__main__':
    get_values()

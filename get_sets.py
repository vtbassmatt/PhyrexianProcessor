"Run this once in a while to get any new sets."
import yaml
import scrython

sets = scrython.sets.Sets()
sets_out = {}

for set_ in sets.data():
    name = f"{set_['name']} [digital]" if set_['digital'] else set_['name']
    sets_out[set_['code']] = {
        'name': name,
        'icon': set_['icon_svg_uri'],
    }

with open('data/set_index.yaml', 'w') as f:
    yaml.dump(sets_out, f)

if sets.has_more():
    print("Warning! There are more sets, and we're not architected to deal with that!")

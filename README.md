# Phyrexian Processor

A quick project to help swim through piles of old cards.

**Note:** This was built for my specific, one-time [workflow](#workflow) digging through a huge pile of old cards.
It's not great code, not great UI, and probably won't see a lot of improvements (unless someone wants to gift me another large batch of old semi-valuable cards...)

## To use

```bash
# one-time
python3 -m venv .env
. .env/bin/activate
pip install -r requirements.txt
python get_sets.py

# each time
. .env/bin/activate
python create_session.py

# when you want to see what you have
. .env/bin/activate
python process_all_sessions.py
python value_of_cards.py
```

## Workflow

So how does this actually work?
The quick summary is: you start with an undifferentiated pile of cards, and using some Scryfall search, end up with between two and four piles differentiated by value.
(For my personal workflow, I ended up using only three piles - anything above $10 was all the same to me, but it was fun to see the occasional "now we're talking real money!" message.)

There are three thresholds defined in `create_session.py`:
- `GARBAGE_THRESHOLD` - $1
- `SLEEVE_THRESHOLD` - $10
- `NOW_WERE_TALKING_REAL_MONEY` - $50

When you enter a search, Phyrexian Processor will run a Scryfall search.
If there's more than one card, you'll have to get more specific.
(The Scryfall syntax for "definitely only get me one card" is documented [here](https://scryfall.com/docs/syntax#exact); it's: `!"cardname"`.)

Even within one card, there may be many printings.
If no printing exceeds `GARBAGE_THRESHOLD`, the app will tell you so, and you can set the card into the "garbage" pile.
Note that this doesn't mean it's completely useless or unsellable -- Card Kingdom and other card shops will often give you pennies or nickels for such cards, and it can add up if you start with a large enough pile!

If _any_ printing exceeds `GARBAGE_THRESHOLD`, the app will ask you to specify which printing you've got.
Then it will check that printing of that card against the three thresholds.
It'll let you know which pile to put it in (as I mentioned above, in my piles, I didn't actually distinguish between the $10-49.99 and $50+ piles).

Whenever you get tired or exhaust the pile, you can press `Ctrl-C` and your session will be saved.
You can run as many sessions as you want, divided however you want.
The card pile I started from was separated into binders, so my sessions were named things like `1" blue binder`.

Once you've done a bunch of independent sessions, run `process_all_sessions.py` to get an aggregated list.
This will de-dupe your cards across sessions.
You'll end up with a big semi-structured YAML file that you can put into Excel or run through post-processing of your choice in order to paste into a buylist, market to your friends, or whatever.

For giggles, you can then pass that through `value_of_cards.py` to see the total haul.

## Oddities

There are a few weird things that I never got around to cleaning up.
Documenting them here so they're less surprising.

- When no printing of a card meets `GARBAGE_THRESHOLD`, all printings of that card are added to the "junk" side of the list.
This is probably not actually what anyone wants; they should end up in a flat list with their value tracked the same as any other card.
- The tools are an odd mix of asking questions and making automated decisions for you.
This reflects how I was trying to get through 20K cards as quickly as possible, but you may want to alter that arrangement.
- There's no native way to sort the output.
It would be nice to have something that understands ~~CMC~~ mana value, color identity, or chronology of sets, and can re-arrange the aggregated output that way.

## Credits / legal stuff

This tool depends on [Scryfall](https://scryfall.com), for which I'm extremely grateful!
Based on my understanding of their [API limits](https://scryfall.com/docs/api#rate-limits-and-good-citizenship), this tool should be perfectly fine - you aren't going to type fast enough to exceed 10 searches/second!

Portions of Phyrexian Processor are unofficial Fan Content permitted under the Wizards of the Coast [Fan Content Policy](https://company.wizards.com/en/legal/fancontentpolicy).
Any literal and graphical information presented on this site about Magic: The Gathering, including card images, the mana symbols, and Oracle text, is copyright Wizards of the Coast, LLC, a subsidiary of Hasbro, Inc.
Phyrexian Processor is not produced by, endorsed by, supported by, or affiliated with Wizards of the Coast. 

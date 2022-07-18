FILES = __init__.py player.py

all:
	for file in $(FILES); do \
		../mch2022-tools/webusb_fat_push.py $$file /flash/apps/python/boogiebadge/$$file; \
	done

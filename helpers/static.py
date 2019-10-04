from collections import ChainMap

import yaml

with open('eve_static_data/invFlags.yaml') as flags_file:
    INV_FLAGS = {item['flagID']: item for item in yaml.full_load(flags_file)}


RIGS = range(92, 99+1)
HIGH_SLOTS = range(27, 34+1)
MEDIUM_SLOTS = range(19, 26+1)
LOW_SLOTS = range(11, 18+1)
IMPLANT = 89
BYPASS = 0

INVENTORY_POSITIONS = [
    *RIGS,
    *HIGH_SLOTS,
    *MEDIUM_SLOTS,
    *LOW_SLOTS,
    IMPLANT,
    BYPASS
]

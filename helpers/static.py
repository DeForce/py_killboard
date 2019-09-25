from collections import ChainMap

import yaml

with open('eve_static_data/invFlags.yaml') as flags_file:
    INV_FLAGS = {item['flagID']: item for item in yaml.full_load(flags_file)}

INVENTORY_POSITIONS = [
    *range(92, 99+1),  # Rigs
    *range(27, 34+1),  # High Slots
    *range(19, 26+1),  # Med Slots
    *range(11, 18+1),  # Low Slots
    0                # Everything Else
]


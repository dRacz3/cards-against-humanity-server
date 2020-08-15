# Note: just copy the content of this script tohe the manage.py shell terminal, it will populate the database

import json

with open('data.json', 'r') as file:
    data = json.load(file)

from cardstore.models import DeckMetaData, WhiteCard, BlackCard
for key in data['metadata'].keys():
    print("Using {key}")
    DeckMetaData.objects.create(id_name = key, **data['metadata'][key]).save()


for key in data['white']:
    WhiteCard.objects.create(**key).save()

for key in data['black']:
    BlackCard.objects.create(**key).save()

print("Finished!")
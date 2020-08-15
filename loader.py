import json
import requests

from cardstore.models import WhiteCard, BlackCard, DeckMetaData

with open('data.json', 'r') as file:
    data = json.load(file)



url = "http://localhost:8000"
def publish_white_card(data):
    full_url = f"{url}/api/whitecards/"
    print(f"Posting WHITE CARD to :{full_url}, -> {data}")
    r = requests.post(full_url, json=data)
    print(r.status_code)

def publish_black_card(data):
    full_url = f"{url}/api/blackcards/"
    print(f"Posting BLACK CARD to :{full_url}, -> {data}")
    r = requests.post(full_url, json=data)
    print(r.status_code)


for card in data['white'][0:50]:
    WhiteCard.objects.create(**card).save()


for card in data['black'][0:50]:
    BlackCard.objects.create(**card).save()
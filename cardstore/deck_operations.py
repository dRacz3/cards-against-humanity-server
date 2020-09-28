import random

from cardstore.models import WhiteCard, BlackCard


class DeckFactory:
    def __init__(self, *args, **kwargs):
        pass

    def get_white_cards(self, count: int):
        # TODO: select based on categories..
        items = WhiteCard.objects.all()
        random_cards = random.sample(list(items), count)
        return random_cards

    def get_black_cards(self, count: int):
        items = BlackCard.objects.all()
        random_cards = random.sample(list(items), count)
        return random_cards


def get_white_cards_from_deck(deck, count):
    available = list(deck.white_cards.all())
    user_cards = random.sample(available, count)
    [deck.white_cards.remove(card) for card in user_cards]
    deck.save()
    return user_cards
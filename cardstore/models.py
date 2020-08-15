from django.db import models


class BlackCard(models.Model):
    text = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    deck = models.CharField(max_length=200)
    pick = models.IntegerField()

    def __str__(self):
        return f"[{self.deck}] {self.text}"


class WhiteCard(models.Model):
    text = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    deck = models.CharField(max_length=200)

    def __str__(self):
        return f"[{self.deck}] {self.text}"


class DeckMetaData(models.Model):
    description = models.CharField(max_length=200)
    official = models.BooleanField()
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)

    def __str__(self):
        if self.official:
            return f"[Official] [{self.name}]"

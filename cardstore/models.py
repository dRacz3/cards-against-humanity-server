from django.db import models


class DeckMetaData(models.Model):
    id_name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    official = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id_name} - {self.name}"


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

from django.db import models


class BlackCard(models.Model):
    text = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    deck = models.CharField(max_length=200)

    def __str__(self):
        return f"[{self.deck}] {self.text}"


    def number_of_injectable_content(self):
        return str(self.text).count('_')

    number_of_injectable_content.short_description = 'Number of words required for it'

class WhiteCard(models.Model):
    text = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    deck = models.CharField(max_length=200)

    def __str__(self):
        return f"[{self.deck}] {self.text}"


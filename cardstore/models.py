from django.db import models


class BlackCard(models.Model):
    card_text = models.CharField(max_length=200)

    def __str__(self):
        return self.card_text

class WhiteCard(models.Model):
    card_text = models.CharField(max_length=200)

    def __str__(self):
        return self.card_text

    def number_of_injectable_content(self):
        return 0

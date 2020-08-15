from django.db import models


class BlackCard(models.Model):
    card_text = models.CharField(max_length=200)
    package = models.CharField(max_length=200)

    def __str__(self):
        return f"[{self.package}] {self.card_text}"


    def number_of_injectable_content(self):
        return str(self.card_text).count('_')

    number_of_injectable_content.short_description = 'Number of words required for it'

class WhiteCard(models.Model):
    card_text = models.CharField(max_length=200)
    package = models.CharField(max_length=200)

    def __str__(self):
        return f"[{self.package}] {self.card_text}"


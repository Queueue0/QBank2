from django.db import models

class Change(models.Model):
    date = models.DateField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return self.date.strftime('%d %B, %Y')
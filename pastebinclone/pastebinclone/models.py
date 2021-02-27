from django.db import models

class Paste(models.Model):
    content=models.TextField(null=False)
    shortlink=models.URLField(null=False)
    clicks=models.BigIntegerField(default=0)
    expiry=models.DateTimeField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def clicked(self):
        self.clicks+=1
        self.save()


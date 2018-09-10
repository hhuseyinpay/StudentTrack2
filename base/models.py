from django.db import models


# Create your models here.

class Course(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)  # django admin için

    def __str__(self):
        return str(self.name)

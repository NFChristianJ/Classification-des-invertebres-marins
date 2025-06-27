#invert_project/predictor/models.py

from django.db import models

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='uploads/')
    url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Image uploaded at {self.image.url if self.image else self.url}"
    
class MarineSpecies(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom commun")
    latin_name = models.CharField(max_length=100, verbose_name="Nom scientifique")
    image = models.ImageField(upload_to='species/', verbose_name="Image")
    description = models.TextField(verbose_name="Description")
    habitat = models.CharField(max_length=200, blank=True)
    size = models.CharField(max_length=50, blank=True)
    conservation_status = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Espèce marine"
        verbose_name_plural = "Espèces marines"
    
    def __str__(self):
        return f"{self.name} ({self.latin_name})"
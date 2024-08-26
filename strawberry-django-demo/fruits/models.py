from django.db import models
from django_choices_field import TextChoicesField


class FruitCategory(models.TextChoices):
    CITRUS = "citrus", "柑橘類"
    BERRY = "berry", "ベリー類"


class Fruit(models.Model):
    """おいしい果物"""

    name = models.CharField(max_length=20, help_text="果物の品種名")
    category = TextChoicesField(choices_enum=FruitCategory, help_text="果物の分類")
    color = models.ForeignKey(
        "Color",
        on_delete=models.CASCADE,
        related_name="fruits",
        blank=True,
        null=True,
        help_text="この種類の果物の色",
    )


class Color(models.Model):
    """おいしい果物の色合い"""

    name = models.CharField(
        max_length=20,
        help_text="色の名前",
    )

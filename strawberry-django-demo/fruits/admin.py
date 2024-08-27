from django.contrib import admin

from .models import Color, Fruit


class FruitAdmin(admin.ModelAdmin):
    pass


class ColorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Fruit, FruitAdmin)
admin.site.register(Color, ColorAdmin)

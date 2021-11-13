from django.contrib import admin

from . import models

# Register your models here.


admin.site.register(models.Recipe)
admin.site.register(models.Ingredient)
admin.site.register(models.Tag)
admin.site.register(models.RecipeIngredient)
admin.site.register(models.CartShopping)
admin.site.register(models.FavoriteRecipe)

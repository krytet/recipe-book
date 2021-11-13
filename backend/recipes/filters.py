from django_filters import rest_framework as filters
from django_filters.filters import CharFilter, ChoiceFilter

from recipes.models import CartShopping, FavoriteRecipe, Ingredient, Recipe


class RecipeFilter(filters.FilterSet):

    is_favorited = ChoiceFilter(method='get_is_favorited',
                                choices=((1, True), (0, False))
                                )
    is_in_shopping_cart = ChoiceFilter(method='get_in_cart',
                                       choices=((1, True), (0, False))
                                       )
    tags = CharFilter(field_name='tags__slug')


    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def get_in_cart(self, obj, name, value):
        user = self.request.user
        carts = CartShopping.objects.filter(person=user).all()
        if value == '1':
            recipe = Recipe.objects.filter(in_cart__in=carts)
            return recipe
        elif value == '0':
            recipe = Recipe.objects.exclude(in_cart__in=carts)
            return recipe

    def get_is_favorited(self, obj, name, value):
        user = self.request.user
        favorits = FavoriteRecipe.objects.filter(person=user).all()
        if value == '1':
            recipe = Recipe.objects.filter(favorite_recipe__in=favorits)
            return recipe
        elif value == '0':
            recipe = Recipe.objects.exclude(favorite_recipe__in=favorits)
            return recipe


class IngredientFilter(filters.FilterSet):
    name = CharFilter(method='get_name')


    class Meta:
        model = Ingredient
        fields = ['name']

    def get_name(self, obj, name, value):
        print(value)
        ingr = Ingredient.objects.filter(name__contains=value).all()
        return ingr

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

MASURE = (
    ('шт.', 'шт.'),
    ('звездочка', 'звездочка'),
    ('г', 'г'),
    ('пучок', 'пучок'),
    ('по вкусу', 'по вкусу'),
    ('мл', 'мл'),
    ('стакан', 'стакан'),
    ('кусок', 'кусок'),
    ('пакет', 'пакет'),
    ('долька', 'долька'),
    ('упаковка', 'упаковка'),
    ('щепотка', 'щепотка'),
    ('стручок', 'стручок'),
    ('зубчик', 'зубчик'),
    ('банка', 'банка'),
    ('стебель', 'стебель'),
    ('веточка', 'веточка'),
    ('кг', 'кг'),
    ('тушка', 'тушка'),
    ('лист', 'лист'),
    ('пласт', 'пласт'),
    ('горсть', 'горсть'),
    ('ч. л.', 'ч. л.'),
    ('капля', 'капля'),
    ('пачка', 'пачка'),
    ('л', 'л'),
    ('ст. л.', 'ст. л.'),
    ('пакетик', 'пакетик'),
    ('батон', 'батон'),
    ('бутылка', 'бутылка'),
)

HEX = (
    ('#000000', 'Черный'),
    ('#808080', 'Серый'),
    ('#c0c0c0', 'Серебряный'),
    ('#ffffff', 'Белый'),
    ('#ff00ff', 'Фуксия'),
    ('#800080', 'Пурпурный'),
    ('#ff0000', 'Красный'),
    ('#800000', 'Коричнево-малиновый'),
    ('#ffff00', 'Жёлтый'),
    ('#808000', 'Оливковый'),
    ('#00ff00', 'Лайм'),
    ('#008000', 'Зелёный'),
    ('#00ffff', 'Цвет морской волны'),
    ('#008080', 'Окраски птицы чирок'),
    ('#0000ff', 'Синий'),
    ('#000080', 'Форма морских офицеров'),
)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(choices=HEX, max_length=100)
    slug = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(choices=MASURE, max_length=100)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    # slug = models.CharField(max_length=20, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient'
                                         )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='images', null=True)

    def __str__(self):
        return f"{self.id} {self.name}"


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient'
                                   )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingedients'
                               )
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.recipe}: {self.ingredient} количеством {self.amount}"


class CartShopping(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='cart'
                               )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_cart'
                               )

    def __str__(self):
        return f"Cart: {self.person}"


class FavoriteRecipe(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='favorite_recipe'
                               )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorite_recipe'
                               )

    def __str__(self):
        return f"Favorite recipe: {self.person}"

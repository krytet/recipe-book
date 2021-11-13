import base64
import re
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import (CartShopping, FavoriteRecipe, Ingredient, Recipe,
                        RecipeIngredient, Tag)
from users.models import Subscription

User = get_user_model()


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label="Email", write_only=True)
    password = serializers.CharField(label="Password",
                                     style={'input_type': 'password'},
                                     trim_whitespace=False,
                                     write_only=True
                                     )
    token = serializers.CharField(label="Token", read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = get_object_or_404(User, email=email)
        if user.check_password(password):
            data['user'] = user
            return data
        else:
            msg = ('Unable to log in with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')


# Сериализатор для тегов
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


# Сериализатор для ингридиентов
class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


# Сериализатор для вспомогательной модели ингридиентов
class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
        )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


# Сериализатор для краткого вывода рецепта
class ShortShowReciprSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# copy with users (error (most likely due to a circular import))
class ShowUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed'
                  ]

    # Проверка на подписку
    def get_is_subscribed(self, obj):
        # контекст пераедаеться из высшего сериализатора
        user = self.context.get('request').user
        try:
            tmp = Subscription.objects.get(respondent=user.id,
                                           subscriptions=obj.id
                                           )
        except:
            return False
        return True


class ShowRecipeSerelizer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingedients'
                                             )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_in_cart'
    )
    author = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    # Получить информаци о авторе
    def get_author(self, obj):
        author = obj.author
        # передаем контекст
        serializer = ShowUserSerializer(author, context=self.context)
        return serializer.data

    # Находиться ли в изброном
    def get_favorited(self, obj):
        # контекст пераедаеться из высшего сериализатора
        user = self.context.get('request').user
        try:
            tmp = FavoriteRecipe.objects.get(person=user.id, recipe=obj.id)
        except:
            return False
        return True

    # Находиться ингридиенты рецепта в корзине
    def get_in_cart(self, obj):
        # контекст пераедаеться из высшего сериализатора
        user = self.context.get('request').user
        try:
            tmp = CartShopping.objects.get(person=user.id, recipe=obj.id)
        except:
            return False
        return True


# CRUD операции над рецептами
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingedients'
                                             )
    author = serializers.SerializerMethodField()
    image = serializers.CharField()

    class Meta:
        fields = '__all__'
        model = Recipe

    # Провека пароля на соотвествие валидации
    def validate_image(self, data):
        try:
            data_foto = base64.b64decode(data.split(',')[1])
            split_data = re.split(':|/|;', data)
            file_name = split_data[1] + '.' + split_data[2]
            return ContentFile(data_foto, file_name)
        except:
            errors = {'image' : 'This format is not supported or it null'}
            raise ValidationError(errors)

    # Создание рецепта
    def create(self, validated_data):
        # Извличение ингридиетов и тегов из данных
        ingredients = validated_data.pop('recipe_ingedients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        # Создание рецепта
        recipe = Recipe.objects.create(**validated_data)
        # Создание ингрединтов рецепта
        for ingredient in ingredients:
            dict_ingredient = dict(ingredient)['ingredient']
            currect_ingredient = Ingredient.objects.get(**dict_ingredient)
            RecipeIngredient.objects.create(ingredient=currect_ingredient,
                                            recipe=recipe,
                                            amount=dict(ingredient)['amount']
                                            )
        # Указане тегов в рецепте
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    # Обновление рецепта
    def update(self, recipe, validated_data):
        # Извличение ингридиетов и тегов из данных
        ingredients = validated_data.pop('recipe_ingedients')
        tags = validated_data.pop('tags')
        # обновление данных
        Recipe.objects.filter(
            id=recipe.pk).update(**validated_data)
        recipe.tags.clear()
        recipe.ingredients.clear()
        # Создание ингрединтов рецепта
        for ingredient in ingredients:
            dict_ingredient = dict(ingredient)['ingredient']
            currect_ingredient = Ingredient.objects.get(**dict_ingredient)
            RecipeIngredient.objects.create(ingredient=currect_ingredient,
                                            recipe=recipe,
                                            amount=dict(ingredient)['amount']
                                            )
        # Указане тегов в рецепте
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    # Демонстрация рецепта
    def to_representation(self, data):
        """
        Object data -> Dict of primitive datatypes.
        """
        # передаем контекст для получения тикущего пользователя
        fields = ShowRecipeSerelizer(data, context=self.context)
        return OrderedDict(fields.data)
        # вариант на основе радительской функции
        '''
        ret = OrderedDict()
        for field in fields:
            attribute = field.get_attribute(data)
            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret
        '''

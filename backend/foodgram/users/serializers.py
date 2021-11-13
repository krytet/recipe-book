from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import Recipe
from recipes.serializers import ShortShowReciprSerializer

from .models import Subscription

User = get_user_model()


# Регистрация пользователя
class RegisterUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    email = serializers.EmailField(label='Email address', max_length=254,
                                   required=True
                                   )
    username = serializers.CharField(max_length=150, required=True,
                                     validators=[UnicodeUsernameValidator],
                                     )
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True,
                                     write_only=True
                                     )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'password'
                  ]

    # Проверка соотвествия пароля
    def validate_password(self, data):
        validate_password(password=data, user=User)
        return data

    # Создание аккауна пользователя
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ShowUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed',
                  ]

    # Вывод являеться ли вы подписчиком
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        try:
            tmp = Subscription.objects.get(
                respondent=user.id,
                subscriptions=obj.id
            )
        except:
            return False
        return True


class UserPasswordSerilazer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=150, required=True,
                                         write_only=True
                                         )
    current_password = serializers.CharField(max_length=150, required=True,
                                             write_only=True
                                             )

    class Meta:
        model = User
        fields = ['new_password', 'current_password']

    # Проверка пороля на совпадение
    def validate_current_password(self, data):
        user = self.context.get('request').user
        if user.check_password(data):
            return data
        else:
            raise serializers.ValidationError("Пароль не изменён, так как "
                                              "прежний пароль введён "
                                              "неправильно."
                                              )

    # Провека пароля на соотвествие валидации
    def validate_new_password(self, data):
        validate_password(password=data, user=User)
        return data

    # Создание нового пароля
    def create(self, validated_data):
        user = self.context.get('request').user
        user.set_password(validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',
                  )

    # Получение данных из адресной строки
    '''
    def give_kwargs(self, name):
        source = self.context.get('request').__dict__['parser_context']['kwargs'][name]
        return source

    # Просмотр всех данных в адресной строки
    def give_list_kwargs(self):
        return self.context.get('request').__dict__['parser_context']['kwargs']
    '''

    # Проверка являеться ли пользователь подписчиком
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        user_check = obj
        try:
            subscript = Subscription.objects.get(respondent=user,
                                                 subscriptions=user_check
                                                 )
        except:
            return False
        return True

    # Получить список рецептов
    def get_recipes(self, obj):
        user_check = obj
        max_recipe = self.context.get('request').GET.get('recipes_limit')
        if max_recipe is None:
            max_recipe = 5
        else:
            max_recipe = int(max_recipe)
        recipe = Recipe.objects.filter(author=user_check)[:max_recipe]
        serializer = ShortShowReciprSerializer(recipe, many=True)
        return serializer.data

    # Получение количества рецептов у пользователя
    def get_recipes_count(self, obj):
        user_check = obj
        recipe = Recipe.objects.filter(author=user_check).all().count()
        return recipe

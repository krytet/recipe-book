from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import mixins, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.filters import IngredientFilter, RecipeFilter

from . import models, serializers
from .pagination import StandardResultsSetPagination
from .permissions import IsAuthorOrAuthOrReadOnly

User = get_user_model()


class CustomObtainAuthToken(APIView):
    serializer_class = serializers.CustomAuthTokenSerializer

    # Получение токена пользователя
    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key})


class CustomDeleteAuthToken(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Удаление токена пользователя
    def post(self, request, *args, **kwargs):
        user = request.user
        token = Token.objects.get(user=user)
        token.delete()
        return Response(status=status.HTTP_201_CREATED)


# CRUD операций над рецептом
class RecipeView(ModelViewSet):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthorOrAuthOrReadOnly, )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    # Вывод список подписок
    @action(detail=False, methods=['get'], url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def favorite_list(self, request, *args, **kwargs):
        favorite = models.FavoriteRecipe.objects.filter(person=request.user.id).all()
        recipes = models.Recipe.objects.filter(favorite_recipe__in=favorite)
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializers.ShortShowReciprSerializer(recipes, many=True
                                                           # TODO ошибка
                                                           # *args, **kwargs
                                                           )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Добавить или удалить из списка изброноых
    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(models.Recipe, id=self.kwargs['pk'])
        if request.method == 'GET':
            favorite, status_ = models.FavoriteRecipe.objects.get_or_create(
                person=request.user,
                recipe=recipe,
            )
            if status_:
                serializer = serializers.ShortShowReciprSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            else:
                error = {
                    'errors': 'Данный рецеп уже добавлен в избраное'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                tmp = models.FavoriteRecipe.objects.get(
                    person=request.user,
                    recipe=recipe,
                )
                tmp.delete()
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

    # Скачать список покупок
    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def shoping_cart(self, request, *args, **kwargs):
        cart = models.CartShopping.objects.filter(person=request.user.id).all()
        recipe = models.Recipe.objects.filter(in_cart__in=cart).all()
        ingredients = models.RecipeIngredient.objects.filter(
            recipe__in=recipe).all()
        response = HttpResponse(content_type='txt/plain')
        response.write('------Список покупок от Foodgram------\n\n')
        for ingredient in ingredients:
            name_ingredient = ingredient.ingredient.name
            amount = ingredient.amount
            measurement_unit = ingredient.ingredient.measurement_unit
            text = f" {name_ingredient} - {amount} {measurement_unit}\n"
            response.write(text)
        response["Content-Disposition"] = ("attachment; "
                                           "filename=shopping_list.txt")
        return response

    # Добавление или удаление из списка покупок
    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(models.Recipe, id=self.kwargs['pk'])
        if request.method == 'GET':
            cart, status_ = models.CartShopping.objects.get_or_create(
                person=request.user,
                recipe=recipe,
            )
            if status_:
                serializer = serializers.ShortShowReciprSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            else:
                error = {
                    'errors': 'Данный рецепт уже добавлен в список покупок'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                tmp = models.CartShopping.objects.get(
                    person=request.user,
                    recipe=recipe,
                )
                tmp.delete()
            except:
                error = {
                    'errors': 'Данного рецепта нет в корзине'
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)


# Получение Тегов
class TagView(mixins.RetrieveModelMixin,
              mixins.ListModelMixin,
              GenericViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


# Получение ингридиентов
class IngerdientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter

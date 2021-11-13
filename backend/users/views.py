from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from recipes.pagination import StandardResultsSetPagination
from .models import Subscription

from . import serializers
from .permissions import CustomUserPermission

User = get_user_model()


class ShowUserView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.ShowUserSerializer
    permission_classes = (CustomUserPermission,)
    pagination_class = StandardResultsSetPagination
    lookup_field = 'pk'

    # Регистрация нового пользовтеля
    def create(self, request, *args, **kwargs):
        serializer = serializers.RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Получение профеля
    def retrieve(self, request, *args, **kwargs):
        # Получение своего профеля
        if self.kwargs['pk'] == 'me':
            user = request.user
        # Получения профеля пользователя с ID
        else:
            user = get_object_or_404(User, id=self.kwargs['pk'])
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Список подписок
    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        subscriptions = Subscription.objects.filter(respondent=self.request.user).all()
        queryset = User.objects.filter(subscribers__in=subscriptions).all()
        page = self.paginate_queryset(queryset)
        serializer = serializers.SubscriptionSerializer(page, many=True,
                                                        context={
                                                            'request': request
                                                        }
                                                        )
        return self.get_paginated_response(serializer.data)

    # Подписаться и отписаться
    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        if request.method == 'GET':
            current_user = request.user
            subscriptions = get_object_or_404(User, id=self.kwargs['pk'])
            if current_user == subscriptions:
                error = {"errors": 'Вы не можете подписаться на самого себя'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            subscription, status_c = Subscription.objects.get_or_create(
                respondent=current_user,
                subscriptions=subscriptions
            )
            if not status_c:
                error = {"errors": 'Вы уже подписаны на данного пользователя'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = serializers.SubscriptionSerializer(subscriptions,
                                                            context={
                                                                'request': request
                                                            }
                                                            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            current_user = request.user
            subscriptions = get_object_or_404(User, id=self.kwargs['pk'])
            try:
                subscription = Subscription.objects.get(
                    respondent=current_user,
                    subscriptions=subscriptions
                )
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # Смена пароля
    @action(detail=False, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializers.UserPasswordSerilazer(data=request.data,
                                                       *args, **kwargs
                                                       )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

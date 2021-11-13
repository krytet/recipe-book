from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersTest(TestCase):

    def setUp(self):
        self.client = Client()

        response = self.client.get('/api/users/')
        self.assertEqual(response.data['count'], 0,
                         msg='Список пользователей должен быть пуст')

        self.user1_data = {
            'email': 'Test111@TestsEmail.com',
            'username': 'TestUser1',
            'first_name': 'Test111',
            'last_name': 'Test1111',
            'password': 'TUserPass111'
        }
        response = self.client.post('/api/users/', self.user1_data)
        self.assertEqual(response.status_code, 201,
                         msg='Создание пользователя не удалось')

        # Получение токена
        self.token1 = self.client.post('/api/auth/token/login/',
                                       self.user1_data).data['auth_token']
        self.header1 = {
            'HTTP_AUTHORIZATION': f'Token {self.token1}',
        }
        response = self.client.get('/api/users/', **self.header1)
        self.assertEqual(response.data['count'], 1,
                         msg='Список пользователей должен быть быть равен 1 '
                         'так как один так как содали 1 пользователя'
                         )
        self.assertEqual(response.status_code, 200,
                         msg='Токен работает не коректно')

        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200,
                         msg='У анонимного пользователя должен быть доступ к'
                         ' списку пользователей'
                         )

        # Созание вторго пользователя
        self.user2_data = {
            'email': 'Test222@TestsEmail.com',
            'username': 'TestUser2',
            'first_name': 'Test222',
            'last_name': 'Test2222',
            'password': 'TUserPass222'
        }
        response = self.client.post('/api/users/', self.user2_data)
        self.assertEqual(response.status_code, 201,
                         msg='Должен создаться пользователя 2')

        self.token2 = self.client.post('/api/auth/token/login/',
                                       self.user2_data).data['auth_token']
        self.header2 = {
            'HTTP_AUTHORIZATION': f'Token {self.token2}',
        }
        response = self.client.get('/api/users/', **self.header2)
        self.assertEqual(response.data['count'], 2,
                         msg='Список пользователей должен быть быть равен 2 '
                         'так как один так как содали 1 пользователя'
                         )
        self.assertEqual(response.status_code, 200,
                         msg='Токен работает не коректно')

    '''
    def tearDown(self):
        user = User.objects.get(email=self.user1_data['email'])
        print(User.objects.get(email=self.user1_data['email']))
        user.delete()
        user = User.objects.get(email=self.user2_data['email'])
        print(User.objects.get(email=self.user2_data['email']))
        user.delete()
    '''

    # Вывод списка пользователей
    def test_users_list(self):
        response = self.client.get('/api/users/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='У Пользователя1 нет доступа к списку '
                         'пользователей'
                         )
        response = self.client.get('/api/users/', **self.header2)
        self.assertEqual(response.status_code, 200,
                         msg='У Пользователя2 нет доступа к списку '
                         'пользователей'
                         )
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200,
                         msg='У Анонимуса нет доступа к списку пользователей')
        # Проверка количества
        self.assertEqual(response.data['count'], 2,
                         msg='Список пользователей должен быть быть равен 2')

    # Вывод информации о пользователе
    def test_me_profile(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 401,
                         msg='У Анономуса не должно быть доступа на просмотр '
                         'своего профеля'
                         )

        ID = User.objects.get(email=self.user1_data['email']).id
        response = self.client.get(f'/api/users/{ID}/')
        self.assertEqual(response.status_code, 401,
                         msg='У Анономуса не должно быть доступа на '
                         'просмотр профелей'
                         )

        response = self.client.get('/api/users/me/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         'У пользователя должна быть возможность просматривать'
                         ' свой профиль'
                         )

        response = self.client.get('/api/users/me/', **self.header2)
        self.assertEqual(response.status_code, 200,
                         'У пользователя должна быть возможность просматривать'
                         ' свой профиль'
                         )

        response = self.client.get(f'/api/users/{ID}/', **self.header2)
        self.assertEqual(response.status_code, 200,
                         msg='У пользователя должна быть возможность '
                         'просматривать профили'
                         )

    # Смена пароля
    def test_password(self):
        password = {
            'current_password': self.user1_data['password'],
            'new_password': f"{self.user1_data['password']}11",
        }
        response = self.client.post('/api/users/set_password/', password,
                                    **self.header1
                                    )
        self.assertEqual(response.status_code, 201,
                         msg='Пороль не помянялся, хотя должен был')
        response = self.client.post('/api/users/set_password/', password)
        self.assertEqual(response.status_code, 401,
                         msg='У Анонимунса не должно быть прав к '
                         'изменению пароля'
                         )
        response = self.client.post('/api/users/set_password/', password,
                                    **self.header2
                                    )
        self.assertEqual(response.status_code, 400,
                         msg='Пароль не должен поменяться так как предыдущий '
                         'введене не верно'
                         )
        password = {
            'current_password': self.user2_data['password'],
            'new_password': f"{self.user2_data['password']}22",
        }
        response = self.client.post('/api/users/set_password/', password,
                                    **self.header2
                                    )
        self.assertEqual(response.status_code, 201,
                         msg='Пороль не помянялся, хотя должен был')
        response = self.client.post('/api/users/set_password/', password,
                                    **self.header2
                                    )
        self.assertEqual(response.status_code, 400,
                         msg='Пароль не должен поменяться так как предыдущий '
                         'введене не верно, так как поменяли его'
                         )

    # Подписки
    def test_subscription(self):
        # Вывод список пописок
        response = self.client.get('/api/users/subscriptions/', **self.header1)
        self.assertEqual(response.data['count'], 0,
                         msg='Список должен быть пуст')

        ID1 = User.objects.get(email=self.user1_data['email']).id
        ID2 = User.objects.get(email=self.user2_data['email']).id

        # Проверка профеля пользователя
        response = self.client.get(f'/api/users/{ID2}/', **self.header1)
        self.assertFalse(response.data['is_subscribed'],
                         msg='Должен быть не подписан на ползователя')

        # Подписаться на пользователя
        response = self.client.get(f'/api/users/{ID2}/subscribe/',
                                   **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Подписка дожны быть удачной')
        # Вывод список пописок
        response = self.client.get('/api/users/subscriptions/', **self.header1)
        self.assertEqual(response.data['count'], 1,
                         msg='Список должен быть с 1 пользователем')
        # Проверка профеля пользователя
        response = self.client.get(f'/api/users/{ID2}/', **self.header1)
        self.assertTrue(response.data['is_subscribed'],
                        msg='Должен быть подписан на ползователя')

        # Повторые попытки подписаться
        response = self.client.get(f'/api/users/{ID2}/subscribe/',
                                   **self.header1)
        self.assertEqual(response.data['errors'],
                         'Вы уже подписаны на данного пользователя')
        response = self.client.get(f'/api/users/{ID1}/subscribe/',
                                   **self.header1)
        self.assertEqual(response.status_code, 400,
                         msg='Дожна выйти ошибка, так как нельзя подписаться '
                         'на себя'
                         )
        self.assertEqual(response.data['errors'],
                         'Вы не можете подписаться на самого себя',
                         msg='Должны быть ошибка о невозможности подписаться '
                         'на себя'
                         )
        # Вывести список подписок
        response = self.client.get('/api/users/subscriptions/', **self.header1)
        self.assertEqual(response.data['count'], 1,
                         msg='Список должен быть с 1 пользователем')
        # Отписаться от пользователя
        response = self.client.delete(f'/api/users/{ID2}/subscribe/',
                                      **self.header1)
        self.assertEqual(response.status_code, 204,
                         msg='Отписка дожны быть удачной')

        # Вывести список подписок
        response = self.client.get('/api/users/subscriptions/', **self.header1)
        self.assertEqual(response.data['count'], 0,
                         msg='Список должен быть пустым')

        # Проверка профеля пользователя
        response = self.client.get(f'/api/users/{ID2}/', **self.header1)
        self.assertFalse(response.data['is_subscribed'],
                         msg='Должен быть не подписан на ползователя')

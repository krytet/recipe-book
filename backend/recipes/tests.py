from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from recipes.models import Ingredient, Tag

User = get_user_model()


class RecipeTest(TestCase):

    def setUp(self):
        self.client = Client()

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
                         msg='Создание пользователя 2 не удалось')

        self.token2 = self.client.post('/api/auth/token/login/',
                                       self.user2_data).data['auth_token']
        self.header2 = {
            'HTTP_AUTHORIZATION': f'Token {self.token2}',
        }

        # создание тегов
        Tag.objects.create(name='Tag1', slug='tag1', color='#c0c0c0')
        Tag.objects.create(name='Tag2', slug='tag2', color='#ff00ff')
        Tag.objects.create(name='Tag3', slug='tag3', color='#ffff00')

        # создание ингридиентов
        Ingredient.objects.create(name='Ингридиент №1', measurement_unit='г')
        Ingredient.objects.create(name='Ингридиент №2', measurement_unit='г')
        Ingredient.objects.create(name='Ингридиент №3', measurement_unit='г')
        Ingredient.objects.create(name='Ингридиент №4', measurement_unit='г')
        Ingredient.objects.create(name='Ингридиент №5', measurement_unit='г')
        Ingredient.objects.create(name='Ингридиент №6', measurement_unit='г')

    '''
    def tearDown(self):
        user = User.objects.get(email=self.user1_data['email'])
        print(User.objects.get(email=self.user1_data['email']))
        user.delete()
        user = User.objects.get(email=self.user2_data['email'])
        print(User.objects.get(email=self.user2_data['email']))
        user.delete()
    '''

    # Рецепты
    def test_recipe(self):
        # Вывести список рецептов
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, 200,
                         msg='Должен быть доступ к рецептам у Ананимуса')
        count = response.data['count']

        # Создать рецепт 1 пользователь 1
        recipe_data = {
            'tags': [1, 2],
            'name': 'Recipe 1',
            'text': 'Recipe 1',
            'cooking_time': 10,
            'ingredients': [
                {
                    'id': 1,
                    'amount': 10
                },
                {
                    'id': 2,
                    'amount': 20
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json'
                                    )
        self.assertEqual(response.status_code, 401,
                         msg='Должен быть отказ для Ананимуса')
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header1
                                    )
        self.assertEqual(response.status_code, 400,
                         msg='рецепт не должен создаться')
        recipe_data['image'] = ('data:image/png;base64,iVBORw0KGgoAAAANSUhE'
                                'UgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX'
                                '1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklE'
                                'QVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==')
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header1
                                    )
        count += 1
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно увеличиться')

        # Создать рецепт 2 пользователь 1
        recipe_data = {
            'tags': [2, 3],
            'name': 'Recipe 2',
            'text': 'Recipe 2',
            'cooking_time': 20,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 2,
                    'amount': 20
                },
                {
                    'id': 3,
                    'amount': 30
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header1
                                    )
        count += 1
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')
        response = self.client.get('/api/recipes/', **self.header1)
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно увеличиться')

        # Создать рецепт 3 пользователь 2
        recipe_data = {
            'tags': [1, 3],
            'name': 'Recipe 3',
            'text': 'Recipe 3',
            'cooking_time': 30,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 4,
                    'amount': 40
                },
                {
                    'id': 5,
                    'amount': 50
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header2
                                    )
        count += 1
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')
        # Проверить список рецептов
        response = self.client.get('/api/recipes/', **self.header2)
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно увеличиться')

        # Изменение рецепта
        recipe_data = {
            'tags': [3],
            'name': 'Recipe 1 Edited',
            'text': 'Recipe 1 Edited',
            'cooking_time': 200,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 6,
                    'amount': 915
                }
            ],
        }
        response = self.client.get('/api/recipes/', **self.header2)
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно совпадать')
        response = self.client.put('/api/recipes/1/', recipe_data,
                                   content_type='application/json',
                                   **self.header2
                                   )
        self.assertEqual(response.status_code, 403,
                         msg='Изменение рецептп не автором должно быть не '
                         'возможно')
        response = self.client.put('/api/recipes/1/', recipe_data,
                                   content_type='application/json',
                                   **self.header1
                                   )
        self.assertEqual(response.status_code, 200,
                         msg='Изменение рецептп автором должно быть возможно')
        response = self.client.get('/api/recipes/', **self.header2)
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно совпадать')

        # Проверка изменений
        self.assertEqual(response.data['results'][0]['id'], 1,
                         msg='Порядок вывода не должен измениться')
        self.assertEqual(len(response.data['results'][0]['ingredients']),
                         len(recipe_data['ingredients']),
                         msg='Количество ингридентов должно быть как при '
                         'изменении(должно измениться)')
        self.assertEqual(len(response.data['results'][0]['tags']),
                         len(recipe_data['tags']),
                         msg='Количество тегов должно быть как при '
                         'изменении(должно измениться)')
        self.assertEqual(response.data['results'][0]['name'],
                         recipe_data['name'],
                         msg='Название должно поеняться')
        self.assertEqual(response.data['results'][0]['text'],
                         recipe_data['text'],
                         msg='Описание должно поменяться')
        self.assertEqual(response.data['results'][0]['cooking_time'],
                         recipe_data['cooking_time'],
                         msg='Время приготовления должно поменяться')

        # Удаление рецепта
        response = self.client.delete('/api/recipes/1/', **self.header2)
        self.assertEqual(response.status_code, 403,
                         msg='Удаление не автором должно быть не возможно')
        response = self.client.get('/api/recipes/', **self.header2)
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно совпадать')
        response = self.client.delete('/api/recipes/1/', **self.header1)
        self.assertEqual(response.status_code, 204,
                         msg='Удаление автором должно быть возможно')
        count -= 1
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.data['count'], count,
                         msg='Количество рецептов должно меньше')

    # Теги
    def test_tags(self):
        # Посмотреть список тегов
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, 200,
                         msg='Теги должны отоброжаться')
        # Постотреть определенный тег
        response = self.client.get('/api/tags/1/')
        self.assertEqual(response.status_code, 200,
                         msg='Тег должен отоброжаться Анонимусу')
        response = self.client.get('/api/tags/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Тег должен отоброжаться Пользователю 1')
        response = self.client.get('/api/tags/', **self.header2)
        self.assertEqual(response.status_code, 200,
                         msg='Тег должен отоброжаться Пользователю 2')

    # Ингридиенты
    def test_ingredients(self):
        # Посмотреть список ингридиентов
        response = self.client.get('/api/ingredients/')
        self.assertEqual(response.status_code, 200,
                         msg='Ингридиенты должны отоброжаться')
        # Посмотреть определеный ингридиент
        response = self.client.get('/api/ingredients/1/')
        self.assertEqual(response.status_code, 200,
                         msg='Ингридиент должен отоброжаться Анонимусу')
        response = self.client.get('/api/ingredients/2/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Ингридиент должен отоброжаться Пользователю 1')
        response = self.client.get('/api/ingredients/3/', **self.header2)
        self.assertEqual(response.status_code, 200,
                         msg='Ингридиент должен отоброжаться Пользователю 2')

    # Избранные
    def test_favorite(self):
        # Создание рецептов
        # Создать рецепт 1 пользователь 1
        recipe_data = {
            'tags': [1, 2],
            'name': 'Recipe 1',
            'text': 'Recipe 1',
            'cooking_time': 10,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 1,
                    'amount': 10
                },
                {
                    'id': 2,
                    'amount': 20
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header1
                                    )
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')
        recipe_data = {
            'tags': [2, 3],
            'name': 'Recipe 2',
            'text': 'Recipe 2',
            'cooking_time': 20,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 2,
                    'amount': 20
                },
                {
                    'id': 3,
                    'amount': 30
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header2
                                    )
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')

        # Вывести список изброного
        response = self.client.get('/api/recipes/favorite/')
        self.assertEqual(response.status_code, 401,
                         msg='Не должно сывестись список избраных рецептов')

        # Вывести список рецептов и проверить отсуствие избранного в Р1
        response = self.client.get('/api/recipes/favorite/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Вывод список избраных рецептов')
        self.assertEqual(response.data, [], msg='Должен быть пустой список')

        # Добавить рецепт П1 Р1 в избраное
        response = self.client.get('/api/recipes/1/', **self.header1)
        self.assertFalse(response.data['is_favorited'],
                         msg='не должно быть в изброном')
        response = self.client.get('/api/recipes/1/favorite/', **self.header1)
        self.assertEqual(response.status_code, 201,
                         msg='Добовление в изброное должно пройти успешно')
        response = self.client.get('/api/recipes/1/favorite/', **self.header1)
        self.assertEqual(response.status_code, 400,
                         msg='Добовление в изброное не должно пройти успешно,'
                         ' так как он уже добавлен'
                         )

        # Вывести список изброного
        response = self.client.get('/api/recipes/favorite/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Вывод список избраных рецептов')
        self.assertEqual(len(response.data), 1,
                         msg='Не Должен быть пустой список')
        response = self.client.get('/api/recipes/1/', **self.header1)
        self.assertTrue(response.data['is_favorited'],
                        msg='Должно быть в изброном')

        #  Вывести список рецептов и проверить наличие изброного в Р3
        response = self.client.get('/api/recipes/2/favorite/', **self.header1)
        self.assertEqual(response.status_code, 201,
                         msg='Добовление в изброное должно пройти в изброное')

        # Вывести список изброного
        response = self.client.get('/api/recipes/favorite/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Вывод список избраных рецептов')
        self.assertEqual(len(response.data), 2,
                         msg='Должен быть пустой список')

        # Удалить изброное Р3
        response = self.client.delete('/api/recipes/2/favorite/',
                                      **self.header1)
        self.assertEqual(response.status_code, 204,
                         msg='Добовление в изброное должно пройти в изброное')

        # Вывести спиок рецептов и проверить наличие изброного
        response = self.client.get('/api/recipes/favorite/', **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Вывод список избраных рецептов'
                         )
        self.assertEqual(len(response.data), 1,
                         msg='Должен быть пустой список')

    # Список поккупок
    def test_cart_shoping(self):
        # Создание рецептов
        # Создать рецепт 1 пользователь 1
        recipe_data = {
            'tags': [1, 2],
            'name': 'Recipe 1',
            'text': 'Recipe 1',
            'cooking_time': 10,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 1,
                    'amount': 10
                },
                {
                    'id': 2,
                    'amount': 20
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header1
                                    )
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')
        # Создать рецепт 2 пользователь 2
        recipe_data = {
            'tags': [2, 3],
            'name': 'Recipe 2',
            'text': 'Recipe 2',
            'cooking_time': 20,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                     'ABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA'
                     '7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5Erk'
                     'Jggg==',
            'ingredients': [
                {
                    'id': 2,
                    'amount': 20
                },
                {
                    'id': 3,
                    'amount': 30
                }
            ],
        }
        response = self.client.post('/api/recipes/', recipe_data,
                                    content_type='application/json',
                                    **self.header2
                                    )
        self.assertEqual(response.status_code, 201,
                         msg='рецепт должен создаться')

        # Вывести список покупок
        response = self.client.get('/api/recipes/download_shopping_cart/')
        self.assertEqual(response.status_code, 401, msg='Анониму не должно '
                         'быть доступно')
        response = self.client.get('/api/recipes/download_shopping_cart/',
                                   **self.header1)
        self.assertEqual(response.status_code, 200,
                         msg='Пользователю дожен быть доступ к просмотру '
                         'корзины'
                         )

        # Проверить Р2 на отсутствие в корзине
        response = self.client.get('/api/recipes/2/', **self.header1)
        self.assertFalse(response.data['is_in_shopping_cart'],
                         msg='У пользователя не должно быть корзине рецепта')

        # Добавить Р2 в список покупок
        response = self.client.get('/api/recipes/2/shopping_cart/',
                                   **self.header1)
        self.assertEqual(response.status_code, 201, msg='Должна быть '
                         'возможность добавить рецепт в корзину')
        response = self.client.get('/api/recipes/2/shopping_cart/',
                                   **self.header1)
        self.assertEqual(response.status_code, 400,
                         msg='Должен быть отказ так как там уже есть это '
                         'рецепт'
                         )
        # Проверить Р2 на присудствие в списке покуупок
        response = self.client.get('/api/recipes/2/', **self.header1)
        self.assertTrue(response.data['is_in_shopping_cart'],
                        msg='У пользователя должен быть рецепт в корзине')

        # Получение списка названия ингридиентов
        ingredients = response.data['ingredients']
        list_ingredient = []
        for ingredient in ingredients:
            name = ingredient['name']
            amount = ingredient['amount']
            measurement = ingredient['measurement_unit']
            string = f" {name} - {amount} {measurement}"
            list_ingredient.append(string)

        # Проверка наличия ингридиентов в списке покупок
        response = self.client.get('/api/recipes/download_shopping_cart/',
                                   **self.header1)
        self.assertEqual(response.status_code, 200, msg='Пользователю дожен'
                         ' быть доступ к просмотру корзины')
        array = response.content.decode().split('\n')
        for ingred in list_ingredient:
            self.assertIn(ingred, array, msg='Дожны быть ингридиенты в списке'
                          ' покупок')

        # Удалить из списка покупок Р2
        response = self.client.delete('/api/recipes/2/shopping_cart/',
                                      **self.header1)
        self.assertEqual(response.status_code, 204, msg='Должна быть '
                         'возможность удалить рецепт из корзины')
        response = self.client.delete('/api/recipes/2/shopping_cart/',
                                      **self.header1)
        self.assertEqual(response.status_code, 400, msg='Должен быть отказ так'
                         ' как там рецепт уже убрали')

        # Проверить Р2 на отсутсвие нахождения в корзине
        response = self.client.get('/api/recipes/2/', **self.header1)
        self.assertFalse(response.data['is_in_shopping_cart'],
                         msg='У пользователя не должно быть в корзине рецепта'
                         )

        # Проверка отсудствия ингридиентов в списке покупок
        response = self.client.get('/api/recipes/download_shopping_cart/',
                                   **self.header1
                                   )
        self.assertEqual(response.status_code, 200, msg='Пользователю дожен'
                         ' быть доступ к просмотру корзины')
        array = response.content.decode().split('\n')
        for ingred in list_ingredient:
            self.assertNotIn(ingred, array, msg='Дожны быть ингридиенты в '
                             'списке покупок')

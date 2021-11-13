import csv
import os
import sys

import django

sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

def load_all_data(func):
    from recipes.models import Ingredient
    func('ingredients.csv', Ingredient)
    print('--------------------\nИнгридиенты загружены\n--------------')


@load_all_data
def load_table_from_csv(fname, model):
    from recipes.models import Ingredient
    file = open(fname, 'r', encoding='utf-8')
    reader = list(csv.reader(file, delimiter=','))
    n = 0
    for i in reader:
        Ingredient.objects.create(
            name=i[0],
            measurement_unit=i[1]
        )
        n += 1
        print(n, '|', i[0], '  -  ', i[1])



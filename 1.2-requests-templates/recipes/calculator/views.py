from django.shortcuts import render, HttpResponse

DATA = {
    'omlet': {
        'яйца, шт': 2,
        'молоко, л': 0.1,
        'соль, ч.л.': 0.5,
    },
    'pasta': {
        'макароны, кг': 0.3,
        'сыр, г': 0.05,
    },
    'buter': {
        'хлеб, ломтик': 1,
        'колбаса, ломтик': 1,
        'сыр, ломтик': 1,
        'помидор, ломтик': 1,
    },
    'borscht': {
        'свекла, шт': 2,
        'картофель, шт': 3,
        'капуста, г': 200,
        'морковь, шт': 1,
        'лук, шт': 1,
        'томатная паста, ст.л.': 2,
        'соль, ч.л.': 1,
        'перец, ч.л.': 0.5,
    },
    'pancakes': {
        'мука, г': 200,
        'молоко, мл': 300,
        'яйца, шт': 2,
        'сахар, ст.л.': 2,
        'соль, щепотка': 1,
        'масло растительное, ст.л.': 2,
    },
    'caesar_salad': {
        'куриное филе, г': 200,
        'салат айсберг, г': 100,
        'помидоры черри, шт': 6,
        'сухарики, г': 50,
        'сыр пармезан, г': 50,
        'соус цезарь, ст.л.': 2,
    },
}

def recipe(request, dish):
    """
    Обрабатывает запрос и возвращает список ингредиентов для блюда.

    Args:
        request (HttpRequest): Объект запроса.
        dish (str): Название блюда.

    Returns:
         HttpResponse: HTML-ответ со списком ингредиентов.
    """
    if dish not in DATA: 
        context = {}
        return HttpResponse(f"Рецепт для '{dish}' не найден")

    servings = request.GET.get('servings') 
    recipe_data = DATA.get(dish, {}) 

    if servings: 
      try: 
          servings = int(servings) 
      except ValueError: 
        return HttpResponse("Неверный формат параметра servings. Укажите целое число.")
      
      if servings <= 0: 
        return HttpResponse("Количество порций должно быть положительным числом.")

      context = { 
        'recipe': {
            ingredient: round(quantity * servings, 1) for ingredient, quantity in recipe_data.items()
          },
          'dish_name': dish 
      }

    else:
      context = {'recipe': recipe_data,
                 'dish_name': dish } 

    return render(request, 'calculator/index.html', context) 
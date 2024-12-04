"""
Доработать класс FlatIterator в коде ниже.
Должен получиться итератор, который принимает список списков и возвращает их плоское представление,
т. е. последовательность, состоящую из вложенных элементов.
Функция test в коде ниже также должна отработать без ошибок.
"""

class FlatIterator:
    def __init__(self, list_of_list):
        self.list_of_list = list_of_list
        self.current_list = 0
        self.current_element = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.current_list < len(self.list_of_list): # до тех пор пока есть списки для обработки
            if self.current_element < len(self.list_of_list[self.current_list]): # если есть элементы в текущем списке
                item = self.list_of_list[self.current_list][self.current_element]
                self.current_element += 1 # сдвигаемся к след. элементу
                return item
            self.current_list += 1 # переходим к следующему вложенному списку
            self.current_element = 0 # переходим в начало нового списка
        raise StopIteration # если элементы закончились, то стоп 

   

def test_1():

    list_of_lists_1 = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f', 'h', False],
        [1, 2, None]
    ]

    for flat_iterator_item, check_item in zip(
            FlatIterator(list_of_lists_1),
            ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]
    ):

        assert flat_iterator_item == check_item

    assert list(FlatIterator(list_of_lists_1)) == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]


if __name__ == '__main__':
    test_1()

"""
Доработать функцию flat_generator.
Должен получиться генератор, который принимает список списков и возвращает их плоское представление.
Функция test в коде ниже также должна отработать без ошибок.
"""

import types

def flat_generator(list_of_lists):
    for sublist in list_of_lists:  # Проходим по каждому вложенному списку
        yield from sublist  # Генерируем элементы из вложенного списка

def test_2():
    list_of_lists_1 = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f', 'h', False],
        [1, 2, None]
    ]

    for flat_iterator_item, check_item in zip(
            flat_generator(list_of_lists_1),
            ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]
    ):
        assert flat_iterator_item == check_item

    assert list(flat_generator(list_of_lists_1)) == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]

    assert isinstance(flat_generator(list_of_lists_1), types.GeneratorType)

if __name__ == '__main__':
    test_2()

"""
Применить написанный логгер к приложению из любого предыдущего д/з.
(Применяем logger к функции flat_generator, который обрабатывает списки с любым уровнем вложенности)
"""

from task_2 import logger


list_of_lists_2 = [
        [['a'], ['b', 'c']],
        ['d', 'e', [['f'], 'h'], False],
        [1, 2, None, [[[[['happy new year!']]]]], []]
    ]

@logger(path='flat_generator.log')
def flat_generator(list_of_list):
    for item in list_of_list:
        if isinstance(item, list):
            yield from flat_generator(item)
        else:
            yield item

for item in flat_generator(list_of_lists_2):
    pass












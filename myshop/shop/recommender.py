import redis
from django.conf import settings
from .models import Product

# соединение с redis
r = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)


class Recommender:
    def get_product_key(self, id):
        return f"product:{id}:purchased_with"

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # получаем другие продукты, купленные вместе с каждым товаром
                if product_id != with_id:
                    # увеличим балл за продукт, приобретенный вместе
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # только 1 product
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True
            )[:max_results]
        else:
            # генерируемвременный ключ
            flat_ids = "".join([str(id) for id in product_ids])
            tmp_key = f"tmp_{flat_ids}"
            # объяединим баллы нескольких продуктов
            # сохраняем полученный отсортированный набор во временном ключе
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # удалиv id для продуктов, для которых предназначена рекомендация
            r.zrem(tmp_key, *product_ids)
            # получаем id продуктов по их оценке, сортировка по потомкам
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # remove the temporary key
            r.delete(tmp_key)
            suggested_products_ids = [int(id) for id in suggestions]
            # получим предлагаемые продукты и сортируем по порядку появления
            suggested_products = list(
                Product.objects.filter(id__in=suggested_products_ids)
            )
            suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
            return suggested_products

    def clear_purchases(self):
        for id in Product.objects.values_list("id", flat=True):
            r.delete(self.get_product_key(id))

import redis
from django.conf import settings
from .models import Product

# Соединение с Redis с обработкой ошибок
try:
    r = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
    )
except redis.ConnectionError as e:
    raise Exception(f"Не удалось подключиться к Redis: {e}")


class Recommender:
    def get_product_key(self, id):
        if not isinstance(id, int):
            raise ValueError("ID должен быть целым числом")
        return f"product:{id}:purchased_with"

    def products_bought(self, products):
        if not products or not hasattr(products, "__iter__"):
            return
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=6):
        if not products or not hasattr(products, "__iter__"):
            return []
        product_ids = [p.id for p in products]
        if len(products) == 1:
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True
            )[:max_results]
            suggested_products_ids = []
            for id in suggestions:
                try:
                    suggested_products_ids.append(int(id))
                except ValueError:
                    continue
            suggested_products = list(
                Product.objects.filter(id__in=suggested_products_ids)
            )
            suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
            return suggested_products
        else:
            flat_ids = "".join([str(id) for id in product_ids])
            tmp_key = f"tmp_{flat_ids}"
            keys = [self.get_product_key(id) for id in product_ids]
            try:
                r.zunionstore(tmp_key, keys)
                r.zrem(tmp_key, *product_ids)
                suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            finally:
                r.delete(tmp_key)
            suggested_products_ids = []
            for id in suggestions:
                try:
                    suggested_products_ids.append(int(id))
                except ValueError:
                    continue
            suggested_products = list(
                Product.objects.filter(id__in=suggested_products_ids)
            )
            suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
            return suggested_products

    def clear_purchases(self):
        for id_tuple in Product.objects.values_list("id", flat=True).iterator():
            r.delete(self.get_product_key(id_tuple))

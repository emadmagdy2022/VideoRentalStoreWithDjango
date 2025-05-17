from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from api.models import Product
from django.core.cache import cache
from django.views.decorators.vary import vary_on_headers


@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate the product list cache when a product is created or updated.
    """
    cache.delete_pattern('*product_list*')
    print("Product cache invalidated.")

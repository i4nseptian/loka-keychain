from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = 'Products & Orders'
    
    # ✅ COMMENT DULU - UNTUK FIX CSRF ERROR
    # def ready(self):
    #     """
    #     Method ini dipanggil ketika app siap
    #     Kita import signals di sini agar ter-register
    #     """
    #     import products.signals
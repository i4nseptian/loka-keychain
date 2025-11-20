from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from datetime import datetime, timedelta

from .models import Category, Product, Order, OrderItem, LoginHistory


# ============================================================
# 🔹 DASHBOARD CUSTOM UNFOLD - SIMPLE & CLEAN
# ============================================================

def dashboard_callback(request, context):
    """Dashboard e-commerce lengkap dengan Order Analytics"""
    
    # === PRODUCT METRICS ===
    total_price = Product.objects.aggregate(total=Sum('price'))['total'] or 0
    try:
        total_price = float(total_price)
    except (TypeError, ValueError):
        total_price = 0

    total_products = Product.objects.count()
    total_images = Product.objects.exclude(image='').count()
    completeness = int((total_images / max(total_products, 1)) * 100)
    formatted_price = f"Rp {total_price:,.0f}".replace(",", ".")

    # === ORDER METRICS ===
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    paid_orders = Order.objects.filter(status='paid').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Total Revenue (dari order yang paid & completed)
    total_revenue = Order.objects.filter(
        Q(status='paid') | Q(status='completed')
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    formatted_revenue = f"Rp {total_revenue:,.0f}".replace(",", ".")
    
    # Revenue hari ini
    today = datetime.now().date()
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status__in=['paid', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    formatted_today_revenue = f"Rp {today_revenue:,.0f}".replace(",", ".")
    
    # Revenue bulan ini
    first_day_of_month = today.replace(day=1)
    month_revenue = Order.objects.filter(
        created_at__date__gte=first_day_of_month,
        status__in=['paid', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    formatted_month_revenue = f"Rp {month_revenue:,.0f}".replace(",", ".")
    
    # === LOGIN METRICS ===
    total_logins = LoginHistory.objects.count()
    today_logins = LoginHistory.objects.filter(login_time__date=today).count()
    active_sessions = LoginHistory.objects.filter(logout_time__isnull=True).count()

    context.update({
        "navigation": [
            {"title": "Dashboard", "link": "#", "active": True},
        ],
        
        # === KPI CARDS ===
        "kpis": [
            # PRODUCT KPIs
            {
                "title": "Total Kategori",
                "metric": Category.objects.count(),
                "footer": "Semua kategori aktif",
                "icon": "category",
                "color": "#1c1c75",
            },
            {
                "title": "Total Produk",
                "metric": total_products,
                "footer": "Termasuk semua varian",
                "icon": "inventory_2",
                "color": "#1c1c75",
            },
            {
                "title": "Stok Rendah",
                "metric": Product.objects.filter(stock__lt=10).count(),
                "footer": "Butuh restock",
                "icon": "warning",
                "color": "#f59e0b",
            },
            {
                "title": "Nilai Stok",
                "metric": formatted_price,
                "footer": "Estimasi nilai produk",
                "icon": "payments",
                "color": "#10b981",
            },
            
            # ORDER KPIs
            {
                "title": "Total Orders",
                "metric": total_orders,
                "footer": f"{pending_orders} pending, {completed_orders} selesai",
                "icon": "shopping_cart",
                "color": "#3b82f6",
            },
            {
                "title": "Pending Orders",
                "metric": pending_orders,
                "footer": "Perlu diproses",
                "icon": "pending_actions",
                "color": "#f59e0b",
            },
            {
                "title": "Paid Orders",
                "metric": paid_orders,
                "footer": "Sudah dibayar",
                "icon": "credit_card",
                "color": "#06b6d4",
            },
            {
                "title": "Completed Orders",
                "metric": completed_orders,
                "footer": "Transaksi selesai",
                "icon": "check_circle",
                "color": "#10b981",
            },
            
            # REVENUE KPIs
            {
                "title": "Total Revenue",
                "metric": formatted_revenue,
                "footer": "Dari semua transaksi sukses",
                "icon": "attach_money",
                "color": "#059669",
            },
            {
                "title": "Revenue Hari Ini",
                "metric": formatted_today_revenue,
                "footer": datetime.now().strftime("%d %B %Y"),
                "icon": "today",
                "color": "#8b5cf6",
            },
            {
                "title": "Revenue Bulan Ini",
                "metric": formatted_month_revenue,
                "footer": datetime.now().strftime("%B %Y"),
                "icon": "calendar_month",
                "color": "#ec4899",
            },
            {
                "title": "Cancelled Orders",
                "metric": cancelled_orders,
                "footer": "Transaksi dibatalkan",
                "icon": "cancel",
                "color": "#ef4444",
            },
            
            # 🆕 LOGIN KPIs
            {
                "title": "Total Login",
                "metric": total_logins,
                "footer": "Semua login history",
                "icon": "login",
                "color": "#6366f1",
            },
            {
                "title": "Login Hari Ini",
                "metric": today_logins,
                "footer": datetime.now().strftime("%d %B %Y"),
                "icon": "today",
                "color": "#8b5cf6",
            },
            {
                "title": "Sesi Aktif",
                "metric": active_sessions,
                "footer": "User yang sedang online",
                "icon": "people",
                "color": "#10b981",
            },
        ],
        
        # === PROGRESS BARS ===
        "progress": [
            {
                "title": "Kelengkapan Data Produk",
                "description": "Produk dengan gambar dan deskripsi lengkap",
                "value": completeness,
            },
            {
                "title": "Order Success Rate",
                "description": f"{completed_orders} dari {total_orders} order berhasil diselesaikan",
                "value": int((completed_orders / max(total_orders, 1)) * 100),
            },
        ],
    })
    return context


# ============================================================
# 🔹 INLINE ADMIN - ORDER ITEMS
# ============================================================

class OrderItemInline(TabularInline):
    """Tampilkan order items dalam detail order"""
    model = OrderItem
    extra = 0
    fields = ['product_name', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ============================================================
# 🔹 CATEGORY ADMIN
# ============================================================

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'total_products']
    search_fields = ['name']
    ordering = ['name']

    @display(description="Total Produk")
    def total_products(self, obj):
        count = Product.objects.filter(category=obj).count()
        color_class = 'indigo' if count > 0 else 'neutral'
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color_class, count
        )


# ============================================================
# 🔹 PRODUCT ADMIN
# ============================================================

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['image_display', 'name', 'category', 'price_display', 'stock_status', 'created_at']
    list_filter = ['category', 'created_at', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    fieldsets = (
        ('📦 Informasi Dasar', {
            'fields': ('name', 'category', 'description', 'price', 'stock', 'is_active')
        }),
        ('🖼️ Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('⏱️ Waktu Dibuat', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at']

    @display(description="Gambar")
    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 4px; object-fit: cover;" />', 
                obj.image.url
            )
        return "-"

    @display(description="Harga")
    def price_display(self, obj):
        try:
            return format_html('<b>Rp {:,.0f}</b>', float(obj.price)).replace(',', '.')
        except (TypeError, ValueError):
            return "Rp 0"

    @display(description="Status Stok")
    def stock_status(self, obj):
        if obj.stock <= 0:
            color_class, text = 'danger', 'Habis'
        elif obj.stock < 10:
            color_class, text = 'warning', 'Menipis'
        else:
            color_class, text = 'success', 'Tersedia'

        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color_class, text
        )


# ============================================================
# 🔹 ORDER ADMIN - SUPER CLEAN VERSION
# ============================================================

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    # HANYA field yang ADA di model
    list_display = ['order_id', 'user_name', 'user_email', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user_email', 'user_name']
    ordering = ['-created_at']
    
    # Bulk actions
    actions = ['mark_as_paid', 'mark_as_completed', 'mark_as_cancelled']
    
    # Inline order items
    inlines = [OrderItemInline]
    
    # HANYA field yang ADA di model
    fieldsets = (
        ('📦 Informasi Order', {
            'fields': ('order_id', 'status')
        }),
        ('👤 Informasi Customer', {
            'fields': ('user_name', 'user_email')
        }),
        ('💰 Informasi Pembayaran', {
            'fields': ('total_amount',)
        }),
        ('📅 Waktu', {
            'fields': ('created_at',),  # HANYA created_at
            'classes': ('collapse',)
        }),
    )
    
    # HANYA field yang ADA di model
    readonly_fields = ['order_id', 'created_at']  # TANPA updated_at

    # === ADMIN ACTIONS ===
    
    @admin.action(description="✅ Tandai sebagai Paid")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f"{updated} order berhasil ditandai sebagai Paid.")

    @admin.action(description="✅ Tandai sebagai Completed")
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} order berhasil ditandai sebagai Completed.")

    @admin.action(description="❌ Tandai sebagai Cancelled")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} order berhasil ditandai sebagai Cancelled.")


# ============================================================
# 🔹 ORDER ITEM ADMIN - SIMPLE VERSION
# ============================================================

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['product_name', 'order__order_id', 'order__user_email']
    ordering = ['-order__created_at']

    fieldsets = (
        ('📦 Order Information', {
            'fields': ('order',)
        }),
        ('🛍️ Product Details', {
            'fields': ('product_name', 'quantity', 'price', 'subtotal')
        }),
    )

    readonly_fields = ['subtotal']


# ============================================================
# 🆕 LOGIN HISTORY ADMIN - TRACKING SIAPA SAJA YANG LOGIN
# ============================================================

@admin.register(LoginHistory)
class LoginHistoryAdmin(ModelAdmin):
    list_display = ['user_display', 'login_time', 'logout_time', 'duration_display', 
                    'ip_address', 'device_info', 'status_display']
    list_filter = ['login_time', 'device', 'os', 'browser']
    search_fields = ['user__username', 'user__email', 'ip_address']
    ordering = ['-login_time']
    date_hierarchy = 'login_time'
    
    fieldsets = (
        ('👤 Informasi User', {
            'fields': ('user', 'session_key')
        }),
        ('📅 Waktu', {
            'fields': ('login_time', 'logout_time')
        }),
        ('🌐 Lokasi & Device', {
            'fields': ('ip_address', 'browser', 'os', 'device', 'user_agent')
        }),
    )
    
    readonly_fields = ['user', 'login_time', 'logout_time', 'ip_address', 
                      'user_agent', 'session_key', 'browser', 'os', 'device']
    
    def has_add_permission(self, request):
        """Tidak bisa menambah manual, hanya dari signal"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Bisa delete untuk cleanup data lama"""
        return True
    
    @display(description="User", ordering='user__username')
    def user_display(self, obj):
        if obj.user.is_superuser:
            badge = '<span class="badge badge-danger">Admin</span>'
        elif obj.user.is_staff:
            badge = '<span class="badge badge-warning">Staff</span>'
        else:
            badge = '<span class="badge badge-info">User</span>'
        
        return format_html(
            '<strong>{}</strong> {}<br><small style="color: #666;">{}</small>',
            obj.user.username, badge, obj.user.email
        )
    
    @display(description="Device Info")
    def device_info(self, obj):
        return format_html(
            '<span style="display: inline-block; padding: 4px 8px; background: #e5e7eb; border-radius: 4px; margin: 2px;">'
            '<strong>{}</strong></span> '
            '<span style="display: inline-block; padding: 4px 8px; background: #dbeafe; border-radius: 4px; margin: 2px;">{}</span> '
            '<span style="display: inline-block; padding: 4px 8px; background: #fef3c7; border-radius: 4px; margin: 2px;">{}</span>',
            obj.device or 'Desktop',
            obj.browser or 'Unknown',
            obj.os or 'Unknown'
        )
    
    @display(description="Durasi")
    def duration_display(self, obj):
        duration = obj.get_duration()
        if duration == "Masih aktif":
            return format_html(
                '<span class="badge badge-success">🟢 {}</span>',
                duration
            )
        return format_html(
            '<span class="badge badge-neutral">{}</span>',
            duration
        )
    
    @display(description="Status", ordering='logout_time')
    def status_display(self, obj):
        if obj.logout_time is None:
            return format_html(
                '<span class="badge badge-success">🟢 Online</span>'
            )
        else:
            return format_html(
                '<span class="badge badge-neutral">⚪ Offline</span>'
            )
    
    # Custom actions
    @admin.action(description="🗑️ Hapus history lebih dari 30 hari")
    def delete_old_history(self, request, queryset):
        thirty_days_ago = datetime.now() - timedelta(days=30)
        deleted = LoginHistory.objects.filter(login_time__lt=thirty_days_ago).delete()
        self.message_user(request, f"Berhasil menghapus {deleted[0]} history login yang lebih dari 30 hari.")
    
    actions = ['delete_old_history']
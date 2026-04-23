from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Event, EventLocation, Ticket, UserProfile, Category, Warenkorb
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


class WarenkorbAdmin(admin.ModelAdmin):
    list_display = ('myuser', 'eventID', 'quantity', 'sessionID')
    list_per_page = 10


class TicketAdmin(admin.ModelAdmin):
    list_display = ('userID', 'eventID', 'eventLocationID', 'price', 'quantity')
    list_per_page = 10


class EventAdmin(admin.ModelAdmin):
    list_display = ('userID', 'name', 'price', 'locationID', 'categoryID', 'video_source', 'datum')
    list_editable = ['name', 'price', 'video_source']
    list_per_page = 10

class EventLocationAdmin(admin.ModelAdmin):
    list_display = ('userID', 'location', 'standort', 'detail', 'seatingCapacity')
    list_editable = ['detail', 'standort']
    list_per_page = 10
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    list_editable = ['description']
    list_per_page = 10

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'birthday')
    list_editable =['nickname']
    list_per_page = 10

class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    list_editable = ['first_name', 'last_name']
    list_per_page = 10


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventLocation, EventLocationAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Warenkorb, WarenkorbAdmin)


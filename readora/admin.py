from django.contrib import admin
from .models import Book, RegisteredUser

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'published_date')

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'email', 'registered_at')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

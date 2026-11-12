from django.contrib import admin
from .models import Book, RegisteredUser, IssuedBook

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'department', 'genre', 'total_copies', 'available_copies', 'rack_location')
    list_filter = ('department', 'genre')
    search_fields = ('title', 'author', 'isbn')

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'email', 'role', 'department', 'register_number', 'registered_at')
    list_filter = ('role', 'department')
    search_fields = ('user__username', 'email', 'register_number')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'user', 'department', 'issued_date', 'due_date', 'status', 'fine_amount', 'returned')
    list_filter = ('status', 'returned', 'department')
    search_fields = ('book_title', 'user__username')

from django.db import models
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal

DEPARTMENT_CHOICES = [
    ('CSE', 'Computer Science & Engineering'),
    ('CSM', 'AI & Machine Learning (CSM)'),
    ('CSD', 'Data Science (CSD)'),
    ('ECE', 'Electronics & Communication'),
    ('EEE', 'Electrical & Electronics'),
    ('MECH', 'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('MBA', 'Master of Business Admin'),
    ('GEN', 'General / Other'),
]

ROLE_CHOICES = [
    ('student', 'Student'),
    ('faculty', 'Faculty'),
    ('librarian', 'Librarian / Admin'),
]

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=30, blank=True, null=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='CSE')
    genre = models.CharField(max_length=100, default='Academic')
    description = models.TextField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=5)
    available_copies = models.PositiveIntegerField(default=5)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    pdf_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Filename in static/books/")
    rack_location = models.CharField(max_length=50, default='Rack A-1', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author} ({self.department})"

    @property
    def is_available(self):
        return self.available_copies > 0


class RegisteredUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registered_profile')
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    register_number = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) - {self.department or 'N/A'}"

    @property
    def is_admin_or_librarian(self):
        return self.role == 'librarian' or self.user.is_staff or self.user.is_superuser


class IssuedBook(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True, related_name='issued_instances')
    book_title = models.CharField(max_length=255)  # kept for legacy/fallback
    department = models.CharField(max_length=100)
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    fine_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return f"{self.book_title} issued to {self.user.username}"

    def update_status_and_fine(self, rate_per_day=Decimal('10.00')):
        """Recalculate fine and status dynamically."""
        today = date.today()
        if not self.returned:
            if today > self.due_date:
                self.status = 'overdue'
                days_overdue = (today - self.due_date).days
                self.fine_amount = Decimal(days_overdue) * rate_per_day
            else:
                self.status = 'issued'
                self.fine_amount = Decimal('0.00')
        else:
            self.status = 'returned'
            if self.return_date and self.return_date > self.due_date:
                days_overdue = (self.return_date - self.due_date).days
                self.fine_amount = Decimal(days_overdue) * rate_per_day

    @property
    def is_overdue(self):
        return not self.returned and date.today() > self.due_date

    @property
    def days_remaining(self):
        if self.returned:
            return 0
        return (self.due_date - date.today()).days

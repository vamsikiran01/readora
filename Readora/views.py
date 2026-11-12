from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models import Q, Count, Sum
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal
import requests
import io
import base64
import qrcode

from .models import Book, RegisteredUser, IssuedBook, DEPARTMENT_CHOICES

def generate_qr_data_url(data_str):
    """Generate base64 encoded PNG QR code."""
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(data_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e1b4b", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""

def global_context(request):
    """Context processor providing global variables to all templates."""
    user_profile = None
    is_librarian = False
    if request.user.is_authenticated:
        try:
            user_profile = request.user.registered_profile
            is_librarian = user_profile.is_admin_or_librarian
        except Exception:
            user_profile = None
            is_librarian = request.user.is_staff or request.user.is_superuser
    return {
        'current_user_profile': user_profile,
        'is_librarian': is_librarian,
        'departments': DEPARTMENT_CHOICES,
        'app_name': 'Readora',
    }

# ==========================================
# PUBLIC PAGES
# ==========================================

def index(request):
    total_books = Book.objects.count()
    total_copies = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    active_borrows = IssuedBook.objects.filter(returned=False).count()
    total_members = User.objects.count()
    featured_books = Book.objects.all()[:6]

    return render(request, 'index.html', {
        'total_books': total_books,
        'total_copies': total_copies,
        'active_borrows': active_borrows,
        'total_members': total_members,
        'featured_books': featured_books,
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user_type = request.POST.get("userType", "student")

        # Allow login by username OR by email
        user = authenticate(request, username=identifier, password=password)
        if user is None and '@' in identifier:
            try:
                matched_user = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=matched_user.username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            return render(request, "login.html", {
                "error": "Invalid username/email or password.",
                "entered_username": identifier,
                "entered_user_type": user_type,
            })

    return render(request, "login.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        full_name = request.POST.get('fullName', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        user_type = request.POST.get('userType', 'student')
        department = request.POST.get('department', 'CSE')
        year = request.POST.get('year', 'firstYear') if user_type == 'student' else 'Faculty'
        register_number = request.POST.get('registerNumber', '').strip()

        if password != confirm_password:
            return render(request, 'register.html', {
                'error': 'Passwords do not match.',
                'formData': request.POST
            })

        username = email.split('@')[0]
        # Guarantee unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'An account with this email already exists.',
                'formData': request.POST
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = full_name
            user.save()

            # Ensure RegisteredUser profile
            profile, _ = RegisteredUser.objects.get_or_create(user=user)
            profile.role = user_type
            profile.department = department
            profile.year = year
            profile.register_number = register_number
            profile.email = email
            profile.save()

            login(request, user)
            messages.success(request, f"Welcome to Readora, {full_name or username}! Your account has been registered.")
            return redirect('dashboard')
        except Exception as e:
            return render(request, 'register.html', {
                'error': f'Registration failed: {str(e)}',
                'formData': request.POST
            })

    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('index')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email__iexact=email)
            token = get_random_string(length=24)
            messages.success(request, f"Password reset instructions have been generated for {user.username}. (Demo token: {token})")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")
    return render(request, 'forgot_password.html')

# ==========================================
# DASHBOARD & ACTIONS
# ==========================================

@login_required
def dashboard(request):
    user = request.user
    profile, _ = RegisteredUser.objects.get_or_create(user=user)
    is_librarian = profile.is_admin_or_librarian

    # Handle Add Book (Librarian action)
    if request.method == "POST" and "add_book_submit" in request.POST and is_librarian:
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        isbn = request.POST.get("isbn", "").strip()
        department = request.POST.get("department", "CSE")
        genre = request.POST.get("genre", "Academic").strip()
        copies = int(request.POST.get("copies", 5))
        rack = request.POST.get("rack", "Rack A-1").strip()
        description = request.POST.get("description", "").strip()
        cover_url = request.POST.get("cover_image_url", "").strip()

        if title and author:
            book = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                department=department,
                genre=genre,
                total_copies=copies,
                available_copies=copies,
                rack_location=rack,
                description=description,
                cover_image_url=cover_url or "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80",
                published_date=date.today()
            )
            messages.success(request, f'Book "{book.title}" added to the catalog successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, "Please enter both Title and Author.")

    # Refresh overdue and fine statuses for active books
    today = date.today()
    active_borrows = IssuedBook.objects.filter(returned=False)
    for borrow in active_borrows:
        borrow.update_status_and_fine()
        borrow.save(update_fields=['status', 'fine_amount'])

    if is_librarian:
        total_books = Book.objects.count()
        total_copies = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
        total_available = Book.objects.aggregate(total=Sum('available_copies'))['total'] or 0
        issued_count = IssuedBook.objects.filter(returned=False).count()
        overdue_count = IssuedBook.objects.filter(returned=False, due_date__lt=today).count()
        total_members = User.objects.count()
        total_fines = IssuedBook.objects.aggregate(fines=Sum('fine_amount'))['fines'] or Decimal('0.00')

        recent_issues = IssuedBook.objects.select_related('user', 'book').all()[:8]
        recent_books = Book.objects.all().order_by('-id')[:6]

        # Department distribution data for charts
        dept_counts = Book.objects.values('department').annotate(count=Count('id')).order_by('-count')
        chart_labels = [dict(DEPARTMENT_CHOICES).get(d['department'], d['department']) for d in dept_counts]
        chart_values = [d['count'] for d in dept_counts]

        return render(request, 'dashboard.html', {
            'is_librarian': True,
            'total_books': total_books,
            'total_copies': total_copies,
            'total_available': total_available,
            'issued_count': issued_count,
            'overdue_count': overdue_count,
            'total_members': total_members,
            'total_fines': total_fines,
            'recent_issues': recent_issues,
            'recent_books': recent_books,
            'chart_labels': chart_labels,
            'chart_values': chart_values,
        })
    else:
        # Student / Faculty Member View
        my_borrows = IssuedBook.objects.filter(user=user).select_related('book').order_by('-issued_date')
        my_active = my_borrows.filter(returned=False)
        my_history = my_borrows.filter(returned=True)[:5]
        my_fines = my_active.aggregate(fines=Sum('fine_amount'))['fines'] or Decimal('0.00')

        # Recommended books in their department
        recommended_books = Book.objects.filter(department=profile.department)[:4]
        if not recommended_books.exists():
            recommended_books = Book.objects.all()[:4]

        return render(request, 'dashboard.html', {
            'is_librarian': False,
            'my_active': my_active,
            'my_history': my_history,
            'my_fines': my_fines,
            'recommended_books': recommended_books,
        })

# ==========================================
# SEARCH & CATALOG
# ==========================================

def search_books(request):
    query = request.GET.get('q', '').strip()
    dept = request.GET.get('dept', 'All')
    availability = request.GET.get('avail', 'All')

    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(genre__icontains=query)
        )

    if dept and dept != 'All':
        books = books.filter(department=dept)

    if availability == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability == 'borrowed':
        books = books.filter(available_copies=0)

    # If AJAX request, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        data = [{
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'department': b.department,
            'genre': b.genre,
            'isbn': b.isbn or 'N/A',
            'available_copies': b.available_copies,
            'total_copies': b.total_copies,
            'rack_location': b.rack_location,
            'cover_image_url': b.cover_image_url or '',
            'pdf_filename': b.pdf_filename or '',
            'description': b.description or 'No summary available.',
        } for b in books]
        return JsonResponse({'results': data, 'count': len(data)})

    return render(request, 'searchbooks.html', {
        'books': books,
        'search_query': query,
        'selected_dept': dept,
        'selected_avail': availability,
        'total_results': books.count(),
    })

# ==========================================
# ISSUE & RETURN BOOKS
# ==========================================

@login_required
def issue_books(request):
    today = date.today()
    books = Book.objects.all().order_by('title')
    users = User.objects.all().order_by('username')

    if request.method == "POST":
        action = request.POST.get("action", "issue")
        book_id = request.POST.get("bookId")
        user_identifier = request.POST.get("userIdentifier", "").strip()

        # Find target user: either current user (if student) or specified user (if librarian)
        profile = getattr(request.user, 'registered_profile', None)
        is_librarian = profile and profile.is_admin_or_librarian

        if is_librarian and user_identifier:
            target_user = User.objects.filter(
                Q(username__iexact=user_identifier) | Q(email__iexact=user_identifier)
            ).first()
            if not target_user:
                messages.error(request, f"User '{user_identifier}' not found in the system.")
                return redirect('issue_books')
        else:
            target_user = request.user

        if action == "issue":
            book = get_object_or_404(Book, id=book_id) if book_id else None
            if not book:
                messages.error(request, "Please select a valid book.")
                return redirect('issue_books')

            if book.available_copies <= 0:
                messages.error(request, f'Sorry, all copies of "{book.title}" are currently checked out.')
                return redirect('issue_books')

            # Check if user already has an active copy of this book
            already_borrowed = IssuedBook.objects.filter(user=target_user, book=book, returned=False).exists()
            if already_borrowed:
                messages.warning(request, f'User {target_user.username} already has a copy of "{book.title}" checked out.')
                return redirect('issue_books')

            due_date = today + timedelta(days=14)
            record = IssuedBook.objects.create(
                user=target_user,
                book=book,
                book_title=book.title,
                department=book.department,
                due_date=due_date,
                status='issued',
                returned=False
            )
            book.available_copies = max(0, book.available_copies - 1)
            book.save(update_fields=['available_copies'])

            messages.success(request, f'✅ "{book.title}" successfully issued to {target_user.username}! Due date: {due_date.strftime("%b %d, %Y")}')
            return redirect('issue_books')

        elif action == "return":
            record_id = request.POST.get("recordId")
            if record_id:
                record = get_object_or_404(IssuedBook, id=record_id)
            else:
                record = IssuedBook.objects.filter(user=target_user, book_id=book_id, returned=False).first()

            if not record or record.returned:
                messages.error(request, "Active issued record not found for this book and user.")
                return redirect('issue_books')

            record.returned = True
            record.return_date = today
            record.update_status_and_fine()
            record.save()

            if record.book:
                record.book.available_copies = min(record.book.total_copies, record.book.available_copies + 1)
                record.book.save(update_fields=['available_copies'])

            fine_msg = f" Fine accrued: ₹{record.fine_amount}" if record.fine_amount > 0 else " Returned on time!"
            messages.success(request, f'✅ "{record.book_title}" returned successfully!{fine_msg}')
            return redirect('issue_books')

    # Get active issued records
    is_librarian = getattr(request.user, 'registered_profile', None) and request.user.registered_profile.is_admin_or_librarian
    if is_librarian:
        active_records = IssuedBook.objects.filter(returned=False).select_related('user', 'book').order_by('due_date')
    else:
        active_records = IssuedBook.objects.filter(user=request.user, returned=False).select_related('book').order_by('due_date')

    return render(request, 'issuebooks.html', {
        'books': books,
        'users': users,
        'active_records': active_records,
        'today': today,
    })

# ==========================================
# REMINDERS & DUE DATES
# ==========================================

@login_required
def reminders(request):
    today = date.today()
    is_librarian = getattr(request.user, 'registered_profile', None) and request.user.registered_profile.is_admin_or_librarian

    # Recalculate fines for all active records
    if is_librarian:
        issued_books = IssuedBook.objects.filter(returned=False).select_related('user', 'book').order_by('due_date')
    else:
        issued_books = IssuedBook.objects.filter(user=request.user, returned=False).select_related('book').order_by('due_date')

    for record in issued_books:
        record.update_status_and_fine()
        record.save(update_fields=['status', 'fine_amount'])

    due_soon_records = [r for r in issued_books if 0 <= r.days_remaining <= 3]
    overdue_records = [r for r in issued_books if r.is_overdue]

    return render(request, 'reminders.html', {
        'issued_books': issued_books,
        'due_soon_records': due_soon_records,
        'overdue_records': overdue_records,
        'today': today,
        'is_librarian': is_librarian,
    })

# ==========================================
# REST API & REAL-WORLD FEATURES
# ==========================================

def api_isbn_lookup(request):
    """Google Books API lookup to autofill book details by ISBN."""
    isbn = request.GET.get('isbn', '').strip().replace('-', '').replace(' ', '')
    if not isbn:
        return JsonResponse({'error': 'ISBN is required'}, status=400)

    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('totalItems', 0) > 0:
                item = data['items'][0]['volumeInfo']
                authors = ", ".join(item.get('authors', ['Unknown Author']))
                categories = item.get('categories', ['General'])
                genre = categories[0] if categories else 'Academic'
                cover_links = item.get('imageLinks', {})
                cover_url = cover_links.get('thumbnail') or cover_links.get('smallThumbnail') or ''
                if cover_url.startswith('http://'):
                    cover_url = 'https://' + cover_url[7:]

                return JsonResponse({
                    'success': True,
                    'title': item.get('title', ''),
                    'author': authors,
                    'description': item.get('description', ''),
                    'published_date': item.get('publishedDate', ''),
                    'genre': genre,
                    'cover_image_url': cover_url,
                })
        return JsonResponse({'success': False, 'message': 'No book found for this ISBN in Google Books.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def download_receipt(request, record_id):
    """Generate printable borrow slip / receipt with QR code."""
    record = get_object_or_404(IssuedBook.objects.select_related('user', 'book'), id=record_id)
    if not (request.user == record.user or request.user.registered_profile.is_admin_or_librarian):
        return HttpResponse("Unauthorized", status=403)

    qr_payload = f"READORA-BORROW-{record.id}|USER:{record.user.username}|BOOK:{record.book_title}|DUE:{record.due_date}"
    qr_data_url = generate_qr_data_url(qr_payload)

    return render(request, 'receipt.html', {
        'record': record,
        'qr_data_url': qr_data_url,
        'today': date.today(),
    })

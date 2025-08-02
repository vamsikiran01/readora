let books = []; 

function addBook() {
    const bookTitle = document.getElementById('bookTitle').value;
    const author = document.getElementById('author').value;
    const isbn = document.getElementById('isbn').value;
    const bookType = document.getElementById('bookType').value;
    const availability = document.getElementById('availability').value;
    const file = document.getElementById('bookFile')?.value || "";  // Optional file path (relative to static/books)

    const newBook = {
        title: bookTitle,
        author: author,
        isbn: isbn,
        type: bookType,
        availability: availability,
        file: file  // new: file name (like 'books/introduction_to_cse.pdf')
    };

    books.push(newBook); // Add new book to the books array
    alert(`Book "${bookTitle}" added successfully!`);

    document.getElementById('addBookForm').reset();
    return false; // Prevent page refresh
}

function searchBooks() {
    const query = document.getElementById('searchQuery').value.toLowerCase();
    const bookTypeFilter = document.getElementById('bookTypeFilter').value;
    const bookList = document.getElementById('bookList');

    const filteredBooks = books.filter(book => {
        const matchesQuery = book.title.toLowerCase().includes(query) || book.author.toLowerCase().includes(query);
        const matchesType = bookTypeFilter === "All" || book.type === bookTypeFilter;
        return matchesQuery && matchesType;
    });

    bookList.innerHTML = "";

    filteredBooks.forEach(book => {
        const bookItem = document.createElement("li");

        if (book.file) {
            const link = document.createElement("a");
            link.href = `/static/${book.file}`;
            link.target = "_blank";
            link.textContent = `${book.title} by ${book.author} - ${book.type} (${book.availability})`;
            bookItem.appendChild(link);
        } else {
            bookItem.textContent = `${book.title} by ${book.author} - ${book.type} (${book.availability})`;
        }

        bookList.appendChild(bookItem);
    });
}

function issueReturnBook() {
    const bookId = document.getElementById('bookId').value;
    const action = document.getElementById('action').value;

    if (action === "issue") {
        alert(`Book with ID ${bookId} issued.`);
    } else {
        alert(`Book with ID ${bookId} returned.`);
    }

    return true;
}


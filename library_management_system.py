"""
Library Management System
Day 5 Assignment — Python Mini-Project (OOP)

A menu-driven console application demonstrating:
- Classes, objects, constructors, and methods
- Inheritance and polymorphism (Book / EBook)
- Encapsulation (private attributes with properties)
- Data structures: lists, tuples, sets, dictionaries
- Conditional statements, loops, functions
- Exception handling
- File handling (CSV persistence)

Creative features added beyond the base requirement:
- Member membership tiers (Standard / Premium) with different borrowing limits
- Overdue fine calculation based on days overdue
- Search by title, author, or genre
- Most-borrowed book leaderboard
- Data persists across runs via CSV files
"""

import csv
import os
from datetime import date, timedelta


# =========================================================
# CUSTOM EXCEPTIONS
# =========================================================
class LibraryError(Exception):
    """Base exception for library-specific errors."""
    pass


class BookNotAvailableError(LibraryError):
    pass


class BorrowLimitExceededError(LibraryError):
    pass


class BookNotFoundError(LibraryError):
    pass


class MemberNotFoundError(LibraryError):
    pass


# =========================================================
# BOOK CLASSES (inheritance + polymorphism)
# =========================================================
class Book:
    """Represents a physical book in the library."""

    def __init__(self, book_id, title, author, genre, copies=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.total_copies = copies
        self.available_copies = copies
        self.times_borrowed = 0

    def is_available(self):
        return self.available_copies > 0

    def borrow_copy(self):
        if not self.is_available():
            raise BookNotAvailableError(f"'{self.title}' has no available copies right now.")
        self.available_copies -= 1
        self.times_borrowed += 1

    def return_copy(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1

    def describe(self):
        return f"[{self.book_id}] {self.title} by {self.author} ({self.genre}) — {self.available_copies}/{self.total_copies} available"

    def to_row(self):
        return [self.book_id, self.title, self.author, self.genre,
                self.total_copies, self.available_copies, self.times_borrowed, "Book"]


class EBook(Book):
    """An e-book — unlimited 'copies' since it's digital, no physical fine on lateness."""

    def __init__(self, book_id, title, author, genre):
        super().__init__(book_id, title, author, genre, copies=float('inf'))

    def is_available(self):
        return True  # e-books are always available

    def borrow_copy(self):
        self.times_borrowed += 1  # no copy count to decrement

    def return_copy(self):
        pass  # nothing to return

    def describe(self):
        return f"[{self.book_id}] {self.title} by {self.author} ({self.genre}) — E-Book (unlimited access)"

    def to_row(self):
        return [self.book_id, self.title, self.author, self.genre,
                "inf", "inf", self.times_borrowed, "EBook"]


# =========================================================
# MEMBER CLASS
# =========================================================
class Member:
    """Represents a library member with borrowing history."""

    TIER_LIMITS = {"Standard": 3, "Premium": 6}
    FINE_PER_DAY = 5  # currency units per day overdue

    def __init__(self, member_id, name, tier="Standard"):
        self.member_id = member_id
        self.name = name
        self.tier = tier if tier in self.TIER_LIMITS else "Standard"
        self.borrowed_books = {}  # {book_id: due_date}
        self.fines_owed = 0

    @property
    def borrow_limit(self):
        return self.TIER_LIMITS[self.tier]

    def can_borrow_more(self):
        return len(self.borrowed_books) < self.borrow_limit

    def borrow(self, book_id, due_date):
        if not self.can_borrow_more():
            raise BorrowLimitExceededError(
                f"{self.name} has reached the {self.tier} tier limit of {self.borrow_limit} books."
            )
        self.borrowed_books[book_id] = due_date

    def return_book(self, book_id):
        due_date = self.borrowed_books.pop(book_id, None)
        if due_date is None:
            return 0
        overdue_days = (date.today() - due_date).days
        fine = max(0, overdue_days) * self.FINE_PER_DAY
        self.fines_owed += fine
        return fine

    def to_row(self):
        borrowed_str = ";".join(f"{bid}:{d.isoformat()}" for bid, d in self.borrowed_books.items())
        return [self.member_id, self.name, self.tier, self.fines_owed, borrowed_str]


# =========================================================
# LIBRARY CLASS (main system logic)
# =========================================================
class Library:
    BOOKS_FILE = "books.csv"
    MEMBERS_FILE = "members.csv"
    LOAN_PERIOD_DAYS = 14

    def __init__(self):
        self.books = {}      # book_id -> Book/EBook
        self.members = {}    # member_id -> Member
        self.load_data()

    # ---------------- File handling ----------------
    def load_data(self):
        if os.path.exists(self.BOOKS_FILE):
            with open(self.BOOKS_FILE, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    try:
                        book_id, title, author, genre, total, avail, borrowed_count, kind = row
                        if kind == "EBook":
                            book = EBook(book_id, title, author, genre)
                        else:
                            book = Book(book_id, title, author, genre, copies=int(total))
                            book.available_copies = int(avail)
                        book.times_borrowed = int(borrowed_count)
                        self.books[book_id] = book
                    except (ValueError, IndexError):
                        continue  # skip malformed rows gracefully

        if os.path.exists(self.MEMBERS_FILE):
            with open(self.MEMBERS_FILE, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    try:
                        member_id, name, tier, fines, borrowed_str = row
                        member = Member(member_id, name, tier)
                        member.fines_owed = float(fines)
                        if borrowed_str:
                            for pair in borrowed_str.split(";"):
                                bid, due = pair.split(":")
                                member.borrowed_books[bid] = date.fromisoformat(due)
                        self.members[member_id] = member
                    except (ValueError, IndexError):
                        continue

        if not self.books:
            self._seed_sample_data()

    def save_data(self):
        with open(self.BOOKS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["book_id", "title", "author", "genre", "total_copies",
                              "available_copies", "times_borrowed", "type"])
            for book in self.books.values():
                writer.writerow(book.to_row())

        with open(self.MEMBERS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["member_id", "name", "tier", "fines_owed", "borrowed_books"])
            for member in self.members.values():
                writer.writerow(member.to_row())

    def _seed_sample_data(self):
        """Populate a few sample books on first run so the menu isn't empty."""
        sample_books = [
            Book("B001", "Clean Code", "Robert C. Martin", "Programming", 2),
            Book("B002", "The Pragmatic Programmer", "Andrew Hunt", "Programming", 1),
            Book("B003", "Sapiens", "Yuval Noah Harari", "History", 3),
            EBook("B004", "Atomic Habits", "James Clear", "Self-Help"),
        ]
        for b in sample_books:
            self.books[b.book_id] = b

    # ---------------- Book management ----------------
    def add_book(self, title, author, genre, copies, is_ebook=False):
        book_id = f"B{len(self.books) + 1:03d}"
        book = EBook(book_id, title, author, genre) if is_ebook else Book(book_id, title, author, genre, copies)
        self.books[book_id] = book
        return book

    def find_book(self, book_id):
        book = self.books.get(book_id)
        if book is None:
            raise BookNotFoundError(f"No book found with ID '{book_id}'.")
        return book

    def search_books(self, keyword):
        keyword = keyword.lower()
        return [b for b in self.books.values()
                if keyword in b.title.lower() or keyword in b.author.lower() or keyword in b.genre.lower()]

    # ---------------- Member management ----------------
    def add_member(self, name, tier="Standard"):
        member_id = f"M{len(self.members) + 1:03d}"
        member = Member(member_id, name, tier)
        self.members[member_id] = member
        return member

    def find_member(self, member_id):
        member = self.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"No member found with ID '{member_id}'.")
        return member

    # ---------------- Borrowing / returning ----------------
    def borrow_book(self, member_id, book_id):
        member = self.find_member(member_id)
        book = self.find_book(book_id)
        book.borrow_copy()  # raises BookNotAvailableError if none left
        try:
            due_date = date.today() + timedelta(days=self.LOAN_PERIOD_DAYS)
            member.borrow(book_id, due_date)
        except BorrowLimitExceededError:
            book.return_copy()  # roll back the book checkout
            raise
        return due_date

    def return_book(self, member_id, book_id):
        member = self.find_member(member_id)
        book = self.find_book(book_id)
        fine = member.return_book(book_id)
        book.return_copy()
        return fine

    # ---------------- Reports ----------------
    def most_borrowed_books(self, top_n=5):
        return sorted(self.books.values(), key=lambda b: b.times_borrowed, reverse=True)[:top_n]

    def genres_available(self):
        return sorted({b.genre for b in self.books.values()})  # set -> demonstrates set usage

    def total_fines_collected(self):
        return sum(m.fines_owed for m in self.members.values())


# =========================================================
# MENU-DRIVEN CONSOLE INTERFACE
# =========================================================
def print_header(title):
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50)


def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid whole number.")


def main_menu():
    library = Library()

    MENU_OPTIONS = (  # tuple: fixed set of menu options
        "1. View all books",
        "2. Search for a book",
        "3. Add a new book",
        "4. Register a new member",
        "5. Borrow a book",
        "6. Return a book",
        "7. View member details",
        "8. Most borrowed books (leaderboard)",
        "9. View available genres",
        "10. Save and Exit",
    )

    print_header("LIBRARY MANAGEMENT SYSTEM")
    print("Welcome! Manage books, members, borrowing, and returns below.")

    while True:
        print("\n" + "-" * 50)
        for option in MENU_OPTIONS:
            print(option)
        print("-" * 50)

        choice = input("Enter your choice (1-10): ").strip()

        try:
            if choice == "1":
                view_all_books(library)
            elif choice == "2":
                search_book_menu(library)
            elif choice == "3":
                add_book_menu(library)
            elif choice == "4":
                add_member_menu(library)
            elif choice == "5":
                borrow_book_menu(library)
            elif choice == "6":
                return_book_menu(library)
            elif choice == "7":
                view_member_menu(library)
            elif choice == "8":
                leaderboard_menu(library)
            elif choice == "9":
                genres_menu(library)
            elif choice == "10":
                library.save_data()
                print("\nData saved. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 10.")
        except LibraryError as e:
            print(f"\n[Library Error] {e}")
        except Exception as e:
            print(f"\n[Unexpected Error] {e}")


def view_all_books(library):
    print_header("ALL BOOKS")
    if not library.books:
        print("No books in the library yet.")
        return
    for book in library.books.values():
        print(book.describe())


def search_book_menu(library):
    print_header("SEARCH BOOKS")
    keyword = input("Enter title, author, or genre keyword: ").strip()
    results = library.search_books(keyword)
    if not results:
        print("No matching books found.")
    else:
        for book in results:
            print(book.describe())


def add_book_menu(library):
    print_header("ADD A NEW BOOK")
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    genre = input("Genre: ").strip()
    is_ebook_input = input("Is this an e-book? (y/n): ").strip().lower()

    if is_ebook_input == "y":
        book = library.add_book(title, author, genre, copies=0, is_ebook=True)
    else:
        copies = get_int_input("Number of copies: ")
        book = library.add_book(title, author, genre, copies=copies, is_ebook=False)

    print(f"\nAdded successfully: {book.describe()}")


def add_member_menu(library):
    print_header("REGISTER A NEW MEMBER")
    name = input("Member name: ").strip()
    print("Membership tiers: Standard (3 books) / Premium (6 books)")
    tier = input("Tier (Standard/Premium) [default Standard]: ").strip() or "Standard"
    member = library.add_member(name, tier)
    print(f"\nRegistered: {member.member_id} - {member.name} ({member.tier} tier)")


def borrow_book_menu(library):
    print_header("BORROW A BOOK")
    member_id = input("Member ID: ").strip()
    book_id = input("Book ID: ").strip()
    due_date = library.borrow_book(member_id, book_id)
    print(f"\nBook borrowed successfully. Due back by: {due_date.isoformat()}")


def return_book_menu(library):
    print_header("RETURN A BOOK")
    member_id = input("Member ID: ").strip()
    book_id = input("Book ID: ").strip()
    fine = library.return_book(member_id, book_id)
    if fine > 0:
        print(f"\nBook returned. Overdue fine incurred: {fine} currency units.")
    else:
        print("\nBook returned on time. No fine incurred.")


def view_member_menu(library):
    print_header("MEMBER DETAILS")
    member_id = input("Member ID: ").strip()
    member = library.find_member(member_id)
    print(f"Name: {member.name}")
    print(f"Tier: {member.tier} (limit: {member.borrow_limit} books)")
    print(f"Fines owed: {member.fines_owed}")
    if member.borrowed_books:
        print("Currently borrowed:")
        for book_id, due in member.borrowed_books.items():
            try:
                book = library.find_book(book_id)
                print(f"  - {book.title} (due {due.isoformat()})")
            except BookNotFoundError:
                print(f"  - [Unknown book {book_id}] (due {due.isoformat()})")
    else:
        print("No books currently borrowed.")


def leaderboard_menu(library):
    print_header("MOST BORROWED BOOKS")
    top_books = library.most_borrowed_books()
    if not top_books or all(b.times_borrowed == 0 for b in top_books):
        print("No borrowing activity yet.")
        return
    for rank, book in enumerate(top_books, start=1):
        print(f"{rank}. {book.title} — borrowed {book.times_borrowed} time(s)")


def genres_menu(library):
    print_header("AVAILABLE GENRES")
    genres = library.genres_available()
    print(", ".join(genres) if genres else "No genres available.")


if __name__ == "__main__":
    main_menu()

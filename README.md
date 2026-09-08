# Library Management System

## Day 5 Assignment — Python Mini-Project (OOP)

A menu-driven console application for managing a library's books, members, and borrowing activity, built entirely with Object-Oriented Programming.

## How to Run

```bash
python3 library_management_system.py
```

The program starts with 4 sample books pre-loaded (on first run only) and presents a numbered menu. Enter the number of the option you want and follow the prompts.

## OOP Concepts Demonstrated

- **Classes & Objects**: `Book`, `EBook`, `Member`, `Library`
- **Inheritance & Polymorphism**: `EBook` inherits from `Book` and overrides `is_available()`, `borrow_copy()`, `return_copy()`, and `describe()` to reflect that e-books are always available and never physically returned
- **Encapsulation**: `Member.borrow_limit` is exposed as a read-only `@property` derived from the member's tier
- **Constructors**: every class initializes its own state via `__init__`
- **Custom Exceptions**: `LibraryError` and its subclasses (`BookNotAvailableError`, `BorrowLimitExceededError`, `BookNotFoundError`, `MemberNotFoundError`) model domain-specific failures instead of relying on generic exceptions

## Week 1 Concepts Applied

- **Variables & conditionals**: tier limits, availability checks, fine calculations
- **Loops**: the main menu loop, iterating over books/members for search and reports
- **Functions**: each menu action is its own function; core logic lives in class methods
- **Data structures**:
  - **Dictionaries** — `books` and `members` are keyed by ID for O(1) lookup; a member's `borrowed_books` maps book ID → due date
  - **Sets** — `genres_available()` returns a deduplicated set of genres
  - **Tuples** — the menu options list is stored as an immutable tuple
  - **Lists** — search results and leaderboard rankings
- **Exception handling**: every menu action is wrapped in a `try/except`, catching both library-specific errors and unexpected ones without crashing the program; malformed CSV rows are skipped gracefully on load
- **File handling (CSV)**: `books.csv` and `members.csv` persist all data between runs, using Python's built-in `csv` module for both reading and writing

## Creative Features Added

1. **Membership tiers** — Standard members can borrow up to 3 books; Premium members up to 6
2. **Overdue fine calculation** — returning a book after its 14-day due date incurs a per-day fine, tracked per member
3. **Search** — find books by keyword across title, author, or genre
4. **Most-borrowed leaderboard** — ranks books by how many times they've been checked out
5. **E-books** — a separate book type with unlimited simultaneous access and no return process
6. **Safe rollback** — if a borrow fails because a member has hit their limit, the book copy that was tentatively checked out is automatically returned, so counts never get out of sync
7. **Persistent storage** — all books and members survive across program runs via CSV files, with graceful handling of any corrupted rows

## Files

- `library_management_system.py` — the complete application
- `books.csv`, `members.csv` — generated automatically on first save (not included until you run the program)

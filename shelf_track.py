"""
EbookStore Database Management System
=======================================
A comprehensive bookstore inventory management system with SQLite database.

Features:
- Add, update, delete, and search for books
- View all books with author details
- Data validation and error handling
- Modular function-based design

Author: [Your Name]
Date: [Current Date]
Course: HyperionDev Capstone Project
"""


import sqlite3


def initialize_db():
    """Create the book table if it doesn't exist and populate with initial data."""
    with sqlite3.connect('ebookstore.db') as conn:
        cursor = conn.cursor()
        
        # Create book table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author_id INTEGER,
            quantity INTEGER
        )
        ''')
        
        # Insert the 5 books
        books = [
            (3001, 'A Tale of Two Cities', 1, 30),
            (3002, 'The Lion, the Witch and the Wardrobe', 2356, 25),
            (3004, 'The Lord of the Rings', 6380, 37),
            (3005, 'Just Kids', 5620, 12)
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO book VALUES (?, ?, ?, ?)
        ''', books)
        
        print("Database and book table created with 5 books!")
    # Connection automatically closes here

# ===== MENU SYSTEM ====

def menu():
    """Display the menu and return the user's choice"""
    print("\n=== Bookstore Management ===")
    print("1. Enter book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search books")
    print("5. View details of all books") 
    print("0. Exit")
    return input("Choose an option: ")


# ====== FUNCTIONS FOR EACH MENU OPTION ======

def add_new_book():
    """Add a new book to the database."""
    with sqlite3.connect('ebookstore.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # all function logic should be handled here
        
        # Validate book ID
        while True:
            try:
                book_id = int(input("Enter book ID (4 digits): "))
                if 1000 <= book_id <= 9999:
                    # Check if ID already exists
                    cursor.execute("SELECT id FROM book WHERE id = ?", (book_id,))
                    if cursor.fetchone():
                        print("Error: Book ID already exists!")
                        continue
                    break
                else:
                    print("Error: Must be 4 digits (1000-9999)")
            except ValueError:
                print("Error: Enter a valid number")
        
        title = input("Enter book title: ").strip()
        if not title:
            print("Error: Title cannot be empty")
            return  # Changed from conn.close() to just return
        
        # Validate author ID
        while True:
            try:
                author_id = int(input("Enter author ID (4 digits): "))
                if 1000 <= author_id <= 9999:
                    # Check if author exists
                    cursor.execute("SELECT id FROM author WHERE id = ?", (author_id,))
                    if not cursor.fetchone():
                        print("Warning: Author ID doesn't exist in author table")
                        proceed = input("Add anyway? (y/n): ").lower()
                        if proceed != 'y':
                            continue
                    break
                else:
                    print("Error: Must be 4 digits (1000-9999)")
            except ValueError:
                print("Error: Enter a valid number")
        
        # Validate quantity
        while True:
            try:
                quantity = int(input("Enter quantity: "))
                if quantity >= 0:
                    break
                print("Error: Quantity cannot be negative")
            except ValueError:
                print("Error: Enter a valid number")
        
        try:
            cursor.execute("INSERT INTO book VALUES (?, ?, ?, ?)", 
                          (book_id, title, author_id, quantity))
            print("Book added successfully!")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    


def update_book():
    """Update book and author information using context manager."""
    with sqlite3.connect('ebookstore.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First, check if book exists and get author info using INNER JOIN
        while True:
            try:
                book_id = int(input("Enter book ID to update: "))
                cursor.execute("""
                    SELECT b.id, b.title, b.quantity, a.id as author_id, a.name, a.country 
                    FROM book b
                    INNER JOIN author a ON b.author_id = a.id
                    WHERE b.id = ?
                """, (book_id,))
                book = cursor.fetchone()
                if not book:
                    print("Error: Book ID not found!")
                    continue
                break
            except ValueError:
                print("Error: Enter a valid number")
        
        # Display current information including author details
        print(f"\nCurrent Book Information:")
        print(f"Title: {book['title']}")
        print(f"Quantity: {book['quantity']}")
        print(f"Author: {book['name']}")
        print(f"Author's Country: {book['country']}")
        
        # Ask what to update
        print("\nWhat would you like to update?")
        print("1. Book quantity only")
        print("2. Book title only")
        print("3. Author name only")
        print("4. Author country only")
        print("5. Both author name and country")
        update_choice = input("Choose an option: ")
        
        try:
            # Update book quantity
            if update_choice == '1':
                while True:
                    try:
                        new_quantity = int(input("Enter new quantity: "))
                        if new_quantity >= 0:
                            cursor.execute("UPDATE book SET quantity = ? WHERE id = ?", 
                                          (new_quantity, book_id))
                            break
                        print("Error: Quantity cannot be negative")
                    except ValueError:
                        print("Error: Enter a valid number")
            
            # Update book title
            elif update_choice == '2':
                new_title = input("Enter new title: ").strip()
                if new_title:
                    cursor.execute("UPDATE book SET title = ? WHERE id = ?", 
                                  (new_title, book_id))
                else:
                    print("Title update cancelled")
            
            # Update author name only
            elif update_choice == '3':
                new_author_name = input(f"Enter new author name (current: {book['name']}): ").strip()
                if new_author_name:
                    cursor.execute("UPDATE author SET name = ? WHERE id = ?", 
                                  (new_author_name, book['author_id']))
                    print("Author name updated successfully!")
            
            # Update author country only
            elif update_choice == '4':
                new_country = input(f"Enter new country (current: {book['country']}): ").strip()
                if new_country:
                    cursor.execute("UPDATE author SET country = ? WHERE id = ?", 
                                  (new_country, book['author_id']))
                    print("Author country updated successfully!")
            
            # Update both author name and country
            elif update_choice == '5':
                new_author_name = input(f"Enter new author name (current: {book['name']}): ").strip()
                new_country = input(f"Enter new country (current: {book['country']}): ").strip()
                
                if new_author_name or new_country:
                    # Build dynamic UPDATE query
                    updates = []
                    params = []
                    if new_author_name:
                        updates.append("name = ?")
                        params.append(new_author_name)
                    if new_country:
                        updates.append("country = ?")
                        params.append(new_country)
                    params.append(book['author_id'])
                    
                    cursor.execute(f"UPDATE author SET {', '.join(updates)} WHERE id = ?", params)
                    print("Author information updated successfully!")
            
            else:
                print("Invalid option")
                return  # Just return, context manager handles cleanup
            
            # No need for conn.commit() - context manager handles it automatically
            print("Update completed successfully!")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # No need for rollback - context manager handles it automatically


def delete_book():
    """Delete a book from the database using context manager."""
    with sqlite3.connect('ebookstore.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        while True:
            try:
                book_id = int(input("Enter book ID to delete: "))
                # Check if book exists
                cursor.execute("SELECT title FROM book WHERE id = ?", (book_id,))
                book = cursor.fetchone()
                if not book:
                    print("Error: Book ID not found!")
                    continue
                
                # Confirm deletion
                confirm = input(f"Are you sure you want to delete '{book['title']}'? (y/n): ").lower()
                if confirm == 'y':
                    cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
                    # No need for conn.commit() - context manager handles it
                    print("Book deleted successfully!")
                else:
                    print("Deletion cancelled")
                break
            except ValueError:
                print("Error: Enter a valid number")
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                # No need to handle rollback - context manager does it automatically


def search_books():
    """Search for books by ID or title using context manager."""
    with sqlite3.connect('ebookstore.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\nSearch by:")
        print("1. ID")
        print("2. Title")
        search_choice = input("Choose: ")
        
        try:
            if search_choice == "1":
                while True:
                    try:
                        book_id = int(input("Enter ID: "))
                        break
                    except ValueError:
                        print("Error: Enter a valid number")
                cursor.execute("""
                    SELECT book.id, book.title, book.quantity, author.name, author.country
                    FROM book 
                    INNER JOIN author ON book.author_id = author.id
                    WHERE book.id = ?
                """, (book_id,))
                
            elif search_choice == "2":
                title = input("Enter title: ").strip()
                cursor.execute("""
                    SELECT book.id, book.title, book.quantity, author.name, author.country
                    FROM book 
                    INNER JOIN author ON book.author_id = author.id
                    WHERE book.title LIKE ?
                """, ('%' + title + '%',))
            else:
                print("Invalid choice")
                return  # Just return, context manager handles cleanup
            
            results = cursor.fetchall()
            
            if results:
                print(f"\nFound {len(results)} book(s):")
                for row in results:
                    print(f"ID: {row['id']}, Title: {row['title']}, "
                          f"Author: {row['name']}, Country: {row['country']}, "
                          f"Quantity: {row['quantity']}")
            else:
                print("No books found.")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # No need for rollback - context manager handles it automatically

def view_all_books():
    """Display all books in inventory with author details using context manager."""
    with sqlite3.connect('ebookstore.db') as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT book.title, author.name, author.country
                FROM book
                LEFT JOIN author ON book.author_id = author.id
                ORDER BY book.title
            ''')
            
            results = cursor.fetchall()
            
            if results:
                print("\n" + "="*50)
                print("=== ALL BOOKS IN INVENTORY ===")
                print("="*50)
                for row in results:
                    # Using index positions: 0=title, 1=name, 2=country
                    author_name = row[1] if row[1] else "Unknown Author"
                    author_country = row[2] if row[2] else "Unknown"
                    print(f"\n📖 Title: {row[0]}")
                    print(f"   ✍️  Author: {author_name}")
                    print(f"   🌍 Country: {author_country}")
                print("\n" + "="*50)
            else:
                print("No books found in database.")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")


# ==== CREATE AUTHOR TABLE ====
def create_author_table():
    """Create the author table if it doesn't exist and populate with initial authors."""
    with sqlite3.connect('ebookstore.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT
        )
        ''')
        
        # Insert authors
        authors = [
            (1, 'Charles Dickens', 'England'),
            (2356, 'C.S. Lewis', 'Ireland'),
            (6380, 'J.R.R. Tolkien', 'South Africa'),
            (5620, 'Lewis Carroll', 'England')
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO author VALUES (?, ?, ?)
        ''', authors)
        
        print("Author table created with authors!")

# ==== MAIN PROGRAM LOOP ====

if __name__ == "__main__":
    initialize_db()
    create_author_table()
    
    # Then run the main menu
    while True:
        choice = menu()
        
        if choice == "1":
            add_new_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            search_books()
        elif choice == "5":
            view_all_books()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


   
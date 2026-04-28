import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        
        # Data storage
        self.books = []
        self.load_data()
        
        # Create GUI elements
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_view()
        self.create_button_frame()
        
        # Refresh display
        self.refresh_display()
    
    def create_input_frame(self):
        """Create input form for adding books"""
        input_frame = ttk.LabelFrame(self.root, text="Добавить новую книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Title
        ttk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Author
        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.author_entry = ttk.Entry(input_frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Genre
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Pages
        ttk.Label(input_frame, text="Количество страниц:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.pages_entry = ttk.Entry(input_frame, width=25)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Add button
        self.add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        self.add_button.grid(row=2, column=0, columnspan=4, pady=10)
    
    def create_filter_frame(self):
        """Create filter controls"""
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Genre filter
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w", padx=5)
        self.genre_filter = ttk.Entry(filter_frame, width=25)
        self.genre_filter.grid(row=0, column=1, padx=5)
        self.genre_filter.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Pages filter
        ttk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, sticky="w", padx=5)
        self.pages_filter = ttk.Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5)
        self.pages_filter.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Clear filters button
        self.clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        self.clear_filter_btn.grid(row=0, column=4, padx=20)
    
    def create_tree_view(self):
        """Create table for displaying books"""
        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("ID", "Title", "Author", "Genre", "Pages", "Date Added")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=v_scrollbar.set,
                                 xscrollcommand=h_scrollbar.set)
        
        # Define column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Название")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("Pages", text="Страницы")
        self.tree.heading("Date Added", text="Дата добавления")
        
        # Define column widths
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=200)
        self.tree.column("Author", width=150)
        self.tree.column("Genre", width=120)
        self.tree.column("Pages", width=100)
        self.tree.column("Date Added", width=150)
        
        self.tree.pack(fill="both", expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Bind double-click for deletion
        self.tree.bind('<Double-Button-1>', self.delete_book)
    
    def create_button_frame(self):
        """Create additional buttons frame"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Statistics button
        self.stats_btn = ttk.Button(button_frame, text="Показать статистику", command=self.show_statistics)
        self.stats_btn.pack(side="left", padx=5)
        
        # Delete button
        self.delete_btn = ttk.Button(button_frame, text="Удалить выбранную книгу", command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=5)
        
        # Save button
        self.save_btn = ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json)
        self.save_btn.pack(side="right", padx=5)
        
        # Load button
        self.load_btn = ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json)
        self.load_btn.pack(side="right", padx=5)
    
    def add_book(self):
        """Add a new book to the collection"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        
        # Validation
        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        try:
            pages = int(pages)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return
        
        # Create book entry
        book = {
            "id": len(self.books) + 1,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.books.append(book)
        self.save_data()
        self.refresh_display()
        
        # Clear input fields
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Книга '{title}' успешно добавлена!")
    
    def apply_filters(self):
        """Apply filters to the displayed books"""
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter = self.pages_filter.get().strip()
        
        filtered_books = self.books.copy()
        
        # Apply genre filter
        if genre_filter:
            filtered_books = [book for book in filtered_books 
                            if genre_filter in book['genre'].lower()]
        
        # Apply pages filter
        if pages_filter:
            try:
                min_pages = int(pages_filter)
                filtered_books = [book for book in filtered_books 
                                if book['pages'] > min_pages]
            except ValueError:
                pass
        
        self.display_books(filtered_books)
    
    def display_books(self, books_to_display):
        """Display books in the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered books
        for book in books_to_display:
            self.tree.insert("", "end", values=(
                book['id'],
                book['title'],
                book['author'],
                book['genre'],
                book['pages'],
                book['date_added']
            ))
    
    def refresh_display(self):
        """Refresh the display with current data"""
        self.apply_filters()
    
    def clear_filters(self):
        """Clear all filters"""
        self.genre_filter.delete(0, tk.END)
        self.pages_filter.delete(0, tk.END)
        self.refresh_display()
    
    def delete_selected(self):
        """Delete selected book"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите книгу для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту книгу?"):
            # Get the book ID from the selected item
            item = self.tree.item(selected[0])
            book_id = item['values'][0]
            
            # Remove book from list
            self.books = [book for book in self.books if book['id'] != book_id]
            
            # Renumber IDs
            for i, book in enumerate(self.books, 1):
                book['id'] = i
            
            self.save_data()
            self.refresh_display()
            messagebox.showinfo("Успех", "Книга успешно удалена!")
    
    def delete_book(self, event):
        """Delete book on double-click"""
        self.delete_selected()
    
    def save_to_json(self):
        """Save books to JSON file"""
        try:
            with open('books.json', 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные успешно сохранены в books.json!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def load_from_json(self):
        """Load books from JSON file"""
        try:
            if os.path.exists('books.json'):
                with open('books.json', 'r', encoding='utf-8') as f:
                    loaded_books = json.load(f)
                
                if messagebox.askyesno("Подтверждение", "Загрузка из JSON заменит текущие данные. Продолжить?"):
                    self.books = loaded_books
                    self.save_data()
                    self.refresh_display()
                    messagebox.showinfo("Успех", f"Загружено {len(self.books)} книг из books.json!")
            else:
                messagebox.showwarning("Предупреждение", "Файл books.json не найден!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")
    
    def save_data(self):
        """Auto-save data to JSON"""
        try:
            with open('books.json', 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except:
            pass
    
    def load_data(self):
        """Auto-load data from JSON"""
        try:
            if os.path.exists('books.json'):
                with open('books.json', 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
        except:
            self.books = []
    
    def show_statistics(self):
        """Display statistics about the books"""
        if not self.books:
            messagebox.showinfo("Статистика", "Нет добавленных книг для статистики.")
            return
        
        total_books = len(self.books)
        total_pages = sum(book['pages'] for book in self.books)
        avg_pages = total_pages // total_books if total_books > 0 else 0
        
        # Genre statistics
        genres = {}
        for book in self.books:
            genres[book['genre']] = genres.get(book['genre'], 0) + 1
        
        most_common_genre = max(genres, key=genres.get) if genres else "N/A"
        
        stats_text = f"""
        📊 Статистика прочитанных книг:
        
        📚 Всего книг: {total_books}
        📖 Всего страниц: {total_pages}
        📏 Среднее количество страниц: {avg_pages}
        🎭 Самый популярный жанр: {most_common_genre} ({genres.get(most_common_genre, 0)} книг)
        
        📈 Жанры:
        """
        
        for genre, count in genres.items():
            stats_text += f"\n   • {genre}: {count} книг"
        
        messagebox.showinfo("Статистика", stats_text)

def main():
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()

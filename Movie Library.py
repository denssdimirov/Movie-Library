import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Сидимиров Денис")
        self.root.geometry("900x600")
        
        self.data_file = "movie_library.json"
        self.movies = []
        
        self.load_data()
        self.create_widgets()
        self.refresh_table()
    
    def create_widgets(self):
        # Рамка ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавление фильма", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, padx=5)
        self.genre_entry = ttk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Год:").grid(row=1, column=0, padx=5, pady=5)
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5)
        
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, padx=5)
        self.rating_entry = ttk.Entry(input_frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5)
        
        ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie).grid(row=0, column=4, rowspan=2, padx=20)
        
        # Рамка фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5)
        self.filter_genre = ttk.Entry(filter_frame, width=20)
        self.filter_genre.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Год:").grid(row=0, column=2, padx=5)
        self.filter_year = ttk.Entry(filter_frame, width=10)
        self.filter_year.grid(row=0, column=3, padx=5)
        
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5)
        
        # Рамка таблицы
        table_frame = ttk.LabelFrame(self.root, text="Список фильмов", padding="10")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("id", "Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        
        self.tree.column("id", width=50)
        self.tree.column("Название", width=250)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=80)
        self.tree.column("Рейтинг", width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="🗑️ Удалить выбранный фильм", command=self.delete_movie).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Удалить все фильмы", command=self.delete_all_movies).pack(side="left", padx=5)
    
    def validate_movie_data(self, title, genre, year, rating):
        if not title or not title.strip():
            return False, "Название не может быть пустым!"
        
        if not genre or not genre.strip():
            return False, "Жанр не может быть пустым!"
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            if year_int < 1888 or year_int > current_year:
                return False, f"Год должен быть от 1888 до {current_year}!"
        except ValueError:
            return False, "Год должен быть числом!"
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                return False, "Рейтинг должен быть от 0 до 10!"
        except ValueError:
            return False, "Рейтинг должен быть числом!"
        
        return True, "OK"
    
    def add_movie(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        is_valid, message = self.validate_movie_data(title, genre, year, rating)
        if not is_valid:
            messagebox.showerror("Ошибка", message)
            return
        
        movie_id = max([m["id"] for m in self.movies], default=0) + 1
        
        movie = {
            "id": movie_id,
            "title": title,
            "genre": genre,
            "year": int(year),
            "rating": float(rating)
        }
        
        self.movies.append(movie)
        self.save_data()
        self.refresh_table()
        
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Фильм '{title}' добавлен!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
            return
        
        item = self.tree.item(selected[0])
        movie_id = item['values'][0]
        movie_title = item['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить фильм '{movie_title}'?"):
            self.movies = [m for m in self.movies if m["id"] != movie_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Фильм удалён!")
    
    def delete_all_movies(self):
        """Удаление всех фильмов"""
        if not self.movies:
            messagebox.showinfo("Информация", "Коллекция пуста!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить ВСЕ фильмы? Отменить нельзя!"):
            self.movies = []
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Все фильмы удалены!")
    
    def apply_filter(self):
        genre_filter = self.filter_genre.get().strip().lower()
        year_filter = self.filter_year.get().strip()
        
        filtered = self.movies.copy()
        
        if genre_filter:
            filtered = [m for m in filtered if genre_filter in m["genre"].lower()]
        
        if year_filter:
            try:
                year_int = int(year_filter)
                filtered = [m for m in filtered if m["year"] == year_int]
            except ValueError:
                messagebox.showwarning("Ошибка", "Год фильтрации должен быть числом!")
                return
        
        self.display_movies(filtered)
    
    def reset_filter(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.refresh_table()
    
    def refresh_table(self):
        self.display_movies(self.movies)
    
    def display_movies(self, movies):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for movie in movies:
            self.tree.insert("", tk.END, values=(
                movie["id"],
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.movies = json.load(f)
            except:
                self.movies = []
        else:
            self.movies = []


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

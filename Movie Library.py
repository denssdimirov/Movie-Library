"""
Movie Library Application
Author: Денис Сидимиров
Description: GUI-приложение для хранения информации о фильмах с фильтрацией
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "movie_library.json"
        
        # Список фильмов
        self.movies = []
        
        # Загрузка существующих данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === Форма ввода ===
        input_frame = ttk.LabelFrame(main_frame, text="Добавление фильма", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.genre_entry = ttk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(input_frame, text="Год выпуска:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.rating_entry = ttk.Entry(input_frame, width=10)
        self.rating_entry.grid(row=1, column=3, sticky=tk.W, pady=(5, 0))
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        self.add_button.grid(row=0, column=4, rowspan=2, padx=(20, 0), pady=(5, 5))
        
        # === Фильтрация ===
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.filter_genre_entry = ttk.Entry(filter_frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(filter_frame, text="Фильтр по году:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.filter_year_entry = ttk.Entry(filter_frame, width=10)
        self.filter_year_entry.grid(row=0, column=3, padx=(0, 20))
        
        self.filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_button.grid(row=0, column=4, padx=(0, 10))
        
        self.reset_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_button.grid(row=0, column=5)
        
        # === Таблица фильмов ===
        table_frame = ttk.LabelFrame(main_frame, text="Список фильмов", padding="10")
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создание таблицы
        columns = ("ID", "Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        
        self.tree.column("ID", width=50)
        self.tree.column("Название", width=250)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=80)
        self.tree.column("Рейтинг", width=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопка удаления
        self.delete_button = ttk.Button(table_frame, text="Удалить выбранный фильм", command=self.delete_movie)
        self.delete_button.grid(row=1, column=0, pady=(10, 0))
        
        # Настройка веса для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def validate_movie_data(self, title, genre, year, rating):
        """Валидация данных фильма"""
        if not title or not title.strip():
            return False, "Название фильма не может быть пустым!"
        
        if not genre or not genre.strip():
            return False, "Жанр не может быть пустым!"
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            if year_int < 1888 or year_int > current_year:
                return False, f"Год должен быть между 1888 и {current_year}!"
        except ValueError:
            return False, "Год должен быть целым числом!"
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                return False, "Рейтинг должен быть от 0 до 10!"
        except ValueError:
            return False, "Рейтинг должен быть числом!"
        
        return True, "OK"
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        # Валидация
        is_valid, message = self.validate_movie_data(title, genre, year, rating)
        if not is_valid:
            messagebox.showerror("Ошибка ввода", message)
            return
        
        # Создание ID
        movie_id = max([m["id"] for m in self.movies], default=0) + 1
        
        # Добавление фильма
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
        
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Фильм '{title}' успешно добавлен!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
            return
        
        # Получение ID фильма
        item = self.tree.item(selected[0])
        movie_id = item['values'][0]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            self.movies = [m for m in self.movies if m["id"] != movie_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Фильм удалён!")
    
    def apply_filter(self):
        """Применение фильтрации"""
        genre_filter = self.filter_genre_entry.get().strip().lower()
        year_filter = self.filter_year_entry.get().strip()
        
        filtered_movies = self.movies.copy()
        
        if genre_filter:
            filtered_movies = [m for m in filtered_movies if genre_filter in m["genre"].lower()]
        
        if year_filter:
            try:
                year_int = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m["year"] == year_int]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Год для фильтрации должен быть числом!")
                return
        
        self.display_movies(filtered_movies)
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_year_entry.delete(0, tk.END)
        self.refresh_table()
    
    def refresh_table(self):
        """Обновление таблицы со всеми фильмами"""
        self.display_movies(self.movies)
    
    def display_movies(self, movies):
        """Отображение фильмов в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление фильмов
        for movie in movies:
            self.tree.insert("", tk.END, values=(
                movie["id"],
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.movies = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.movies = []
        else:
            self.movies = []


def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()


if __name__ == "__main__":
    main()
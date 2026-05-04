"""
Movie Library Application - Личная кинотека
Author: Иван Петров
Version: 1.0
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
        self.root.geometry("1000x650")
        self.root.resizable(True, True)
        
        # Настройка стилей
        style = ttk.Style()
        style.theme_use('clam')
        
        # Файл для хранения данных
        self.data_file = "movie_library.json"
        
        # Список фильмов
        self.movies = []
        
        # Флаг фильтрации
        self.is_filtered = False
        self.filtered_movies = []
        
        # Загрузка существующих данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
        
        # Настройка обработчиков событий
        self.setup_bindings()
    
    def setup_bindings(self):
        """Настройка привязки клавиш"""
        self.root.bind('<Return>', lambda e: self.add_movie())
        self.root.bind('<Delete>', lambda e: self.delete_movie())
        self.filter_genre_entry.bind('<KeyRelease>', lambda e: self.auto_filter())
        self.filter_year_entry.bind('<KeyRelease>', lambda e: self.auto_filter())
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер с прокруткой
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === Форма ввода ===
        input_frame = ttk.LabelFrame(self.scrollable_frame, text="➕ Добавление нового фильма", padding="15")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Создание сетки для полей ввода
        grid_frame = ttk.Frame(input_frame)
        grid_frame.pack(fill="x")
        
        # Название
        ttk.Label(grid_frame, text="Название:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(grid_frame, width=35, font=('Arial', 10))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        self.title_entry.focus()
        
        # Жанр
        ttk.Label(grid_frame, text="Жанр:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.genre_entry = ttk.Entry(grid_frame, width=25, font=('Arial', 10))
        self.genre_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Год
        ttk.Label(grid_frame, text="Год выпуска:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.year_entry = ttk.Entry(grid_frame, width=15, font=('Arial', 10))
        self.year_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Рейтинг
        ttk.Label(grid_frame, text="Рейтинг (0-10):", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.rating_entry = ttk.Entry(grid_frame, width=15, font=('Arial', 10))
        self.rating_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_button = tk.Button(grid_frame, text="🎬 Добавить фильм", bg='#4CAF50', fg='white', 
                                   font=('Arial', 11, 'bold'), padx=20, pady=5,
                                   command=self.add_movie)
        self.add_button.grid(row=0, column=4, rowspan=2, padx=20, pady=5)
        
        # Статусная строка
        self.status_label = ttk.Label(self.scrollable_frame, text="✅ Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill="x", padx=10, pady=5)
        
        # === Фильтрация ===
        filter_frame = ttk.LabelFrame(self.scrollable_frame, text="🔍 Фильтрация коллекции", padding="15")
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        filter_grid = ttk.Frame(filter_frame)
        filter_grid.pack(fill="x")
        
        ttk.Label(filter_grid, text="Фильтр по жанру:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_genre_entry = ttk.Entry(filter_grid, width=30, font=('Arial', 10))
        self.filter_genre_entry.grid(row=0, column=1, padx=5)
        self.filter_genre_entry.insert(0, "Введите жанр...")
        self.filter_genre_entry.bind('<FocusIn>', self.on_filter_genre_focus)
        self.filter_genre_entry.bind('<FocusOut>', self.on_filter_genre_blur)
        
        ttk.Label(filter_grid, text="Фильтр по году:", font=('Arial', 10)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filter_year_entry = ttk.Entry(filter_grid, width=15, font=('Arial', 10))
        self.filter_year_entry.grid(row=0, column=3, padx=5)
        self.filter_year_entry.insert(0, "Год...")
        self.filter_year_entry.bind('<FocusIn>', self.on_filter_year_focus)
        self.filter_year_entry.bind('<FocusOut>', self.on_filter_year_blur)
        
        button_frame = ttk.Frame(filter_grid)
        button_frame.grid(row=0, column=4, padx=20)
        
        self.filter_button = tk.Button(button_frame, text="🔍 Применить фильтр", bg='#2196F3', fg='white',
                                      font=('Arial', 10), command=self.apply_filter)
        self.filter_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(button_frame, text="🔄 Сбросить фильтр", bg='#FF9800', fg='white',
                                     font=('Arial', 10), command=self.reset_filter)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Информация о количестве
        self.filter_info_label = ttk.Label(filter_frame, text="", font=('Arial', 9, 'italic'))
        self.filter_info_label.pack(anchor=tk.W, pady=(10, 0))
        
        # === Таблица фильмов ===
        table_frame = ttk.LabelFrame(self.scrollable_frame, text="📋 Список фильмов", padding="10")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Создание таблицы
        columns = ("ID", "Название", "Жанр", "Год", "Рейтинг", "Оценка")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20, selectmode="extended")
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название фильма")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        self.tree.heading("Оценка", text="Оценка")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Название", width=300)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=80, anchor="center")
        self.tree.column("Рейтинг", width=80, anchor="center")
        self.tree.column("Оценка", width=100, anchor="center")
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Кнопки управления таблицей
        control_frame = ttk.Frame(table_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.delete_button = tk.Button(control_frame, text="🗑️ Удалить выбранные фильмы", bg='#f44336', fg='white',
                                      font=('Arial', 10), command=self.delete_movie)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(control_frame, text="🗑️ Очистить всю коллекцию", bg='#9E9E9E', fg='white',
                                     font=('Arial', 10), command=self.clear_all_movies)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = tk.Button(control_frame, text="🔄 Обновить", bg='#607D8B', fg='white',
                                       font=('Arial', 10), command=self.refresh_table)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Настройка веса для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_canvas.columnconfigure(0, weight=1)
        main_canvas.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def on_filter_genre_focus(self, event):
        """Обработка фокуса поля фильтра жанра"""
        if self.filter_genre_entry.get() == "Введите жанр...":
            self.filter_genre_entry.delete(0, tk.END)
    
    def on_filter_genre_blur(self, event):
        """Обработка потери фокуса поля фильтра жанра"""
        if not self.filter_genre_entry.get():
            self.filter_genre_entry.insert(0, "Введите жанр...")
    
    def on_filter_year_focus(self, event):
        """Обработка фокуса поля фильтра года"""
        if self.filter_year_entry.get() == "Год...":
            self.filter_year_entry.delete(0, tk.END)
    
    def on_filter_year_blur(self, event):
        """Обработка потери фокуса поля фильтра года"""
        if not self.filter_year_entry.get():
            self.filter_year_entry.insert(0, "Год...")
    
    def auto_filter(self):
        """Автоматическая фильтрация при вводе"""
        genre = self.filter_genre_entry.get()
        year = self.filter_year_entry.get()
        
        if genre and genre != "Введите жанр..." or year and year != "Год...":
            self.apply_filter()
    
    def validate_movie_data(self, title, genre, year, rating):
        """Валидация данных фильма"""
        if not title or not title.strip():
            return False, "❌ Ошибка: Название фильма не может быть пустым!"
        
        if len(title) > 100:
            return False, "❌ Ошибка: Название не должно превышать 100 символов!"
        
        if not genre or not genre.strip():
            return False, "❌ Ошибка: Жанр не может быть пустым!"
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            if year_int < 1888:
                return False, f"❌ Ошибка: Год должен быть не меньше 1888 (первый фильм в истории)!"
            if year_int > current_year:
                return False, f"❌ Ошибка: Год не может быть больше {current_year}!"
        except ValueError:
            return False, "❌ Ошибка: Год должен быть целым числом!"
        
        try:
            rating_float = float(rating)
            if rating_float < 0:
                return False, "❌ Ошибка: Рейтинг не может быть меньше 0!"
            if rating_float > 10:
                return False, "❌ Ошибка: Рейтинг не может быть больше 10!"
        except ValueError:
            return False, "❌ Ошибка: Рейтинг должен быть числом (можно использовать точку)!"
        
        # Проверка на дубликат
        for movie in self.movies:
            if movie["title"].lower() == title.lower() and movie["year"] == year_int:
                return False, f"❌ Ошибка: Фильм '{title}' ({year_int}) уже существует в коллекции!"
        
        return True, "✅ Данные валидны"
    
    def get_rating_stars(self, rating):
        """Получение звёздного рейтинга"""
        full_stars = int(rating // 1)
        half_star = 1 if rating % 1 >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars = "★" * full_stars + "½" * half_star + "☆" * empty_stars
        return stars
    
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
            self.status_label.config(text=message, foreground='red')
            return
        
        # Создание ID
        movie_id = max([m["id"] for m in self.movies], default=0) + 1
        
        # Добавление фильма
        rating_float = float(rating)
        movie = {
            "id": movie_id,
            "title": title,
            "genre": genre,
            "year": int(year),
            "rating": rating_float,
            "stars": self.get_rating_stars(rating_float)
        }
        
        self.movies.append(movie)
        self.save_data()
        
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
        self.title_entry.focus()
        
        # Обновление отображения
        if not self.is_filtered:
            self.refresh_table()
        else:
            self.apply_filter()
        
        self.status_label.config(text=f"✅ Фильм '{title}' успешно добавлен!", foreground='green')
        messagebox.showinfo("Успех", f"🎉 Фильм '{title}' успешно добавлен в коллекцию!")
    
    def delete_movie(self):
        """Удаление выбранных фильмов"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "⚠️ Выберите фильм(ы) для удаления!")
            return
        
        # Получение ID выбранных фильмов
        movie_ids = []
        for item in selected:
            movie_id = self.tree.item(item)['values'][0]
            movie_ids.append(movie_id)
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить {len(movie_ids)} фильм(ов)?"):
            self.movies = [m for m in self.movies if m["id"] not in movie_ids]
            self.save_data()
            
            if self.is_filtered:
                self.apply_filter()
            else:
                self.refresh_table()
            
            self.status_label.config(text=f"🗑️ Удалено {len(movie_ids)} фильм(ов)", foreground='orange')
            messagebox.showinfo("Успех", f"✅ {len(movie_ids)} фильм(ов) удалено!")
    
    def clear_all_movies(self):
        """Очистка всей коллекции"""
        if not self.movies:
            messagebox.showinfo("Информация", "Коллекция уже пуста!")
            return
        
        if messagebox.askyesno("Подтверждение", "⚠️ ВНИМАНИЕ! Вы уверены, что хотите удалить ВСЕ фильмы? Это действие нельзя отменить!"):
            self.movies = []
            self.save_data()
            self.refresh_table()
            self.reset_filter()
            self.status_label.config(text="🗑️ Вся коллекция очищена", foreground='orange')
            messagebox.showinfo("Успех", "✅ Вся коллекция фильмов очищена!")
    
    def apply_filter(self):
        """Применение фильтрации"""
        genre_filter = self.filter_genre_entry.get().strip()
        year_filter = self.filter_year_entry.get().strip()
        
        # Проверка на плейсхолдеры
        if genre_filter == "Введите жанр...":
            genre_filter = ""
        if year_filter == "Год...":
            year_filter = ""
        
        filtered_movies = self.movies.copy()
        filter_description = []
        
        if genre_filter:
            filtered_movies = [m for m in filtered_movies if genre_filter.lower() in m["genre"].lower()]
            filter_description.append(f"жанр содержит '{genre_filter}'")
        
        if year_filter:
            try:
                year_int = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m["year"] == year_int]
                filter_description.append(f"год = {year_int}")
            except ValueError:
                if year_filter:
                    self.status_label.config(text="⚠️ Год для фильтрации должен быть числом!", foreground='red')
                    return
        
        self.filtered_movies = filtered_movies
        self.is_filtered = True
        self.display_movies(filtered_movies)
        
        if filter_description:
            filter_text = "Фильтр: " + ", ".join(filter_description)
            self.filter_info_label.config(text=f"{filter_text} | Найдено: {len(filtered_movies)} фильм(ов)")
        else:
            self.filter_info_label.config(text="")
        
        self.status_label.config(text=f"🔍 Применён фильтр | Найдено: {len(filtered_movies)} фильм(ов)", foreground='blue')
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_genre_entry.insert(0, "Введите жанр...")
        self.filter_year_entry.delete(0, tk.END)
        self.filter_year_entry.insert(0, "Год...")
        self.is_filtered = False
        self.refresh_table()
        self.filter_info_label.config(text="")
        self.status_label.config(text="🔄 Фильтр сброшен", foreground='green')
    
    def refresh_table(self):
        """Обновление таблицы со всеми фильмами"""
        self.display_movies(self.movies)
        self.status_label.config(text=f"📊 Всего фильмов в коллекции: {len(self.movies)}", foreground='blue')
    
    def display_movies(self, movies):
        """Отображение фильмов в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Сортировка по ID
        movies_sorted = sorted(movies, key=lambda x: x["id"])
        
        # Добавление фильмов
        for movie in movies_sorted:
            rating_value = movie["rating"]
            stars = self.get_rating_stars(rating_value)
            
            # Цветовая индикация рейтинга
            if rating_value >= 8:
                rating_color = "🟢"
            elif rating_value >= 6:
                rating_color = "🟡"
            else:
                rating_color = "🔴"
            
            self.tree.insert("", tk.END, values=(
                movie["id"],
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{rating_value:.1f}",
                f"{rating_color} {stars}"
            ))
        
        # Альтернативная раскраска строк
        for i, item in enumerate(self.tree.get_children()):
            if i % 2 == 0:
                self.tree.tag_configure('evenrow', background='#f0f0f0')
                self.tree.item(item, tags=('evenrow',))
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            # Создаём копию без поля stars для сохранения
            movies_to_save = []
            for movie in self.movies:
                movie_copy = movie.copy()
                if 'stars' in movie_copy:
                    del movie_copy['stars']
                movies_to_save.append(movie_copy)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(movies_to_save, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Не удалось сохранить данные: {str(e)}")
            return False
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_movies = json.load(f)
                    # Восстанавливаем поле stars
                    self.movies = []
                    for movie in loaded_movies:
                        movie['stars'] = self.get_rating_stars(movie['rating'])
                        self.movies.append(movie)
                return True
            except Exception as e:
                messagebox.showerror("Ошибка", f"❌ Не удалось загрузить данные: {str(e)}")
                self.movies = []
                return False
        else:
            # Создаём примеры фильмов при первом запуске
            self.movies = []
            self.add_sample_movies()
            return True
    
    def add_sample_movies(self):
        """Добавление примеров фильмов при первом запуске"""
        sample_movies = [
            {"id": 1, "title": "Побег из Шоушенка", "genre": "Драма", "year": 1994, "rating": 9.3},
            {"id": 2, "title": "Крёстный отец", "genre": "Драма", "year": 1972, "rating": 9.2},
            {"id": 3, "title": "Тёмный рыцарь", "genre": "Боевик", "year": 2008, "rating": 9.0},
            {"id": 4, "title": "Криминальное чтиво", "genre": "Криминал", "year": 1994, "rating": 8.9},
            {"id": 5, "title": "Властелин колец: Возвращение короля", "genre": "Фэнтези", "year": 2003, "rating": 9.0},
            {"id": 6, "title": "Форрест Гамп", "genre": "Драма", "year": 1994, "rating": 8.8},
            {"id": 7, "title": "Начало", "genre": "Фантастика", "year": 2010, "rating": 8.8},
            {"id": 8, "title": "Матрица", "genre": "Фантастика", "year": 1999, "rating": 8.7},
        ]
        
        for movie in sample_movies:
            movie['stars'] = self.get_rating_stars(movie['rating'])
            self.movies.append(movie)
        
        self.save_data()


def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import configparser
import os
import random
import re
import sys
import time
from datetime import datetime

# Workaround for PyInstaller onefile mode with customtkinter
application_path = ''
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(application_path)
sys.path.append(application_path)

# Импорт для FunPay API
try:
    import FunPayAPI
    from FunPayAPI.common import exceptions
    from FunPayAPI.types import OrderStatuses as OrderState
except ImportError:
    pass  # Обработаем в GUI

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    MODERN_GUI = True
except ImportError:
    MODERN_GUI = False

CONFIG_FILE = "config.ini"

class FunPayKeyChecker:
    def __init__(self):
        self.root = ctk.CTk() if MODERN_GUI else tk.Tk()
        self.root.title("FunPay Key Checker v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)  # Минимальный размер
        
        # Устанавливаем иконку для окна программы
        self.setup_icon()
        
        if not MODERN_GUI:
            self.root.configure(bg='#2b2b2b')
        
        self.account = None
        self.is_running = False
        self.is_paused = False
        self.all_sold_keys = []
        
        self.setup_gui()
        self.load_config()
    
    def setup_icon(self):
        """Настройка иконки для окна программы"""
        try:
            # Создаем иконку если её нет
            if not os.path.exists("icon.ico"):
                self.create_icon_programmatically()
            
            # Устанавливаем иконку только если файл существует
            if os.path.exists("icon.ico"):
                try:
                    self.root.iconbitmap("icon.ico")
                except Exception as e:
                    print(f"Предупреждение: не удалось установить иконку .ico: {e}")
                    
            # Альтернативный способ через PNG
            if os.path.exists("icon_32x32.png"):
                try:
                    icon_photo = tk.PhotoImage(file="icon_32x32.png")
                    self.root.iconphoto(True, icon_photo)
                    self.icon_photo = icon_photo  # Сохраняем ссылку
                except Exception as e:
                    print(f"Предупреждение: не удалось установить иконку .png: {e}")
                    
        except Exception as e:
            print(f"Предупреждение: проблемы с иконкой: {e}")
    
    def force_icon_update(self):
        """Принудительное обновление иконки после создания GUI"""
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
            if os.path.exists("icon_32x32.png"):
                icon_photo = tk.PhotoImage(file="icon_32x32.png")
                self.root.iconphoto(True, icon_photo)
                self.icon_photo = icon_photo
        except:
            pass
    
    def create_icon_programmatically(self):
        """Создание иконки программно если файла нет"""
        try:
            from PIL import Image, ImageDraw
            
            # Создаем простую иконку 32x32
            size = 32
            img = Image.new('RGB', (size, size), (30, 144, 255))  # Синий фон
            draw = ImageDraw.Draw(img)
            
            # Простой белый ключ
            key_color = (255, 255, 255)
            
            # Основа ключа (горизонтальная линия)
            draw.rectangle([8, 14, 24, 18], fill=key_color)
            
            # Головка ключа (круг)
            draw.ellipse([6, 10, 16, 20], fill=key_color)
            draw.ellipse([8, 12, 14, 18], fill=(30, 144, 255))  # Отверстие
            
            # Зубцы
            draw.rectangle([20, 14, 24, 12], fill=key_color)
            draw.rectangle([20, 18, 24, 20], fill=key_color)
            
            # Сохраняем как ICO и PNG
            img.save('icon.ico', format='ICO', sizes=[(32, 32), (16, 16)])
            img.save('icon_32x32.png', format='PNG')
            
        except ImportError:
            print("PIL не установлен, иконка не создана")
        except Exception as e:
            print(f"Ошибка создания иконки: {e}")
        
    def setup_gui(self):
        """Создание интерфейса"""
        # Главный контейнер
        if MODERN_GUI:
            self.main_frame = ctk.CTkFrame(self.root)
            self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Создаем вкладки
            self.tabview = ctk.CTkTabview(self.main_frame)
            self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Вкладки
            self.tab_settings = self.tabview.add("⚙️ Настройки")
            self.tab_analysis = self.tabview.add("🔍 Анализ")
            self.tab_results = self.tabview.add("📊 Результаты")
        else:
            # Fallback для обычного tkinter
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.tab_settings = ttk.Frame(self.notebook)
            self.tab_analysis = ttk.Frame(self.notebook)
            self.tab_results = ttk.Frame(self.notebook)
            
            self.notebook.add(self.tab_settings, text="⚙️ Настройки")
            self.notebook.add(self.tab_analysis, text="🔍 Анализ")
            self.notebook.add(self.tab_results, text="📊 Результаты")
        
        self.setup_settings_tab()
        self.setup_analysis_tab()
        self.setup_results_tab()
        
    def setup_settings_tab(self):
        """Вкладка настроек"""
        if MODERN_GUI:
            # Заголовок
            title = ctk.CTkLabel(self.tab_settings, text="Настройки FunPay API", 
                               font=ctk.CTkFont(size=20, weight="bold"))
            title.pack(pady=10)
            
            # Основные настройки
            settings_frame = ctk.CTkFrame(self.tab_settings)
            settings_frame.pack(fill="x", padx=20, pady=10)
            
            # Golden Key
            ctk.CTkLabel(settings_frame, text="Golden Key:", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
            self.golden_key_entry = ctk.CTkEntry(settings_frame, width=700, show="*")
            self.golden_key_entry.pack(padx=20, pady=(0,10))
            
            # User Agent
            ctk.CTkLabel(settings_frame, text="User Agent:", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10,5))
            self.user_agent_entry = ctk.CTkEntry(settings_frame, width=700)
            self.user_agent_entry.pack(padx=20, pady=(0,20))
            
            # Настройки безопасности
            safety_frame = ctk.CTkFrame(self.tab_settings)
            safety_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(safety_frame, text="Настройки безопасности", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            # Задержки
            delay_frame = ctk.CTkFrame(safety_frame)
            delay_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(delay_frame, text="Минимальная задержка (сек):").pack(side="left", padx=10)
            self.min_delay_var = tk.StringVar(value="2")
            self.min_delay_entry = ctk.CTkEntry(delay_frame, textvariable=self.min_delay_var, width=100)
            self.min_delay_entry.pack(side="left", padx=10)
            
            ctk.CTkLabel(delay_frame, text="Максимальная задержка (сек):").pack(side="left", padx=10)
            self.max_delay_var = tk.StringVar(value="5")
            self.max_delay_entry = ctk.CTkEntry(delay_frame, textvariable=self.max_delay_var, width=100)
            self.max_delay_entry.pack(side="left", padx=10)
            
            # Лимиты
            limits_frame = ctk.CTkFrame(safety_frame)
            limits_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(limits_frame, text="Лимит заказов для анализа (0 = без лимита):").pack(side="left", padx=10)
            self.order_limit_var = tk.StringVar(value="0")
            self.order_limit_entry = ctk.CTkEntry(limits_frame, textvariable=self.order_limit_var, width=100)
            self.order_limit_entry.pack(side="left", padx=10)
            
            # Лимит страниц
            pages_frame = ctk.CTkFrame(safety_frame)
            pages_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(pages_frame, text="Лимит страниц для загрузки (0 = без лимита):").pack(side="left", padx=10)
            self.page_limit_var = tk.StringVar(value="0")
            self.page_limit_entry = ctk.CTkEntry(pages_frame, textvariable=self.page_limit_var, width=100)
            self.page_limit_entry.pack(side="left", padx=10)
            
            ctk.CTkLabel(pages_frame, text="(1 страница ≈ 100 заказов)").pack(side="left", padx=10)
            
            # Кнопки
            buttons_frame = ctk.CTkFrame(self.tab_settings)
            buttons_frame.pack(fill="x", padx=20, pady=20)
            
            self.save_config_btn = ctk.CTkButton(buttons_frame, text="💾 Сохранить настройки", 
                                               command=self.save_config)
            self.save_config_btn.pack(side="left", padx=10)
            
            self.test_connection_btn = ctk.CTkButton(buttons_frame, text="🔗 Тест подключения", 
                                                   command=self.test_connection)
            self.test_connection_btn.pack(side="left", padx=10)
        
    def setup_analysis_tab(self):
        """Вкладка анализа"""
        if MODERN_GUI:
            # Заголовок
            title = ctk.CTkLabel(self.tab_analysis, text="Анализ проданных ключей", 
                               font=ctk.CTkFont(size=20, weight="bold"))
            title.pack(pady=10)
            
            # Форма ввода
            input_frame = ctk.CTkFrame(self.tab_analysis)
            input_frame.pack(fill="x", padx=20, pady=10)
            
            # Game ID
            ctk.CTkLabel(input_frame, text="ID игры:", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
            self.game_id_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="Например: 1234")
            self.game_id_entry.pack(padx=20, pady=(0,10))
            
            # Название лота
            ctk.CTkLabel(input_frame, text="Название лота:", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10,5))
            self.lot_name_entry = ctk.CTkEntry(input_frame, width=600, placeholder_text="Точное название лота")
            self.lot_name_entry.pack(padx=20, pady=(0,20))
            
            # Прогресс
            progress_frame = ctk.CTkFrame(self.tab_analysis)
            progress_frame.pack(fill="x", padx=20, pady=10)
            
            self.progress_label = ctk.CTkLabel(progress_frame, text="Готов к анализу")
            self.progress_label.pack(pady=10)
            
            self.progress_bar = ctk.CTkProgressBar(progress_frame, width=700)
            self.progress_bar.pack(pady=10)
            self.progress_bar.set(0)
            
            # Лог
            self.log_text = ctk.CTkTextbox(progress_frame, height=250, width=700)
            self.log_text.pack(pady=10, fill="both", expand=True)
            
            # Кнопки управления
            control_frame = ctk.CTkFrame(self.tab_analysis)
            control_frame.pack(fill="x", padx=20, pady=20)
            
            self.start_btn = ctk.CTkButton(control_frame, text="🚀 Начать анализ", 
                                         command=self.start_analysis, 
                                         font=ctk.CTkFont(size=14, weight="bold"))
            self.start_btn.pack(side="left", padx=10)
            
            self.stop_btn = ctk.CTkButton(control_frame, text="⏹️ Остановить", 
                                        command=self.stop_analysis, state="disabled")
            self.stop_btn.pack(side="left", padx=10)
            
            self.pause_btn = ctk.CTkButton(control_frame, text="⏸️ Пауза", 
                                         command=self.pause_analysis, state="disabled")
            self.pause_btn.pack(side="left", padx=10)
            
            self.clear_log_btn = ctk.CTkButton(control_frame, text="🗑️ Очистить лог", 
                                             command=self.clear_log)
            self.clear_log_btn.pack(side="right", padx=10)
    
    def setup_results_tab(self):
        """Вкладка результатов"""
        if MODERN_GUI:
            # Заголовок
            title = ctk.CTkLabel(self.tab_results, text="Результаты анализа", 
                               font=ctk.CTkFont(size=20, weight="bold"))
            title.pack(pady=10)
            
            # Статистика
            stats_frame = ctk.CTkFrame(self.tab_results)
            stats_frame.pack(fill="x", padx=20, pady=10)
            
            self.stats_label = ctk.CTkLabel(stats_frame, text="Статистика появится после анализа", 
                                          font=ctk.CTkFont(size=14))
            self.stats_label.pack(pady=20)
            
            # Таблица ключей (используем Treeview)
            table_frame = ctk.CTkFrame(self.tab_results)
            table_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Создаем Treeview для таблицы
            columns = ("№", "Ключ", "Заказ", "Дата")
            self.keys_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            # Настройка колонок
            self.keys_tree.heading("№", text="№")
            self.keys_tree.heading("Ключ", text="Ключ")
            self.keys_tree.heading("Заказ", text="ID Заказа")
            self.keys_tree.heading("Дата", text="Дата")
            
            self.keys_tree.column("№", width=50)
            self.keys_tree.column("Ключ", width=300)
            self.keys_tree.column("Заказ", width=150)
            self.keys_tree.column("Дата", width=150)
            
            # Скроллбар для таблицы
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.keys_tree.yview)
            self.keys_tree.configure(yscrollcommand=scrollbar.set)
            
            self.keys_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Кнопки экспорта
            export_frame = ctk.CTkFrame(self.tab_results)
            export_frame.pack(fill="x", padx=20, pady=20)
            
            self.export_all_btn = ctk.CTkButton(export_frame, text="📄 Экспорт всех ключей", 
                                              command=self.export_all_keys)
            self.export_all_btn.pack(side="left", padx=10)
            
            self.export_unique_btn = ctk.CTkButton(export_frame, text="🔑 Экспорт уникальных", 
                                                 command=self.export_unique_keys)
            self.export_unique_btn.pack(side="left", padx=10)
            
            self.export_duplicates_btn = ctk.CTkButton(export_frame, text="👥 Экспорт дубликатов", 
                                                     command=self.export_duplicates)
            self.export_duplicates_btn.pack(side="left", padx=10)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        if MODERN_GUI:
            self.log_text.insert("end", formatted_message)
            self.log_text.see("end")
        
        self.root.update_idletasks()
    
    def clear_log(self):
        """Очистка лога"""
        if MODERN_GUI:
            self.log_text.delete("1.0", "end")
    
    def load_config(self):
        """Загрузка конфигурации"""
        if os.path.exists(CONFIG_FILE):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE, encoding="utf-8")
            
            try:
                if MODERN_GUI:
                    # Загружаем Golden Key
                    golden_key = config.get("FunPay", "golden_key", fallback="")
                    if golden_key:
                        self.golden_key_entry.insert(0, golden_key)
                    
                    # Загружаем User Agent
                    user_agent = config.get("FunPay", "user_agent", fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    self.user_agent_entry.insert(0, user_agent)
                    
                    # Загружаем настройки безопасности
                    self.min_delay_var.set(config.get("Safety", "min_delay_sec", fallback="2"))
                    self.max_delay_var.set(config.get("Safety", "max_delay_sec", fallback="5"))
                    self.order_limit_var.set(config.get("Safety", "order_limit", fallback="0"))
                    self.page_limit_var.set(config.get("Safety", "page_limit", fallback="0"))
                    
            except Exception as e:
                self.log_message(f"Ошибка при загрузке конфигурации: {e}")
        else:
            # Устанавливаем значения по умолчанию
            if MODERN_GUI:
                self.user_agent_entry.insert(0, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    def save_config(self):
        """Сохранение конфигурации"""
        config = configparser.ConfigParser()
        
        if MODERN_GUI:
            config["FunPay"] = {
                "golden_key": self.golden_key_entry.get(),
                "user_agent": self.user_agent_entry.get()
            }
            config["Safety"] = {
                "min_delay_sec": self.min_delay_var.get(),
                "max_delay_sec": self.max_delay_var.get(),
                "order_limit": self.order_limit_var.get(),
                "page_limit": self.page_limit_var.get()
            }
        
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as configfile:
                config.write(configfile)
            messagebox.showinfo("Успех", "Настройки сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def test_connection(self):
        """Тест подключения к FunPay"""
        def test_thread():
            try:
                self.log_message("Тестирование подключения...")
                
                if MODERN_GUI:
                    golden_key = self.golden_key_entry.get().strip()
                    user_agent = self.user_agent_entry.get().strip()
                
                if not golden_key or "ВАШ_GOLDEN_KEY_СЮДА" in golden_key:
                    self.log_message("❌ Ошибка: Укажите корректный Golden Key")
                    return
                
                # Очищаем User-Agent от недопустимых символов
                user_agent_clean = user_agent.encode('ascii', 'ignore').decode('ascii')
                if not user_agent_clean:
                    user_agent_clean = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                
                self.log_message(f"🔑 Используется Golden Key: {golden_key[:10]}...")
                self.log_message(f"🌐 User Agent: {user_agent_clean[:50]}...")
                
                account = FunPayAPI.Account(golden_key=golden_key, user_agent=user_agent_clean)
                account.get()
                
                self.log_message(f"✅ Подключение успешно! Пользователь: {account.username} (ID: {account.id})")
                self.account = account
                
            except exceptions.UnauthorizedError:
                self.log_message("❌ Ошибка: Неверный Golden Key или проблемы с авторизацией")
            except UnicodeEncodeError as e:
                self.log_message(f"❌ Ошибка кодировки User-Agent: {e}")
                self.log_message("💡 Попробуйте использовать стандартный User-Agent без специальных символов")
            except Exception as e:
                self.log_message(f"❌ Ошибка подключения: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def start_analysis(self):
        """Запуск анализа"""
        if not self.account:
            messagebox.showwarning("Предупреждение", "Сначала протестируйте подключение!")
            return
        
        game_id = self.game_id_entry.get().strip()
        lot_name = self.lot_name_entry.get().strip()
        
        if not game_id or not lot_name:
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return
        
        try:
            game_id = int(game_id)
        except ValueError:
            messagebox.showerror("Ошибка", "ID игры должен быть числом!")
            return
        
        self.is_running = True
        self.is_paused = False
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.pause_btn.configure(state="normal")
        self.all_sold_keys = []
        
        # Очищаем таблицу результатов
        for item in self.keys_tree.get_children():
            self.keys_tree.delete(item)
        
        def analysis_thread():
            try:
                self.run_analysis(game_id, lot_name)
            except Exception as e:
                self.log_message(f"❌ Критическая ошибка: {e}")
            finally:
                self.is_running = False
                self.is_paused = False
                self.start_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled")
                self.pause_btn.configure(state="disabled")
                self.progress_bar.set(0)
        
        threading.Thread(target=analysis_thread, daemon=True).start()
    
    def stop_analysis(self):
        """Остановка анализа"""
        self.is_running = False
        self.is_paused = False
        self.log_message("🛑 Анализ остановлен пользователем")
    
    def pause_analysis(self):
        """Пауза/возобновление анализа"""
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.configure(text="⏸️ Пауза")
            self.log_message("▶️ Анализ возобновлен")
        else:
            self.is_paused = True
            self.pause_btn.configure(text="▶️ Продолжить")
            self.log_message("⏸️ Анализ приостановлен")
    
    def run_analysis(self, game_id, lot_name):
        """Основная логика анализа"""
        try:
            # Проверяем, что аккаунт инициализирован
            if not self.account:
                self.log_message("❌ Ошибка: Аккаунт не инициализирован. Сначала протестируйте подключение!")
                return
            
            # Получение настроек
            min_delay = float(self.min_delay_var.get())
            max_delay = float(self.max_delay_var.get())
            order_limit = int(self.order_limit_var.get()) if self.order_limit_var.get() != "0" else None
            page_limit = int(self.page_limit_var.get()) if self.page_limit_var.get() != "0" else None
            
            self.log_message(f"🔍 Начинаю поиск заказов для игры ID: {game_id}")
            self.log_message(f"📦 Лот: {lot_name}")
            if page_limit:
                self.log_message(f"📄 Лимит страниц: {page_limit} (≈ {page_limit * 100} заказов)")
            if order_limit:
                self.log_message(f"🔢 Лимит заказов для анализа: {order_limit}")
            
            # Сбор заказов
            all_orders = []
            start_from = None
            page_num = 1
            
            while self.is_running:
                # Проверка паузы
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    break
                self.log_message(f"📄 Загружаю страницу {page_num}...")
                
                try:
                    next_start_from, orders_batch = self.account.get_sells(
                        start_from=start_from,
                        game=game_id,
                        state="closed",
                        include_paid=False,
                        include_refunded=False
                    )
                    
                    if not orders_batch:
                        self.log_message("ℹ️ Больше заказов не найдено")
                        break
                    
                    all_orders.extend(orders_batch)
                    self.log_message(f"✅ Загружено {len(orders_batch)} заказов (всего: {len(all_orders)})")
                    
                    if not next_start_from:
                        self.log_message("ℹ️ Достигнут конец списка заказов")
                        break
                    
                    # Проверяем лимит страниц
                    if page_limit and page_num >= page_limit:
                        self.log_message(f"⚠️ Достигнут лимит страниц: {page_limit}")
                        break
                    
                    start_from = next_start_from
                    page_num += 1
                    
                    # Задержка с отображением
                    delay = random.uniform(min_delay, max_delay)
                    self.log_message(f"⏳ Задержка {delay:.1f} сек...")
                    time.sleep(delay)
                    
                except exceptions.RequestFailedError as e:
                    self.log_message(f"❌ Ошибка запроса на странице {page_num}: {e}")
                    self.log_message("⏳ Увеличиваю задержку и повторяю...")
                    time.sleep(min_delay * 2)
                    continue
                    
                except Exception as e:
                    self.log_message(f"❌ Неожиданная ошибка на странице {page_num}: {e}")
                    break
            
            if not self.is_running:
                return
            
            # Фильтрация по названию лота
            self.log_message(f"🔎 Фильтрую заказы по названию лота...")
            target_orders = []
            
            for order in all_orders:
                if not self.is_running:
                    return
                
                description = getattr(order, 'description', '')
                if lot_name in description:
                    target_orders.append(order)
                    
                    if order_limit and len(target_orders) >= order_limit:
                        self.log_message(f"⚠️ Достигнут лимит заказов: {order_limit}")
                        break
            
            if not target_orders:
                self.log_message("❌ Заказы с указанным названием лота не найдены")
                return
            
            self.log_message(f"✅ Найдено {len(target_orders)} подходящих заказов")
            
            # Анализ заказов
            processed = 0
            for order_header in target_orders:
                # Проверка паузы
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    return
                
                processed += 1
                progress = processed / len(target_orders)
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"Обработка заказа {processed}/{len(target_orders)}")
                
                self.log_message(f"🔍 Анализ заказа {order_header.id} ({processed}/{len(target_orders)})")
                
                try:
                    # Задержка перед запросом
                    delay = random.uniform(min_delay, max_delay)
                    time.sleep(delay)
                    
                    full_order = self.account.get_order(order_header.id)
                    if full_order and hasattr(full_order, 'html') and full_order.html:
                        keys = self.extract_keys_from_html(full_order.html)
                        
                        if keys:
                            self.log_message(f"✅ Найдено ключей: {len(keys)}")
                            for key in keys:
                                self.all_sold_keys.append({
                                    'key': key,
                                    'order_id': order_header.id,
                                    'date': getattr(order_header, 'created_at', 'Неизвестно')
                                })
                        else:
                            self.log_message("⚠️ Ключи не найдены в заказе")
                    else:
                        self.log_message("⚠️ Не удалось получить содержимое заказа")
                    
                except exceptions.RequestFailedError as e:
                    self.log_message(f"❌ Ошибка запроса заказа {order_header.id}: {e}")
                    # Увеличиваем задержку при ошибке
                    time.sleep(min_delay * 2)
                    
                except exceptions.UnauthorizedError:
                    self.log_message("❌ Ошибка авторизации. Проверьте Golden Key")
                    break
                    
                except Exception as e:
                    self.log_message(f"❌ Неожиданная ошибка при обработке заказа {order_header.id}: {e}")
            
            # Обновление результатов
            self.update_results()
            
            # Финальная статистика
            total_keys = len(self.all_sold_keys)
            unique_keys = len(set(k['key'] for k in self.all_sold_keys))
            duplicates = total_keys - unique_keys
            
            self.log_message(f"🎉 Анализ завершен!")
            self.log_message(f"📊 Всего ключей: {total_keys}")
            self.log_message(f"🔑 Уникальных: {unique_keys}")
            self.log_message(f"👥 Дубликатов: {duplicates}")
            self.log_message(f"📄 Обработано страниц: {page_num - 1}")
            self.log_message(f"📦 Найдено подходящих заказов: {len(target_orders)}")
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {e}")
    
    def extract_keys_from_html(self, html):
        """Извлечение ключей из HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            keys = []
            
            # Основной способ - поиск по классу secret-placeholder
            secret_elements = soup.find_all('span', class_='secret-placeholder')
            for element in secret_elements:
                key = element.get_text().strip()
                if key and len(key) > 5:  # Уменьшили минимальную длину
                    keys.append(key)
            
            # Дополнительный поиск - по другим возможным классам
            if not keys:
                # Поиск по другим классам, которые могут содержать ключи
                other_selectors = [
                    'span.secret',
                    'div.secret-placeholder',
                    'code',
                    'pre',
                    'span[style*="font-family: monospace"]'
                ]
                
                for selector in other_selectors:
                    elements = soup.select(selector)
                    for element in elements:
                        key = element.get_text().strip()
                        if key and len(key) > 5 and len(key) < 200:  # Разумные ограничения
                            keys.append(key)
            
            # Удаляем дубликаты, сохраняя порядок
            seen = set()
            unique_keys = []
            for key in keys:
                if key not in seen:
                    seen.add(key)
                    unique_keys.append(key)
            
            return unique_keys
            
        except Exception as e:
            print(f"Ошибка извлечения ключей: {e}")
            return []
    
    def update_results(self):
        """Обновление таблицы результатов"""
        # Очищаем таблицу
        for item in self.keys_tree.get_children():
            self.keys_tree.delete(item)
        
        # Добавляем ключи
        for i, key_data in enumerate(self.all_sold_keys, 1):
            self.keys_tree.insert("", "end", values=(
                i,
                key_data['key'],
                key_data['order_id'],
                key_data['date']
            ))
        
        # Обновляем статистику
        total_keys = len(self.all_sold_keys)
        unique_keys = len(set(k['key'] for k in self.all_sold_keys))
        duplicates = total_keys - unique_keys
        
        stats_text = f"📊 Всего ключей: {total_keys} | 🔑 Уникальных: {unique_keys} | 👥 Дубликатов: {duplicates}"
        self.stats_label.configure(text=stats_text)
    
    def export_all_keys(self):
        """Экспорт всех ключей"""
        if not self.all_sold_keys:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    for key_data in self.all_sold_keys:
                        f.write(f"{key_data['key']}\n")
                messagebox.showinfo("Успех", f"Экспортировано {len(self.all_sold_keys)} ключей!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def export_unique_keys(self):
        """Экспорт уникальных ключей"""
        if not self.all_sold_keys:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        unique_keys = list(set(k['key'] for k in self.all_sold_keys))
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    for key in unique_keys:
                        f.write(f"{key}\n")
                messagebox.showinfo("Успех", f"Экспортировано {len(unique_keys)} уникальных ключей!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def export_duplicates(self):
        """Экспорт дубликатов"""
        if not self.all_sold_keys:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        # Находим дубликаты
        seen = set()
        duplicates = []
        
        for key_data in self.all_sold_keys:
            key = key_data['key']
            if key in seen:
                duplicates.append(key)
            else:
                seen.add(key)
        
        if not duplicates:
            messagebox.showinfo("Информация", "Дубликатов не найдено!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    for key in set(duplicates):  # Убираем дубликаты дубликатов
                        f.write(f"{key}\n")
                messagebox.showinfo("Успех", f"Экспортировано {len(set(duplicates))} дубликатов!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

if __name__ == "__main__":
    # Проверка зависимостей
    try:
        import FunPayAPI
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"Ошибка: Не установлены необходимые библиотеки: {e}")
        print("Установите их командой: pip install FunPayAPI beautifulsoup4 customtkinter")
        sys.exit(1)
    
    app = FunPayKeyChecker()
    app.run()
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
        self.all_sold_keys = []
        
        self.setup_gui()
        self.load_config()
    
    def setup_icon(self):
        """Настройка иконки для окна программы"""
        try:
            # Сначала пытаемся создать иконку если её нет
            if not os.path.exists("icon.ico"):
                self.create_icon_programmatically()
            
            # Устанавливаем иконку для окна - несколько способов для надежности
            if os.path.exists("icon.ico"):
                # Способ 1: стандартный iconbitmap
                try:
                    self.root.iconbitmap("icon.ico")
                except:
                    pass
                
                # Способ 2: через wm_iconbitmap (для некоторых версий tkinter)
                try:
                    self.root.wm_iconbitmap("icon.ico")
                except:
                    pass
                
                # Способ 3: через PhotoImage (для PNG)
                try:
                    if os.path.exists("icon_32x32.png"):
                        icon_photo = tk.PhotoImage(file="icon_32x32.png")
                        self.root.iconphoto(True, icon_photo)
                        # Сохраняем ссылку чтобы не удалилась из памяти
                        self.icon_photo = icon_photo
                except:
                    pass
                    
            elif os.path.exists("icon.png"):
                # Если ico нет, но есть png, конвертируем
                try:
                    from PIL import Image
                    img = Image.open("icon.png")
                    img.save("icon.ico", format='ICO', sizes=[(32, 32), (16, 16)])
                    self.root.iconbitmap("icon.ico")
                except:
                    pass
                    
        except Exception as e:
            # Если не удалось установить иконку, продолжаем без неё
            print(f"Не удалось установить иконку: {e}")
    
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
            import math
            
            # Создаем простую иконку 64x64
            size = 64
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Градиентный фон
            center = size // 2
            for y in range(size):
                for x in range(size):
                    distance = math.sqrt((x - center)**2 + (y - center)**2)
                    max_distance = math.sqrt(2) * center
                    ratio = min(distance / max_distance, 1.0)
                    
                    start_color = (25, 25, 112)  # MidnightBlue
                    end_color = (30, 144, 255)   # DodgerBlue
                    
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                    
                    img.putpixel((x, y), (r, g, b, 255))
            
            # Простой ключ
            key_color = (255, 255, 255, 255)
            
            # Основа ключа
            draw.rectangle([18, 28, 48, 36], fill=key_color)
            
            # Головка ключа
            draw.ellipse([12, 22, 32, 42], fill=key_color)
            draw.ellipse([16, 26, 28, 38], outline=(25, 25, 112), width=2)
            
            # Зубцы
            draw.rectangle([42, 28, 48, 24], fill=key_color)
            draw.rectangle([42, 36, 48, 40], fill=key_color)
            
            # Сохраняем
            img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
            
        except ImportError:
            # Если PIL не установлен, создаем базовую иконку
            pass
        except Exception:
            pass
        
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
                    self.golden_key_entry.insert(0, config["FunPay"]["golden_key"])
                    self.user_agent_entry.insert(0, config["FunPay"]["user_agent"])
                    self.min_delay_var.set(config["Safety"]["min_delay_sec"])
                    self.max_delay_var.set(config["Safety"]["max_delay_sec"])
                    
                    if "order_limit" in config["Safety"]:
                        self.order_limit_var.set(config["Safety"]["order_limit"])
                    if "page_limit" in config["Safety"]:
                        self.page_limit_var.set(config["Safety"]["page_limit"])
            except KeyError:
                self.log_message("Ошибка в файле конфигурации")
    
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
                    golden_key = self.golden_key_entry.get()
                    user_agent = self.user_agent_entry.get()
                
                if not golden_key or "ВАШ_GOLDEN_KEY_СЮДА" in golden_key:
                    self.log_message("❌ Ошибка: Укажите корректный Golden Key")
                    return
                
                account = FunPayAPI.Account(golden_key=golden_key, user_agent=user_agent)
                account.get()
                
                self.log_message(f"✅ Подключение успешно! Пользователь: {account.username} (ID: {account.id})")
                self.account = account
                
            except exceptions.InvalidGoldenKey:
                self.log_message("❌ Ошибка: Неверный Golden Key")
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
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
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
                self.start_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled")
                self.progress_bar.set(0)
        
        threading.Thread(target=analysis_thread, daemon=True).start()
    
    def stop_analysis(self):
        """Остановка анализа"""
        self.is_running = False
        self.log_message("🛑 Анализ остановлен пользователем")
    
    def run_analysis(self, game_id, lot_name):
        """Основная логика анализа"""
        try:
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
                self.log_message(f"📄 Загружаю страницу {page_num}...")
                
                next_start_from, orders_batch = self.account.get_sells(
                    start_from=start_from,
                    game=game_id,
                    state="closed",
                    include_paid=False,
                    include_refunded=False
                )
                
                if not orders_batch:
                    break
                
                all_orders.extend(orders_batch)
                self.log_message(f"✅ Загружено {len(orders_batch)} заказов")
                
                if not next_start_from:
                    break
                
                # Проверяем лимит страниц
                if page_limit and page_num >= page_limit:
                    self.log_message(f"⚠️ Достигнут лимит страниц: {page_limit}")
                    break
                
                start_from = next_start_from
                page_num += 1
                
                time.sleep(random.uniform(min_delay, max_delay))
            
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
                if not self.is_running:
                    return
                
                processed += 1
                progress = processed / len(target_orders)
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"Обработка заказа {processed}/{len(target_orders)}")
                
                self.log_message(f"🔍 Анализ заказа {order_header.id} ({processed}/{len(target_orders)})")
                
                try:
                    time.sleep(random.uniform(min_delay, max_delay))
                    
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
                            self.log_message("⚠️ Ключи не найдены")
                    
                except Exception as e:
                    self.log_message(f"❌ Ошибка при обработке заказа {order_header.id}: {e}")
            
            # Обновление результатов
            self.update_results()
            self.log_message(f"🎉 Анализ завершен! Найдено {len(self.all_sold_keys)} ключей")
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {e}")
    
    def extract_keys_from_html(self, html):
        """Извлечение ключей из HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            keys = []
            secret_elements = soup.find_all('span', class_='secret-placeholder')
            
            for element in secret_elements:
                key = element.get_text().strip()
                if key and len(key) > 10:
                    keys.append(key)
            
            return keys
        except Exception:
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
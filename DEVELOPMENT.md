# 🛠️ Руководство для разработчиков

Это руководство поможет вам настроить среду разработки и внести вклад в проект FunPay Key Checker.

## 🚀 Быстрый старт

### Настройка окружения

```bash
# Клонируйте репозиторий
git clone https://github.com/slonce70/funpay-key-checker.git
cd funpay-key-checker

# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости для разработки
pip install -r requirements.txt
pip install -r requirements-dev.txt  # если будет создан
```

### Первый запуск

```bash
# Запустите приложение
python gui_main.py

# Или создайте exe для тестирования
python build_exe.py
```

## 📁 Структура проекта

```
funpay-key-checker/
├── .github/                    # GitHub конфигурация
│   ├── workflows/             # CI/CD пайплайны
│   └── ISSUE_TEMPLATE/        # Шаблоны для Issues
├── gui_main.py                # Основное GUI приложение
├── build_exe.py               # Скрипт сборки exe
├── icon.ico                   # Иконка приложения
├── icon_32x32.png            # PNG иконка для GUI
├── requirements.txt           # Зависимости
├── .gitignore                # Игнорируемые файлы
├── README.md                 # Основная документация
├── CHANGELOG.md              # История изменений
├── CONTRIBUTING.md           # Руководство для контрибьюторов
├── DEVELOPMENT.md            # Это руководство
├── EXAMPLES.md               # Примеры использования
├── SECURITY.md               # Политика безопасности
└── LICENSE                   # Лицензия MIT
```

## 🏗️ Архитектура приложения

### Основные компоненты

```python
# gui_main.py
class FunPayKeyChecker:
    def __init__(self):          # Инициализация GUI
    def setup_icon(self):        # Настройка иконки
    def setup_gui(self):         # Создание интерфейса
    def setup_settings_tab(self): # Вкладка настроек
    def setup_analysis_tab(self): # Вкладка анализа
    def setup_results_tab(self):  # Вкладка результатов
    def run_analysis(self):      # Основная логика анализа
    def extract_keys_from_html(self): # Извлечение ключей
```

### Поток данных

1. **Настройки** → `config.ini`
2. **Аутентификация** → FunPay API
3. **Получение заказов** → Пагинация
4. **Фильтрация** → По названию лота
5. **Извлечение ключей** → HTML парсинг
6. **Анализ** → Подсчет статистики
7. **Отображение** → GUI таблица
8. **Экспорт** → Текстовые файлы

## 🔧 Инструменты разработки

### Рекомендуемые IDE
- **VS Code** с расширениями:
  - Python
  - Python Docstring Generator
  - GitLens
- **PyCharm** (Community/Professional)

### Полезные команды

```bash
# Форматирование кода
python -m black gui_main.py build_exe.py

# Проверка стиля
python -m flake8 gui_main.py

# Проверка типов
python -m mypy gui_main.py

# Тестирование импортов
python -c "from gui_main import FunPayKeyChecker; print('OK')"
```

## 🧪 Тестирование

### Ручное тестирование

```bash
# Тест GUI без подключения к API
python -c "
import os
os.environ['FUNPAY_TEST_MODE'] = '1'
from gui_main import FunPayKeyChecker
app = FunPayKeyChecker()
print('GUI test passed')
"

# Тест создания иконки
python -c "
from gui_main import FunPayKeyChecker
app = FunPayKeyChecker()
app.create_icon_programmatically()
print('Icon creation test passed')
"
```

### Тест сборки exe

```bash
# Быстрая сборка для тестирования
python build_exe.py
# Выберите опцию "2" для сборки exe

# Проверка размера
dir FunPayKeyChecker.exe
```

## 🎨 Работа с GUI

### CustomTkinter особенности

```python
# Создание элементов
button = ctk.CTkButton(parent, text="Text", command=callback)
entry = ctk.CTkEntry(parent, width=400, placeholder_text="Hint")
label = ctk.CTkLabel(parent, text="Text", font=ctk.CTkFont(size=14))

# Темы и цвета
ctk.set_appearance_mode("dark")  # "light" или "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
```

### Добавление новых элементов

1. Создайте элемент в соответствующем `setup_*_tab()` методе
2. Добавьте обработчик событий
3. Обновите логику сохранения/загрузки настроек
4. Протестируйте в разных разрешениях

## 🔌 Работа с API

### FunPay API особенности

```python
# Аутентификация
account = FunPayAPI.Account(golden_key=key, user_agent=ua)
account.get()

# Получение заказов с пагинацией
next_start_from, orders = account.get_sells(
    start_from=start_from,
    game=game_id,
    state="closed"
)

# Получение деталей заказа
full_order = account.get_order(order_id)
```

### Обработка ошибок

```python
try:
    # API вызов
except exceptions.InvalidGoldenKey:
    # Неверный ключ
except exceptions.RequestFailedError as e:
    if e.code == 429:
        # Слишком много запросов
    else:
        # Другие ошибки API
```

## 📦 Сборка и релиз

### Локальная сборка

```bash
# Полная сборка с очисткой
python build_exe.py
# Выберите опцию "5"

# Ручная сборка
python -m PyInstaller --onefile --windowed --name=FunPayKeyChecker --icon=icon.ico gui_main.py
```

### GitHub Actions

Автоматическая сборка запускается при:
- Push тегов `v*` (например, `v2.0.1`)
- Pull requests в `main`
- Ручном запуске

### Создание релиза

1. Обновите `CHANGELOG.md`
2. Создайте тег: `git tag v2.0.1`
3. Отправьте тег: `git push origin v2.0.1`
4. GitHub Actions автоматически создаст релиз

## 🐛 Отладка

### Частые проблемы

**Проблема**: GUI не отображается
```python
# Решение: проверьте импорт customtkinter
try:
    import customtkinter as ctk
    MODERN_GUI = True
except ImportError:
    import tkinter as tk
    MODERN_GUI = False
```

**Проблема**: Иконка не устанавливается
```python
# Решение: проверьте наличие файлов
if os.path.exists("icon.ico"):
    self.root.iconbitmap("icon.ico")
```

**Проблема**: Ошибки при сборке exe
```bash
# Решение: очистите кэш
python -m PyInstaller --clean gui_main.py
```

### Логирование

```python
# Добавьте отладочные сообщения
def log_message(self, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}\n"
    self.log_text.insert("end", formatted_message)
```

## 📝 Стандарты кода

### Python стиль
- Следуйте PEP 8
- Максимальная длина строки: 88 символов (Black)
- Используйте type hints где возможно
- Документируйте функции docstrings

### Именование
```python
# Классы: PascalCase
class FunPayKeyChecker:

# Функции и переменные: snake_case
def extract_keys_from_html(self):
    golden_key = self.config["golden_key"]

# Константы: UPPER_CASE
CONFIG_FILE = "config.ini"
MODERN_GUI = True
```

### Комментарии
```python
# Однострочные комментарии для пояснений
golden_key = config["golden_key"]  # API ключ от FunPay

def complex_function(self):
    """
    Многострочные docstrings для функций.
    
    Args:
        param: описание параметра
        
    Returns:
        описание возвращаемого значения
    """
```

## 🚀 Планы развития

### Ближайшие задачи
- [ ] Добавить поддержку Linux/Mac
- [ ] Улучшить обработку ошибок
- [ ] Добавить темы оформления
- [ ] Оптимизировать производительность

### Долгосрочные цели
- [ ] Поддержка других торговых площадок
- [ ] Веб-интерфейс
- [ ] API для интеграции
- [ ] Плагины и расширения

## 📞 Поддержка разработчиков

- **Вопросы по коду**: [GitHub Discussions](https://github.com/slonce70/funpay-key-checker/discussions)
- **Баги**: GitHub Issues
- **Предложения**: GitHub Issues с меткой "enhancement"
- **Разработчик**: @slonce70

---

**Удачной разработки! 🚀**
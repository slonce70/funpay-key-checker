"""
Скрипт для создания exe файла из GUI приложения
"""
import os
import sys
import subprocess
import shutil

def install_dependencies():
    """Установка всех зависимостей"""
    print("📦 Устанавливаю зависимости...")
    
    dependencies = [
        "FunPayAPI",
        "beautifulsoup4", 
        "customtkinter",
        "pyinstaller",
        "Pillow"  # Для создания иконки
    ]
    
    for dep in dependencies:
        try:
            print(f"⚙️ Устанавливаю {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "--upgrade"])
        except subprocess.CalledProcessError:
            print(f"⚠️ Не удалось установить {dep}")

def create_icon_if_needed():
    """Создание иконки если её нет"""
    if not os.path.exists("icon.ico"):
        print("🎨 Создаю иконку...")
        try:
            subprocess.check_call([sys.executable, "create_icon.py"])
        except Exception as e:
            print(f"⚠️ Не удалось создать иконку: {e}")

def build_exe():
    """Создание exe файла"""
    print("🚀 Начинаю сборку exe файла...")
    
    # Создаем иконку если нужно
    create_icon_if_needed()
    
    # Проверяем наличие pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller не найден. Устанавливаю...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Параметры для PyInstaller
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # Один exe файл
        "--windowed",                   # Без консоли
        "--name=FunPayKeyChecker",      # Имя exe файла
        "--hidden-import=customtkinter", # Скрытые импорты
        "--hidden-import=FunPayAPI",
        "--hidden-import=bs4",
        "--hidden-import=PIL",
        "--hidden-import=tkinter",
        "--collect-all=customtkinter",   # Собрать все файлы customtkinter
        "--clean",                      # Очистить кэш
        "--noconfirm",                  # Не спрашивать подтверждения
        "gui_main.py"                   # Основной файл
    ]
    
    # Добавляем иконку если есть
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
    
    # Добавляем config.ini если есть
    if os.path.exists("config.ini"):
        cmd.insert(-1, "--add-data=config.ini;.")
    
    try:
        print("⚙️ Запускаю PyInstaller...")
        print("📝 Команда:", " ".join(cmd))
        subprocess.check_call(cmd)
        
        print("✅ Сборка завершена успешно!")
        print("📁 Exe файл находится в папке: dist/FunPayKeyChecker.exe")
        
        # Копируем exe в корневую папку для удобства
        if os.path.exists("dist/FunPayKeyChecker.exe"):
            shutil.copy2("dist/FunPayKeyChecker.exe", "FunPayKeyChecker.exe")
            print("📋 Exe файл скопирован в корневую папку")
            
            # Показываем размер файла
            size = os.path.getsize("FunPayKeyChecker.exe")
            size_mb = size / (1024 * 1024)
            print(f"📏 Размер exe файла: {size_mb:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке: {e}")
        return False
    
    return True

def build_portable():
    """Создание портативной версии (папка с файлами)"""
    print("📦 Создаю портативную версию...")
    
    cmd = [
        "python", "-m", "PyInstaller",
        "--onedir",                     # Папка с файлами
        "--windowed",                   # Без консоли
        "--name=FunPayKeyChecker",      # Имя папки
        "--hidden-import=customtkinter",
        "--hidden-import=FunPayAPI", 
        "--hidden-import=bs4",
        "--collect-all=customtkinter",
        "--clean",
        "--noconfirm",
        "gui_main.py"
    ]
    
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Портативная версия создана в папке: dist/FunPayKeyChecker/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании портативной версии: {e}")
        return False

def clean_build_files():
    """Очистка временных файлов сборки"""
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["FunPayKeyChecker.spec"]
    
    print("🧹 Очищаю временные файлы...")
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ Удалена папка: {dir_name}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"🗑️ Удален файл: {file_name}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FunPay Key Checker - Сборка EXE v2.0")
    print("=" * 60)
    
    # Проверяем наличие основного файла
    if not os.path.exists("gui_main.py"):
        print("❌ Файл gui_main.py не найден!")
        sys.exit(1)
    
    # Спрашиваем пользователя
    print("Выберите действие:")
    print("1. 📦 Установить зависимости")
    print("2. 🚀 Собрать exe файл")
    print("3. 📁 Создать портативную версию")
    print("4. 🧹 Очистить временные файлы")
    print("5. 🎯 Полная сборка (установка + exe + очистка)")
    print("6. 🎨 Создать иконку")
    
    choice = input("\nВвод: ")
    
    if choice == "1":
        install_dependencies()
    elif choice == "2":
        build_exe()
    elif choice == "3":
        build_portable()
    elif choice == "4":
        clean_build_files()
    elif choice == "5":
        print("🎯 Запускаю полную сборку...")
        install_dependencies()
        if build_exe():
            input("\nНажмите Enter для очистки временных файлов...")
            clean_build_files()
    elif choice == "6":
        try:
            exec(open("create_icon.py").read())
        except Exception as e:
            print(f"❌ Ошибка создания иконки: {e}")
    else:
        print("❌ Неверный выбор!")
    
    print("\n✨ Готово!")
    input("Нажмите Enter для выхода...")
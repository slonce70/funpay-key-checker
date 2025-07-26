#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback

def debug_imports():
    """Отладка импортов"""
    print("=== ОТЛАДКА ИМПОРТОВ ===")
    
    # Проверяем основные модули
    modules_to_check = [
        'tkinter',
        'customtkinter', 
        'FunPayAPI',
        'beautifulsoup4',
        'configparser',
        'threading',
        'PIL'
    ]
    
    for module in modules_to_check:
        try:
            if module == 'beautifulsoup4':
                import bs4
                print(f"✅ {module} (bs4) - OK")
            elif module == 'PIL':
                from PIL import Image, ImageDraw
                print(f"✅ {module} - OK")
            else:
                __import__(module)
                print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - ОШИБКА: {e}")
        except Exception as e:
            print(f"⚠️ {module} - ПРЕДУПРЕЖДЕНИЕ: {e}")

def debug_funpay_api():
    """Отладка FunPayAPI"""
    print("\n=== ОТЛАДКА FUNPAY API ===")
    
    try:
        import FunPayAPI
        print(f"✅ FunPayAPI импортирован")
        
        # Проверяем основные классы
        try:
            from FunPayAPI.common import exceptions
            print("✅ FunPayAPI.common.exceptions - OK")
            
            # Показываем доступные исключения
            available_exceptions = [attr for attr in dir(exceptions) if not attr.startswith('_') and 'Error' in attr]
            print(f"   Доступные исключения: {', '.join(available_exceptions)}")
            
        except ImportError as e:
            print(f"❌ FunPayAPI.common.exceptions - ОШИБКА: {e}")
            
        try:
            from FunPayAPI.types import OrderStatuses
            print("✅ FunPayAPI.types.OrderStatuses - OK")
        except ImportError as e:
            print(f"❌ FunPayAPI.types.OrderStatuses - ОШИБКА: {e}")
            
        try:
            account_class = getattr(FunPayAPI, 'Account', None)
            if account_class:
                print("✅ FunPayAPI.Account - OK")
                
                # Проверяем методы Account
                test_account = account_class("test_key")
                methods = [method for method in dir(test_account) if not method.startswith('_') and callable(getattr(test_account, method))]
                print(f"   Доступные методы: {len(methods)} (get, get_sells, get_order и др.)")
                
            else:
                print("❌ FunPayAPI.Account - НЕ НАЙДЕН")
        except Exception as e:
            print(f"❌ FunPayAPI.Account - ОШИБКА: {e}")
            
    except ImportError as e:
        print(f"❌ FunPayAPI - КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("   Решение: pip install FunPayAPI>=1.0.0")

def debug_gui_creation():
    """Отладка создания GUI"""
    print("\n=== ОТЛАДКА GUI ===")
    
    try:
        import customtkinter as ctk
        print("✅ CustomTkinter импортирован")
        
        # Пробуем создать окно
        try:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            print("✅ Настройки CustomTkinter применены")
            
            root = ctk.CTk()
            root.title("Test Window")
            print("✅ Тестовое окно создано")
            root.destroy()
            print("✅ Тестовое окно закрыто")
            
        except Exception as e:
            print(f"❌ Ошибка создания GUI: {e}")
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ CustomTkinter - ОШИБКА: {e}")

def debug_config():
    """Отладка конфигурации"""
    print("\n=== ОТЛАДКА КОНФИГУРАЦИИ ===")
    
    config_file = "config.ini"
    
    if os.path.exists(config_file):
        print(f"✅ Файл {config_file} найден")
        
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            
            # Проверяем секции
            sections = config.sections()
            print(f"   Секции: {sections}")
            
            if "FunPay" in sections:
                golden_key = config.get("FunPay", "golden_key", fallback="")
                user_agent = config.get("FunPay", "user_agent", fallback="")
                
                print(f"   Golden Key: {'установлен' if golden_key else 'НЕ УСТАНОВЛЕН'}")
                print(f"   User Agent: {'установлен' if user_agent else 'НЕ УСТАНОВЛЕН'}")
                
                # Проверяем User Agent на недопустимые символы
                if user_agent:
                    try:
                        user_agent.encode('ascii')
                        print("   ✅ User Agent содержит только допустимые символы")
                    except UnicodeEncodeError:
                        print("   ⚠️ User Agent содержит недопустимые символы (кириллица)")
            
            if "Safety" in sections:
                min_delay = config.get("Safety", "min_delay_sec", fallback="2")
                max_delay = config.get("Safety", "max_delay_sec", fallback="5")
                print(f"   Задержки: {min_delay}-{max_delay} сек")
                
        except Exception as e:
            print(f"❌ Ошибка чтения конфигурации: {e}")
    else:
        print(f"⚠️ Файл {config_file} не найден (будет создан при первом сохранении)")

def main():
    """Основная функция отладки"""
    print("🔍 ДИАГНОСТИКА FUNPAY KEY CHECKER")
    print("=" * 50)
    
    debug_imports()
    debug_funpay_api()
    debug_config()
    debug_gui_creation()
    
    print("\n=== ПОПЫТКА ЗАПУСКА ОСНОВНОГО ПРИЛОЖЕНИЯ ===")
    
    try:
        # Импортируем основной класс
        sys.path.insert(0, '.')
        from gui_main import FunPayKeyChecker
        
        print("✅ Класс FunPayKeyChecker импортирован")
        
        # Пробуем создать экземпляр
        app = FunPayKeyChecker()
        print("✅ Экземпляр FunPayKeyChecker создан")
        
        print("🚀 Запускаем приложение...")
        print("   (Закройте окно приложения для завершения диагностики)")
        app.run()
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
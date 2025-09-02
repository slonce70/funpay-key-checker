#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание иконки для FunPay Key Checker
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_app_icon():
    """Создание красивой иконки приложения"""
    print("🎨 Создаю иконку приложения...")
    
    # Размеры для разных форматов
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # Создаем изображение с прозрачным фоном
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Цвета
        bg_color = (30, 144, 255, 255)      # DodgerBlue
        key_color = (255, 255, 255, 255)    # White
        shadow_color = (0, 0, 0, 100)       # Semi-transparent black
        
        # Размеры элементов пропорционально размеру иконки
        margin = size // 8
        key_width = size - 2 * margin
        key_height = size // 3
        
        # Фон - градиентный круг
        center = size // 2
        radius = center - 2
        
        # Создаем градиентный фон
        for y in range(size):
            for x in range(size):
                distance = ((x - center) ** 2 + (y - center) ** 2) ** 0.5
                if distance <= radius:
                    # Градиент от центра к краям
                    ratio = distance / radius
                    r = int(bg_color[0] * (1 - ratio * 0.3))
                    g = int(bg_color[1] * (1 - ratio * 0.2))
                    b = int(bg_color[2])
                    img.putpixel((x, y), (r, g, b, 255))
        
        # Тень ключа
        shadow_offset = max(1, size // 32)
        draw_key(draw, margin + shadow_offset, center - key_height//2 + shadow_offset, 
                key_width, key_height, shadow_color, size)
        
        # Основной ключ
        draw_key(draw, margin, center - key_height//2, key_width, key_height, key_color, size)
        
        # Сохраняем в разных форматах
        if size == 32:
            img.save('icon_32x32.png', 'PNG')
            print(f"✅ Создан icon_32x32.png")
        
        if size == 64:
            img.save('icon_64x64.png', 'PNG')
            print(f"✅ Создан icon_64x64.png")
    
    # Создаем ICO файл с несколькими размерами
    try:
        # Загружаем созданные PNG
        icon_sizes = []
        for size in [16, 32, 48, 64]:
            if size == 32 and os.path.exists('icon_32x32.png'):
                icon_sizes.append(Image.open('icon_32x32.png').resize((size, size), Image.Resampling.LANCZOS))
            elif size == 64 and os.path.exists('icon_64x64.png'):
                icon_sizes.append(Image.open('icon_64x64.png').resize((size, size), Image.Resampling.LANCZOS))
            else:
                # Создаем размер на лету
                img = create_single_icon(size)
                icon_sizes.append(img)
        
        # Сохраняем как ICO
        if icon_sizes:
            icon_sizes[0].save('icon.ico', format='ICO', sizes=[(img.width, img.height) for img in icon_sizes])
            print("✅ Создан icon.ico")
        
    except Exception as e:
        print(f"⚠️ Ошибка создания ICO: {e}")
        # Fallback - создаем простую ICO
        create_simple_ico()

def draw_key(draw, x, y, width, height, color, icon_size):
    """Рисование ключа"""
    # Пропорции ключа
    head_size = height
    shaft_width = max(2, height // 4)
    teeth_size = max(1, height // 6)
    
    # Головка ключа (круг)
    head_x = x
    head_y = y
    draw.ellipse([head_x, head_y, head_x + head_size, head_y + head_size], fill=color)
    
    # Отверстие в головке
    hole_margin = max(1, head_size // 4)
    draw.ellipse([head_x + hole_margin, head_y + hole_margin, 
                 head_x + head_size - hole_margin, head_y + head_size - hole_margin], 
                fill=(0, 0, 0, 0))
    
    # Стержень ключа
    shaft_x = head_x + head_size
    shaft_y = y + (head_size - shaft_width) // 2
    shaft_length = width - head_size - teeth_size
    
    if shaft_length > 0:
        draw.rectangle([shaft_x, shaft_y, shaft_x + shaft_length, shaft_y + shaft_width], fill=color)
        
        # Зубцы ключа
        teeth_x = shaft_x + shaft_length
        teeth_y1 = shaft_y
        teeth_y2 = shaft_y + shaft_width
        
        # Верхний зубец
        draw.rectangle([teeth_x, teeth_y1 - teeth_size, teeth_x + teeth_size, teeth_y1], fill=color)
        # Нижний зубец
        draw.rectangle([teeth_x, teeth_y2, teeth_x + teeth_size, teeth_y2 + teeth_size], fill=color)

def create_single_icon(size):
    """Создание одной иконки заданного размера"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Простой синий фон
    bg_color = (30, 144, 255, 255)
    key_color = (255, 255, 255, 255)
    
    # Круглый фон
    margin = 2
    draw.ellipse([margin, margin, size - margin, size - margin], fill=bg_color)
    
    # Простой ключ
    key_margin = size // 4
    key_width = size - 2 * key_margin
    key_height = size // 3
    
    draw_key(draw, key_margin, (size - key_height) // 2, key_width, key_height, key_color, size)
    
    return img

def create_simple_ico():
    """Создание простой ICO иконки как fallback"""
    try:
        img = create_single_icon(32)
        img.save('icon.ico', format='ICO', sizes=[(32, 32), (16, 16)])
        print("✅ Создан простой icon.ico")
    except Exception as e:
        print(f"❌ Не удалось создать даже простую иконку: {e}")

if __name__ == "__main__":
    print("🎨 Создание иконки для FunPay Key Checker")
    print("=" * 50)
    
    try:
        create_app_icon()
        print("\n✅ Иконки созданы успешно!")
        
        # Показываем созданные файлы
        icon_files = ['icon.ico', 'icon_32x32.png', 'icon_64x64.png']
        for file in icon_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"📁 {file} ({size} байт)")
        
    except ImportError:
        print("❌ Библиотека PIL (Pillow) не установлена!")
        print("Установите её командой: pip install Pillow")
    except Exception as e:
        print(f"❌ Ошибка создания иконки: {e}")

    print("\n🎯 Готово!")

import re
import urllib.parse
from urllib.parse import urlparse


class TranslitParser:
    """Парсер для транслитерации кириллицы в латиницу"""
    
    def __init__(self):
        # Таблица транслитерации кириллица -> латиница
        self.translit_table = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
    
    def transliterate_text(self, text):
        """Транслитерация текста"""
        if not text:
            return ""
        
        # Переводим в строчные буквы
        text = text.lower()
        
        # Транслитерация
        result = ""
        for char in text:
            if char in self.translit_table:
                result += self.translit_table[char]
            else:
                result += char
        
        return result
    
    def process_url(self, url):
        """Обработка URL - только path, не затрагивая другие компоненты"""
        if not url:
            return ""
        
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Транслитерируем только path
            translit_path = self.transliterate_text(path)
            
            # Заменяем пробелы, _ и , на тире
            translit_path = re.sub(r'[\s_,]+', '-', translit_path)
            
            # Удаляем повторяющиеся тире
            translit_path = re.sub(r'-+', '-', translit_path)
            
            # Убираем тире в начале и конце
            translit_path = translit_path.strip('-')
            
            # Собираем URL обратно
            result = f"{parsed.scheme}://{parsed.netloc}{translit_path}"
            if parsed.query:
                result += f"?{parsed.query}"
            if parsed.fragment:
                result += f"#{parsed.fragment}"
            
            return result
            
        except Exception:
            # Если не URL, обрабатываем как обычный текст
            return self.process_text(url)
    
    def process_text(self, text):
        """Обработка обычного текста"""
        if not text:
            return ""
        
        # Декодируем %## символы
        try:
            text = urllib.parse.unquote(text)
        except:
            pass
        
        # Транслитерация
        result = self.transliterate_text(text)
        
        # Заменяем пробелы, _ и , на тире
        result = re.sub(r'[\s_,]+', '-', result)
        
        # Удаляем повторяющиеся тире
        result = re.sub(r'-+', '-', result)
        
        # Убираем тире в начале и конце
        result = result.strip('-')
        
        # Добавляем слэши в начале и конце
        if result:
            result = f"/{result}/"
        
        return result
    
    def process_multiple_lines(self, text, is_url=False):
        """Обработка нескольких строк"""
        if not text:
            return []
        
        lines = text.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if is_url:
                processed = self.process_url(line)
            else:
                processed = self.process_text(line)
            
            results.append({
                'original': line,
                'translit': processed
            })
        
        return results

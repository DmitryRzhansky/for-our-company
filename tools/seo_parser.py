import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from django.utils import timezone


class SEOParser:
    """Парсер для базового SEO-анализа"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def parse_url(self, url):
        """Парсит URL и возвращает SEO-данные"""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    'error': f'HTTP {response.status_code}',
                    'status_code': response.status_code
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Проверяем на защиту от ботов
            if self._is_bot_protection(soup, response):
                return {
                    'error': 'Сайт защищен от автоматического парсинга. Попробуйте другой сайт или используйте ручной анализ.',
                    'status_code': response.status_code,
                    'page_size': len(response.content)
                }
            
            # Базовые данные
            data = {
                'page_url': url,
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'page_size': len(response.content),
            }
            
            # Title
            title_tag = soup.find('title')
            data['page_title'] = title_tag.get_text().strip() if title_tag else ''
            
            # Meta теги
            data.update(self._parse_meta_tags(soup))
            
            # Заголовки H1-H6
            data.update(self._parse_headings(soup))
            
            # Open Graph
            data.update(self._parse_open_graph(soup))
            
            # Twitter Cards
            data.update(self._parse_twitter_cards(soup))
            
            # Canonical
            canonical = soup.find('link', rel='canonical')
            data['canonical_url'] = canonical.get('href') if canonical else ''
            
            # SEO проблемы
            data['seo_issues'] = self._find_seo_issues(data, soup)
            
            return data
            
        except requests.RequestException as e:
            return {'error': f'Ошибка запроса: {str(e)}'}
        except Exception as e:
            return {'error': f'Ошибка парсинга: {str(e)}'}
    
    def _is_bot_protection(self, soup, response):
        """Проверяет, защищен ли сайт от ботов"""
        # Проверяем размер контента (слишком маленький)
        if len(response.content) < 500:
            return True
        
        # Проверяем на типичные защиты от ботов
        text = soup.get_text().lower()
        
        # Beget защита (очень специфичная)
        if 'beget' in text and 'set_cookie' in text and 'location.reload' in text:
            return True
        
        # Cloudflare защита
        if 'cloudflare' in text and 'checking your browser' in text:
            return True
        
        # Другие защиты
        if 'access denied' in text or 'forbidden' in text:
            return True
        
        # Проверяем на пустую страницу с редиректом
        if len(response.content) < 1000 and 'location.reload' in text and not soup.find('title'):
            return True
        
        return False
    
    def _parse_meta_tags(self, soup):
        """Парсит мета-теги"""
        meta_data = {}
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_data['meta_description'] = meta_desc.get('content', '') if meta_desc else ''
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        meta_data['meta_keywords'] = meta_keywords.get('content', '') if meta_keywords else ''
        
        # Meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        meta_data['meta_robots'] = meta_robots.get('content', '') if meta_robots else ''
        
        return meta_data
    
    def _parse_headings(self, soup):
        """Парсит заголовки H1-H6"""
        headings = {}
        
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}_tags'] = [tag.get_text().strip() for tag in h_tags]
        
        return headings
    
    def _parse_open_graph(self, soup):
        """Парсит Open Graph теги"""
        og_data = {}
        
        og_tags = {
            'og:title': 'og_title',
            'og:description': 'og_description',
            'og:image': 'og_image',
            'og:type': 'og_type',
        }
        
        for og_property, field_name in og_tags.items():
            og_tag = soup.find('meta', property=og_property)
            og_data[field_name] = og_tag.get('content', '') if og_tag else ''
        
        return og_data
    
    def _parse_twitter_cards(self, soup):
        """Парсит Twitter Cards теги"""
        twitter_data = {}
        
        twitter_tags = {
            'twitter:title': 'twitter_title',
            'twitter:description': 'twitter_description',
            'twitter:image': 'twitter_image',
            'twitter:card': 'twitter_card',
        }
        
        for twitter_name, field_name in twitter_tags.items():
            twitter_tag = soup.find('meta', attrs={'name': twitter_name})
            twitter_data[field_name] = twitter_tag.get('content', '') if twitter_tag else ''
        
        return twitter_data
    
    def _find_seo_issues(self, data, soup):
        """Находит SEO проблемы"""
        issues = []
        
        # Отсутствует title
        if not data.get('page_title'):
            issues.append({
                'category': 'meta',
                'severity': 'critical',
                'title': 'Отсутствует title',
                'description': 'Страница не имеет заголовка title',
                'recommendation': 'Добавьте уникальный и описательный title для каждой страницы'
            })
        
        # Отсутствует meta description
        if not data.get('meta_description'):
            issues.append({
                'category': 'meta',
                'severity': 'high',
                'title': 'Отсутствует meta description',
                'description': 'Страница не имеет meta description',
                'recommendation': 'Добавьте meta description длиной 150-160 символов'
            })
        
        # Слишком длинный title
        if data.get('page_title') and len(data['page_title']) > 60:
            issues.append({
                'category': 'meta',
                'severity': 'medium',
                'title': 'Слишком длинный title',
                'description': f'Title содержит {len(data["page_title"])} символов',
                'recommendation': 'Сократите title до 50-60 символов'
            })
        
        # Слишком длинная meta description
        if data.get('meta_description') and len(data['meta_description']) > 160:
            issues.append({
                'category': 'meta',
                'severity': 'medium',
                'title': 'Слишком длинная meta description',
                'description': f'Meta description содержит {len(data["meta_description"])} символов',
                'recommendation': 'Сократите meta description до 150-160 символов'
            })
        
        # Отсутствует H1
        if not data.get('h1_tags'):
            issues.append({
                'category': 'structure',
                'severity': 'high',
                'title': 'Отсутствует H1',
                'description': 'Страница не имеет заголовка H1',
                'recommendation': 'Добавьте один заголовок H1 на страницу'
            })
        
        # Множественные H1
        if data.get('h1_tags') and len(data['h1_tags']) > 1:
            issues.append({
                'category': 'structure',
                'severity': 'medium',
                'title': 'Множественные H1',
                'description': f'Найдено {len(data["h1_tags"])} заголовков H1',
                'recommendation': 'Используйте только один заголовок H1 на страницу'
            })
        
        # Изображения без alt
        images_without_alt = soup.find_all('img', alt='')
        if images_without_alt:
            issues.append({
                'category': 'content',
                'severity': 'medium',
                'title': 'Изображения без alt-текста',
                'description': f'Найдено {len(images_without_alt)} изображений без alt-текста',
                'recommendation': 'Добавьте описательные alt-тексты для всех изображений'
            })
        
        return issues
    
    def get_robots_txt(self, url):
        """Получает robots.txt"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            return response.text if response.status_code == 200 else ''
        except:
            return ''
    
    def get_sitemap_xml(self, url):
        """Получает sitemap.xml"""
        try:
            parsed_url = urlparse(url)
            sitemap_url = f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml"
            response = self.session.get(sitemap_url, timeout=10)
            return response.text if response.status_code == 200 else ''
        except:
            return ''

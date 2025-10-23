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
    
    def parse_url(self, url, keywords=None):
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
            
            # Простые метрики
            metrics_data = self._analyze_simple_metrics(soup, url, keywords)
            data.update(metrics_data)
            
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
        
        # Meta robots - более надежный поиск
        meta_robots = None
        
        # Ищем по разным вариантам name
        for name_attr in ['robots', 'ROBOTS', 'Robots']:
            meta_robots = soup.find('meta', attrs={'name': name_attr})
            if meta_robots:
                break
        
        # Если не нашли, ищем по content
        if not meta_robots:
            for content_value in ['index, follow', 'noindex, nofollow', 'index, nofollow', 'noindex, follow']:
                meta_robots = soup.find('meta', attrs={'content': content_value})
                if meta_robots:
                    break
        
        # Если все еще не нашли, ищем любые meta с robots в content
        if not meta_robots:
            all_meta = soup.find_all('meta')
            for meta in all_meta:
                content = meta.get('content', '')
                if 'robots' in content.lower() or 'index' in content.lower() or 'follow' in content.lower():
                    meta_robots = meta
                    break
        
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
    
    def _analyze_simple_metrics(self, soup, url, keywords=None):
        """Анализирует простые метрики"""
        import re
        
        # Удаляем header, footer, nav и другие служебные элементы
        for element in soup(['header', 'footer', 'nav', 'aside', 'script', 'style', 'noscript']):
            element.decompose()
        
        # Удаляем элементы с классами header/footer
        for element in soup.find_all(class_=lambda x: x and any(word in x.lower() for word in ['header', 'footer', 'nav', 'menu', 'sidebar'])):
            element.decompose()
        
        # Извлекаем только основной контент
        main_content = soup.find('main')
        if main_content:
            text = main_content.get_text()
        else:
            # Если нет main, ищем article или div с контентом
            article = soup.find('article')
            if article:
                text = article.get_text()
            else:
                # В крайнем случае берем body, но без служебных элементов
                body = soup.find('body')
                if body:
                    text = body.get_text()
                else:
                    text = soup.get_text()
        
        data = {
            'extracted_text': text,  # Убираем ограничение размера
        }
        
        # Подсчет слов
        words = re.findall(r'\b\w+\b', text.lower())
        data['word_count'] = len(words)
        
        # Длина title и description (используем уже извлеченные данные)
        data['title_length'] = len(data.get('page_title', ''))
        data['description_length'] = len(data.get('meta_description', ''))
        
        # Анализ ссылок
        links_data = self._analyze_links(soup, url)
        data.update(links_data)
        
        # Сохраняем детальную информацию о ссылках
        detailed_links = self._get_detailed_links(soup, url)
        data['detailed_links'] = detailed_links
        
        # Анализ ключевых слов
        if keywords:
            keyword_analysis = self._analyze_keywords(text, keywords)
            data['keyword_analysis'] = keyword_analysis
        else:
            data['keyword_analysis'] = {}
        
        return data
    
    def _analyze_links(self, soup, base_url):
        """Анализ ссылок на странице"""
        links = soup.find_all('a', href=True)
        base_domain = urlparse(base_url).netloc
        
        internal_links = 0
        external_links = 0
        
        for link in links:
            href = link['href']
            
            # Пропускаем якорные ссылки и javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Преобразуем относительные ссылки в абсолютные
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith('http'):
                href = urljoin(base_url, href)
            
            try:
                link_domain = urlparse(href).netloc
                if link_domain == base_domain:
                    internal_links += 1
                else:
                    external_links += 1
            except:
                continue
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'total_links': internal_links + external_links
        }
    
    def _analyze_keywords(self, text, keywords):
        """Анализ плотности ключевых слов"""
        import re
        text_lower = text.lower()
        analysis = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Подсчитываем количество вхождений
            count = text_lower.count(keyword_lower)
            
            # Вычисляем плотность (в процентах)
            word_count = len(re.findall(r'\b\w+\b', text_lower))
            density = (count / word_count * 100) if word_count > 0 else 0
            
            analysis[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
        
        return analysis
    
    def _get_detailed_links(self, soup, base_url):
        """Получает детальную информацию о ссылках"""
        links = soup.find_all('a', href=True)
        base_domain = urlparse(base_url).netloc
        
        internal_links = []
        external_links = []
        
        for link in links:
            href = link['href']
            text = link.get_text().strip()
            
            # Пропускаем якорные ссылки и javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Преобразуем относительные ссылки в абсолютные
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith('http'):
                href = urljoin(base_url, href)
            
            try:
                link_domain = urlparse(href).netloc
                link_info = {
                    'url': href,
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'title': link.get('title', ''),
                    'domain': link_domain
                }
                
                if link_domain == base_domain:
                    internal_links.append(link_info)
                else:
                    external_links.append(link_info)
            except:
                continue
        
        return {
            'internal': internal_links,
            'external': external_links
        }

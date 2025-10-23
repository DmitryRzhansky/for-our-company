import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        
    def _parse_date(self, date_str: str) -> datetime:
        """Парсит строку даты в объект datetime"""
        if not date_str:
            return datetime.now()
            
        # Стандартные форматы дат
        date_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y", 
            "%d.%m.%y",
            "%d.%m.%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # Обработка русского формата "07 Октября 2025"
        try:
            ru_months = {
                'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
            }
            parts = date_str.replace(',', '').split()
            if len(parts) == 3 and parts[1].lower() in ru_months:
                reformatted_date = f"{parts[0]}.{ru_months[parts[1].lower()]}.{parts[2]}"
                return datetime.strptime(reformatted_date.strip(), "%d.%m.%Y")
        except (ValueError, KeyError):
            pass

        # Обработка относительных дат
        lower_date = date_str.lower()
        if any(word in lower_date for word in ["сегодня", "час", "минут", "вчера"]):
            return datetime.now()
            
        # Если не удалось распарсить, возвращаем текущую дату
        return datetime.now()

    def is_recent_news(self, date_str: str) -> bool:
        """Проверяет, является ли новость свежей (за последнюю неделю)"""
        if not date_str:
            return False
            
        today = datetime.now().date()
        
        # Стандартные форматы дат
        date_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y", 
            "%d.%m.%y",
            "%d.%m.%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt).date()
                days_diff = (today - date_obj).days
                return 0 <= days_diff <= 7
            except ValueError:
                continue
        
        # Обработка русского формата "07 Октября 2025"
        try:
            ru_months = {
                'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
            }
            parts = date_str.replace(',', '').split()
            if len(parts) == 3 and parts[1].lower() in ru_months:
                reformatted_date = f"{parts[0]}.{ru_months[parts[1].lower()]}.{parts[2]}"
                date_obj = datetime.strptime(reformatted_date.strip(), "%d.%m.%Y").date()
                days_diff = (today - date_obj).days
                return 0 <= days_diff <= 7
        except (ValueError, KeyError):
            pass

        # Обработка относительных дат
        lower_date = date_str.lower()
        if any(word in lower_date for word in ["сегодня", "час", "минут", "вчера"]):
            return True
            
        return False

    def safe_request(self, url: str) -> Optional[BeautifulSoup]:
        """Безопасный запрос с обработкой ошибок"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе {url}: {e}")
            return None

    def parse_seonews(self) -> List[Dict]:
        """Парсинг seonews.ru"""
        news_list = []
        url = "https://m.seonews.ru/"
        soup = self.safe_request(url)
        
        if not soup:
            return news_list
            
        try:
            items = soup.select('div.item')
            for item in items:
                date_el = item.select_one("div.date")
                news_date = date_el.get_text(strip=True) if date_el else ""
                
                if not self.is_recent_news(news_date):
                    continue
                    
                link_el = item.select_one("a")
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if href.startswith("/"):
                    href = urljoin(url, href)
                    
                title_el = item.select_one("div.title")
                title = title_el.get_text(strip=True) if title_el else ""
                
                if title:
                    # Преобразуем дату в объект datetime
                    parsed_date = self._parse_date(news_date)
                    news_list.append({
                        "title": title,
                        "url": href,
                        "source": "seonews.ru",
                        "date": parsed_date,
                        "img": ""  # На мобильной версии нет изображений
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге seonews.ru: {e}")
            
        return news_list

    def parse_vcru(self) -> List[Dict]:
        """Парсинг vc.ru/seo"""
        news_list = []
        url = "https://vc.ru/seo"
        soup = self.safe_request(url)
        
        if not soup:
            return news_list
            
        try:
            items = soup.select("div.content__body")
            today = datetime.now().strftime("%Y-%m-%d")
            
            for item in items:
                link_el = item.select_one("div.content-title > a")
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if href.startswith("/"):
                    href = urljoin(url, href)
                    
                title = link_el.get_text(strip=True)
                
                img_el = item.select_one("img")
                img_url = img_el.get("src", "") if img_el else ""
                
                if title:
                    news_list.append({
                        "title": title,
                        "url": href,
                        "source": "vc.ru",
                        "date": datetime.strptime(today, "%Y-%m-%d"),
                        "img": img_url
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге vc.ru: {e}")
            
        return news_list

    def parse_topvisor(self) -> List[Dict]:
        """Парсинг journal.topvisor.com"""
        news_list = []
        url = "https://journal.topvisor.com/ru/news/"
        soup = self.safe_request(url)
        
        if not soup:
            return news_list
            
        try:
            items = soup.select("div.journalArticlePreview")
            
            for item in items:
                date_el = item.select_one("div.journalArticlePreview_date")
                news_date = date_el.get_text(strip=True) if date_el else ""
                
                if not self.is_recent_news(news_date):
                    continue
                    
                link_el = item.select_one("a[href]")
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if href.startswith("/"):
                    href = urljoin(url, href)
                    
                title_el = item.select_one("h2.journalArticlePreview_title")
                title = title_el.get_text(strip=True) if title_el else ""
                
                if title:
                    parsed_date = self._parse_date(news_date)
                    news_list.append({
                        "title": title,
                        "url": href,
                        "source": "journal.topvisor.com",
                        "date": parsed_date,
                        "img": ""
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге topvisor: {e}")
            
        return news_list

    def parse_habr(self) -> List[Dict]:
        """Парсинг habr.com"""
        news_list = []
        url = "https://habr.com/ru/hubs/seo/articles/"
        soup = self.safe_request(url)
        
        if not soup:
            return news_list
            
        try:
            items = soup.select('article.tm-articles-list__item')
            
            for item in items:
                time_el = item.select_one('time[datetime]')
                news_date = time_el.get("datetime", "") if time_el else ""
                
                if not self.is_recent_news(news_date):
                    continue
                    
                link_el = item.select_one('h2.tm-title > a.tm-title__link')
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if href.startswith("/"):
                    href = urljoin(url, href)
                    
                title = link_el.get_text(strip=True)
                
                img_el = item.select_one('img.tm-article-snippet__lead-image')
                img_url = img_el.get("src", "") if img_el else ""
                
                if title:
                    parsed_date = self._parse_date(news_date)
                    news_list.append({
                        "title": title,
                        "url": href,
                        "source": "habr.com",
                        "date": parsed_date,
                        "img": img_url
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге habr.com: {e}")
            
        return news_list

    def parse_seofaqt(self) -> List[Dict]:
        """Парсинг seofaqt.ru"""
        news_list = []
        url = "https://seofaqt.ru/"
        soup = self.safe_request(url)
        
        if not soup:
            return news_list
            
        try:
            items = soup.select('div.white-box-question')
            
            for item in items:
                date_el = item.select_one("div.question-footer p:last-child")
                news_date = date_el.get_text(strip=True) if date_el else ""
                
                if not self.is_recent_news(news_date):
                    continue
                    
                channel_el = item.select_one("div.question-header-channel a")
                channel_name = channel_el.get_text(strip=True) if channel_el else ""
                
                link_el = item.select_one("a.question-content-link")
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if href.startswith("/"):
                    href = urljoin(url, href)
                    
                content_el = item.select_one("div.question-content p")
                title = content_el.get_text(strip=True) if content_el else ""
                
                if channel_name:
                    title = f"[{channel_name}] {title}"
                    
                if title:
                    parsed_date = self._parse_date(news_date)
                    news_list.append({
                        "title": title,
                        "url": href,
                        "source": "seofaqt.ru",
                        "date": parsed_date,
                        "img": ""
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге seofaqt.ru: {e}")
            
        return news_list

    def parse_pixelplus(self) -> List[Dict]:
        """Парсинг tools.pixelplus.ru"""
        news_list = []
        url = "https://tools.pixelplus.ru/news/"
        soup = self.safe_request(url)
        
        if not soup:
            return news_list
            
        try:
            items = soup.select('article.news-card')
            
            for item in items:
                date_el = item.select_one("div.news-card__date")
                news_date = date_el.get_text(strip=True) if date_el else ""
                
                if not self.is_recent_news(news_date):
                    continue
                    
                link_el = item.select_one("a.news-card__title")
                if not link_el:
                    continue
                    
                href = link_el.get("href", "")
                if href.startswith("/"):
                    href = urljoin(url, href)
                    
                title = link_el.get_text(strip=True)
                
                img_el = item.select_one("div.news-card__img img")
                img_url = ""
                if img_el and img_el.get("src"):
                    img_src = img_el["src"]
                    if img_src.startswith("/"):
                        img_url = urljoin(url, img_src)
                    else:
                        img_url = img_src
                        
                if title:
                    parsed_date = self._parse_date(news_date)
                    news_list.append({
                        "title": title,
                        "url": href,
                        "source": "tools.pixelplus.ru",
                        "date": parsed_date,
                        "img": img_url
                    })
                    
        except Exception as e:
            logger.error(f"Ошибка при парсинге pixelplus: {e}")
            
        return news_list

    def parse_all_sources(self) -> List[Dict]:
        """Парсинг всех источников"""
        all_news = []
        parsers = [
            self.parse_seonews,
            self.parse_vcru,
            self.parse_topvisor,
            self.parse_habr,
            self.parse_seofaqt,
            self.parse_pixelplus
        ]
        
        for parser in parsers:
            try:
                news = parser()
                all_news.extend(news)
                logger.info(f"Получено {len(news)} новостей из {parser.__name__}")
                time.sleep(1)  # Пауза между запросами
            except Exception as e:
                logger.error(f"Ошибка в парсере {parser.__name__}: {e}")
                
        # Сортируем по дате
        all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        logger.info(f"Всего получено {len(all_news)} новостей")
        return all_news

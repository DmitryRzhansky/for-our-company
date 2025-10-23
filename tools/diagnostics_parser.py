import requests
import socket
import ssl
import subprocess
import platform
import re
import dns.resolver
import dns.exception
from urllib.parse import urlparse
from datetime import datetime, timedelta
import json


class SiteDiagnostics:
    """Класс для диагностики сайтов"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def ping_site(self, url):
        """Ping проверка сайта"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc or parsed_url.path
            
            # Определяем команду ping в зависимости от ОС
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "4", domain]
            else:
                cmd = ["ping", "-c", "4", domain]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Парсим время отклика
                output = result.stdout
                times = re.findall(r'time[<=](\d+(?:\.\d+)?)', output)
                if times:
                    avg_time = sum(float(t) for t in times) / len(times)
                    return {
                        'status': 'success',
                        'domain': domain,
                        'avg_time': round(avg_time, 2),
                        'times': [float(t) for t in times],
                        'raw_output': output
                    }
                else:
                    return {
                        'status': 'success',
                        'domain': domain,
                        'avg_time': 0,
                        'times': [],
                        'raw_output': output
                    }
            else:
                return {
                    'status': 'error',
                    'domain': domain,
                    'error': result.stderr,
                    'raw_output': result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'domain': domain,
                'error': 'Ping timeout'
            }
        except Exception as e:
            return {
                'status': 'error',
                'domain': domain,
                'error': str(e)
            }
    
    def check_http_status(self, url):
        """Проверка HTTP статуса и редиректов"""
        try:
            # Нормализуем URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, allow_redirects=False, timeout=10)
            
            redirects = []
            current_url = url
            
            # Отслеживаем редиректы
            while response.status_code in [301, 302, 303, 307, 308]:
                redirects.append({
                    'from': current_url,
                    'to': response.headers.get('Location', ''),
                    'status': response.status_code,
                    'reason': response.reason
                })
                
                if not response.headers.get('Location'):
                    break
                    
                current_url = response.headers['Location']
                response = self.session.get(current_url, allow_redirects=False, timeout=10)
            
            return {
                'status': 'success',
                'final_url': current_url,
                'final_status': response.status_code,
                'final_reason': response.reason,
                'redirects': redirects,
                'headers': dict(response.headers),
                'response_time': response.elapsed.total_seconds()
            }
            
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'error': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'connection_error',
                'error': 'Connection failed'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_ssl_certificate(self, url):
        """Проверка SSL сертификата"""
        try:
            parsed_url = urlparse(url if url.startswith(('http://', 'https://')) else 'https://' + url)
            domain = parsed_url.netloc or parsed_url.path
            port = parsed_url.port or 443
            
            # Создаем SSL контекст
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Парсим даты
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    return {
                        'status': 'success',
                        'domain': domain,
                        'issuer': cert.get('issuer', {}),
                        'subject': cert.get('subject', {}),
                        'not_before': not_before.isoformat(),
                        'not_after': not_after.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'serial_number': cert.get('serialNumber', ''),
                        'version': cert.get('version', ''),
                        'is_valid': days_until_expiry > 0
                    }
                    
        except socket.timeout:
            return {
                'status': 'timeout',
                'error': 'SSL connection timeout'
            }
        except ssl.SSLError as e:
            return {
                'status': 'ssl_error',
                'error': f'SSL Error: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_dns_info(self, domain):
        """Получение DNS информации"""
        try:
            # Очищаем домен
            if domain.startswith(('http://', 'https://')):
                domain = urlparse(domain).netloc
            domain = domain.replace('www.', '')
            
            dns_info = {}
            
            # A записи (IPv4)
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                dns_info['A'] = [str(record) for record in a_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                dns_info['A'] = []
            except Exception as e:
                dns_info['A'] = [f'Error: {str(e)}']
            
            # AAAA записи (IPv6)
            try:
                aaaa_records = dns.resolver.resolve(domain, 'AAAA')
                dns_info['AAAA'] = [str(record) for record in aaaa_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                dns_info['AAAA'] = []
            except Exception as e:
                dns_info['AAAA'] = [f'Error: {str(e)}']
            
            # MX записи (почтовые серверы)
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                dns_info['MX'] = [{'priority': record.preference, 'exchange': str(record.exchange)} for record in mx_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                dns_info['MX'] = []
            except Exception as e:
                dns_info['MX'] = [f'Error: {str(e)}']
            
            # CNAME записи
            try:
                cname_records = dns.resolver.resolve(domain, 'CNAME')
                dns_info['CNAME'] = [str(record) for record in cname_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                dns_info['CNAME'] = []
            except Exception as e:
                dns_info['CNAME'] = [f'Error: {str(e)}']
            
            # TXT записи
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                dns_info['TXT'] = [str(record).strip('"') for record in txt_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                dns_info['TXT'] = []
            except Exception as e:
                dns_info['TXT'] = [f'Error: {str(e)}']
            
            # NS записи (серверы имен)
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                dns_info['NS'] = [str(record) for record in ns_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                dns_info['NS'] = []
            except Exception as e:
                dns_info['NS'] = [f'Error: {str(e)}']
            
            return {
                'status': 'success',
                'domain': domain,
                'records': dns_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'domain': domain,
                'error': str(e)
            }
    
    def get_whois_info(self, domain):
        """Получение WHOIS информации"""
        try:
            # Очищаем домен
            if domain.startswith(('http://', 'https://')):
                domain = urlparse(domain).netloc
            domain = domain.replace('www.', '')
            
            # Простая WHOIS проверка через whois команду
            try:
                result = subprocess.run(['whois', domain], capture_output=True, text=True, timeout=30)
                whois_data = result.stdout
                
                # Парсим основные поля
                info = {}
                
                # Регистратор
                registrar_match = re.search(r'Registrar:\s*(.+)', whois_data, re.IGNORECASE)
                if registrar_match:
                    info['registrar'] = registrar_match.group(1).strip()
                
                # Дата создания
                created_match = re.search(r'Creation Date:\s*(.+)', whois_data, re.IGNORECASE)
                if created_match:
                    created_str = created_match.group(1).strip()
                    info['created'] = created_str
                    # Парсим дату для расчета возраста
                    try:
                        # Пробуем разные форматы дат
                        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%Y.%m.%d', '%d.%m.%Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%d-%b-%Y']:
                            try:
                                # Берем только дату, убираем время
                                date_part = created_str.split()[0]
                                created_date = datetime.strptime(date_part, fmt)
                                age_days = (datetime.now() - created_date).days
                                info['age_days'] = age_days
                                info['age_years'] = age_days // 365
                                print(f"Domain age calculated: {age_days} days, {age_days // 365} years")
                                break
                            except Exception as e:
                                print(f"Date parsing failed for format {fmt}: {e}")
                                continue
                    except Exception as e:
                        print(f"Age calculation failed: {e}")
                        pass
                
                # Дата истечения
                expiry_match = re.search(r'Registry Expiry Date:\s*(.+)', whois_data, re.IGNORECASE)
                if expiry_match:
                    info['expires'] = expiry_match.group(1).strip()
                
                # Статус
                status_match = re.search(r'Status:\s*(.+)', whois_data, re.IGNORECASE)
                if status_match:
                    info['status'] = status_match.group(1).strip()
                
                return {
                    'status': 'success',
                    'domain': domain,
                    'info': info,
                    'raw_data': whois_data
                }
                
            except subprocess.TimeoutExpired:
                return {
                    'status': 'timeout',
                    'domain': domain,
                    'error': 'WHOIS timeout'
                }
            except FileNotFoundError:
                return {
                    'status': 'error',
                    'domain': domain,
                    'error': 'WHOIS command not found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'domain': domain,
                'error': str(e)
            }
    
    def run_full_diagnostics(self, url):
        """Полный анализ сайта"""
        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'ping': None,
            'http': None,
            'ssl': None,
            'dns': None,
            'whois': None
        }
        
        # Ping проверка
        results['ping'] = self.ping_site(url)
        
        # HTTP статус
        results['http'] = self.check_http_status(url)
        
        # SSL сертификат
        results['ssl'] = self.check_ssl_certificate(url)
        
        # DNS информация
        results['dns'] = self.get_dns_info(url)
        
        # WHOIS информация
        results['whois'] = self.get_whois_info(url)
        
        return results

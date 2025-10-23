#!/bin/bash

# Скрипт для настройки автоматического парсинга новостей
# Запускается каждое воскресенье в 9:00

# Получаем путь к проекту
PROJECT_PATH="/home/dmitriy/Видео/for-our-company"

# Создаем cron задачу
(crontab -l 2>/dev/null; echo "0 9 * * 0 cd $PROJECT_PATH && python3 manage.py parse_news --cleanup >> /tmp/news_parser.log 2>&1") | crontab -

echo "Cron задача добавлена!"
echo "Парсинг новостей будет запускаться каждое воскресенье в 9:00"
echo "Логи будут сохраняться в /tmp/news_parser.log"
echo ""
echo "Для просмотра текущих cron задач выполните: crontab -l"
echo "Для удаления cron задачи выполните: crontab -e"

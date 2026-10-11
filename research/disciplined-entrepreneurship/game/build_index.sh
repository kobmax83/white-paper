#!/bin/sh
# Собирает из startup-quest.html (версия для Claude Artifact без <html>/<head>) полные HTML-документы:
#   index.html          — для хостинга (Vercel и т.п.);
#   Стартап-квест.html  — тот же файл с названием игры, чтобы отправить и открыть как приложение.
# В <head> встраиваются иконка и название приложения для «Добавить на экран „Домой“».
cd "$(dirname "$0")"
ICON_SVG=$(base64 -w0 icon.svg)
ICON_PNG=$(base64 -w0 icon-180.png)
{
  printf '<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="description" content="Игра из 8 миссий по методике MIT Disciplined Entrepreneurship для подростков.">\n'
  printf '<meta name="application-name" content="Стартап-квест">\n'
  printf '<meta name="apple-mobile-web-app-title" content="Стартап-квест">\n'
  printf '<meta name="apple-mobile-web-app-capable" content="yes">\n'
  printf '<meta name="mobile-web-app-capable" content="yes">\n'
  printf '<meta name="theme-color" content="#2b95d6">\n'
  printf '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,%s">\n' "$ICON_SVG"
  printf '<link rel="apple-touch-icon" href="data:image/png;base64,%s">\n' "$ICON_PNG"
  printf '<style>html{color-scheme:light}body{margin:0}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n'
  printf '</head>\n<body>\n'
  cat startup-quest.html
  printf '\n</body>\n</html>\n'
} > index.html
cp index.html "Стартап-квест.html"

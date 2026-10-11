#!/bin/sh
# Собирает index.html (полный HTML-документ для хостинга, например Vercel)
# из startup-quest.html (версия для Claude Artifact без <html>/<head>).
cd "$(dirname "$0")"
{
  printf '<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="description" content="Игра из 8 миссий по методике MIT Disciplined Entrepreneurship для подростков.">\n'
  printf '<style>html{color-scheme:light}body{margin:0}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n'
  printf '</head>\n<body>\n'
  cat startup-quest.html
  printf '\n</body>\n</html>\n'
} > index.html

#!/usr/bin/env python3
"""Генератор русской векторной версии плаката «Disciplined Entrepreneurship: 24 шага».

Весь текст переводится в кривые (шрифт Inter), поэтому SVG/PDF печатаются одинаково
на любом компьютере. Запуск: python3 make_poster.py  → poster-ru.svg
"""
import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/opentype/inter"
W, H = 1190, 1684  # пропорции A-формата (1 : √2)

# ---------------------------------------------------------------- шрифты → кривые
WEIGHTS = {
    "regular": "Inter-Regular.otf",
    "medium": "Inter-Medium.otf",
    "semibold": "Inter-SemiBold.otf",
    "bold": "Inter-Bold.otf",
    "extrabold": "Inter-ExtraBold.otf",
    "black": "InterDisplay-Black.otf",
}


class Font:
    def __init__(self, key, path):
        self.key = key
        self.tt = TTFont(path)
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.hmtx = self.tt["hmtx"]
        self.defs = {}

    def glyph(self, ch):
        name = self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))
        return name

    def adv(self, ch):
        return self.hmtx[self.glyph(ch)][0]

    def width(self, s, size, tracking=0):
        return sum(self.adv(c) for c in s) * size / self.upm + tracking * size * max(len(s) - 1, 0)

    def ref(self, name):
        gid = f"{self.key}-{name}"
        if gid not in self.defs:
            pen = SVGPathPen(self.gs)
            self.gs[name].draw(pen)
            self.defs[gid] = pen.getCommands()
        return gid


FONTS = {k: Font(k, os.path.join(FONT_DIR, v)) for k, v in WEIGHTS.items()}


def text(s, x, y, size, weight="regular", fill="#1d2b3a", anchor="start", rotate=0, tracking=0.0, opacity=None):
    """Строка текста кривыми. tracking — доп. межбуквенный интервал в долях кегля."""
    f = FONTS[weight]
    w = f.width(s, size, tracking)
    dx = {"start": 0, "middle": -w / 2, "end": -w}[anchor]
    k = size / f.upm
    parts, cx = [], 0.0
    for ch in s:
        name = f.glyph(ch)
        if ch != " ":
            parts.append(f'<use href="#{f.ref(name)}" x="{cx:.0f}"/>')
        cx += f.adv(ch) + tracking * f.upm
    op = f' opacity="{opacity}"' if opacity is not None else ""
    tr = f"translate({x:.2f} {y:.2f})"
    if rotate:
        tr += f" rotate({rotate:.2f})"
    tr += f" translate({dx:.2f} 0) scale({k:.5f} {-k:.5f})"
    return f'<g transform="{tr}" fill="{fill}"{op}>{"".join(parts)}</g>'


def wrap(s, size, weight, maxw):
    f = FONTS[weight]
    lines, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if f.width(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- содержание
INK = "#1d2b3a"
BG = "#fbf7ef"
THEMES = [
    # цвет, цвет текста на клетке, вопрос
    ("#2b95d6", "#ffffff", "Кто ваш клиент?"),
    ("#e23d4f", "#ffffff", "Что вы можете сделать для клиента?"),
    ("#f4b72a", INK, "Как клиент приобретает ваш продукт?"),
    ("#74b63c", "#ffffff", "Как вы зарабатываете на продукте?"),
    ("#f27b21", "#ffffff", "Как спроектировать и построить продукт?"),
    ("#8a5bbd", "#ffffff", "Как масштабировать бизнес?"),
]

# номер: (тема, подпись на дороге, название в таблице, описание)
STEPS = {
    1: (0, "Сегментация рынка", "Сегментация рынка",
        "Перечислите 6–12 возможных рынков для идеи и изучите их в живых разговорах с клиентами."),
    2: (0, "Рынок-плацдарм", "Выбор рынка-плацдарма",
        "Выберите один узкий рынок, где можно быстро стать лидером. Остальные — потом."),
    3: (0, "Профиль пользователя", "Профиль конечного пользователя",
        "Опишите типичного пользователя: кто он, чем живёт, что ценит и чего боится."),
    4: (0, "Объём плацдарма (TAM)", "Объём рынка-плацдарма (TAM)",
        "Посчитайте снизу вверх: число клиентов × годовой доход с одного клиента."),
    5: (0, "Персона плацдарма", "Персона плацдарма",
        "Опишите одного реального клиента-персону и сверяйте с ним каждое решение."),
    6: (1, "Полный цикл использования", "Полный цикл использования",
        "Весь путь клиента: от осознания проблемы до покупки, использования и рекомендаций."),
    7: (1, "Спецификация продукта", "Общая спецификация продукта",
        "Покажите продукт наглядно: макет или брошюра о выгодах, а не о функциях."),
    8: (1, "Ценность в цифрах", "Ценностное предложение в цифрах",
        "Выразите выгоду количественно: как у клиента сейчас и как будет с продуктом."),
    9: (0, "Первые 10 клиентов", "Следующие 10 клиентов",
        "Найдите 10 реальных людей, похожих на персону, и подтвердите гипотезы. Не вышло — назад."),
    10: (1, "Ядро и защита", "Определите своё ядро",
         "То, что даёт устойчивое преимущество и что конкурентам трудно скопировать."),
    11: (1, "Конкурентная позиция", "Конкурентная позиция",
         "Сравните себя с конкурентами и статус-кво по двум главным для персоны критериям."),
    12: (2, "Кто решает (DMU)", "Кто принимает решение (DMU)",
         "Инициатор, пользователь, плательщик, влиятели и те, у кого есть право вето."),
    13: (2, "Путь к оплате", "Процесс привлечения клиента",
         "Распишите шаг за шагом, как клиент приходит к оплате: сроки, бюджеты, барьеры."),
    14: (5, "Объём следующих рынков", "Объём следующих рынков",
         "Оцените рынки после плацдарма — это показывает, что бизнес может вырасти."),
    15: (3, "Бизнес-модель", "Бизнес-модель",
         "Как вы забираете часть созданной ценности: подписка, продажа, лицензия, комиссия."),
    16: (3, "Ценообразование", "Ценообразование",
         "Цена определяется ценностью для клиента, а не вашей себестоимостью."),
    17: (3, "Ценность клиента (LTV)", "Ценность клиента за всё время (LTV)",
         "Сколько прибыли принесёт один клиент за весь срок работы с вами."),
    18: (3, "Процесс продаж", "Процесс продаж",
         "Каналы продаж на короткий, средний и долгий срок."),
    19: (3, "Стоимость привлечения (COCA)", "Стоимость привлечения клиента (COCA)",
         "Во сколько обходится один новый клиент. Правило: LTV ≥ 3 × COCA."),
    20: (4, "Ключевые допущения", "Ключевые допущения",
         "Выпишите главные непроверенные допущения, от которых зависит успех."),
    21: (4, "Проверка допущений", "Проверка допущений",
         "Проверьте каждое допущение быстрым и дешёвым экспериментом."),
    22: (4, "Минимальный продукт (MVBP)", "Минимальный продукт за деньги (MVBP)",
         "Минимальный продукт, который клиент использует, ценит и оплачивает."),
    23: (4, "«Собаки едят корм»", "Докажите, что «собаки едят корм»",
         "Покажите цифрами, что клиенты действительно покупают и пользуются продуктом."),
    24: (5, "План продукта", "План развития продукта",
         "План развития продукта и выхода на следующие рынки."),
}

# ---------------------------------------------------------------- геометрия дороги
LEFT, RIGHT = 250, 975
ROW_Y = [322, 512, 702, 892]
ROAD_W = 118
WAVE = 34


def build_centerline():
    pts = []
    L = RIGHT - LEFT
    n = 900
    for i, y0 in enumerate(ROW_Y):
        d = 1 if i % 2 == 0 else -1
        for j in range(n + 1):
            t = j / n
            x = LEFT + t * L if d > 0 else RIGHT - t * L
            u = (x - LEFT) / L
            y = y0 + WAVE * math.sin(2 * math.pi * u) * math.sin(math.pi * u) ** 2
            pts.append((x, y))
        if i < len(ROW_Y) - 1:
            cy = (y0 + ROW_Y[i + 1]) / 2
            r = (ROW_Y[i + 1] - y0) / 2
            cx = RIGHT if d > 0 else LEFT
            for j in range(1, 300):
                a = -math.pi / 2 + math.pi * j / 300
                x = cx + d * r * math.cos(a)
                y = cy + r * math.sin(a)
                pts.append((x, y))
    cum = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(x1 - x0, y1 - y0))
    return pts, cum


PTS, CUM = build_centerline()
TOTAL = CUM[-1]
SEG = TOTAL / 24


def at(s):
    s = max(0.0, min(TOTAL, s))
    lo, hi = 0, len(CUM) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if CUM[mid] <= s:
            lo = mid
        else:
            hi = mid
    span = CUM[hi] - CUM[lo] or 1
    t = (s - CUM[lo]) / span
    (x0, y0), (x1, y1) = PTS[lo], PTS[hi]
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t


def tangent(s):
    x0, y0 = at(s - 1.5)
    x1, y1 = at(s + 1.5)
    a = math.atan2(y1 - y0, x1 - x0)
    return a


def offset(s, d):
    x, y = at(s)
    a = tangent(s)
    return x - math.sin(a) * d, y + math.cos(a) * d  # d>0 — справа по ходу движения


def band(s0, s1, half):
    n = max(8, int((s1 - s0) / 2))
    left = [offset(s0 + (s1 - s0) * i / n, -half) for i in range(n + 1)]
    right = [offset(s0 + (s1 - s0) * i / n, half) for i in range(n + 1)]
    poly = left + right[::-1]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + " Z"


def polyline(s0, s1, step=3):
    n = max(2, int((s1 - s0) / step))
    return "M" + " L".join("%.1f,%.1f" % at(s0 + (s1 - s0) * i / n) for i in range(n + 1))


# ---------------------------------------------------------------- иконки (собственные)
def rocket(x, y, scale=1.0, rot=0):
    return f'''<g transform="translate({x} {y}) rotate({rot}) scale({scale})">
  <path d="M-9,30 Q0,78 9,30 Z" fill="#f27b21"/>
  <path d="M-5,30 Q0,58 5,30 Z" fill="#f4b72a"/>
  <path d="M-15,6 L-31,34 L-14,28 Z" fill="#e23d4f" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M15,6 L31,34 L14,28 Z" fill="#e23d4f" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M0,-50 C20,-34 22,-2 15,30 L-15,30 C-22,-2 -20,-34 0,-50 Z" fill="#ffffff" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>
  <path d="M-11,-30 Q0,-40 11,-30" fill="none" stroke="#e23d4f" stroke-width="5" stroke-linecap="round"/>
  <circle cx="0" cy="-8" r="9" fill="#2b95d6" stroke="{INK}" stroke-width="3"/>
  <path d="M-6,30 L-6,22 M0,30 L0,20 M6,30 L6,22" stroke="{INK}" stroke-width="2"/>
</g>'''


def flag(x, y, color="#e23d4f"):
    return f'''<g transform="translate({x} {y})">
  <path d="M0,0 L0,-62" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M0,-62 L40,-52 L0,-40 Z" fill="{color}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>
  <ellipse cx="0" cy="2" rx="18" ry="5" fill="{INK}" opacity="0.15"/>
</g>'''


def castle(x, y):
    c = "#e23d4f"
    return f'''<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round">
  <path d="M-34,0 L-34,-34 L-26,-34 L-26,-28 L-18,-28 L-18,-34 L-10,-34 L-10,-28 L-2,-28 L-2,-34 L6,-34 L6,-28 L14,-28 L14,-34 L22,-34 L22,-28 L30,-28 L30,-34 L34,-34 L34,0 Z" fill="#ffffff"/>
  <path d="M-8,0 L-8,-14 Q0,-24 8,-14 L8,0 Z" fill="{INK}"/>
  <path d="M-4,-40 L-4,-58 L14,-52 L-4,-46" fill="{c}"/>
  <path d="M-46,4 Q0,16 46,4" fill="none" stroke="#2b95d6" stroke-width="5" stroke-linecap="round"/>
</g>'''


def megaphone(x, y):
    return f'''<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">
  <path d="M-24,-8 L-24,8 L-12,8 L20,22 L20,-22 L-12,-8 Z" fill="#ffffff"/>
  <path d="M-12,-8 L-12,8" fill="none"/>
  <path d="M-18,8 L-14,22 L-6,22 L-8,10" fill="#e23d4f"/>
  <path d="M28,-12 L36,-18 M30,0 L40,0 M28,12 L36,18" fill="none"/>
</g>'''


def people(x, y, n=5, color="#2b95d6"):
    out = [f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2">']
    for i in range(n):
        px = (i - (n - 1) / 2) * 17
        out.append(f'<circle cx="{px}" cy="-26" r="6" fill="#ffffff"/>')
        out.append(f'<path d="M{px-8},0 L{px-8},-10 Q{px},-20 {px+8},-10 L{px+8},0 Z" fill="{color}"/>')
    out.append("</g>")
    return "".join(out)


def magnifier(x, y):
    return f'''<g transform="translate({x} {y})" stroke="{INK}" stroke-width="3" stroke-linecap="round">
  <circle cx="-4" cy="-6" r="15" fill="#ffffff"/>
  <path d="M7,5 L22,20" stroke-width="6"/>
  <path d="M-11,-10 Q-6,-16 1,-15" fill="none" stroke="#f27b21"/>
</g>'''


def coins(x, y):
    out = [f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.2">']
    for i in range(4):
        out.append(f'<ellipse cx="0" cy="{-i*8}" rx="17" ry="6" fill="#f4b72a"/>')
    out.append(f'<ellipse cx="30" cy="0" rx="17" ry="6" fill="#f4b72a"/><ellipse cx="30" cy="-8" rx="17" ry="6" fill="#f4b72a"/>')
    out.append("</g>")
    return "".join(out)


def dogbowl(x, y):
    return f'''<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">
  <path d="M-18,0 L-14,-16 L14,-16 L18,0 Z" fill="#e23d4f"/>
  <path d="M-10,-16 Q-6,-24 0,-18 Q6,-25 10,-16" fill="#a0612d"/>
  <path d="M30,0 L30,-26 Q30,-44 46,-46 L56,-56 L58,-44 Q66,-40 64,-30 L50,-28 L48,0" fill="#ffffff"/>
  <circle cx="54" cy="-38" r="2" fill="{INK}"/>
</g>'''


def chart_up(x, y):
    return f'''<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">
  <rect x="-30" y="-14" width="12" height="14" fill="#8a5bbd"/>
  <rect x="-14" y="-26" width="12" height="26" fill="#8a5bbd"/>
  <rect x="2" y="-40" width="12" height="40" fill="#8a5bbd"/>
  <path d="M-34,-24 L-8,-44 L18,-56" fill="none"/>
  <path d="M10,-60 L19,-56 L14,-48" fill="none"/>
</g>'''


def bulb(x, y):
    return f'''<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">
  <path d="M-8,0 L8,0 M-7,-6 L7,-6" fill="none"/>
  <path d="M-8,-10 Q-20,-22 -16,-36 Q-10,-52 0,-52 Q10,-52 16,-36 Q20,-22 8,-10 Z" fill="#f4b72a"/>
  <path d="M-26,-50 L-32,-56 M26,-50 L32,-56 M0,-60 L0,-68" fill="none"/>
</g>'''


# ---------------------------------------------------------------- сборка
def main():
    out = []
    add = out.append

    # --- заголовок
    add(text("ДИСЦИПЛИНИРОВАННОЕ", W / 2, 96, 62, "black", "#e23d4f", "middle", tracking=0.01))
    add(text("ПРЕДПРИНИМАТЕЛЬСТВО", W / 2, 162, 62, "black", INK, "middle", tracking=0.01))
    sub = "24 ШАГА К УСПЕШНОМУ СТАРТАПУ"
    sw = FONTS["bold"].width(sub, 21, 0.12)
    add(text(sub, W / 2, 204, 21, "bold", INK, "middle", tracking=0.12))
    for sgn in (-1, 1):
        x0 = W / 2 + sgn * (sw / 2 + 18)
        add(f'<path d="M{x0:.1f},197 L{x0 + sgn * 70:.1f},197" stroke="#e23d4f" stroke-width="3" stroke-linecap="round"/>')
        add(f'<circle cx="{x0 + sgn * 80:.1f}" cy="197" r="3.5" fill="#e23d4f"/>')

    # --- дорога: тень, обводка, клетки
    full = polyline(0, TOTAL)
    add(f'<path d="{full}" transform="translate(5 8)" fill="none" stroke="{INK}" stroke-opacity="0.13" stroke-width="{ROAD_W + 12}" stroke-linejoin="round"/>')
    add(f'<path d="{full}" fill="none" stroke="{INK}" stroke-width="{ROAD_W + 12}" stroke-linejoin="round"/>')

    # стрелка-финиш после шага 24
    ex, ey = at(TOTAL)
    a = tangent(TOTAL - 2)
    ca, sa = math.cos(a), math.sin(a)

    def P(fw, side):  # точка относительно конца дороги
        return ex + ca * fw - sa * side, ey + sa * fw + ca * side

    hw = ROAD_W / 2
    arrow = [P(-2, -hw), P(14, -hw), P(14, -hw - 22), P(64, 0), P(14, hw + 22), P(14, hw), P(-2, hw)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in arrow) + " Z"
    add(f'<path d="{d}" fill="{THEMES[5][0]}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')

    for n in range(1, 25):
        th = THEMES[STEPS[n][0]]
        s0, s1 = SEG * (n - 1), SEG * n
        add(f'<path d="{band(s0, s1, hw)}" fill="{th[0]}" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>')
    # тонкая светлая «разметка» по краям дороги
    for side in (-1, 1):
        pts = [offset(s, side * (hw - 7)) for s in [i * 3 for i in range(int(TOTAL / 3) + 1)]]
        dd = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        add(f'<path d="{dd}" fill="none" stroke="#ffffff" stroke-opacity="0.45" stroke-width="1.6" stroke-dasharray="2 7" stroke-linecap="round"/>')

    # подписи на клетках
    for n in range(1, 25):
        ti, label, *_ = STEPS[n]
        th = THEMES[ti]
        sm = SEG * (n - 0.5)
        x, y = at(sm)
        ang = math.degrees(tangent(sm))
        while ang > 90:
            ang -= 180
        while ang <= -90:
            ang += 180
        size = 12.5
        lines = wrap(label, size, "bold", SEG - 34)
        while len(lines) > 2 and size > 10.5:
            size -= 0.5
            lines = wrap(label, size, "bold", SEG - 30)
        lead = size * 1.18
        num_size = 34
        block = num_size * 0.72 + 7 + lead * (len(lines) - 1) + size * 0.72
        top = -block / 2
        r = math.radians(ang)

        def loc(lx, ly):
            return x + lx * math.cos(r) - ly * math.sin(r), y + lx * math.sin(r) + ly * math.cos(r)

        nx, ny = loc(0, top + num_size * 0.72)
        add(text(str(n), nx, ny, num_size, "black", th[1], "middle", rotate=ang))
        for i, ln in enumerate(lines):
            lx, ly = loc(0, top + num_size * 0.72 + 7 + size * 0.72 + i * lead)
            add(text(ln.upper(), lx, ly, size, "bold", th[1], "middle", rotate=ang, tracking=0.02))

    # --- пунктирные возвраты (итерации)
    def up_side(sv):  # сторона «вверх» для клетки: ряд слева направо → -1, справа налево → +1
        return -1 if math.cos(tangent(sv)) > 0 else 1

    def ret(n_from, n_to, label=None, lx=0, ly=0, anchor="start", f_at=0.5, t_at=0.5):
        """Пунктирный возврат из клетки нижнего ряда к клетке верхнего ряда (через промежуток)."""
        s_from, s_to = SEG * (n_from - 1 + f_at), SEG * (n_to - 1 + t_at)
        x0, y0 = offset(s_from, up_side(s_from) * (hw + 12))
        x1, y1 = offset(s_to, -up_side(s_to) * (hw + 16))
        mx, my = (x0 + x1) / 2 + (x1 - x0) * 0.15, (y0 + y1) / 2
        add(f'<path d="M{x0:.1f},{y0:.1f} Q{mx:.1f},{my:.1f} {x1:.1f},{y1:.1f}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-dasharray="7 6" stroke-linecap="round" marker-end="url(#arr)"/>')
        if label:
            for k, ln in enumerate(label.split("|")):
                add(text(ln, (x0 + x1) / 2 + lx, (y0 + y1) / 2 + ly + k * 14, 11.5, "semibold", INK, anchor, opacity=0.8))

    ret(9, 3, "нет 10 клиентов?|вернитесь назад", 14, -4)
    ret(16, 8, "цена следует|из ценности", 24, -2, f_at=0.85, t_at=0.8)
    ret(23, 15, "клиенты не платят?|меняйте модель", 14, -4, t_at=0.4)
    ret(21, 17, "проверки уточняют|экономику", 14, -4)

    # --- метки и иконки
    sx, sy = at(0)
    add(f'<rect x="54" y="{sy - 110:.0f}" width="168" height="38" rx="19" fill="{INK}"/>')
    add(text("НАЧНИТЕ ЗДЕСЬ", 138, sy - 85, 15, "extrabold", "#ffffff", "middle", tracking=0.06))
    add(f'<path d="M138,{sy - 70:.0f} Q140,{sy:.0f} {sx - 22:.0f},{sy:.0f}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" marker-end="url(#arr)"/>')
    add(bulb(92, sy + 66))

    def gap_y(x, upper_row):  # середина промежутка между рядами upper_row и upper_row+1
        L = RIGHT - LEFT
        u = (x - LEFT) / L
        wv = WAVE * math.sin(2 * math.pi * u) * math.sin(math.pi * u) ** 2
        return (ROW_Y[upper_row] + ROW_Y[upper_row + 1]) / 2 + wv

    x2, y2 = offset(SEG * 1.5, -(hw + 6))
    add(flag(x2 - 10, y2))
    add(castle(470, gap_y(470, 0) + 16))
    add(megaphone(890, gap_y(890, 0) + 2))
    add(people(372, gap_y(372, 1) + 16, 5, THEMES[2][0]))
    add(coins(640, gap_y(640, 2) + 6))
    add(chart_up(330, gap_y(330, 2) + 18))
    x21, y21 = offset(SEG * 20.5, 0)
    add(magnifier(x21 + 20, y21 + hw + 42))
    x23, y23 = offset(SEG * 23.1, 0)
    add(dogbowl(x23 - 40, y23 + hw + 46))
    add(rocket(ex - 92, ey - 84, 1.0, -18))
    for i, (ox, oy) in enumerate([(-60, -6), (-50, 18), (-72, 36)]):
        add(f'<path d="M{ex - 92 + ox:.0f},{ey - 84 + oy:.0f} l-26,8" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="6 6" opacity="0.5"/>')

    # --- подписи под картой
    yb = 1032
    add(text("Узнайте больше о методике, скачайте рабочие листы и присоединяйтесь к сообществу:", 54, yb, 12.5, "medium", INK))
    add(text("www.d-eship.com", 54, yb + 19, 13.5, "extrabold", "#e23d4f"))
    add(text("Книги серии: www.d-eship.com/books", W - 54, yb, 12.5, "medium", INK, "end"))
    add(text("на русском: Б. Олет, «Путеводитель предпринимателя» (МИФ)", W - 54, yb + 19, 12.5, "semibold", "#e23d4f", "end"))

    # --- шесть тем
    top = 1078
    add(f'<path d="M54,{top - 6} L{W - 54},{top - 6}" stroke="{INK}" stroke-width="2"/>')
    add(text("ШЕСТЬ ТЕМ", 54, top + 20, 16, "black", INK, tracking=0.1))
    add(text("Цвет клетки на дороге = тема. Пунктир = возврат к прошлым шагам: путь последовательный, но не линейный.",
             W - 54, top + 19, 11.5, "medium", INK, "end", opacity=0.75))
    colgap, x0 = 12, 54
    weights = [1.27, 1.12, 0.8, 1.12, 0.93, 0.8]
    unit = (W - 2 * 54 - 5 * colgap) / sum(weights)
    colx = [x0 + sum(weights[:k]) * unit + k * colgap for k in range(6)]
    order = [[1, 2, 3, 4, 5, 9], [6, 7, 8, 10, 11], [12, 13], [15, 16, 17, 18, 19], [20, 21, 22, 23], [14, 24]]
    ybox = top + 36
    bottom = 1642
    for i, (col, steps) in enumerate(zip(THEMES, order)):
        cx, colw = colx[i], weights[i] * unit
        add(f'<rect x="{cx:.1f}" y="{ybox}" width="{colw:.1f}" height="{bottom - ybox}" rx="12" fill="{col[0]}" fill-opacity="0.09"/>')
        add(f'<rect x="{cx:.1f}" y="{ybox}" width="{colw:.1f}" height="64" rx="12" fill="{col[0]}"/>')
        add(f'<circle cx="{cx + 22:.1f}" cy="{ybox + 32}" r="14" fill="#ffffff"/>')
        add(text(str(i + 1), cx + 22, ybox + 38.5, 17, "black", col[0] if i != 2 else "#c98f0a", "middle"))
        qs = 11.5
        ql = wrap(col[2].upper(), qs, "extrabold", colw - 50)
        while (len(ql) > 4 or max(FONTS["extrabold"].width(q, qs) for q in ql) > colw - 46) and qs > 8:
            qs -= 0.25
            ql = wrap(col[2].upper(), qs, "extrabold", colw - 50)
        lead = qs * 1.2
        qy = ybox + 32 - (len(ql) - 1) * lead / 2 + qs * 0.36
        for j, ln in enumerate(ql):
            add(text(ln, cx + 42, qy + j * lead, qs, "extrabold", col[1]))
        y = ybox + 90
        for n in steps:
            _, _, title, desc = STEPS[n]
            add(f'<rect x="{cx + 8:.1f}" y="{y - 14:.1f}" width="24" height="18" rx="9" fill="{col[0]}"/>')
            add(text(str(n), cx + 20, y, 11.5, "extrabold", col[1], "middle"))
            tl = wrap(title, 11.5, "bold", colw - 46)
            for j, ln in enumerate(tl):
                add(text(ln, cx + 38, y + j * 14, 11.5, "bold", INK))
            y += 14 * len(tl) + 2
            for ln in wrap(desc, 10.5, "regular", colw - 20):
                add(text(ln, cx + 10, y, 10.5, "regular", "#3b4856"))
                y += 13.4
            y += 11
        print("col", i + 1, "bottom", round(y))
        assert y - 11 < bottom - 8, (i, y)

    # --- подвал
    add(text("Неофициальная русская адаптация по книге Билла Аулета (Олета) «Disciplined Entrepreneurship: 24 Steps to a Successful Startup», MIT / Wiley. Собственный дизайн, перевод и иллюстрации.",
             W / 2, H - 22, 10, "medium", INK, "middle", opacity=0.6))

    defs = []
    for f in FONTS.values():
        for gid, d in f.defs.items():
            defs.append(f'<path id="{gid}" d="{d}"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>Дисциплинированное предпринимательство — 24 шага к успешному стартапу</title>
<defs>
<marker id="arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="{INK}"/></marker>
{"".join(defs)}
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="18" y="18" width="{W - 36}" height="{H - 36}" rx="18" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity="0.18"/>
{chr(10).join(out)}
</svg>
'''
    with open(os.path.join(HERE, "poster-ru.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("ok", len(svg) // 1024, "KB; segment", round(SEG, 1))


if __name__ == "__main__":
    main()

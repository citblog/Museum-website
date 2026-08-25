import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "scripts" / "data"

IMG_W, IMG_H = 1100, 733
EAGER_FIRST = 2


def esc(value):
    return html.escape(str(value), quote=True)


def plural_museums(n):
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} музей"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f"{n} музея"
    return f"{n} музеев"


def load_data():
    site = json.loads((DATA_DIR / "site.json").read_text(encoding="utf-8"))
    regions = {}
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name == "site.json":
            continue
        region = json.loads(path.read_text(encoding="utf-8"))
        regions[region["id"]] = region
    ordered = [regions[rid] for rid in site["regions_order"] if rid in regions]
    return site, ordered


def head_tags(site, title, description, page_file, robots="index, follow"):
    url = site.get("url", "").rstrip("/")
    og_image = site["og_image"]
    lines = [
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'  <title>{esc(title)}</title>',
        f'  <meta name="description" content="{esc(description)}">',
        f'  <meta name="robots" content="{esc(robots)}">',
        '  <meta name="theme-color" content="#050e17">',
        '  <link rel="icon" type="image/svg+xml" href="favicon.svg">',
    ]
    if url:
        canonical = f"{url}/{page_file}"
        lines.append(f'  <link rel="canonical" href="{esc(canonical)}">')
    lines += [
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{esc(title)}">',
        f'  <meta property="og:description" content="{esc(description)}">',
        f'  <meta property="og:image" content="{esc(url + "/" + og_image if url else og_image)}">',
    ]
    if url:
        lines.append(f'  <meta property="og:url" content="{esc(canonical)}">')
    lines += [
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{esc(title)}">',
        f'  <meta name="twitter:description" content="{esc(description)}">',
        f'  <meta name="twitter:image" content="{esc(url + "/" + og_image if url else og_image)}">',
    ]
    return "\n".join(lines)


def render_head(site, title, description, jsonld, page_file, robots="index, follow"):
    tags = head_tags(site, title, description, page_file, robots=robots)
    parts = [
        '<!DOCTYPE html>\n'
        '<html lang="ru">\n'
        '<head>\n'
        f'{tags}\n'
        '  <link rel="stylesheet" href="css/style.css">\n'
        '  <script>document.documentElement.classList.add("js");</script>\n',
    ]
    if jsonld:
        ld = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")
        parts.append(f'  <script type="application/ld+json">{ld}</script>\n')
    parts.append('</head>\n<body>\n')
    return "".join(parts)


def render_header(site, active_file):
    links = [('<a href="index.html"' + (' class="active"' if active_file == "index.html" else "") + '>Главная</a>')]
    for region in REGIONS:
        cls = ' class="active"' if region["file"] == active_file else ""
        links.append(f'<a href="{region["file"]}"{cls}>{esc(region["nav"])}</a>')
    nav = "\n      ".join(links)
    return (
        '<header class="header">\n'
        '  <a href="index.html" class="logo">\n'
        '    <span class="logo-icon" aria-hidden="true">🏛</span>\n'
        f'    {esc(site["name"])}\n'
        '  </a>\n'
        '  <nav class="nav" id="site-nav" aria-label="Основная навигация">\n'
        f'      {nav}\n'
        '  </nav>\n'
        '  <button class="burger" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="site-nav">\n'
        '    <span></span><span></span><span></span>\n'
        '  </button>\n'
        '</header>\n'
    )


def render_footer(site, extra_scripts=""):
    year = date.today().year
    return (
        '<footer class="footer">\n'
        f'  <p>© {year} «{esc(site["name"])}» — образовательный проект. Все изображения принадлежат правообладателям.</p>\n'
        '</footer>\n'
        '\n'
        '<button class="back-to-top" aria-label="Наверх">↑</button>\n'
        '\n'
        f'{extra_scripts}'
        '<script src="js/main.js"></script>\n'
        '</body>\n'
        '</html>\n'
    )


def museum_card(museum, eager=False):
    img_attrs = (
        f'src="{museum["image"]}" alt="{esc(museum["name"])}" width="{IMG_W}" height="{IMG_H}" decoding="async"'
    )
    if not eager:
        img_attrs += ' loading="lazy"'
    return (
        '<article class="museum-card fade-in">\n'
        '  <div class="museum-image">\n'
        f'    <img {img_attrs}>\n'
        f'    <span class="museum-overlay">{esc(museum["city"])}</span>\n'
        '  </div>\n'
        '  <div class="museum-body">\n'
        f'    <h3>{esc(museum["name"])}</h3>\n'
        f'    <div class="museum-city">{esc(museum["city"])}, {esc(museum["country"])}</div>\n'
        f'    <p>{esc(museum["desc"])}</p>\n'
        f'    <a href="{museum["url"]}" class="museum-link" target="_blank" rel="noopener">\n'
        '      Сайт музея\n'
        '      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>\n'
        '    </a>\n'
        '  </div>\n'
        '</article>\n'
    )


def search_block():
    return (
        '<div class="search-bar fade-in">\n'
        '  <span class="search-icon" aria-hidden="true">🔍</span>\n'
        '  <input id="museum-search" type="search" placeholder="Поиск музея..." aria-label="Поиск музея" '
        'autocomplete="off" role="combobox" aria-expanded="false" aria-controls="search-results">\n'
        '  <div class="search-results" id="search-results" role="listbox" hidden></div>\n'
        '</div>\n'
    )


def museums_index_script(regions):
    items = [
        {
            "name": m["name"],
            "city": m["city"],
            "country": m["country"],
            "url": region["file"],
        }
        for region in regions
        for m in region["museums"]
    ]
    payload = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    return f'<script>window.MUSEUMS_INDEX={payload};</script>\n'


def build_index(site, regions):
    total = sum(len(r["museums"]) for r in regions)
    countries = sorted({m["country"] for r in regions for m in r["museums"]})
    stats = (
        '<div class="hero-stats">\n'
        f'        <div class="stat"><span class="stat-number" data-target="{len(regions)}">0</span><span class="stat-label">Регионов</span></div>\n'
        f'        <div class="stat"><span class="stat-number" data-target="{total}">0</span><span class="stat-label">Музеев</span></div>\n'
        f'        <div class="stat"><span class="stat-number" data-target="{len(countries)}">0</span><span class="stat-label">Стран</span></div>\n'
        '      </div>'
    )
    cards = []
    for region in regions:
        cards.append(
            f'    <a href="{region["file"]}" class="region-card fade-in">\n'
            f'      <div class="region-card-visual {region["visual_class"]}">\n'
            f'        <div class="region-visual-emoji" aria-hidden="true">{region["emoji"]}</div>\n'
            '      </div>\n'
            '      <div class="region-card-body">\n'
            f'        <h3>{esc(region["nav"])}</h3>\n'
            f'        <p>{esc(region["card_desc"])}</p>\n'
            '        <div class="region-card-footer">\n'
            f'          <span class="museum-count">{plural_museums(len(region["museums"]))}</span>\n'
            '          <span class="arrow-icon" aria-hidden="true">→</span>\n'
            '        </div>\n'
            '      </div>\n'
            '    </a>\n'
        )
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f'Регионы сайта «{site["name"]}»',
        "numberOfItems": len(regions),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": r["heading"],
                "url": r["file"],
            }
            for i, r in enumerate(regions)
        ],
    }
    parts = [render_head(site, site["index_title"], site["index_description"], jsonld, "index.html")]
    parts.append(render_header(site, "index.html"))
    parts.append('<main class="site-main">\n')
    parts.append(
        '\n<section class="hero">\n'
        '  <div class="hero-content">\n'
        f'    <div class="hero-badge">{esc(site["hero_badge"])}</div>\n'
        f'    <h1>{esc(site["hero_h1"])}</h1>\n'
        f'    <p>{esc(site["hero_p"])}</p>\n'
        f'    {stats}\n'
        '  </div>\n'
        '</section>\n'
        '\n'
        '<section class="section">\n'
        f'{search_block()}'
        '  <div class="section-header fade-in">\n'
        '    <div class="section-label" aria-hidden="true">◆ Выберите регион</div>\n'
        '    <h2 class="section-title">Куда отправимся?</h2>\n'
        '    <p class="section-desc">Каждый регион хранит уникальные сокровища искусства и истории</p>\n'
        '  </div>\n'
        '\n'
        '  <div class="regions-grid">\n\n'
        + "".join(cards) +
        '  </div>\n'
        '</section>\n\n'
    )
    parts.append('</main>\n')
    parts.append(render_footer(site, museums_index_script(regions)))
    (ROOT / "index.html").write_text("".join(parts), encoding="utf-8")


def build_region(site, region):
    museums = region["museums"]
    cards = "".join(museum_card(m, eager=(i < EAGER_FIRST)) for i, m in enumerate(museums))
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": region["heading"],
        "numberOfItems": len(museums),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "Museum",
                    "name": m["name"],
                    "description": m["desc"],
                    "url": m["url"],
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": m["city"],
                        "addressCountry": m["country"],
                    },
                },
            }
            for i, m in enumerate(museums)
        ],
    }
    page = "".join([
        render_head(site, region["page_title"], region["tagline"], jsonld, region["file"]),
        render_header(site, region["file"]),
        '<main class="site-main">\n',
        (
            f'\n<section class="page-hero {region["hero_class"]}">\n'
            f'  <div class="page-hero-flag" aria-hidden="true">{region["flag"]}</div>\n'
            f'  <h1>{esc(region["heading"])}</h1>\n'
            f'  <p>{esc(region["tagline"])}</p>\n'
            '</section>\n'
            '\n'
            '<section class="section">\n'
            f'  <h2 class="visually-hidden">{esc(region["heading"])}</h2>\n'
            '  <div class="museums-grid" id="museums-grid">\n\n'
            + cards +
            '  </div>\n'
            '</section>\n\n'
        ),
        '</main>\n',
        render_footer(site),
    ])
    (ROOT / region["file"]).write_text(page, encoding="utf-8")


def build_404(site):
    page = "".join([
        render_head(site, "Страница не найдена — Музеи мира", "Запрашиваемая страница не найдена.", None, "404.html", robots="noindex"),
        render_header(site, ""),
        '<main class="site-main">\n',
        (
            '\n<section class="hero">\n'
            '  <div class="hero-content">\n'
            '    <div class="hero-badge">404</div>\n'
            '    <h1>Экспонат утерян</h1>\n'
            '    <p>Такой страницы нет в нашей коллекции — возможно, её переместили в другой зал.</p>\n'
            '    <a href="index.html" class="museum-link" style="margin-top:1rem">На главную\n'
            '      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>\n'
            '    </a>\n'
            '  </div>\n'
            '</section>\n\n'
        ),
        '</main>\n',
        render_footer(site),
    ])
    (ROOT / "404.html").write_text(page, encoding="utf-8")


site, REGIONS = load_data()


def main():
    build_index(site, REGIONS)
    for region in REGIONS:
        build_region(site, region)
    build_404(site)
    total = sum(len(r["museums"]) for r in REGIONS)
    print(f"OK: {len(REGIONS)} регионов, {total} музеев, страницы: index, 404, " + ", ".join(r["file"] for r in REGIONS))


if __name__ == "__main__":
    main()

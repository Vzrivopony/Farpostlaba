import asyncio
import json
import re
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any

import aiohttp
from bs4 import BeautifulSoup

BASE_URL = "https://markets.businessinsider.com"
INDEX_URL = BASE_URL + "/index/components/s&p_500?p={}"
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


async def fetch(session, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


async def get_usd_to_rub(session) -> Decimal:
    xml = await fetch(session, CBR_URL)
    soup = BeautifulSoup(xml, "xml")
    usd_rate = soup.find("Valute", {"ID": "R01235"}).Value.text.replace(
        ",", "."
    )
    print(f"Текущий курс USD к RUB: {usd_rate}")
    return Decimal(usd_rate)


def safe_decimal(value: str) -> Decimal:
    """Преобразует строку в Decimal, обрабатывая ошибки."""
    try:
        return Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return Decimal(0)


async def parse_company_page(
    session, url: str, usd_to_rub: Decimal
) -> Dict[str, Any]:
    """Парсит страницу компании, вытаскивает P/E, 52 Week Low/High."""
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "lxml")

    name_code_section = soup.find("h1", class_="price-section__identifiers")
    if not name_code_section:
        print(f"Не найден блок с названием и кодом компании: {url}")
        return {}

    name = name_code_section.find(
        "span", class_="price-section__label"
    ).text.strip()
    code = name_code_section.find(
        "span", class_="price-section__category"
    ).text.strip()

    price_usd = safe_decimal(
        soup.find("span", class_="price-section__current-value").text
    )
    price_rub = price_usd * usd_to_rub

    pe_tag = soup.find(string=re.compile("P/E Ratio"))
    pe = (
        safe_decimal(pe_tag.find_next("span").text)
        if pe_tag
        else Decimal("inf")
    )

    # 52 Week Low / High
    try:
        week_low = safe_decimal(
            soup.find(string="52 Week Low").find_next("span").text
        )
        week_high = safe_decimal(
            soup.find(string="52 Week High").find_next("span").text
        )
        potential_profit = (
            ((week_high - week_low) / week_low) * 100
            if week_low and week_high
            else 0
        )
    except AttributeError:
        print(f"Неполные данные о 52 Week Low/High для {name} ({code})")
        potential_profit = 0

    print(f"{name} ({code}) успешно обработана")
    return {
        "name": name,
        "code": code,
        "price": float(price_rub),
        "P/E": float(pe),
        "potential_profit": float(potential_profit),
    }


async def parse_sp500():
    """Парсит индекс S&P 500 по страницам."""
    async with aiohttp.ClientSession() as session:
        usd_to_rub = await get_usd_to_rub(session)
        companies = []

        for page in range(1, 3):
            url = INDEX_URL.format(page)
            index_page = await fetch(session, url)
            soup = BeautifulSoup(index_page, "lxml")

            table_rows = soup.select(
                "div.table-responsive table.table tbody tr"
            )
            print(f"Страница {page}: найдено {len(table_rows)} компаний")

            for row in table_rows:
                cols = row.find_all("td")
                if len(cols) < 2:
                    continue  # Пропуск пустых строк

                company_link = BASE_URL + cols[0].find("a")["href"]
                print(f"Обработка компании: {company_link}")

                year_growth_text = (
                    cols[-1]
                    .text.strip()
                    .replace("\n", "")
                    .replace("%", "")
                    .replace(",", ".")
                )
                try:
                    year_growth = float(year_growth_text)
                except ValueError:
                    print(
                        f"Ошибка чтения роста компании: '{year_growth_text}'"
                    )
                    year_growth = 0

                company_data = await parse_company_page(
                    session, company_link, usd_to_rub
                )
                if company_data:
                    company_data["growth"] = year_growth
                    companies.append(company_data)

        print(f"Всего компаний собрано: {len(companies)}")
        await save_top_10(companies)


def save_json(filename: str, data: List[Dict[str, Any]]):
    """Сохраняет JSON-файл."""
    print(f"Сохранение {len(data)} записей в файл: {filename}")
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def save_top_10(companies: List[Dict[str, Any]]):
    """Сортирует и сохраняет топ-10 компаний по критериям."""
    save_json(
        "top_10_price.json", sorted(companies, key=lambda x: -x["price"])[:10]
    )
    save_json("top_10_pe.json", sorted(companies, key=lambda x: x["P/E"])[:10])
    save_json(
        "top_10_growth.json",
        sorted(companies, key=lambda x: -x["growth"])[:10],
    )
    save_json(
        "top_10_potential_profit.json",
        sorted(companies, key=lambda x: -x["potential_profit"])[:10],
    )


if __name__ == "__main__":
    await parse_sp500()
    print("Все данные успешно собраны и сохранены.")
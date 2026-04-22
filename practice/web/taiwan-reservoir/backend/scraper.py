import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://water.taiwanstat.com/"
_BRAVE_DEFAULT = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"


def _format_status(text: str) -> str:
    if not text or text == "狀態未知":
        return text
    match = re.search(r"(\d+\.?\d*)%", text)
    if not match:
        return text
    pct = match.group(1)
    if "下降" in text:
        return f"-{pct}%"
    if "上升" in text or "上昇" in text:
        return f"+{pct}%"
    return text


def _find_field(container, *selectors, h5_keywords=()) -> str | None:
    for sel in selectors:
        try:
            val = container.find_element(By.CSS_SELECTOR, sel).text.strip()
            if val:
                return val
        except NoSuchElementException:
            pass
    if h5_keywords:
        for h5 in container.find_elements(By.TAG_NAME, "h5"):
            t = h5.text.strip()
            if any(kw in t for kw in h5_keywords):
                return t
    return None


def _make_driver() -> webdriver.Chrome:
    opts = Options()
    brave_path = os.environ.get("BRAVE_BIN", _BRAVE_DEFAULT)
    if os.path.exists(brave_path):
        opts.binary_location = brave_path
    opts.add_argument("--headless")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    return driver


def scrape() -> list[dict]:
    driver = _make_driver()
    results = []

    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "main-content")))
        time.sleep(3)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "reservoir-wrap")))
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "reservoir")))
        time.sleep(2)

        reservoirs = driver.find_elements(By.CLASS_NAME, "reservoir")

        for i, reservoir in enumerate(reservoirs):
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", reservoir)

                WebDriverWait(reservoir, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".name h3"))
                )
                WebDriverWait(reservoir, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "svg"))
                )

                name = reservoir.find_element(By.CSS_SELECTOR, ".name h3").text.strip()

                percent_str = None
                try:
                    percent_str = reservoir.find_element(
                        By.CSS_SELECTOR, "svg text.liquidFillGaugeText"
                    ).text.strip()
                except NoSuchElementException:
                    for elem in reservoir.find_elements(By.CSS_SELECTOR, "svg text"):
                        t = elem.text.strip()
                        if "%" in t:
                            percent_str = t
                            break

                percent_val = None
                if percent_str:
                    m = re.search(r"([\d.]+)", percent_str)
                    if m:
                        percent_val = float(m.group(1))

                volume = _find_field(
                    reservoir,
                    ".volume h5", '[class*="volume"]',
                    h5_keywords=("蓄水量", "萬立方公尺"),
                )

                status_raw = _find_field(
                    reservoir,
                    '[class*="state"] h5',
                    h5_keywords=("昨日水量", "水量上升", "水量下降"),
                )
                status = _format_status(status_raw) if status_raw else "狀態未知"

                update_time = _find_field(
                    reservoir,
                    ".updateAt h5",
                    h5_keywords=("更新時間",),
                )
                if update_time:
                    update_time = update_time.replace("更新時間：", "").replace("更新時間:", "").strip()

                results.append({
                    "name": name,
                    "percent": percent_val,
                    "volume": volume,
                    "status": status,
                    "update_time": update_time,
                })

            except Exception as e:
                print(f"[scraper] skipped reservoir {i}: {type(e).__name__}: {e}")
                continue

    finally:
        driver.quit()

    return results

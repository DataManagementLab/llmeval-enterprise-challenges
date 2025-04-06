import logging
import re

import attrs
import bs4
import hydra
import pandas as pd
from hydra.core.config_store import ConfigStore
from playwright.sync_api import sync_playwright, Browser

from llms4de.data import get_experiments_path, load_str

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    url: str = "https://help.sap.com"


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    experiment_dir = get_experiments_path() / "enterprise_knowledge_text2signal"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    documentation_dir = experiment_dir

    # Gather entry links from table of contents
    logger.info("Gather entry links from table of contents.")
    signal_toc_html = load_str(experiment_dir / "signal_toc.html")
    entries = re.findall(
        r"""href="([^"]+)">([^<]+)""", signal_toc_html
    )
    entries = pd.DataFrame(entries, columns=["url", "title"])
    entries["url"] = entries["url"].apply(lambda url: f"{cfg.url}{url}")
    entries["title"] = entries["title"].apply(lambda title: re.sub(r"\s+", " ", title).strip())

    # Scrape pages
    logger.info("Scrape pages.")
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            entries["html"] = entries["url"].apply(lambda url: scrape_url(url, browser))

    # Extract content
    logger.info("Extract content.")
    entries["breadcrumbs"] = entries["html"].apply(extract_breadcrumbs)
    entries["html_content"] = entries["html"].apply(extract_html_content)
    entries["str_content"] = entries["html"].apply(extract_str_content)

    # Save result
    logger.info("Save result.")
    entries.to_csv(documentation_dir / "entries.csv", index=False)

    logger.info("Done!")


def scrape_url(url: str, browser: Browser) -> str:
    page = browser.new_page()
    page.goto(url)
    # page.wait_for_selector("css_selector_for_element")
    content = page.content()
    logger.info(f"Scraped {url}")
    return content


def extract_breadcrumbs(html: str) -> str:
    beautifulsoup = bs4.BeautifulSoup(html, "html.parser")
    ul = beautifulsoup.find("ul", class_="breadcrumbs")
    lis = [li.text for li in ul.find_all("li")]
    lis = [re.sub(r"\s+", " ", li).strip() for li in lis]
    assert lis[0:3] == ["Home", "SAP Signavio Process Intelligence", "SAP Signavio Analytics Language Guide"]
    assert len(lis) > 3
    return " ".join(lis[3:])


def extract_html_content(html: str) -> str:
    article_div = bs4.BeautifulSoup(html, "html.parser").find("div", role="article")
    for tag in article_div.find_all(True):
        tag.attrs = {}
    for text in article_div.find_all(text=True):
        text.replace_with(re.sub(r"\n", " ", text))  # replace newlines in content with spaces
    html = article_div.decode_contents()

    html = html.replace("<div>", "").replace("</div>", "")
    html = html.replace("<button>", "").replace("</button>", "")
    html = html.replace("<object>", "").replace("</object>", "")
    html = html.replace("<span>", "").replace("</span>", "")
    html = html.replace("<p>", "").replace("</p>", "")
    html = html.replace("<samp>", "").replace("</samp>", "")
    html = html.replace("<section>", "").replace("</section>", "")
    html = html.replace("<strong>", "").replace("</strong>", "")
    html = html.replace("", "")
    html = re.sub(r"\n", "", html).strip()  # remove newlines outside of content
    html = re.sub(r"\s+", " ", html).strip()

    return html


def extract_str_content(html: str) -> str:
    article_div = bs4.BeautifulSoup(html, "html.parser").find("div", role="article")
    for text in article_div.find_all(text=True):
        text.replace_with(" " + re.sub(r"\n", " ", text))  # replace newlines in content with spaces
    s = article_div.text

    s = s.replace("", "")
    s = re.sub(r"\s+", " ", s).strip()

    return s


if __name__ == "__main__":
    main()

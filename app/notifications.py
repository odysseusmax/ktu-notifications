import re
import traceback
import logging

import aiohttp
from yarl import URL
from bs4 import BeautifulSoup, element

base_url = URL("https://www.ktu.edu.in")
ktu_url = base_url.join(URL("/eu/core/announcements.htm"))
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0"
}
logger = logging.getLogger(__name__)


def get_string(tag):
    r_string = ""
    for i in tag.children:
        if isinstance(i, element.Comment):
            continue
        elif isinstance(i, element.NavigableString):
            r_string += re.sub(r"[\n\r]", "", i.string)
        else:
            if i.name in ["a"]:
                href = URL(i.get("href", "").strip())
                if not href.is_absolute():
                    href = base_url.join(href)
                href_str = "".join([x.strip() for x in i.stripped_strings])
                r_string += f"<a href='{href}'>{href_str}</a>"
            elif i.name in ["br"]:
                r_string += "\n"
            else:
                tag_string = get_string(i)
                if i.name in ["b", "u"]:
                    r_string += f"<b>{tag_string}</b>\n\n"
                elif i.name in ["li"]:
                    r_string += f"\n - {tag_string}"
                elif i.name in ["p"]:
                    r_string += f"\n{tag_string}"
                else:
                    r_string += tag_string
    return r_string.strip()


async def fetch_notifications():
    try:
        async with aiohttp.ClientSession() as session:
            r = await session.get(ktu_url, headers=headers)
            if r.status != 200:
                return f"`{ktu_url}` returned {r.status} status code!"

            html = await r.text()
            soup = BeautifulSoup(html, "html.parser")
            table = soup.table
            trs = table.find_all("tr")
            notifications = []
            for tr in trs:
                try:
                    date_td, content_td = tr.find_all("td")
                except Exception:
                    continue

                date = date_td.b
                text = "\n".join(tx.strip() for tx in content_td.stripped_strings)
                lis = content_td.ul.li
                f_text = get_string(lis)
                notifications.append(
                    {
                        "text": f"{text}\n\n{date.string}",
                        "formatted": f"{f_text}\n\n{date.string}",
                    }
                )
            return notifications
    except Exception as e:
        logger.error(e, exc_info=True)
        return "error in notification fetch\n\n" + traceback.format_exc()


# if __name__ == "__main__":
#     import asyncio

#     r = asyncio.run(fetch_notifications())
#     print(r)

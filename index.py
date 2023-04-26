from requests_html import AsyncHTMLSession
from aioflask import Flask
from flask_cors import CORS
from flask_caching import Cache
import nest_asyncio
import asyncio

nest_asyncio.apply()

app = Flask(__name__)
cors = CORS(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/', methods=['GET'])
@cache.cached(timeout=86_400)  # Set a cache timeout of 24 hours
async def fetchPizzas(URL="https://www.pizzabakeren.no/originalpizza"):
    htmlSession = AsyncHTMLSession()
    r = await htmlSession.get(URL)

    r.html.arender()

    pizzas = {"original": [], "tynn": [], "vegansk": [], "dessert": []}

    links = r.html.absolute_links
    tasks = []

    async def fetch_and_parse(link, category):
        session = await htmlSession.get(link)
        session.html.arender()

        options = session.html.find(".content")

        for option in options:
            summary = option.text.split("\n")
            if len(summary) < 3:
                summary.append("Ingen")
            extra = summary[2]
            if extra.count("Allergener:") > 1:
                extra = extra[:extra.find("Allergener", 11) - 1]
            pizza = {"name": summary[0],
                     "description": summary[1], "extra": extra}
            pizzas[category].append(pizza)

    for link in links:
        for category in pizzas.keys():
            if category in link:
                tasks.append(fetch_and_parse(link, category))

    await asyncio.gather(*tasks)

    return pizzas

if __name__ == '__main__':
    app.run(debug=True)

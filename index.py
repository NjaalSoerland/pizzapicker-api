from requests_html import AsyncHTMLSession
from aioflask import Flask
from flask_cors import CORS
import nest_asyncio

nest_asyncio.apply()

app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['GET'])
async def fetchPizzas(URL = "https://www.pizzabakeren.no/originalpizza"):
    htmlSession = AsyncHTMLSession()
    r = await htmlSession.get(URL)

    r.html.arender()

    pizzas = {"original": [], "tynn": [], "vegansk": [], "dessert": []}

    links = r.html.absolute_links
    for link in links:
        for category in pizzas.keys():
            if category in link:
                session = await htmlSession.get(link)
                session.html.arender()
                
                options = session.html.find(".content")
                
                for option in options:
                    summary = option.text.split("\n")
                    if len(summary) < 3:
                        summary.append("Ingen")
                    extra = summary[2]
                    if extra.count("Allergener:") > 1:
                        extra = extra[:extra.find("Allergener", 11)-1]
                    pizza = {"name": summary[0], "description": summary[1], "extra": extra}
                    pizzas[category].append(pizza)

    return pizzas

if __name__ == '__main__':
    app.run(debug=True)

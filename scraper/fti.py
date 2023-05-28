from iso3166 import countries as iso3166_countries
import requests
import requests_cache
from lxml import html

requests_cache.install_cache("fti")


def code_to_emoji(code):
    OFFSET = ord("🇦") - ord("A")
    return "".join([chr(ord(c.upper()) + OFFSET) for c in code])


countries = {}


class Country:
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
        self.flag = code_to_emoji(code)
        self.cbdc = None
        self.cash_limit = None
        self.inflation = None
        # self.nfsi = None

    @staticmethod
    def by_name(name):
        for c in countries.values():
            if c.name == name:
                return c
        if name == "Republic of Palau":
            return countries["PW"]
        if name == "Czech Republic":
            return countries["CZ"]
        if name == "Macau":
            return countries["MO"]
        if name == "Russian Federation":
            return countries["RU"]
        if name == "Cape Verde":
            return countries["CV"]
        if name == "United States":
            return countries["US"]
        if name == "Ivory Coast":
            return countries["CI"]
        if name == "Swaziland":
            return countries["SZ"]
        if name == "East Timor":
            return countries["TL"]
        if name == "Guinea Bissau":
            return countries["GW"]
        if name == "Macedonia":
            return countries["MK"]
        assert False, f"unknown country: {name}"


# add CBDC rollout data from https://cbdctracker.org/
def add_cbdc(countries):
    WEIGHT = {
        "Cancelled": 0,
        "Research": 1,
        "Proof of concept": 2,
        "Pilot": 3,
        "Launched": 4,
    }

    def process(country, status):
        # already present, let's set the highest status
        if country.cbdc is not None:
            if WEIGHT[status] > WEIGHT[country.cbdc]:
                country.cbdc = status
            return
        country.cbdc = status

    # for c in countries.values():
    data = requests.get("https://cbdctracker.org/api/currencies").json()
    for d in data:
        country, status = d["country"].strip(), d["status"].strip()
        assert status in WEIGHT, f"unknown status: {status}"
        try:
            c = Country.by_name(country)
        except AssertionError:
            c = None
        if not c:
            cc = None
            if country == "Euro Area":
                # fmt: off
                cc = ["AT", "BE", "HR", "CY", "EE", "FI", "FR", "DE", "GR", "IE",
                      "IT", "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES"]
                # fmt: on
            elif country == "France & Switzerland":
                cc = ["FR", "CH"]
            elif country == "France & Singapore":
                cc = ["FR", "SG"]
            elif country == "France & Tunisia":
                cc = ["FR", "TN"]
            elif country == "Hong Kong, Thailand, China and UAE":
                cc = ["HK", "TH", "CN", "AE"]
            elif country == "Israel & Norway & Sweden":
                cc = ["IL", "NO", "SE"]
            elif country == "Israel, Hong Kong":
                cc = ["IL", "HK"]
            elif country == "Eastern Caribbean Economic and Currency Union (OECS/ECCU)":
                cc = ["AI", "AG", "DM", "GD", "MS", "KN", "LC", "VC"]
            else:
                assert False, f"unknown country: {country}"
            for c in cc:
                process(countries[c], status)
        else:
            process(c, status)


def add_cash_limit(countries):
    # from https://www.europe-consommateurs.eu/en/shopping-internet/cash-payment-limitations.html
    d1 = {
        "Austria": "no limit",
        "Belgium": "3000 EUR",
        "Bulgaria": "5000 EUR",
        "Croatia": "15000 EUR",
        "Cyprus": "no limit",
        "Czechia": "10000 EUR",
        "Denmark": "2500 EUR",
        "Estonia": "no limit",
        "Finland": "no limit",
        "France": "1000 EUR",
        "Germany": "10000 EUR",
        "Greece": "500 EUR",
        "Hungary": "4000 EUR",
        "Iceland": "no limit",
        "Ireland": "no limit",
        "Italy": "1000 EUR",
        "Latvia": "7000 EUR",
        "Lithuania": "3000 EUR",
        "Luxembourg": "no limit",
        "Malta": "10000 EUR",
        "Netherlands": "3000 EUR",
        "Norway": "10000 EUR",
        "Poland": "3000 EUR",
        "Portugal": "3000 EUR",
        "Romania": "10000 EUR",
        "Slovakia": "5000 EUR",
        "Slovenia": "5000 EUR",
        "Spain": "1000 EUR",
        "Sweden": "no limit",
        "United Kingdom": "10000 EUR",
    }
    # from https://www.sgs.com/en/-/media/sgscorp/documents/corporate/brochures/355sgsctsanticorruptioncashpayments-limitations75x105v2lr.cdn.en.pdf
    d2 = {
        "Australia": "10000 AUD",
        "Brazil": "30000 BRL",
        "Canada": "10000 CAD",
        "China": "50000 RMB",
        "Russia": "100000 RUB",
        "Singapore": "20000 SGD",
        "South Africa": "25000 ZAR",
        "Taiwan": "500000 TWD",
        "United Arab Emirates": "2000 AED",
        "United States of America": "10000 USD",
        "India": "10000 INR",
        "Mexico": "200000 MXN",
        "Switzerland": "100000 CHF",
        "Uruguay": "5000 USD",
    }
    # others
    d3 = {
        "Israel": "6000 ILS",
        "Saudi Arabia": "60000 SAR",
        "Turkey": "75000 TRY",
        "Argentina": "10000 USD",
        "Indonesia": "100000000 IDR",
        "Japan": "1000000 JPY",
        "South Korea": "10000000 KRW",
    }
    dd = d1.copy()
    dd.update(d2)
    dd.update(d3)
    for d in dd.items():
        c = Country.by_name(d[0])
        c.cash_limit = d[1]


def add_inflation(countries):
    page = requests.get(
        "https://tradingeconomics.com/country-list/inflation-rate?continent=world",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    tree = html.fromstring(page.content)
    trs = tree.xpath("//tr")
    for tr in trs[1:]:
        trc = tr.getchildren()
        country = trc[0].text_content().strip()
        inflation = trc[1].text_content().strip()
        if country in ["Euro Area", "European Union"]:
            continue
        c = Country.by_name(country)
        c.inflation = inflation


"""
# add negated financial secrecy index data from https://fsi.taxjustice.net/
def add_nfsi(countries):
    data = requests.get("https://fsi.taxjustice.net/api/countries.php?period=22").json()
    for c in data:
        country = countries[c["country_id"]]
        country.nfsi = int(100.0 - c["index_score"])
"""


def main():
    for c in iso3166_countries:
        r = {
            "Iran, Islamic Republic of": "Iran",
            "Lao People's Democratic Republic": "Laos",
            "Curaçao": "Curacao",
            "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
            "Viet Nam": "Vietnam",
            "Côte d'Ivoire": "Cote d'Ivoire",
            "Türkiye": "Turkey",
            "Korea, Democratic People's Republic of": "North Korea",
            "Korea, Republic of": "South Korea",
            "Tanzania, United Republic of": "Tanzania",
            "Bolivia, Plurinational State of": "Bolivia",
            "Bonaire, Sint Eustatius and Saba": "Bonaire",
            "Micronesia, Federated States of": "Micronesia",
            "Moldova, Republic of": "Moldova",
            "Venezuela, Bolivarian Republic of": "Venezuela",
            "Virgin Islands, British": "British Virgin Islands",
            "Virgin Islands, U.S.": "US Virgin Islands",
            "Saint Helena, Ascension and Tristan da Cunha": "Saint Helena",
            "Congo, Democratic Republic of the": "Democratic Republic of the Congo",
            "Russian Federation": "Russia",
            "Brunei Darussalam": "Brunei",
            "Syrian Arab Republic": "Syria",
        }
        name = c.apolitical_name
        if name in r:
            name = r[name]
        countries[c.alpha2] = Country(c.alpha2, name)

    add_cbdc(countries)
    add_cash_limit(countries)
    add_inflation(countries)
    # add_nfsi(countries)

    print(f"code;flag;name;cbdc;cash_limit;inflation")
    for c in countries.values():
        if c.cash_limit is not None:
            print(f"{c.code};{c.flag};{c.name};{c.cbdc};{c.cash_limit};{c.inflation}")


if __name__ == "__main__":
    main()

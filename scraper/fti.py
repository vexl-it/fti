import math
from iso3166 import countries as iso3166_countries
import requests
import requests_cache
from lxml import html

requests_cache.install_cache("fti")

# fmt: off
EURO_AREA_COUNTRIES = ["AT", "BE", "HR", "CY", "EE", "FI", "FR", "DE", "GR", "IE",
                       "IT", "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES"]
# fmt: on


def code_to_emoji(code):
    OFFSET = ord("🇦") - ord("A")
    return "".join([chr(ord(c.upper()) + OFFSET) for c in code])


countries = {}


class Country:
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
        self.flag = code_to_emoji(code)
        self.cbdc_status = "Unknown"
        self.cbdc_status_normalized = 0
        self.cryptocurrency_status = "Unknown"
        self.cryptocurrency_status_normalized = 0
        self.cash_limit = None
        self.cash_limit_normalized = None
        self.money_supply_growth = None
        self.money_supply_growth_normalized = None
        self.social_security = None
        self.social_security_normalized = None
        self.personal_income_tax = None
        self.personal_income_tax_normalized = None
        self.financial_tyranny_index = None

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
        if name == "Bosnia And Herzegovina":
            return countries["BA"]
        if name == "Republic of the Congo":
            return countries["CG"]
        if name == "St Lucia":
            return countries["LC"]
        if name == "Trinidad And Tobago":
            return countries["TT"]
        assert False, f"unknown country: {name}"


# add CBDC rollout data from https://cbdctracker.org/
def add_cbdc_status(countries):
    STATUS = {
        "Unknown": 0,
        "Cancelled": 0,
        "Research": 20,
        "Proof of concept": 50,
        "Pilot": 80,
        "Launched": 100,
    }

    def process(country, status):
        # already present, let's set the highest status
        if country.cbdc_status is not None:
            if STATUS[status] > STATUS[country.cbdc_status]:
                country.cbdc_status = status
                country.cbdc_status_normalized = STATUS[status]
            return
        country.cbdc_status = status
        country.cbdc_status_normalized = STATUS[status]

    data = requests.get("https://cbdctracker.org/api/currencies").json()
    for d in data:
        country, status = d["country"].strip(), d["status"].strip()
        assert status in STATUS, f"unknown status: {status}"
        try:
            c = Country.by_name(country)
        except AssertionError:
            c = None
        if not c:
            cc = None
            if country == "Euro Area":
                cc = EURO_AREA_COUNTRIES
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
        "Austria": "No limit",
        "Belgium": "3000 EUR",
        "Bulgaria": "5000 EUR",
        "Croatia": "15000 EUR",
        "Cyprus": "No limit",
        "Czechia": "10000 EUR",
        "Denmark": "2500 EUR",
        "Estonia": "No limit",
        "Finland": "No limit",
        "France": "1000 EUR",
        "Germany": "10000 EUR",
        "Greece": "500 EUR",
        "Hungary": "4000 EUR",
        "Iceland": "No limit",
        "Ireland": "No limit",
        "Italy": "1000 EUR",
        "Latvia": "7000 EUR",
        "Lithuania": "3000 EUR",
        "Luxembourg": "No limit",
        "Malta": "10000 EUR",
        "Netherlands": "3000 EUR",
        "Norway": "10000 EUR",
        "Poland": "3000 EUR",
        "Portugal": "3000 EUR",
        "Romania": "10000 EUR",
        "Slovakia": "5000 EUR",
        "Slovenia": "5000 EUR",
        "Spain": "1000 EUR",
        "Sweden": "No limit",
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
        "United Arab Emirates": "55000 AED",
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
    CURRENCY_TO_EURO = {
        "AED": 0.25,
        "AUD": 0.61,
        "BRL": 0.18,
        "CAD": 0.69,
        "CHF": 1.03,
        "IDR": 0.000062,
        "ILS": 0.25,
        "INR": 0.011,
        "JPY": 0.0067,
        "KRW": 0.00071,
        "MXN": 0.053,
        "RMB": 0.13,
        "RUB": 0.011,
        "SAR": 0.25,
        "SGD": 0.69,
        "TRY": 0.045,
        "TWD": 0.03,
        "USD": 0.94,
        "ZAR": 0.047,
    }
    dd = d1.copy()
    dd.update(d2)
    dd.update(d3)
    for country, limit in dd.items():
        c = Country.by_name(country)
        if limit == "No limit":
            c.cash_limit = "No limit"
            c.cash_limit_normalized = 0
            continue
        limit = limit.split(" ")
        if limit[1] == "EUR":
            eur = int(limit[0])
        else:
            eur = round(int(limit[0]) * CURRENCY_TO_EURO[limit[1]])
        c.cash_limit = eur
        c.cash_limit_normalized = round(max(0, 20000 - eur) / 200)


def add_money_supply_growth(countries):
    # from https://porkopolis.io/basemoney
    data = {
        "United States": -15.7,
        "China": 9.6,
        "Euro area": -4.5,
        "Japan": -5.6,
        "India": 10.3,
        "United Kingdom": -3.4,
        "Canada": -18.9,
        "Russia": 20.1,
        "Iran": 27.8,
        "Brazil": 16.6,
        "South Korea": 10.7,
        "Australia": 9.5,
        "Mexico": 10.6,
        "Indonesia": 27.0,
        "Saudi Arabia": 2.2,
        "Turkey": 68.5,
        "Taiwan": 10.8,
        "Switzerland": -21.0,
        "Poland": -6.4,
        "Argentina": 42.4,
        "Sweden": 3.3,
        "Thailand": -1.3,
        "Israel": 2.5,
        "Norway": 2.8,
        "Nigeria": 20.6,
        "United Arab Emirates": 5.3,
        "Egypt": 15.6,
        "Bangladesh": 17.4,
        "Malaysia": 27.6,
        "Singapore": -1.1,
        "Vietnam": -9.7,
        "South Africa": 14.0,
        "Philippines": 5.1,
        "Denmark": 15.5,
        "Pakistan": 7.7,
        "Hong Kong": -10.1,
        "Colombia": 6.5,
        "Chile": -17.8,
        "Romania": 12.3,
        "Czech Republic": -1.8,
        "Iraq": 21.0,
        "New Zealand": 22.7,
        "Peru": -4.4,
        "Kazakhstan": 11.9,
        "Qatar": -7.5,
        "Ukraine": 19.6,
        "Algeria": 21.9,
        "Hungary": 54.4,
        "WA CFA": 4.7,
        "CA CFA": 21.5,
    }
    for country, growth in data.items():
        if country == "Euro area":
            cc = [countries[c] for c in EURO_AREA_COUNTRIES]
        elif country == "WA CFA":
            WA_CFA_COUNTRIES = ["BJ", "BF", "CI", "GW", "ML", "NE", "SN", "TG"]
            cc = [countries[c] for c in WA_CFA_COUNTRIES]
        elif country == "CA CFA":
            CA_CFA_COUNTRIES = ["CM", "CF", "TD", "CG", "GA", "GQ"]
            cc = [countries[c] for c in CA_CFA_COUNTRIES]
        else:
            cc = [Country.by_name(country)]
        for c in cc:
            c.money_supply_growth = growth
            c.money_supply_growth_normalized = min(100, max(0, growth) * 2)


def add_social_security(countries):
    page = requests.get(
        "https://tradingeconomics.com/country-list/social-security-rate?continent=world",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    tree = html.fromstring(page.content)
    trs = tree.xpath("//tr")
    for tr in trs[1:]:
        trc = tr.getchildren()
        country = trc[0].text_content().strip()
        social_security = trc[1].text_content().strip()
        if country.lower() in ["euro area", "european union"]:
            continue
        c = Country.by_name(country)
        c.social_security = social_security
        c.social_security_normalized = round(min(100, float(social_security) * 2))


def add_personal_income_tax(countries):
    page = requests.get(
        "https://tradingeconomics.com/country-list/personal-income-tax-rate?continent=world",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    tree = html.fromstring(page.content)
    trs = tree.xpath("//tr")
    for tr in trs[1:]:
        trc = tr.getchildren()
        country = trc[0].text_content().strip()
        personal_income_tax = trc[1].text_content().strip()
        if country.lower() in ["euro area", "european union"]:
            continue
        c = Country.by_name(country)
        c.personal_income_tax = personal_income_tax
        c.personal_income_tax_normalized = round(min(100, float(personal_income_tax) * 2))


def add_cryptocurrency_status(countries):
    STATUS = {
        "Hostile": 100,
        "Contentious": 70,
        "Restricted": 40,
        "Permissive": 0,
        "Legal tender": 0,
        "Unknown": 0,
    }
    # from https://en.wikipedia.org/wiki/Legality_of_cryptocurrency_by_country_or_territory
    data = {
        "Algeria": "Hostile",
        "Egypt": "Hostile",
        "Morocco": "Hostile",
        "Nigeria": "Contentious",
        "Tanzania": "Permissive",
        "Central African Republic": "Legal tender",
        "Mauritius": "Permissive",
        "Angola": "Permissive",
        "South Africa": "Permissive",
        "Namibia": "Contentious",
        "Canada": "Contentious",
        "United States": "Permissive",
        "Mexico": "Permissive",
        "Costa Rica": "Permissive",
        "El Salvador": "Legal tender",
        "Nicaragua": "Permissive",
        "Jamaica": "Permissive",
        "Trinidad and Tobago": "Permissive",
        "Argentina": "Contentious",
        "Bolivia": "Hostile",
        "Brazil": "Permissive",
        "Chile": "Permissive",
        "Colombia": "Contentious",
        "Ecuador": "Contentious",
        "Venezuela": "Permissive",
        "Afghanistan": "Hostile",
        "Kyrgyzstan": "Permissive",
        "Uzbekistan": "Permissive",
        "United Arab Emirates": "Contentious",
        "Israel": "Permissive",
        "Saudi Arabia": "Contentious",
        "Jordan": "Contentious",
        "Lebanon": "Permissive",
        "Turkey": "Contentious",
        "Qatar": "Contentious",
        "Iran": "Contentious",
        "Bangladesh": "Hostile",
        "India": "Permissive",
        "Nepal": "Hostile",
        "Pakistan": "Permissive",
        "China": "Hostile",
        "Hong Kong": "Permissive",
        "Japan": "Permissive",
        "South Korea": "Permissive",
        "Taiwan": "Contentious",
        "Cambodia": "Contentious",
        "Indonesia": "Restricted",
        "Malaysia": "Permissive",
        "Philippines": "Permissive",
        "Singapore": "Permissive",
        "Thailand": "Restricted",
        "Vietnam": "Restricted",
        "Brunei": "Permissive",
        "Austria": "Permissive",
        "Croatia": "Permissive",
        "Czech Republic": "Permissive",
        "Germany": "Permissive",
        "Hungary": "Permissive",
        "Gibraltar": "Permissive",
        "Poland": "Permissive",
        "Romania": "Permissive",
        "Slovakia": "Permissive",
        "Slovenia": "Permissive",
        "Switzerland": "Permissive",
        "Albania": "Permissive",
        "Belarus": "Permissive",
        "Georgia": "Permissive",
        "Kosovo": "Permissive",
        "Russia": "Contentious",
        "Ukraine": "Contentious",
        "Denmark": "Permissive",
        "Estonia": "Permissive",
        "Finland": "Permissive",
        "Iceland": "Permissive",
        "Lithuania": "Permissive",
        "Norway": "Permissive",
        "Sweden": "Permissive",
        "Bosnia and Herzegovina": "Permissive",
        "Bulgaria": "Permissive",
        "Cyprus": "Permissive",
        "Greece": "Permissive",
        "Italy": "Permissive",
        "Malta": "Permissive",
        "North Macedonia": "Permissive",
        "Portugal": "Permissive",
        "Spain": "Permissive",
        "Belgium": "Permissive",
        "France": "Permissive",
        "Ireland": "Permissive",
        "Luxembourg": "Permissive",
        "Netherlands": "Permissive",
        "United Kingdom": "Permissive",
        "Australia": "Permissive",
        "New Zealand": "Permissive",
        "Fiji": "Permissive",
        "Tuvalu": "Permissive",
        "Vanuatu": "Permissive",
        "Marshall Islands": "Permissive",
        "Palau": "Permissive",
        "Samoa": "Permissive",
        "Tonga": "Permissive",
    }
    for c, s in data.items():
        country = Country.by_name(c)
        country.cryptocurrency_status = s
        country.cryptocurrency_status_normalized = STATUS[s]


def print_csv(countries):
    FIELDS = [
        # "code",
        "flag",
        "name",
        "cbdc_status",
        # "cbdc_status_normalized",
        "cryptocurrency_status",
        # "cryptocurrency_status_normalized",
        "cash_limit",
        # "cash_limit_normalized",
        "money_supply_growth",
        # "money_supply_growth_normalized",
        "social_security",
        # "social_security_normalized",
        "personal_income_tax",
        # "personal_income_tax_normalized",
        "financial_tyranny_index",
    ]
    print("#\t" + "\t".join(FIELDS))
    i = 1
    for c in countries.values():
        if all(getattr(c, f) is not None for f in FIELDS):
            print(f"{i}\t" + "\t".join([str(getattr(c, f)) for f in FIELDS]))
            i += 1


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

    add_cbdc_status(countries)
    add_cryptocurrency_status(countries)
    add_cash_limit(countries)
    add_money_supply_growth(countries)
    add_social_security(countries)
    add_personal_income_tax(countries)

    for c in countries.values():
        v = 0
        try:
            v += c.cbdc_status_normalized * 0.2
            v += c.cryptocurrency_status_normalized * 0.2
            v += c.cash_limit_normalized * 0.2
            v += c.money_supply_growth_normalized * 0.2
            v += c.social_security_normalized * 0.1
            v += c.personal_income_tax_normalized * 0.1
            v = round(v)
            c.financial_tyranny_index = v
        except TypeError:
            c.financial_tyranny_index = None

    print_csv(countries)


if __name__ == "__main__":
    main()

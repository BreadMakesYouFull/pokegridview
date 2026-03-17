from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from time import sleep
import csv
import icrawler.builtin
import os
import random
import re
import requests

CSV_FILE = "cards.csv"

OUTPUT_DIR = Path("static/gallery")
OUTPUT_DIR.mkdir(exist_ok=True)

REQUEST_DELAY = 1.0
MAX_RETRIES = 1

CRAWL = os.getenv("PGV_CRAWL", False)
FILL = os.getenv("PGV_FILL", False)

# Collectr set names → Pokémon TCG API set codes
#https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/refs/heads/master/sets/en.json
SET_MAP = {
    "Base": "base1",
    "Base Set (Unlimited)": "base1",
    "Jungle": "base2",
    "Wizards Black Star Promos": "basep",
    "Fossil": "base3",
    "Base Set 2": "base4",
    "Team Rocket": "base5",
    "Gym Heroes": "gym1",
    "Gym Challenge": "gym2",
    "Neo Genesis": "neo1",
    "Neo Discovery": "neo2",
    "Southern Islands": "si1",
    "Neo Revelation": "neo3",
    "Neo Destiny": "neo4",
    "Legendary Collection": "base6",
    "Expedition Base Set": "ecard1",
    "Best of Game": "bp",
    "Aquapolis": "ecard2",
    "Skyridge": "ecard3",
    "Ruby & Sapphire": "ex1",
    "Sandstorm": "ex2",
    "Dragon": "ex3",
    "Nintendo Black Star Promos": "np",
    "Team Magma vs Team Aqua": "ex4",
    "EX Trainer Kit Latias": "tk1a",
    "EX Trainer Kit Latios": "tk1b",
    "Hidden Legends": "ex5",
    "FireRed & LeafGreen": "ex6",
    "POP Series 1": "pop1",
    "Team Rocket Returns": "ex7",
    "Deoxys": "ex8",
    "Emerald": "ex9",
    "Unseen Forces": "ex10",
    "POP Series 2": "pop2",
    "Delta Species": "ex11",
    "Legend Maker": "ex12",
    "EX Trainer Kit 2 Plusle": "tk2a",
    "EX Trainer Kit 2 Minun": "tk2b",
    "POP Series 3": "pop3",
    "Holon Phantoms": "ex13",
    "Crystal Guardians": "ex14",
    "POP Series 4": "pop4",
    "Dragon Frontiers": "ex15",
    "POP Series 5": "pop5",
    "Power Keepers": "ex16",
    "Diamond & Pearl": "dp1",
    "DP Black Star Promos": "dpp",
    "Mysterious Treasures": "dp2",
    "POP Series 6": "pop6",
    "Secret Wonders": "dp3",
    "Great Encounters": "dp4",
    "POP Series 7": "pop7",
    "Majestic Dawn": "dp5",
    "Legends Awakened": "dp6",
    "POP Series 8": "pop8",
    "Stormfront": "dp7",
    "Platinum": "pl1",
    "POP Series 9": "pop9",
    "Rising Rivals": "pl2",
    "Supreme Victors": "pl3",
    "Arceus": "pl4",
    "Pokémon Rumble": "ru1",
    "HeartGold & SoulSilver": "hgss1",
    "HGSS Black Star Promos": "hsp",
    "HS—Unleashed": "hgss2",
    "HS—Undaunted": "hgss3",
    "HS—Triumphant": "hgss4",
    "Call of Legends": "col1",
    "BW Black Star Promos": "bwp",
    "Black & White": "bw1",
    "McDonald's Collection 2011": "mcd11",
    "Emerging Powers": "bw2",
    "Noble Victories": "bw3",
    "Next Destinies": "bw4",
    "Dark Explorers": "bw5",
    "McDonald's Collection 2012": "mcd12",
    "Dragons Exalted": "bw6",
    "Dragon Vault": "dv1",
    "Boundaries Crossed": "bw7",
    "Plasma Storm": "bw8",
    "Plasma Freeze": "bw9",
    "Plasma Blast": "bw10",
    "XY Black Star Promos": "xyp",
    "Legendary Treasures": "bw11",
    "Legendary Treasures: Radiant Collections": "bw11",
    "Kalos Starter Set": "xy0",
    "XY": "xy1",
    "Flashfire": "xy2",
    "McDonald's Collection 2014": "mcd14",
    "Furious Fists": "xy3",
    "Phantom Forces": "xy4",
    "Primal Clash": "xy5",
    "Double Crisis": "dc1",
    "Roaring Skies": "xy6",
    "Ancient Origins": "xy7",
    "BREAKthrough": "xy8",
    "McDonald's Collection 2015": "mcd15",
    "BREAKpoint": "xy9",
    "Generations": "g1",
    "Fates Collide": "xy10",
    "Steam Siege": "xy11",
    "McDonald's Collection 2016": "mcd16",
    "Evolutions": "xy12",
    "Sun & Moon": "sm1",
    "SM Black Star Promos": "smp",
    "Guardians Rising": "sm2",
    "Burning Shadows": "sm3",
    "Shining Legends": "sm35",
    "Crimson Invasion": "sm4",
    "McDonald's Collection 2017": "mcd17",
    "Ultra Prism": "sm5",
    "Forbidden Light": "sm6",
    "Celestial Storm": "sm7",
    "Dragon Majesty": "sm75",
    "McDonald's Collection 2018": "mcd18",
    "Lost Thunder": "sm8",
    "Team Up": "sm9",
    "Detective Pikachu": "det1",
    "Unbroken Bonds": "sm10",
    "Unified Minds": "sm11",
    "Hidden Fates": "sm115",
    "Hidden Fates Shiny Vault": "sma",
    "McDonald's Collection 2019": "mcd19",
    "Cosmic Eclipse": "sm12",
    "SWSH Black Star Promos": "swshp",
    "Sword & Shield": "swsh1",
    "Rebel Clash": "swsh2",
    "Darkness Ablaze": "swsh3",
    "Pokémon Futsal Collection": "fut20",
    "Champion's Path": "swsh35",
    "Vivid Voltage": "swsh4",
    "Shining Fates": "swsh45",
    "Shining Fates Shiny Vault": "swsh45sv",
    "Battle Styles": "swsh5",
    "Chilling Reign": "swsh6",
    "Evolving Skies": "swsh7",
    "McDonald's Collection 2021": "mcd21",
    "Celebrations": "cel25",
    "Celebrations: Classic Collection": "cel25c",
    "Fusion Strike": "swsh8",
    "Brilliant Stars": "swsh9",
    "Brilliant Stars Trainer Gallery": "swsh9tg",
    "Astral Radiance": "swsh10",
    "Astral Radiance Trainer Gallery": "swsh10tg",
    "Pokémon GO": "pgo",
    "McDonald's Collection 2022": "mcd22",
    "Lost Origin": "swsh11",
    "Lost Origin Trainer Gallery": "swsh11tg",
    "Silver Tempest": "swsh12",
    "Silver Tempest Trainer Gallery": "swsh12tg",
    "Crown Zenith": "swsh12pt5",
    "Crown Zenith Galarian Gallery": "swsh12pt5gg",
    "Scarlet & Violet Black Star Promos": "svp",
    "Scarlet & Violet Energies": "sve",
    "Scarlet & Violet": "sv1",
    "Paldea Evolved": "sv2",
    "Obsidian Flames": "sv3",
    "151": "sv3pt5",
    "Paradox Rift": "sv4",
    "Paldean Fates": "sv4pt5",
    "Temporal Forces": "sv5",
    "Twilight Masquerade": "sv6",
    "Shrouded Fable": "sv6pt5",
    "Stellar Crown": "sv7",
    "Surging Sparks": "sv8",
    "Prismatic Evolutions": "sv8pt5",
    "Journey Together": "sv9",
    "Destined Rivals": "sv10",
    "Black Bolt": "zsv10pt5",
    "White Flare": "rsv10pt5",
    "Mega Evolution": "me1",
    "Phantasmal Flames": "me2",
    "Ascended Heroes": "me2pt5",
}

def crawl_card(set_id, number, query):
    os.makedirs("static/tmp", exist_ok=True)
    crawler = icrawler.builtin.BingImageCrawler(storage={'root_dir': 'static/tmp'})
    crawler.crawl(keyword=query, max_num=1)
    files = os.listdir("static/tmp")
    if files:
        os.rename(
            os.path.join("static/tmp", files[0]),
            os.path.join("static/gallery", f"{set_id}_{number}.png")
        )

# Dummy card size for missing downloads
CARD_W = 367
CARD_H = 512

def make_placeholder(set_code, number):
    img = Image.new("RGB", (CARD_W, CARD_H), "#3C5AA6")
    draw = ImageDraw.Draw(img)

    text = f"{set_code.upper().replace(' ', '\n')}\n{number}"

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (CARD_W - w) / 2
    y = (CARD_H - h) / 2

    draw.text((x,y), text, fill="white", font=font)

    filename = OUTPUT_DIR / f"{set_code}_{number}.png"
    img.save(filename)

    print("Saved", filename)


def normalize_number(num):
    return re.sub(r"[^\d]", "", num)

def download_with_retry(url, path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, timeout=10)

            if r.status_code == 200:
                path.write_bytes(r.content)
                return True

            print(f"Attempt {attempt} failed ({r.status_code})")

        except Exception as e:
            print(f"Attempt {attempt} error: {e}")

        sleep(1)

    return False

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = list(csv.DictReader(f))
    random.shuffle(reader)

    for row in reader:
        set_name = row["Set"]
        card_name = row["Product Name"]
        number = normalize_number(row["Card Number"])

        set_code = SET_MAP.get(set_name)

        if not set_code:
            print("Unknown set:", set_name)
            if not FILL:
                continue
            else:
                set_code=set_name

        filename = f"{set_code}_{number}.png"
        filepath = OUTPUT_DIR / filename

        if filepath.exists():
            print("Skipping existing:", filename)
            continue
        url = f"https://images.pokemontcg.io/{set_code}/{number}_hires.png"
        print("Downloading:", card_name, number)
        if not (CRAWL or FILL):
            sleep(REQUEST_DELAY)
            if download_with_retry(url, filepath):
                print("Saved:", filename)
            else:
                print("Failed:", url)
                print("Is set code correct?", set_name)
                print(f"Missing: {set_code} {number}")
        if CRAWL:
            sleep(REQUEST_DELAY)
            try:
                print(f"Web search: pokemon card {set_name} {card_name}")
                # Grab first search result
                crawl_card(set_code, number, f"pokemon card {set_name} {card_name} {set_code} {number}")
                continue
            except:
                pass
        if FILL:
            # Finally lets generate a placeholder that could be replaced manually:
            print(f"Generated: {set_code} {number}")
            make_placeholder(set_code, number)

#!/usr/bin/env python3
"""Skibiditopia fake-drop generator with Discord webhook notifications."""

from __future__ import annotations

import json
import os
import random
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from flask import Flask, jsonify

app = Flask(__name__)

STATE_DIR = Path(os.getenv("STATE_DIR", "state"))
STATE_FILE = Path(os.getenv("STATE_FILE", str(STATE_DIR / "next_fire.json")))
LOG_FILE = Path(os.getenv("LOG_FILE", str(STATE_DIR / "poller.log")))
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

CATEGORIES = ("highlight", "peaklight", "og")
COLOURS = {"og": 0xFF0000, "peaklight": 0xF1C40F, "highlight": 0x9B59B6}
LABELS = {"og": "OG", "peaklight": "Peaklights", "highlight": "Highlights"}
INTERVALS = {
    "og": (1200, 3600),
    "highlight": (3, 8),
    "peaklight": (30, 90),
}

OG_PETS = [
    {
        "name": "Strawberry Elephant",
        "income_num": 750,
        "income": "$750M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/5/58/Strawberryelephant.png/revision/latest?cb=20260317001745",
    },
    {
        "name": "Meowl",
        "income_num": 600,
        "income": "$600M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/b/b8/Clear_background_clear_meowl_image.png/revision/latest?cb=20251022133154",
    },
    {
        "name": "John Pork",
        "income_num": 500,
        "income": "$500M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/d/d2/John_Pork.png/revision/latest?cb=20260502233229",
    },
    {
        "name": "Skibidi Toilet",
        "income_num": 450,
        "income": "$450M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/a/a7/Default_Skibidi_Toilet.png/revision/latest?cb=20260528092806",
    },
]

PEAKLIGHT_PETS = [
    {
        "name": "Dragon Cannelloni",
        "income_num": 8000,
        "income": "$250M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/a/a5/Dragon_Cannelloni.png/revision/latest?cb=20260428162417",
    },
    {
        "name": "Hydra Dragon Cannelloni",
        "income_num": 700,
        "income": "$300M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/e/ee/Hydra_Dragon_Cannelloni.png/revision/latest?cb=20260207220000",
    },
    {
        "name": "Venuspino",
        "income_num": 700,
        "income": "$175M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/0/0c/Venuspino.png/revision/latest?cb=20260616235620",
    },
    {
        "name": "Ginger Gerat",
        "income_num": 300,
        "income": "$75M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/b/be/Ginger_gerat.png/revision/latest?cb=20260723004607",
    },
    {
        "name": "La Supreme Combinasion",
        "income_num": 400,
        "income": "$200M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/c/c8/La_Supreme_Combinasion.png/revision/latest?cb=20260723010352",
    },
    {
        "name": "Dragon Gingerini",
        "income_num": 100,
        "income": "$350M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/a/a6/Dragon_Gingerini.png/revision/latest?cb=20260528114017",
    },
    {
        "name": "Griffin",
        "income_num": 50,
        "income": "$400M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/f/f8/Griffin.png/revision/latest?cb=20260417151951",
    },
]

HIGHLIGHT_PETS = [
    {
        "name": "Cerberus",
        "income_num": 175,
        "income": "$175M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/4/45/Cerberus.png/revision/latest?cb=20260217181804",
    },
    {
        "name": "Burguro And Fryuro",
        "income_num": 150,
        "income": "$150M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/6/65/Burguro-And-Fryuro.png/revision/latest?cb=20251007133840",
    },
    {
        "name": "Ganganzelli Trulala",
        "income_num": 0.009,
        "income": "$9K/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/b/b4/Ganganzelli_Trulala.png/revision/latest?cb=20260709005214",
    },
    {
        "name": "La Secret Combinasion",
        "income_num": 125,
        "income": "$125M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/1/1c/La_Secret_Combinasion.png/revision/latest?cb=20260417153348",
    },
    {
        "name": "Chillin Chili",
        "income_num": 25,
        "income": "$25M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/e/e0/Chilin.png/revision/latest?cb=20251226231712",
    },
    {
        "name": "Capitano Moby",
        "income_num": 160,
        "income": "$160M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/b/be/Capitano_Moby.png/revision/latest?cb=20260428162232",
    },
    {
        "name": "La Ginger Sekolah",
        "income_num": 75,
        "income": "$75M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/6/6b/La_Ginger_Sekolah.png/revision/latest?cb=20260723014016",
    },
    {
        "name": "Avocadorilla",
        "income_num": 0.007,
        "income": "$7K/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/8/85/Avocadorilla.png/revision/latest?cb=20260708203602",
    },
    {
        "name": "Garama and Madundung",
        "income_num": 50,
        "income": "$50M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/e/ee/Garamadundung.png/revision/latest?cb=20250816022557",
    },
    {
        "name": "Ketchuru and Musturu",
        "income_num": 42.5,
        "income": "$42.5M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/1/14/Ketchuru.png/revision/latest?cb=20251021163857",
    },
    {
        "name": "Spaghetti Tualetti",
        "income_num": 60,
        "income": "$60M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/c/ce/Spaghetti_Tualetti.png/revision/latest?cb=20260323001759",
    },
    {
        "name": "Ketupat Kepat",
        "income_num": 35,
        "income": "$35M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/a/ac/KetupatKepat.png/revision/latest?cb=20260324191002",
    },
    {
        "name": "Tralaledon",
        "income_num": 22,
        "income": "$22M/s",
        "image": "https://static.wikia.nocookie.net/stealabr/images/3/34/Tralaledon.png/revision/latest?cb=20260630134820",
    },
]

POOLS = {
    "og": OG_PETS,
    "peaklight": PEAKLIGHT_PETS,
    "highlight": HIGHLIGHT_PETS,
}

state: dict[str, Any] = {}
state_lock = threading.Lock()
stats = {"drop_counter": 0, "total_sent": 0, "started_at": time.time()}


def log(message: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    try:
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


def load_state() -> None:
    global state
    try:
        with STATE_FILE.open(encoding="utf-8") as handle:
            loaded = json.load(handle)
        if isinstance(loaded, dict):
            state = loaded
            stats["drop_counter"] = int(state.get("drop_counter", 0))
    except (FileNotFoundError, OSError, ValueError, TypeError):
        state = {}


def save_state() -> None:
    with state_lock:
        state["drop_counter"] = stats["drop_counter"]
        temporary = STATE_FILE.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
        temporary.replace(STATE_FILE)


def webhook_for(category: str) -> str:
    category_specific = os.getenv(f"DISCORD_WEBHOOK_{category.upper()}", "").strip()
    return category_specific or os.getenv("DISCORD_WEBHOOK_URL", "").strip()


def weighted_pick(pet_list: list[dict[str, Any]]) -> dict[str, Any]:
    weights = [pet.get("income_num", 1) for pet in pet_list]
    return pet_list[random.choices(range(len(pet_list)), weights=weights, k=1)[0]]


def generate_drop(category: str) -> dict[str, Any]:
    stats["drop_counter"] += 1
    pet = weighted_pick(POOLS[category])
    return {
        "id": f"fake_{category}_{stats['drop_counter']}",
        "name": pet["name"],
        "category": category,
        "image": pet["image"],
        "income": pet["income"],
    }


def build_embed(drop: dict[str, Any]) -> dict[str, Any]:
    category = drop["category"]
    embed: dict[str, Any] = {
        "title": f"Skibiditopia Notifier | {LABELS[category]}",
        "description": f"### Best\n**{drop['name']}** — {drop['income']}",
        "color": COLOURS[category],
        "footer": {"text": "Skibiditopia Notifier"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if str(drop.get("image", "")).startswith("http"):
        embed["thumbnail"] = {"url": drop["image"]}
    return embed


def send_drop(drop: dict[str, Any]) -> bool:
    category = drop["category"]
    url = webhook_for(category)
    if not url:
        log("Webhook fehlt: DISCORD_WEBHOOK_URL (oder eine Kategorie-Variable) setzen.")
        return False

    payload = {
        "content": os.getenv("DISCORD_OG_MENTION", "@everyone")
        if category == "og"
        else "",
        "embeds": [build_embed(drop)],
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code in (200, 204):
            stats["total_sent"] += 1
            log(f"Gesendet: {category.upper()} -> {drop['name']} ({drop['income']})")
            return True
        log(f"Discord HTTP {response.status_code}: {response.text[:150]}")
    except requests.RequestException as error:
        log(f"Discord-Fehler: {error}")
    return False


def run_cycle() -> None:
    now = time.time()
    fired = False
    with state_lock:
        due_categories = [
            category
            for category in CATEGORIES
            if now >= float(state.get(f"next_{category}", 0))
        ]

    for category in due_categories:
        drop = generate_drop(category)
        log(f"Neuer Drop: {category.upper()} -> {drop['name']} ({drop['income']})")
        send_drop(drop)
        with state_lock:
            state[f"next_{category}"] = now + random.uniform(*INTERVALS[category])
        fired = True

    if fired:
        save_state()


def poll_loop() -> None:
    log("Skibiditopia-Poller gestartet (24/7-Modus).")
    log("Intervalle: OG 20-60min | Highlights 3-8s | Peaklights 30-90s")
    load_state()

    while True:
        try:
            run_cycle()
            with state_lock:
                future = [
                    float(state.get(f"next_{category}", 0)) - time.time()
                    for category in CATEGORIES
                    if float(state.get(f"next_{category}", 0)) > time.time()
                ]
            time.sleep(max(1, min(future)) if future else 1)
        except Exception as error:  # Keep the service alive after one bad cycle.
            log(f"Poller-Fehler: {error}")
            time.sleep(5)


poller_started = False
poller_start_lock = threading.Lock()


def start_poller() -> None:
    global poller_started
    with poller_start_lock:
        if poller_started or os.getenv("DISABLE_POLLER", "").lower() == "true":
            return
        threading.Thread(target=poll_loop, name="skibiditopia-poller", daemon=True).start()
        poller_started = True


@app.get("/")
def home():
    with state_lock:
        next_drops = {
            category: state.get(f"next_{category}") for category in CATEGORIES
        }
    return jsonify(
        {
            "service": "skibiditopia-poller",
            "status": "running",
            "drops_sent": stats["total_sent"],
            "uptime_seconds": int(time.time() - stats["started_at"]),
            "next_drops": next_drops,
        }
    )


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


@app.get("/ping")
def ping():
    return "pong", 200


start_poller()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), debug=False)
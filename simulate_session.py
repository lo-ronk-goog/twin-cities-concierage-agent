#!/usr/bin/env python3
# ruff: noqa
import sys
import os
import time
import asyncio


def print_typewriter(text, delay=0.015):
    """Prints text with a typewriter effect to feel like a live streaming LLM."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def simulate_interactive():
    print_header("🤖 TWIN CITIES CONCIERGE — INTERACTIVE DEMO SIMULATOR")

    print(
        "\033[93m[System Info] This simulator showcases the agent's contextual memory, multi-turn dialogue,"
    )
    print(
        "and precise BigQuery database query generation for your customer demo.\033[0m\n"
    )

    # Turn 1
    print(
        "\033[1;36m[User]:\033[0m Hi! I'm planning a day out in Minneapolis this Thursday, August 13th, 2026. Can you recommend a nice local coffee shop to start my morning?"
    )
    time.sleep(1.5)

    print("\n\033[1;35m[Agent Thinking]:\033[0m")
    print("  -> User wants: Coffee shop, Minneapolis, Thursday morning.")
    print(
        "  -> Generating SQL query to retrieve Minneapolis coffee shops and their vibes..."
    )
    time.sleep(1.2)

    print("\n\033[1;32m[Tool Call] execute_sql_readonly:\033[0m")
    print(
        "\033[34mSELECT venue_id, name, neighborhood, vibe \nFROM `lpr-gemini-enterprise-1.msp_coffee_and_music.venues` \nWHERE city = 'Minneapolis' AND category = 'Coffee';\033[0m"
    )
    time.sleep(1.0)

    print("\n\033[1;32m[Tool Response]:\033[0m")
    print(
        "+----------+-------------------+--------------+---------------------------------+"
    )
    print(
        "| venue_id | name              | neighborhood | vibe                            |"
    )
    print(
        "+----------+-------------------+--------------+---------------------------------+"
    )
    print(
        "| V03      | Spyhouse Coffee   | Northeast    | Industrial, Hipster, Pour-overs |"
    )
    print(
        "| V09      | Dogwood Coffee Co| Longfellow   | Modern, Vibrant, Craft Espresso |"
    )
    print(
        "+----------+-------------------+--------------+---------------------------------+"
    )
    time.sleep(1.0)

    print("\n\033[1;35m[Agent Thinking]:\033[0m")
    print(
        "  -> Verifying operating hours for Spyhouse (V03) and Dogwood (V09) on Thursday..."
    )
    time.sleep(0.8)

    print("\n\033[1;32m[Tool Call] execute_sql_readonly:\033[0m")
    print(
        "\033[34mSELECT venue_id, open_time, close_time \nFROM `lpr-gemini-enterprise-1.msp_coffee_and_music.operating_hours` \nWHERE venue_id IN ('V03', 'V09') AND day_of_week = 'Thursday';\033[0m"
    )
    time.sleep(1.0)

    print("\n\033[1;32m[Tool Response]:\033[0m")
    print("+----------+-----------+------------+")
    print("| venue_id | open_time | close_time |")
    print("+----------+-----------+------------+")
    print("| V03      | 06:00:00  | 20:00:00   |")
    print("| V09      | 06:30:00  | 18:00:00   |")
    print("+----------+-----------+------------+")
    time.sleep(1.0)

    print("\n\033[1;33m[Agent]:\033[0m ", end="")
    print_typewriter(
        "Good morning! To kick off a wonderful Thursday in Minneapolis, I highly recommend starting "
        "your day in Northeast Minneapolis at **Spyhouse Coffee** (located at V03). It has an amazing hipster-industrial vibe "
        "with excellent pour-overs, and they open early at 6:00 AM on Thursdays.\n\n"
        "Alternatively, if you prefer a bright, vibrant, and ultra-modern space, **Dogwood Coffee Co.** in Longfellow (V09) is "
        "another craft-espresso powerhouse open from 6:30 AM to 6:00 PM. Both are local legends!",
        delay=0.012,
    )

    # Turn 2
    print("\n" + "-" * 80 + "\n")
    input("\033[1;30mPress [Enter] to simulate User response...\033[0m")
    print(
        "\n\033[1;36m[User]:\033[0m That sounds great! After coffee, I'd love to see some live music later that night. Are there any events scheduled at local bars or jazz clubs on Thursday?"
    )
    time.sleep(1.5)

    print("\n\033[1;35m[Agent Thinking]:\033[0m")
    print(
        "  -> User wants: Live music events, Thursday, August 13th, 2026, Minneapolis."
    )
    print("  -> Joining events and venues tables on date '2026-August-13'...")
    time.sleep(1.2)

    print("\n\033[1;32m[Tool Call] execute_sql_readonly:\033[0m")
    print(
        "\033[34mSELECT e.event_id, e.artist, e.genre, e.start_time, v.name AS venue_name \nFROM `lpr-gemini-enterprise-1.msp_coffee_and_music.events` e \nJOIN `lpr-gemini-enterprise-1.msp_coffee_and_music.venues` v ON e.venue_id = v.venue_id \nWHERE e.event_date = '2026-August-13';\033[0m"
    )
    time.sleep(1.0)

    print("\n\033[1;32m[Tool Response]:\033[0m")
    print(
        "+----------+----------------------------------------+---------------------+------------+--------------------+"
    )
    print(
        "| event_id | artist                                 | genre               | start_time | venue_name         |"
    )
    print(
        "+----------+----------------------------------------+---------------------+------------+--------------------+"
    )
    print(
        "| E22      | Icehouse Live Hip-Hop & Brass Jam      | Hip-Hop/Jazz        | 21:00:00   | The Icehouse       |"
    )
    print(
        "| E23      | Legendary Palmer's Blues Open Mic      | Blues               | 20:00:00   | Palmer's Bar       |"
    )
    print(
        "| E24      | Dogwood Espresso Cupping & Vinyl Beats | Electronic/Chillout | 16:30:00   | Dogwood Coffee Co. |"
    )
    print(
        "+----------+----------------------------------------+---------------------+------------+--------------------+"
    )
    time.sleep(1.0)

    print("\n\033[1;33m[Agent]:\033[0m ", end="")
    print_typewriter(
        "You are in luck! We have three fantastic events scheduled in Minneapolis this Thursday, August 13th, 2026:\n\n"
        "1. 🎷 **The Icehouse** (Whittier neighborhood): hosting the **Icehouse Live Hip-Hop & Brass Jam** at **9:00 PM (21:00:00)**. "
        "This is an incredible, high-energy fusion of jazz and live hip-hop beats in a very trendy, modern bi-level restaurant space.\n"
        "2. 🎸 **Palmer's Bar** (West Bank): holding their **Legendary Palmer's Blues Open Mic** starting at **8:00 PM (20:00:00)**. "
        "Palmer's is historic, gritty, and features some of the most authentic blues performers in the Midwest.\n"
        "3. 🎧 **Dogwood Coffee Co.** (Longfellow): hosting their **Espresso Cupping & Vinyl DJ Set** starting at **4:30 PM (16:30:00)**. "
        "This is a perfect chill transition event if you want to sample some coffees and listen to vinyl spins!",
        delay=0.012,
    )

    # Turn 3
    print("\n" + "-" * 80 + "\n")
    input("\033[1;30mPress [Enter] to simulate User response...\033[0m")
    print(
        "\n\033[1;36m[User]:\033[0m Awesome. I think I'll go with Icehouse! What are their operating hours on Thursdays?"
    )
    time.sleep(1.5)

    print("\n\033[1;35m[Agent Thinking]:\033[0m")
    print("  -> User selected: Icehouse (V06).")
    print(
        "  -> Querying operating hours for Icehouse on Thursday to verify schedule compatibility..."
    )
    time.sleep(1.0)

    print("\n\033[1;32m[Tool Call] execute_sql_readonly:\033[0m")
    print(
        "\033[34mSELECT open_time, close_time \nFROM `lpr-gemini-enterprise-1.msp_coffee_and_music.operating_hours` \nWHERE venue_id = 'V06' AND day_of_week = 'Thursday';\033[0m"
    )
    time.sleep(1.0)

    print("\n\033[1;32m[Tool Response]:\033[0m")
    print("+-----------+------------+")
    print("| open_time | close_time |")
    print("+-----------+------------+")
    print("| 11:00:00  | 00:00:00   |")
    print("+-----------+------------+")
    time.sleep(1.0)

    print("\n\033[1;33m[Agent]:\033[0m ", end="")
    print_typewriter(
        "Great choice! **The Icehouse** is open from **11:00 AM to midnight (00:00:00)** on Thursdays. \n\n"
        "Since the live Hip-Hop & Brass Jam starts at **9:00 PM (21:00:00)** and finishes before midnight, "
        "you'll have plenty of time to grab a table, enjoy a premium dinner or a craft cocktail, and experience "
        "one of the coolest live music showcases in the Twin Cities. It fits your Thursday schedule beautifully!",
        delay=0.012,
    )

    print_header("🎉 DEMO SIMULATION COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    simulate_interactive()

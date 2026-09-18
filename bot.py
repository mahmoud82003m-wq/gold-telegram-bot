import json
import time
import os
import urllib.request
import urllib.parse

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

API = f"https://api.telegram.org/bot{TOKEN}/"


def telegram(method, data=None):
    if data is None:
        data = {}

    encoded = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(API + method, data=encoded)

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode())


def get_gold_price():
    with urllib.request.urlopen(
        "https://api.gold-api.com/price/XAU",
        timeout=15
    ) as response:
        gold_data = json.loads(response.read().decode())

    gold_usd_ounce = float(gold_data["price"])

    with urllib.request.urlopen(
        "https://open.er-api.com/v6/latest/USD",
        timeout=15
    ) as response:
        currency_data = json.loads(response.read().decode())

    usd_egp = float(currency_data["rates"]["EGP"])

    gram_24 = (gold_usd_ounce / 31.1034768) * usd_egp

    gram_24 = round(gram_24)
    gram_21 = round(gram_24 * 21 / 24)
    gram_18 = round(gram_24 * 18 / 24)

    return gram_24, gram_21, gram_18


def send_message(chat_id, text):
    telegram("sendMessage", {
        "chat_id": chat_id,
        "text": text
    })


def main():
    print("Gold Telegram Bot is running...")

    offset = 0

    while True:
        try:
            result = telegram("getUpdates", {
                "offset": offset,
                "timeout": 30
            })

            for update in result.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()

                if text == "/start":
                    send_message(
                        chat_id,
                        "🪙 أهلاً بك في بوت أسعار الذهب\n\n"
                        "اكتب /gold لمعرفة أسعار الذهب."
                    )

                elif text == "/gold" or text == "ذهب":
                    try:
                        g24, g21, g18 = get_gold_price()

                        message_text = (
                            "🪙 أسعار الذهب\n\n"
                            f"🥇 عيار 24: {g24:,} جنيه\n"
                            f"🥇 عيار 21: {g21:,} جنيه\n"
                            f"🥇 عيار 18: {g18:,} جنيه\n\n"
                            "⏱ آخر تحديث: الآن\n\n"
                            "⚠️ الأسعار استرشادية وقد تختلف عن أسعار السوق المحلية."
                        )

                        send_message(chat_id, message_text)

                    except Exception:
                        send_message(
                            chat_id,
                            "❌ تعذر الحصول على الأسعار حالياً.\n"
                            "حاول مرة أخرى بعد قليل."
                        )

                else:
                    send_message(
                        chat_id,
                        "اكتب /gold لمعرفة أسعار الذهب 🪙"
                    )

        except Exception as error:
            print("Error:", error)
            time.sleep(5)


if __name__ == "__main__":
    main()

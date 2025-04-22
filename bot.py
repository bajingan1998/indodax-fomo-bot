import requests
import asyncio
import datetime

# List koin pilihan (344 coin milik ente), contoh disederhanakan dulu
# Format: ['btcidr', 'ethidr', 'dogeidr', ...]
MY_COINS = [
    'btcidr', 'ethidr', 'dogeidr'
    # tambahkan sisanya nanti di file atau langsung di sini
]

# Simpan data harga sebelumnya untuk perbandingan
previous_data = {}

async def fetch_price(coin):
    try:
        url = f"https://indodax.com/api/ticker/{coin}"
        response = requests.get(url, timeout=10)
        data = response.json()
        last_price = float(data['ticker']['last'])
        volume = float(data['ticker']['vol'])
        return coin, last_price, volume
    except Exception as e:
        return coin, None, None

async def analyze():
    while True:
        print("\n[INFO] Checking prices...", datetime.datetime.now())
        tasks = [fetch_price(coin) for coin in MY_COINS]
        results = await asyncio.gather(*tasks)

        triggered = []

        for coin, price, volume in results:
            if price is None or volume is None:
                continue

            prev = previous_data.get(coin, {'price': price, 'volume': volume})
            price_diff = price - prev['price']
            vol_diff = volume - prev['volume']

            # Deteksi kenaikan signifikan
            if price_diff / prev['price'] > 0.03 and vol_diff / prev['volume'] > 0.5:
                triggered.append({
                    'coin': coin,
                    'price': price,
                    'volume': volume,
                    'price_up_%': round(price_diff / prev['price'] * 100, 2),
                    'volume_up_%': round(vol_diff / prev['volume'] * 100, 2)
                })

            # Simpan data saat ini
            previous_data[coin] = {'price': price, 'volume': volume}

        # Output coin strategis
        if triggered:
            print("\n[!] Coin Potensi Bullish/FOMO:")
            for t in triggered:
                print(f"- {t['coin']}: Price naik {t['price_up_%']}%, Volume naik {t['volume_up_%']}%")
        else:
            print("[INFO] Tidak ada coin signifikan saat ini.")

        await asyncio.sleep(300)  # 5 menit

if __name__ == "__main__":
    asyncio.run(analyze())

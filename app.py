import os
import json
import requests
from flask import Flask, render_template_string, request
from groq import Groq

app = Flask(__name__)

# --- دریافت کلیدها از تنظیمات رندر (Environment Variables) ---
# پیشنهاد می‌شود کلیدها را در پنل Render ست کنید تا امنیت حفظ شود
CLASH_API_KEY = os.environ.get("CLASH_API_KEY", "YOUR_DEFAULT_API_KEY_IF_NOT_SET")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_DEFAULT_GROQ_KEY_IF_NOT_SET")

client = Groq(api_key=GROQ_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clash AI Architect | Ayhan</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
    <style>
        :root {
            --glass: rgba(255, 255, 255, 0.08);
            --border: rgba(255, 255, 255, 0.2);
            --primary: #00d2ff;
            --accent: #ffce00;
        }

        body {
            font-family: 'Vazirmatn', sans-serif;
            margin: 0; padding: 0; min-height: 100vh;
            background: radial-gradient(circle at center, #1a1a2e 0%, #0a0a12 100%);
            color: white; display: flex; flex-direction: column; align-items: center;
        }

        .glass-panel {
            background: var(--glass);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid var(--border);
            border-radius: 35px;
            padding: 40px 20px;
            margin: 40px 10px;
            width: 95%; max-width: 650px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.6);
        }

        h1 { color: var(--accent); font-size: 2.5rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px; }

        input, select {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border);
            padding: 15px;
            border-radius: 18px;
            color: white !important;
            margin: 12px auto;
            width: 85%;
            font-family: 'Vazirmatn';
            font-size: 1rem;
            display: block;
            outline: none;
        }

        select option { background: #1a1a2e; color: white; }

        button {
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            border: none; padding: 16px 60px; border-radius: 18px;
            color: white; font-weight: bold; font-size: 1.2rem;
            cursor: pointer; transition: 0.4s; margin-top: 20px;
        }

        button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,210,255,0.4); }

        .deck-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px; margin-top: 35px;
        }

        @media (max-width: 550px) { .deck-grid { grid-template-columns: repeat(2, 1fr); } }

        .card-wrapper {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px; padding: 12px;
            border: 1px solid var(--border);
            transition: 0.3s;
        }

        .card-wrapper:hover { border-color: var(--primary); transform: translateY(-8px); background: rgba(0, 210, 255, 0.1); }
        .card-wrapper img { width: 100%; height: auto; filter: drop-shadow(0 5px 15px rgba(0,0,0,0.5)); }
        .card-name { font-size: 0.75rem; margin-top: 10px; font-weight: bold; color: #fff; }

        .elixir-badge {
            background: linear-gradient(90deg, #e94560, #950740);
            padding: 12px 35px; border-radius: 50px;
            display: inline-block; margin-top: 30px;
            font-weight: bold; font-size: 1.2rem;
            box-shadow: 0 5px 15px rgba(233, 69, 96, 0.4);
        }

        footer { margin-top: auto; padding: 40px; font-size: 0.9rem; opacity: 0.8; }
        .loader { display: none; color: var(--accent); margin-top: 25px; font-weight: bold; }
    </style>
</head>
<body>

    <div class="glass-panel animate__animated animate__zoomIn">
        <h1>Clash AI</h1>
        <p style="opacity: 0.7;">معماری هوشمند دک بر اساس متای جهانی</p>

        <form method="POST" onsubmit="document.getElementById('loading').style.display='block';">
            <input type="text" name="tag" placeholder="تگ بازیکن: مثلا VQY8QCVL0" required>
            <select name="style">
                <option value="Fast Cycle">سایکل سریع (Fast Cycle)</option>
                <option value="Heavy Beatdown">سنگین (Beatdown)</option>
                <option value="Bridge Spam">تهاجمی پل (Bridge Spam)</option>
                <option value="Control">کنترلی (Control)</option>
                <option value="7x Elixir">اکسیر ۷ برابر (Infinite)</option>
            </select>
            <button type="submit">آنالیز و ساخت دک</button>
        </form>

        <div id="loading" class="loader animate__animated animate__flash animate__infinite">در حال دریافت اطلاعات از سرور سوپرسل...</div>

        {% if deck %}
            <div class="deck-grid">
                {% for card in deck %}
                <div class="card-wrapper animate__animated animate__fadeInUp" style="animation-delay: {{ loop.index0 * 0.1 }}s">
                    <img src="{{ card.image }}" alt="{{ card.name }}">
                    <div class="card-name">{{ card.name }}</div>
                </div>
                {% endfor %}
            </div>
            {% if elixir %}
            <div class="elixir-badge animate__animated animate__bounceIn">
                میانگین اکسیر: {{ elixir }}
            </div>
            {% endif %}
        {% endif %}

        {% if error %}
            <div style="color: #ff4d6d; margin-top: 20px;">{{ error }}</div>
        {% endif %}
    </div>

    <footer>
        ساخته شده با ❤️ توسط آیهان قلی زاده
    </footer>

</body>
</html>
"""

def fetch_player_cards(tag):
    tag = tag.replace("#", "").upper()
    url = f"https://api.clashroyale.com/v1/players/%23{tag}"
    headers = {"Authorization": f"Bearer {CLASH_API_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            card_db = {}
            api_cards = []
            for c in data.get('cards', []):
                name = c['name']
                card_db[name.lower()] = {"image": c['iconUrls']['medium'], "elixir": c.get('elixirCost', 0)}
                api_cards.append({
                    "name": name,
                    "level": c['level'] + (14 - c['maxLevel']),
                    "elixir": c.get('elixirCost', 0)
                })
            return api_cards, card_db
        return None, None
    except:
        return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    deck_data, elixir_avg, error_msg = [], None, None
    if request.method == "POST":
        tag = request.form.get("tag")
        style = request.form.get("style")
        cards_list, card_db = fetch_player_cards(tag)
        
        if cards_list:
            json_input = json.dumps(cards_list, separators=(',', ':'))
            system_instruction = "Professional Clash Royale Analyst. Build a top-tier deck. Output EXACTLY 8 card names from the data provided, one per line. No extra words."
            
            try:
                chat = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"Archetype: {style}. Data: {json_input}"}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2
                )
                
                lines = chat.choices[0].message.content.strip().split('\n')
                total_elixir, count = 0, 0
                
                for line in lines:
                    clean_name = line.strip().strip('0123456789. -*')
                    lower_name = clean_name.lower()
                    if lower_name in card_db and count < 8:
                        deck_data.append({"name": clean_name, "image": card_db[lower_name]["image"]})
                        total_elixir += card_db[lower_name]["elixir"]
                        count += 1
                
                if count > 0:
                    elixir_avg = round(total_elixir / count, 1)
            except:
                error_msg = "خطا در ارتباط با هوش مصنوعی."
        else:
            error_msg = "خطا: تگ پیدا نشد یا آی‌پی مسدود است."

    return render_template_string(HTML_TEMPLATE, deck=deck_data, elixir=elixir_avg, error=error_msg)

if __name__ == "__main__":
    # تنظیمات پورت برای رندر
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
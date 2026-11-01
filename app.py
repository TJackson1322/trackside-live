
from flask import Flask, render_template_string, send_from_directory, abort
from pathlib import Path
import json

app = Flask(__name__)
BASE = Path(__file__).resolve().parent

with (BASE / "drivers.json").open(encoding="utf-8") as f:
    drivers = json.load(f)["drivers"]
with (BASE / "race_data.json").open(encoding="utf-8") as f:
    race_data = json.load(f)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TrackSide Live</title>
    <style>
        body {
            margin: 0;
            background: #101116;
            color: white;
            font-family: Arial, sans-serif;
        }
        header {
            padding: 35px 20px;
            text-align: center;
            background: #1b1d25;
            border-bottom: 4px solid #ed2939;
        }
        h1 { font-size: 42px; margin: 0; }
        .red { color: #ff3548; }
        .subtitle { color: #bfc1c9; margin-top: 12px; }
        main { max-width: 1100px; margin: auto; padding: 30px 20px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 22px;
        }
        .card {
            background: #20232c;
            border-radius: 14px;
            overflow: hidden;
            text-decoration: none;
            color: white;
            transition: transform .2s;
        }
        .card:hover { transform: translateY(-6px); }
        .card img {
            width: 100%;
            height: 260px;
            object-fit: cover;
        }
        .info { padding: 20px; }
        .number { color: #ff3548; font-size: 26px; font-weight: bold; }
        .division { color: #bfc1c9; }
        .back { color: #ff3548; text-decoration: none; }
        .profile { max-width: 650px; margin: auto; }
        .profile img { width: 100%; border-radius: 12px; }
    </style>
</head>
<body>
<header>
    <h1>🏁 TRACK<span class="red">SIDE</span> LIVE</h1>
    <p class="subtitle">Driver Profiles • Racing History • Live Timing</p>
</header>
<main>
{% if driver %}
    <div class="profile">
        <a class="back" href="/">← All Drivers</a>
        <h2>#{{ driver.car_number }} {{ driver.name }}</h2>
        <img src="{{ url_for('driver_photo', filename=driver.profile_photo.split('/')[-1]) }}"
             alt="{{ driver.name }}">
        <p class="division">{{ driver.divisions | join(', ') }}</p>
        <h3>🏆 Achievements</h3>
        {% for achievement in driver.achievements %}
            <p>{{ achievement.year }} — {{ achievement.title }}</p>
            <p>{{ achievement.location }}</p>
        {% else %}
            <p>Achievements coming soon.</p>
        {% endfor %}
        <h3>🏎️ Race History</h3>
        <p>Race history coming soon.</p>
    </div>
{% else %}
    <h2>Featured Drivers</h2>
    <div class="grid">
        {% for racer in drivers %}
        <a class="card" href="{{ url_for('driver_profile', driver_id=racer.driver_id) }}">
            <img src="{{ url_for('driver_photo', filename=racer.profile_photo.split('/')[-1]) }}"
                 alt="{{ racer.name }}">
            <div class="info">
                <div class="number">#{{ racer.car_number }}</div>
                <h2>{{ racer.name }}</h2>
                <p class="division">{{ racer.divisions | join(', ') }}</p>
                <strong>View Profile →</strong>
            </div>
        </a>
        {% endfor %}
    </div>
{% endif %}
</main>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, drivers=drivers, driver=None)

@app.route("/driver/<driver_id>")
def driver_profile(driver_id):
    driver = next(
        (d for d in drivers if d["driver_id"] == driver_id),
        None
    )
    if driver is None:
        abort(404)
    return render_template_string(HTML, drivers=drivers, driver=driver)

@app.route("/photos/<path:filename>")
def driver_photo(filename):
    return send_from_directory(BASE / "driver_photos", filename)

@app.route("/race-center")
def race_center():
    from flask import request

    selected_track = request.args.get("track", "salem")
    selected_division = request.args.get("division", "Legends")

    tracks = race_data["tracks"]
    divisions = race_data["divisions"]

    sessions = [
        session for session in race_data["sessions"]
        if session["track_id"] == selected_track
        and session["division"] == selected_division
    ]

    page = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TrackSide Live - Race Center</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                background: #101116;
                color: white;
                font-family: Arial, sans-serif;
                margin: 0;
            }
            header {
                background: #1b1d25;
                padding: 25px;
                text-align: center;
                border-bottom: 4px solid #ed2939;
            }
            main {
                max-width: 1000px;
                margin: auto;
                padding: 30px 20px;
            }
            a { color: #ff3548; }
            select, button {
                padding: 12px;
                margin: 8px;
                border-radius: 6px;
                font-size: 16px;
            }
            button {
                background: #ed2939;
                color: white;
                border: none;
                cursor: pointer;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 25px;
            }
            th, td {
                padding: 15px;
                border-bottom: 1px solid #444;
                text-align: left;
            }
            th { color: #ff3548; }
            .demo {
                color: #ffcc66;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
    <header>
        <h1>🏁 TRACKSIDE LIVE</h1>
        <h2>RACE CENTER</h2>
    </header>
    <main>
        <a href="/">← Driver Profiles</a>

        <h2>Select Your Race</h2>

        <form method="get">
            <select name="track">
                {% for track in tracks %}
                <option value="{{ track.id }}"
                    {% if track.id == selected_track %}selected{% endif %}>
                    {{ track.name }}
                </option>
                {% endfor %}
            </select>

            <select name="division">
                {% for division in divisions %}
                <option value="{{ division }}"
                    {% if division == selected_division %}selected{% endif %}>
                    {{ division }}
                </option>
                {% endfor %}
            </select>

            <button type="submit">View Results</button>
        </form>

        {% for session in sessions %}
            <h2>{{ session.session_type }} Results</h2>
            <p class="demo">DEMONSTRATION DATA — NOT REAL RACE RESULTS</p>

            <table>
                <tr>
                    <th>Position</th>
                    <th>Car #</th>
                    <th>Driver</th>
                    <th>Best Lap</th>
                </tr>
                {% for result in session.results %}
                <tr>
                    <td>{{ result.position }}</td>
                    <td>#{{ result.car_number }}</td>
                    <td>{{ result.driver }}</td>
                    <td>{{ "%.3f"|format(result.best_lap_seconds) }} sec</td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>No race results available for this selection yet.</p>
        {% endfor %}
    </main>
    </body>
    </html>
    """

    return render_template_string(
        page,
        tracks=tracks,
        divisions=divisions,
        sessions=sessions,
        selected_track=selected_track,
        selected_division=selected_division
    )

if __name__ == "__main__":
    app.run(debug=True)

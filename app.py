
from flask import Flask, render_template_string, render_template, send_from_directory, abort, request
from pathlib import Path
import json

app = Flask(__name__)
BASE = Path(__file__).resolve().parent

with (BASE / "drivers.json").open(encoding="utf-8") as f:
    drivers = json.load(f)["drivers"]
with (BASE / "race_data.json").open(encoding="utf-8") as f:
    race_data = json.load(f)
with (BASE / "race_history.json").open(encoding="utf-8") as f:
    history_data = json.load(f)["races"]

with (BASE / "verified_results.json").open(encoding="utf-8") as f:
    verified_results = json.load(f)["results"]

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
<nav style="text-align:center; margin-bottom:30px;">
    <a href="/" style="color:white; margin-right:25px;">🏠 Home</a>
    <a href="/race-center" style="background:#ed2939; color:white; padding:12px 22px; border-radius:8px; text-decoration:none;">🏁 Race Center</a>
    <a href="/live-timing" style="color:white; margin-left:20px;">⏱ Live Timing</a>
    <a href="/race-history" style="color:white; margin-left:20px;">📅 Race History</a>
    <a href="/verified-results" style="color:white; margin-left:20px;">✓ Verified Results</a>
    <a href="/driver-garage" style="color:white; margin-left:20px;">🔒 Driver Garage</a>
</nav>
{% if driver %}
    <div class="profile">
        <a class="back" href="/">← All Drivers</a>
        <h2>#{{ driver.car_number }} {{ driver.name }}</h2>
        <img src="{{ url_for('driver_photo', filename=driver.profile_photo.split('/')[-1]) }}"
             alt="{{ driver.name }}">
        <p class="division">{{ driver.divisions | join(', ') }}</p>
        <h3>🏆 Career Timeline</h3>
        <p style="color:#bfc1c9;font-size:13px;">Reported milestones, shown by season. Additional track records and sponsors can be added when provided.</p>
        {% for achievement in driver.achievements %}
            <p>{{ achievement.year }} — {{ achievement.title }}</p>
            <p>{{ achievement.location }}{% if achievement.source_status %} <span style="color:#bfc1c9;font-size:12px;">({{ achievement.source_status }})</span>{% endif %}</p>
        {% else %}
            <p>Achievements coming soon.</p>
        {% endfor %}
        <h3>🏁 Source-backed Racing Statistics</h3>
        <p style="color:#bfc1c9;font-size:14px;">INEX points records are separate from race finishes. These are recorded event points, not a complete season total or career statistics.</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;">
            {% for label, value in [('INEX Records', verified_stats.records), ('Recorded Points', verified_stats.points), ('Championships', verified_stats.championships)] %}
            <div style="background:#20232c;border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#bfc1c9;font-size:13px;">{{ label }}</div>
                <strong style="font-size:25px;">{{ value }}</strong>
            </div>
            {% endfor %}
        </div>
        <p style="color:#bfc1c9;font-size:13px;">Championships are family-reported until independently sourced. Verified race starts, wins, podiums and average finish are not available yet.</p>
        <h3>📊 Driver Statistics <span style="font-size:13px;color:#ffdb92;">DEMO ONLY</span></h3>
        <p style="color:#bfc1c9;font-size:14px;">Statistics below are calculated from fictional demonstration race records, not verified career totals.</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;">
            {% for label, value in [('Starts', stats.starts), ('Wins', stats.wins), ('Podiums', stats.podiums), ('Top 5s', stats.top_fives), ('Avg Finish', stats.avg_finish)] %}
            <div style="background:#20232c;border-radius:10px;padding:15px;text-align:center;">
                <div style="color:#bfc1c9;font-size:13px;">{{ label }}</div>
                <strong style="font-size:25px;">{{ value }}</strong>
            </div>
            {% endfor %}
        </div>
        <p><a class="back" href="{{ url_for('verified_results_page', driver=driver.driver_id) }}">View source-backed results →</a></p>
        <p><a class="back" href="/driver-garage">🔒 Driver Garage — prototype &amp; privacy information →</a></p>
        <h3>🏎️ Race History</h3>
        <p><a class="back" href="{{ url_for('race_history_page', driver=driver.driver_id) }}">View {{ driver.name }}'s demonstration race history →</a></p>
        <p style="color:#bfc1c9;font-size:13px;">Career statistics will become available when verified racing results are added.</p>
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
    # Count only clearly labeled demonstration races; never imply these are career totals.
    finishes = [
        result["finish"]
        for race in history_data
        if race.get("status") == "DEMO"
        for result in race.get("results", [])
        if result.get("driver_id") == driver_id
    ]
    starts = len(finishes)
    stats = {
        "starts": starts,
        "wins": sum(finish == 1 for finish in finishes),
        "podiums": sum(finish <= 3 for finish in finishes),
        "top_fives": sum(finish <= 5 for finish in finishes),
        "avg_finish": f"{sum(finishes) / starts:.1f}" if starts else "—",
    }
    points_records = [
        item for item in verified_results
        if item.get("driver_id") == driver_id and item.get("record_type") == "INEX class points position"
    ]
    verified_stats = {
        "records": len(points_records),
        "points": sum(item.get("points", 0) for item in points_records),
        "championships": sum("champion" in a.get("title", "").lower() for a in driver.get("achievements", [])),
    }
    return render_template_string(HTML, drivers=drivers, driver=driver, stats=stats, verified_stats=verified_stats)

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
        <a href="/">← Driver Profiles</a> &nbsp; <a href="/live-timing">⏱ Live Timing Demo</a> &nbsp; <a href="/race-history">📅 Race History</a>

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

@app.route("/live-timing")
def live_timing():
    return render_template("live_timing.html", tracks=race_data["tracks"], divisions=race_data["divisions"])

@app.route("/race-history")
def race_history_page():
    selected_track = request.args.get("track", "")
    selected_driver = request.args.get("driver", "")
    selected_date = request.args.get("date", "")

    tracks_by_id = {track["id"]: track for track in race_data["tracks"]}
    drivers_by_id = {driver["driver_id"]: driver for driver in drivers}
    matching_races = []

    for race in history_data:
        if selected_track and race["track_id"] != selected_track:
            continue
        if selected_date and race["date"] != selected_date:
            continue
        results = []
        for result in race["results"]:
            if selected_driver and result["driver_id"] != selected_driver:
                continue
            driver = drivers_by_id.get(result["driver_id"])
            if not driver:
                continue
            results.append({
                **result,
                "driver_name": driver["name"],
                "car_number": driver["car_number"]
            })
        if not results:
            continue
        matching_races.append({
            **race,
            "track_name": tracks_by_id.get(race["track_id"], {}).get("name", race["track_id"]),
            "results": sorted(results, key=lambda result: result["finish"])
        })

    matching_races.sort(key=lambda race: race["date"], reverse=True)
    return render_template(
        "race_history.html",
        races=matching_races,
        tracks=race_data["tracks"],
        drivers=drivers,
        selected_track=selected_track,
        selected_driver=selected_driver,
        selected_date=selected_date
    )


@app.route("/verified-results")
def verified_results_page():
    selected_driver = request.args.get("driver", "")
    drivers_by_id = {driver["driver_id"]: driver for driver in drivers}
    results = []
    for result in verified_results:
        if selected_driver and result.get("driver_id") != selected_driver:
            continue
        driver = drivers_by_id.get(result.get("driver_id"))
        if not driver or not result.get("source_url") or not result.get("verified_on"):
            continue
        results.append({**result, "driver_name": driver["name"]})
    results.sort(key=lambda result: result.get("date", ""), reverse=True)
    return render_template("verified_results.html", results=results, drivers=drivers, selected_driver=selected_driver)


@app.route("/driver-garage")
def driver_garage():
    # Informational prototype only. Never accept private setup submissions without auth/storage.
    return render_template("driver_garage.html")


if __name__ == "__main__":
    app.run(debug=True)

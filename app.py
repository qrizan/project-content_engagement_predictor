from flask import Flask, render_template, request
import joblib
import pandas as pd
from datetime import datetime
import re

app = Flask(__name__)

# load model
model = joblib.load("model/content_engagement_rf.joblib")

# opsi untuk dropdown
PLATFORMS = ["TikTok", "YouTube"]
GENRES = ["Comedy", "Education", "Music", "Gaming", "Lifestyle", "Beauty", "Food", "Travel", "Tech", "Sports", "Entertainment"]
CATEGORIES = ["Entertainment", "Education", "Gaming", "Music", "Howto & Style", "Science & Tech", "Sports", "News", "People & Blogs"]

# kreator tier dengan keterangan avg views
CREATOR_TIERS = {
    "Micro": "5K views",
    "Mid": "50K views", 
    "Macro": "500K views",
    "Star": "2M views"
}
EVENT_SEASONS = ["Regular", "Ramadan", "HolidaySeason", "SummerBreak", "BackToSchool"]

# values untuk market Indonesia
DEFAULT_SETTINGS = {
    "country": "Id",
    "country_name": "Indonesia",
    "region": "Asia",
    "language": "id",
    "language_name": "Bahasa Indonesia"
}

# rata-rata engagement per platform, diambil dari tampilan distribusi di notebook 
PLATFORM_AVG = {
    "TikTok": 0.0918,
    "YouTube": 0.0509
}


# helper
def has_emoji(text: str) -> int:
    """Cek apakah text mengandung emoji"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U0001F900-\U0001F9FF"
        "]+",
        flags=re.UNICODE,
    )
    return 1 if emoji_pattern.search(text) else 0


def get_publish_period(hour: int) -> str:
    """Mapping jam ke periode hari"""
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


def get_day_name(weekday: int) -> str:
    """Convert weekday int ke nama hari"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[weekday]


def get_avg_views_from_tier(tier: str) -> float:
    """Mapping creator_tier ke estimasi avg views"""
    mapping = {
        "Micro": 5000.0,
        "Mid": 50000.0,
        "Macro": 500000.0,
        "Star": 2000000.0
    }
    return mapping.get(tier, 50000.0)


def get_season_from_date(dt: datetime) -> str:
    """Hitung season dari tanggal (untuk belahan bumi utara/Indonesia)"""
    month = dt.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:  # 9, 10, 11
        return "Fall"


def build_features(form_data, upload_dt: datetime) -> dict:
    """Build 20 fitur untuk model"""
    return {
        # Input langsung dari user
        "platform": form_data["platform"],
        "genre": form_data["genre"],
        "category": form_data["category"],
        "duration_sec": float(form_data["duration_sec"]),
        "creator_tier": form_data["creator_tier"],
        
        # Dihitung dari title
        "title_length": len(form_data["title"]),
        "has_emoji": has_emoji(form_data["title"]),
        "title_keywords": form_data["title"],
        
        # Dari hashtags
        "hashtag": form_data["hashtags"],
        "tags": "",  # Kosong (tidak digunakan)
        
        # Dihitung dari waktu upload
        "upload_hour": upload_dt.hour,
        "publish_dayofweek": get_day_name(upload_dt.weekday()),
        "publish_period": get_publish_period(upload_dt.hour),
        "is_weekend": 1 if upload_dt.weekday() >= 5 else 0,
        
        # Dihitung dari tier
        "creator_avg_views": get_avg_views_from_tier(form_data["creator_tier"]),
        
        # Dihitung dari waktu upload
        "season": get_season_from_date(upload_dt),
        
        # Input dari user
        "event_season": form_data["event_season"],
        
        # Default values untuk market Indonesia
        "country": DEFAULT_SETTINGS["country"],
        "region": DEFAULT_SETTINGS["region"],
        "language": DEFAULT_SETTINGS["language"],
    }


#routes
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    form_data = {
        "platform": "TikTok",
        "genre": "Comedy",
        "category": "Entertainment",
        "duration_sec": 60,
        "title": "",
        "hashtags": "",
        "creator_tier": "Mid",
        "upload_datetime": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "event_season": "Regular"
    }
    
    if request.method == "POST":
        # data dari form
        form_data = {
            "platform": request.form.get("platform", "TikTok"),
            "genre": request.form.get("genre", "Comedy"),
            "category": request.form.get("category", "Entertainment"),
            "duration_sec": request.form.get("duration_sec", 60),
            "title": request.form.get("title", ""),
            "hashtags": request.form.get("hashtags", ""),
            "creator_tier": request.form.get("creator_tier", "Mid"),
            "upload_datetime": request.form.get("upload_datetime", ""),
            "event_season": request.form.get("event_season", "Regular")
        }
        
        # memparse datetime
        try:
            upload_dt = datetime.strptime(form_data["upload_datetime"], "%Y-%m-%dT%H:%M")
        except:
            upload_dt = datetime.now()
        
        # features
        features = build_features(form_data, upload_dt)
        
        # Predict
        df = pd.DataFrame([features])
        if hasattr(model, "feature_names_in_"):
            df = df[list(model.feature_names_in_)]
        
        prediction = model.predict(df)[0]
        
        # perbandingan rata2 platform dengan prediksi
        platform_avg = PLATFORM_AVG.get(form_data["platform"], 0.07)
        diff = prediction - platform_avg
        diff_percent = abs(diff) * 100

        # menentukan posisi dengan toleransi untuk floating point
        if abs(diff) < 0.0001:  # untuk nilai yang sama
            position = "sama dengan"
        elif diff > 0:
            position = "di atas"
        else:
            position = "di bawah"

        result = {
            "engagement_rate": round(prediction * 100, 2),
            "platform_avg": round(platform_avg * 100, 2),
            "position": position,
            "diff_percent": round(diff_percent, 2),
            
            # 20 fitur 
            "all_features": {
                # input user
                "platform": features["platform"],
                "genre": features["genre"],
                "category": features["category"],
                "duration_sec": features["duration_sec"],
                "creator_tier": features["creator_tier"],
                "event_season": features["event_season"],
                
                # hitung dari title
                "title_length": features["title_length"],
                "has_emoji": "Ya" if features["has_emoji"] else "Tidak",
                "title_keywords": features["title_keywords"],
                
                # dari hashtags
                "hashtag": features["hashtag"],
                
                # hitung dari waktu
                "upload_hour": f"{features['upload_hour']}:00",
                "publish_period": features["publish_period"],
                "publish_dayofweek": features["publish_dayofweek"],
                "is_weekend": "Ya" if features["is_weekend"] else "Tidak",
                "season": features["season"],
                
                # hitung dari tier
                "creator_avg_views": f"{int(features['creator_avg_views']):,}",
                
                # default values
                "country": features["country"],
                "region": features["region"],
                "language": features["language"],
                "tags": features.get("tags", ""),
            }
        }
        
        # raw model output 
        result["raw_prediction"] = round(prediction, 6)  # Nilai mentah dari model.predict()
    
    return render_template(
        "index.html",
        result=result,
        form_data=form_data,
        platforms=PLATFORMS,
        genres=GENRES,
        categories=CATEGORIES,
        creator_tiers=CREATOR_TIERS,
        event_seasons=EVENT_SEASONS,
        default_settings=DEFAULT_SETTINGS
    )


@app.route("/health")
def health():
    return {"status": "ok", "model_loaded": True}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


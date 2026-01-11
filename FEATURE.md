## Fitur Model

Model menggunakan **20 fitur** untuk memprediksi engagement rate.

---

### Input Form User (9 field)

User mengisi 9 field berikut di form:

| No | Field Form | Tipe | Menjadi Fitur Model |
|----|------------|------|---------------------|
| 1 | Platform | Dropdown | `platform` |
| 2 | Genre | Dropdown | `genre` |
| 3 | Category | Dropdown | `category` |
| 4 | Duration | Slider | `duration_sec` |
| 5 | Video Title | Text | `title_keywords` + dihitung `title_length`, `has_emoji` |
| 6 | Hashtags | Text | `hashtag` |
| 7 | Waktu Upload | DateTime | Dihitung otomatis: `upload_hour`, `publish_dayofweek`, `publish_period`, `is_weekend`, `season` |
| 8 | Creator Tier | Dropdown | `creator_tier` + dihitung `creator_avg_views` |
| 9 | Event | Dropdown | `event_season` |

---

### 20 Fitur Model

| No | Fitur | Sumber | Keterangan |
|----|-------|--------|------------|
| 1 | `platform` | Input langsung | TikTok / YouTube |
| 2 | `genre` | Input langsung | Comedy, Education, dll |
| 3 | `category` | Input langsung | Entertainment, Gaming, dll |
| 4 | `duration_sec` | Input langsung | Durasi dalam detik |
| 5 | `creator_tier` | Input langsung | Micro, Mid, Macro, Star |
| 6 | `title_keywords` | = title | Judul video dari input user |
| 7 | `hashtag` | = hashtags | Isi hashtag dari form |
| 8 | `tags` | Default | "" (kosong, tidak digunakan) |
| 9 | `title_length` | Dihitung | `len(title)` |
| 10 | `has_emoji` | Dihitung | 1 jika ada emoji, 0 jika tidak |
| 11 | `upload_hour` | Dihitung | Jam dari upload_datetime (0-23) |
| 12 | `publish_dayofweek` | Dihitung | Nama hari (Monday-Sunday) |
| 13 | `publish_period` | Dihitung | Morning/Afternoon/Evening/Night |
| 14 | `is_weekend` | Dihitung | 1 jika Sabtu/Minggu |
| 15 | `season` | Dihitung otomatis | Winter, Spring, Summer, Fall (dari bulan tanggal upload) |
| 16 | `creator_avg_views` | Dihitung | Mapping dari tier (5K-2M) |
| 17 | `event_season` | Input langsung | Regular, Ramadan, dll |
| 18 | `country` | Default | "Id" (Indonesia) |
| 19 | `region` | Default | "Asia" |
| 20 | `language` | Default | "id" |

---

### Ringkasan

| Kategori | Jumlah |
|----------|--------|
| Input langsung dari form | 6 fitur |
| Dari input user (diproses) | 2 fitur (`title_keywords`, `hashtag`) |
| Dihitung otomatis | 8 fitur |
| Default (hardcoded) | 4 fitur |
| **Total** | **20 fitur** |
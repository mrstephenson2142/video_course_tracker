# 📚 Video Course Tracker

A local Flask web app for organizing and watching your personal video courses with progress tracking.

Made with Claude.ai

---

## 🔧 Requirements

- Python 3.7+
- Flask

Install dependencies:
```bash
pip install flask
```

---

## 🚀 Getting Started

1. **Run the App**:
   ```bash
   python app.py
   ```

2. **Open in Browser**:
   Navigate to [http://localhost:5000](http://localhost:5000)

---

## 🧠 Features

- ✅ Organize videos into **courses and sections**
- ✅ Track watch **progress** and **resume playback**
- ✅ Automatically mark videos as watched after 90%
- ✅ Drag-and-drop video reordering
- ✅ Playback speed control (0.5x to 2x)
- ✅ Fully offline — no internet or uploads

---

## 📂 Adding Videos

1. Click **+ Course** to create a new course.
2. Optionally, add sections inside a course.
3. Click **+ Videos** and enter the **local folder path** containing your videos.
4. Videos are added by **file path** only (not uploaded or copied).

---

## 💾 Data Storage

- All metadata is stored in `video_tracker.db` (SQLite)
- Video files stay in their **original location**
- No internet access required




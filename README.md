# Video Course Tracker - Setup Guide

## TODO: 

UPDATE README: 
- Refrences file paths instead of uploading videos. Haven't confirmed all features Claude talks about exist. The web app was updated several times without updating the README. 

## 🚀 Quick Setup

You can use this quick setup, but probably want to use a virtual environment. 

### 1. Install Python Dependencies
```bash
pip install flask
```

### 2. Create Project Structure
Create a new folder for your project and set up these files:

```
video-tracker/
├── app.py                  # Main Flask application
├── video_tracker.db       # SQLite database (created automatically)
├── videos/                 # Video files folder (created automatically)
└── templates/
    └── index.html          # Web interface
```

### 3. Run the Application
```bash
python app.py
```

### 4. Open in Browser
Navigate to: **http://localhost:5000**

---

## ✨ Features

### 📊 **Progress Tracking**
- **Automatic progress saving** every 5 seconds
- **Resume from where you left off** - videos remember your position
- **Visual progress bars** show completion percentage
- **Watch statistics** with total time and completion counts

### 🎬 **Video Management**
- **Upload multiple videos** at once
- **Organize videos into sections** (collapsible sidebar)
- **Manual watch/unwatch** toggle with checkboxes
- **Auto-mark as watched** when 90% complete
- **Drag-and-drop** video organization (planned for future update)

### ⚡ **Playback Controls**
- **Variable speed playback** (0.5x to 2x)
- **Auto-advance** to next video when current ends
- **Previous/Next navigation** across sections
- **Keyboard shortcuts**:
  - `Space` - Play/Pause
  - `←` - Previous video
  - `→` - Next video  
  - `F` - Fullscreen

### 🗂️ **Organization**
- **Collapsible sections** in left sidebar
- **Section management** (rename, delete, reorder)
- **Progress overview** shows watched/total counts
- **Persistent state** - everything saves to database

---

## 🔧 Usage Tips

### Adding Content
1. **Create sections first** using the "+ Section" button
2. **Upload videos** using the "+ Videos" button
3. **Videos automatically go** to the most recent section
4. **Rename sections** by clicking the edit (✏️) button

### Watching Videos
- **Click any video** to start playing
- **Progress saves automatically** every 5 seconds
- **Use checkboxes** to manually mark videos as watched/unwatched
- **Navigation buttons** help you move between videos

### Data Storage
- **All data persists** in `video_tracker.db` SQLite database
- **Video files stored** in the `videos/` folder
- **Progress, sections, and watch status** all saved locally
- **No internet required** - works completely offline

---

## 🛠️ Customization Options

### Database Schema
The app creates these tables automatically:
- `sections` - Course sections/chapters
- `videos` - Video files and metadata  
- `video_progress` - Detailed progress tracking

### File Storage
- Videos are copied to the `videos/` folder when uploaded
- Original filenames are preserved
- Large files supported (up to 500MB per file)

### Extending Functionality
The Flask app is easily extensible:
- Add video thumbnails
- Implement drag-and-drop reordering
- Add notes/bookmarks per video
- Export progress reports
- Add video search/filtering

---

## 🔍 Troubleshooting

### Common Issues

**Videos won't play:**
- Check that video files are in supported formats (MP4, WebM, etc.)
- Ensure browser supports the video codec

**Upload fails:**
- Check file size (max 500MB per file)
- Ensure videos/ folder has write permissions

**Database errors:**
- Delete `video_tracker.db` to reset (loses all progress)
- Check folder write permissions

**Port already in use:**
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000

### Performance Tips
- Keep video files under 100MB for best performance
- Close browser tabs when not using the app
- Restart the Flask app occasionally for optimal performance

---

## 🎯 Perfect For

- **Online course tracking** (Udemy, Coursera, etc.)
- **Training video libraries**
- **Educational content organization**
- **Personal learning progress**
- **Workshop and tutorial series**

Your video progress will never be lost again! 🎉
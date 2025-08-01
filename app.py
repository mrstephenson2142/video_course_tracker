# app.py
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
import json
from datetime import datetime
import mimetypes
import urllib.parse

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Courses table
    c.execute('''CREATE TABLE IF NOT EXISTS courses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  order_index INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Sections table (now belongs to a course, optional)
    c.execute('''CREATE TABLE IF NOT EXISTS sections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  course_id INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  order_index INTEGER NOT NULL,
                  collapsed BOOLEAN DEFAULT FALSE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (course_id) REFERENCES courses (id))''')
    
    # Videos table - can belong directly to course OR to a section
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  course_id INTEGER NOT NULL,
                  section_id INTEGER,
                  name TEXT NOT NULL,
                  file_path TEXT NOT NULL,
                  order_index INTEGER NOT NULL,
                  duration REAL DEFAULT 0,
                  current_time REAL DEFAULT 0,
                  watched BOOLEAN DEFAULT FALSE,
                  watch_count INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (course_id) REFERENCES courses (id),
                  FOREIGN KEY (section_id) REFERENCES sections (id))''')
    
    # Progress tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS video_progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  video_id INTEGER NOT NULL,
                  current_time REAL NOT NULL,
                  duration REAL,
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (video_id) REFERENCES videos (id))''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/courses')
def get_courses():
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Get courses
    c.execute('SELECT * FROM courses ORDER BY order_index')
    courses_data = c.fetchall()
    
    courses = []
    for course in courses_data:
        course_id = course[0]
        
        # Get sections for this course
        c.execute('SELECT * FROM sections WHERE course_id = ? ORDER BY order_index', (course_id,))
        sections_data = c.fetchall()
        
        sections = []
        for section in sections_data:
            section_id = section[0]
            
            # Get videos for this section
            c.execute('''SELECT v.*, vp.current_time as progress_time 
                         FROM videos v 
                         LEFT JOIN video_progress vp ON v.id = vp.video_id 
                         WHERE v.section_id = ? 
                         ORDER BY v.order_index''', (section_id,))
            videos_data = c.fetchall()
            
            videos = []
            for video in videos_data:
                videos.append({
                    'id': video[0],
                    'name': video[3],
                    'file_path': video[4],
                    'order_index': video[5],
                    'duration': video[6],
                    'current_time': video[7],
                    'watched': bool(video[8]),
                    'watch_count': video[9],
                    'progress_time': video[11] if video[11] else video[7]
                })
            
            sections.append({
                'id': section_id,
                'name': section[2],
                'order_index': section[3],
                'collapsed': bool(section[4]),
                'videos': videos
            })
        
        # Get videos directly in course (no section)
        c.execute('''SELECT v.*, vp.current_time as progress_time 
                     FROM videos v 
                     LEFT JOIN video_progress vp ON v.id = vp.video_id 
                     WHERE v.course_id = ? AND v.section_id IS NULL
                     ORDER BY v.order_index''', (course_id,))
        direct_videos_data = c.fetchall()
        
        direct_videos = []
        for video in direct_videos_data:
            direct_videos.append({
                'id': video[0],
                'name': video[3],
                'file_path': video[4],
                'order_index': video[5],
                'duration': video[6],
                'current_time': video[7],
                'watched': bool(video[8]),
                'watch_count': video[9],
                'progress_time': video[11] if video[11] else video[7]
            })
        
        courses.append({
            'id': course_id,
            'name': course[1],
            'description': course[2],
            'order_index': course[3],
            'sections': sections,
            'videos': direct_videos  # Videos without sections
        })
    
    conn.close()
    return jsonify(courses)

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    name = data.get('name', 'New Course')
    description = data.get('description', '')
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Get max order_index
    c.execute('SELECT MAX(order_index) FROM courses')
    max_order = c.fetchone()[0] or 0
    
    c.execute('INSERT INTO courses (name, description, order_index) VALUES (?, ?, ?)', 
              (name, description, max_order + 1))
    course_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({'id': course_id, 'name': name, 'description': description, 'order_index': max_order + 1})

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json()
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    if 'name' in data:
        c.execute('UPDATE courses SET name = ? WHERE id = ?', (data['name'], course_id))
    
    if 'description' in data:
        c.execute('UPDATE courses SET description = ? WHERE id = ?', (data['description'], course_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Delete progress for all videos in this course
    c.execute('''DELETE FROM video_progress 
                 WHERE video_id IN (SELECT id FROM videos WHERE course_id = ?)''', (course_id,))
    # Delete videos
    c.execute('DELETE FROM videos WHERE course_id = ?', (course_id,))
    # Delete sections
    c.execute('DELETE FROM sections WHERE course_id = ?', (course_id,))
    # Delete course
    c.execute('DELETE FROM courses WHERE id = ?', (course_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/sections', methods=['POST'])
def create_section():
    data = request.get_json()
    course_id = data.get('course_id')
    name = data.get('name', 'New Section')
    
    if not course_id:
        return jsonify({'error': 'Course ID required'}), 400
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Get max order_index for this course
    c.execute('SELECT MAX(order_index) FROM sections WHERE course_id = ?', (course_id,))
    max_order = c.fetchone()[0] or 0
    
    c.execute('INSERT INTO sections (course_id, name, order_index) VALUES (?, ?, ?)', 
              (course_id, name, max_order + 1))
    section_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({'id': section_id, 'name': name, 'order_index': max_order + 1})

@app.route('/api/sections/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    data = request.get_json()
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    if 'name' in data:
        c.execute('UPDATE sections SET name = ? WHERE id = ?', 
                  (data['name'], section_id))
    
    if 'collapsed' in data:
        c.execute('UPDATE sections SET collapsed = ? WHERE id = ?', 
                  (data['collapsed'], section_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/sections/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Delete videos and their progress in this section
    c.execute('DELETE FROM video_progress WHERE video_id IN (SELECT id FROM videos WHERE section_id = ?)', (section_id,))
    c.execute('DELETE FROM videos WHERE section_id = ?', (section_id,))
    c.execute('DELETE FROM sections WHERE id = ?', (section_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/videos', methods=['POST'])
def add_video_paths():
    """Add video file paths to database without copying files"""
    data = request.get_json()
    course_id = data.get('course_id')
    section_id = data.get('section_id')  # Optional - can be null for course-level videos
    file_paths = data.get('file_paths', [])
    
    if not course_id or not file_paths:
        return jsonify({'error': 'Course ID and file paths required'}), 400
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Get max order_index for this course/section
    if section_id:
        c.execute('SELECT MAX(order_index) FROM videos WHERE section_id = ?', (section_id,))
    else:
        c.execute('SELECT MAX(order_index) FROM videos WHERE course_id = ? AND section_id IS NULL', (course_id,))
    max_order = c.fetchone()[0] or 0
    
    # Prepare video data with filenames for sorting
    video_data = []
    for file_path in file_paths:
        # Normalize the path
        full_path = os.path.abspath(file_path)
        
        if os.path.exists(full_path):
            filename = os.path.basename(full_path)
            
            # Check if this file is already in the database for this course/section
            if section_id:
                c.execute('SELECT id FROM videos WHERE file_path = ? AND section_id = ?', (full_path, section_id))
            else:
                c.execute('SELECT id FROM videos WHERE file_path = ? AND course_id = ? AND section_id IS NULL', (full_path, course_id))
            
            if not c.fetchone():  # Only add if not duplicate
                video_data.append({
                    'filename': filename,
                    'full_path': full_path
                })
    
    # Sort videos by filename (natural sort for numbers)
    import re
    def natural_sort_key(item):
        # Split filename into text and number parts for natural sorting
        # This handles cases like: "1. Introduction.mp4", "10. Advanced.mp4" properly
        filename = item['filename'].lower()
        return [int(text) if text.isdigit() else text for text in re.split('([0-9]+)', filename)]
    
    video_data.sort(key=natural_sort_key)
    
    added_videos = []
    current_order = max_order + 1
    
    # Add videos in sorted order
    for video_info in video_data:
        filename = video_info['filename']
        full_path = video_info['full_path']
        
        # Add to database
        c.execute('''INSERT INTO videos (course_id, section_id, name, file_path, order_index) 
                     VALUES (?, ?, ?, ?, ?)''', 
                  (course_id, section_id, filename, full_path, current_order))
        
        video_id = c.lastrowid
        
        added_videos.append({
            'id': video_id,
            'name': filename,
            'file_path': full_path,
            'order_index': current_order
        })
        
        current_order += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'videos': added_videos})

@app.route('/api/videos/<int:video_id>/progress', methods=['POST'])
def update_video_progress(video_id):
    data = request.get_json()
    current_time = data.get('currentTime', 0)
    duration = data.get('duration', 0)
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Update or insert progress
    c.execute('DELETE FROM video_progress WHERE video_id = ?', (video_id,))
    c.execute('INSERT INTO video_progress (video_id, current_time, duration) VALUES (?, ?, ?)', 
              (video_id, current_time, duration))
    
    # Update video current_time and duration
    c.execute('UPDATE videos SET current_time = ?, duration = ? WHERE id = ?', 
              (current_time, duration, video_id))
    
    # Mark as watched if >90% complete
    if duration > 0 and current_time / duration > 0.9:
        c.execute('UPDATE videos SET watched = TRUE WHERE id = ?', (video_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/videos/<int:video_id>/watched', methods=['POST'])
def mark_video_watched(video_id):
    data = request.get_json()
    watched = data.get('watched', True)
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    c.execute('UPDATE videos SET watched = ?, watch_count = watch_count + 1 WHERE id = ?', 
              (watched, video_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/videos/<int:video_id>/order', methods=['PUT'])
def update_video_order(video_id):
    data = request.get_json()
    new_order = data.get('order_index')
    
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    c.execute('UPDATE videos SET order_index = ? WHERE id = ?', (new_order, video_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video and its progress"""
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    # Delete video progress first
    c.execute('DELETE FROM video_progress WHERE video_id = ?', (video_id,))
    
    # Delete the video record
    c.execute('DELETE FROM videos WHERE id = ?', (video_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/video/<int:video_id>')
def serve_video(video_id):
    """Serve video file from its original location"""
    conn = sqlite3.connect('video_tracker.db')
    c = conn.cursor()
    
    c.execute('SELECT file_path FROM videos WHERE id = ?', (video_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return "Video not found", 404
    
    file_path = result[0]
    
    if not os.path.exists(file_path):
        return "Video file not found on disk", 404
    
    return send_file(file_path)

@app.route('/api/browse-folder', methods=['POST'])
def browse_folder():
    """Browse a folder for video files"""
    data = request.get_json()
    folder_path = data.get('folder_path', '')
    
    if not folder_path or not os.path.exists(folder_path):
        return jsonify({'error': 'Invalid folder path'}), 400
    
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.mpg', '.mpeg'}
    video_files = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, folder_path)
                    video_files.append({
                        'name': file,
                        'path': full_path,
                        'relative_path': relative_path
                    })
    except Exception as e:
        return jsonify({'error': f'Error browsing folder: {str(e)}'}), 500
    
    return jsonify({'videos': video_files})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
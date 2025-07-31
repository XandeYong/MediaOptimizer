# 📦 Media Optimizer

**Media Optimizer** is a Python-based application designed to streamline the process of collecting, optimizing, and managing media files (images and videos). It supports logging, dependency injection, and modular architecture for scalability and maintainability.

---

## 🚀 Features

- ✅ Collects media files from a user-specified directory
- ✅ Supports image and video file types via MIME constants
- ✅ Logs application events and user input
- ✅ Optimizes media files using a modular pipeline
- 🔜 Planned: Google Drive integration for download/upload

---

## Development Stage
1. Auto Retrieve data from Google Photos **[Due to [Google Scopes Deprecation](https://issuetracker.google.com/issues/368779600?pli=1) this module is temporary paused]**
2. Optimize image and video to jpg and mp4 for smaller file size yet maintain similar quality **[Done]**
3. Upload Media back to Google Photos **[In-Progress]**
4. Apply Async to all the functions, currently only support single thread **[Haven't]**
5. Implement AVIF image optimization using libaom via ffmpeg **[Haven't]**

--- 

## Known Issue
1. Unable to process HEIF image properly

---

## 🧰 Project Structure

```bash
.
├── classes/
│   ├── google_auth.py
│   └── path_manager.py
├── components/
│   ├── startup.py
│   ├── my_logging.py
│   └── file_manager.py
├── constants/
│   └── media_mime_types.py
├── modules/
│   ├── download_files.py  # (commented out in main)
│   └── optimizer.py
└── main.py
```
---

## 🛠️ Installation

**1. Clone the repository**
``` 
git clone https://github.com/your-username/media-optimizer.git
cd media-optimizer
```


**2. Create a virtual environment**
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```
pip install -r requirements.txt
```

---

## 📂 Usage

**Run the application using:**
```
python main.py
```

**You'll be prompted to enter a folder path containing media files. The application will:**

1. Log startup and user input
2. Collect image and video files from the specified folder
3. Optimize the collected media files
4. Log completion

---

## 📄 License
This project is licensed under the MIT License.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

## 📬 Contact
For questions or feedback, feel free to reach out via GitHub Issues or email.
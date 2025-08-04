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
3. Implement AVIF image optimization using libaom via ffmpeg **[Done]**
4. Upload Media back to Google Photos **[In-Progress]**
5. Apply Async to all the functions, currently only support single thread **[Haven't]**

--- 

## Known Issue
1. Unable to process HEIF image properly **[Resolved]**

---

## 🧰 Project Structure

```bash
.
├── classes/*                  # Object classes
├── components/
│   ├── startup.py             # Manage startup process
│   ├── google_api_manager.py  # Manage Google API
│   ├── media_optimizer.py     # Manage media optimization
│   └── file_manager.py        # Manage files operation
├── constants/
│   └── media_mime_types.py
├── modules/
│   ├── download_files.py      # (Temporary not working)
│   ├── optimizer.py           # Handle optimization workflow
│   └── upload_files.py        # Handle upload files workflow
├── output/
│   └── {folder}
│       ├── failed_media       # Failed to process media files
│       ├── optimized_media    # Success media files
│       ├── raw_media          # Raw media files (raw format media files)
│       └── temp_media         # Temporary generated files
├── tools/*                    # 3rd party tools (exiftool, ffmpeg, etc...)
├── config.json                # Configuration on your setup
├── client_secret.json         # Google Generated secret file to identify your account
├── app_info.py                # Application Information
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

**4. Download and Install ffmpeg**
Recommend using ffmpeg build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
The version I use for developing this project is **[ffmpeg version 7.1.1-full_build-www.gyan.dev]**, you can use any other version that suits your needs.
```
Download ffmpeg
Install it into tools folder
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
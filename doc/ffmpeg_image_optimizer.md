# FFmpeg Image Optimizer

To **optimize HEIF, JPG, PNG, and WEBP images** and **convert them into JPEG using FFmpeg** in Python **without noticeable quality loss**, you can use the `subprocess` module with FFmpeg commands carefully tuned for quality.

---

### ✅ Key goals:

1. **Maintain high visual quality**.
2. **Ensure final format is JPEG**.
3. **Compress reasonably without artifacts**.

---

### ⚙️ FFmpeg Command Logic:

* Use `-q:v` for JPEG quality (1 is best, 31 is worst).
* Strip metadata with `-map_metadata -1`.
* Ensure proper pixel format for JPEG: `-pix_fmt yuvj420p` (optional).

---

### 🧪 Example usage:

```python
converted = optimize_to_jpeg("input.webp")
print(f"Saved to: {converted}")
```

---

### 💡 Notes:

* `quality=2` gives nearly lossless results. `1` is max but can increase file size a lot.
* HEIF support may require FFmpeg compiled with `libheif`.
* If working with `webp` or `png`, you can safely use this same method.
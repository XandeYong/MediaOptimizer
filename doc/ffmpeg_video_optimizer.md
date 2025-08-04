# FFmpeg Video Optimizer
**FFmpeg** can use to **reduce video file size effectively** while maintaining **acceptable visual quality**, for formats like `mp4`, `mkv`, `avi`, `mov`, `webm`, `flv`, `wmv`.

---

### ✅ Optimization Approach:

* **Video encoder**: `libx264` (widely compatible)
* **Quality control**: `-crf` (Constant Rate Factor) for size/quality balance
* **Speed/efficiency trade-off**: `-preset`
* **Audio downsampling**: Optional (reduce bitrate to save space)

---

### 🧪 Example Usage:

```python
optimized = optimize_to_mp4(
    input_path="input.mov",
    crf=23,
    preset="medium",
    target_audio_bitrate="96k",
    scale_resolution="1280:720"  # Optional downscale
)
print(f"Optimized video: {optimized}")
```

---

### ⚖️ CRF Quick Guide:

**For `libx264` (H.264):**
| CRF Value | Quality               | Use Case                            |
| --------- | --------------------- | ----------------------------------- |
| 0         | **Lossless**          | Archival, editing (huge file size)  |
| 18–20     | **Visually lossless** | High-quality storage                |
| 21–23     | Good quality          | General-purpose high-quality export |
| 24–28     | Acceptable            | Streaming, YouTube, web delivery    |
| 29–35     | Low quality           | Small size, noticeable degradation  |
| >35       | Trash                 | Only if size > everything else      |

**For `libx265` (H.265):**
- Same range, but CRF values are more efficient.
- CRF 28 in `H.265` ≈ CRF 23 in `H.264` in terms of quality. 
- Basically a different of 5 between `H.265` and `H.264`.

---

### 📌 Extra Notes:

* `libx264` ensures compatibility across all devices.
* `libx265` ensures smaller file size and maintain quality but not compatible for older device.
* For **maximum reduction**, set `crf=28`, `preset=veryslow`, and reduce resolution.
* You can add support for hardware encoding or batch processing if needed.

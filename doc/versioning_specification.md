# 🧩 Versioning Specification

**Format:**  [Major].[Minor].[Expand].[Extra]
**Example:** `1.2.3.4`

---

## **1️⃣ Major — Structural / Engine-Level Overhaul**
**Definition:**  
Indicates a full overhaul or architectural redesign that affects core structure, performance model, or system behavior.

**Internal meaning:**  
- Engine or library change  
- Core logic rewrite  
- Architecture, framework, or compatibility shift  

**External meaning:**  
- Users *must update* to stay compatible or to gain major performance and efficiency improvements.

**Examples:**  
- Migrating to a new image engine or optimization library  
- Switching from CPU to GPU processing  
- Refactoring the tool’s structure for efficiency  

**Version change:**  
`1.4.5.6 → 2.0.0.0`

---

## **2️⃣ Minor — New Feature Introduction**
**Definition:**  
Introduces new user-facing functionality without altering the existing structure.

**Internal meaning:**  
- Added new module, command, or feature  
- Extended capabilities (new file type, new mode)  

**External meaning:**  
- Users can now access new features by updating.

**Examples:**  
- Added support for a new image format  
- Introduced a new compression method  
- Added new CLI flag or UI control  

**Version change:**  
`2.0.0.0 → 2.1.0.0`

---

## **3️⃣ Expand — Feature Enhancement, Fix, or Efficiency Update**
**Definition:**  
Covers small but meaningful changes such as expanding features, fixing bugs, or minor performance improvements.

**Internal meaning:**  
- Expanded an existing feature  
- Fixed bugs or edge cases  
- Minor internal optimization or efficiency tweak  

**External meaning:**  
- Optional update; functionality remains mostly unchanged.  
- Users can update for improved experience or stability, but it’s not critical.

**Examples:**  
- Improved compression ratio or quality  
- Fixed a rare image load crash  
- Optimized runtime for better performance  

**Version change:**  
`2.1.0.0 → 2.1.1.0`

---

## **4️⃣ Extra — Documentation and Non-Core Updates**
**Definition:**  
Tracks updates unrelated to the main application logic.

**Internal meaning:**  
- Documentation updates (e.g., README.md)  
- Added test code or dev tools  
- Added or updated auxiliary scripts or resources  

**External meaning:**  
- No change in features or behavior.  
- Purely informational or maintenance-related updates.

**Examples:**  
- Updated README or changelog  
- Added automated test scripts  
- Included new example files or configuration templates  

**Version change:**  
`2.1.1.0 → 2.1.1.1`

---

## **🧭 Version Change Summary**

| Level | Trigger | Example | User Impact | Update Urgency |
|-------|----------|----------|--------------|----------------|
| **Major** | Engine / structure change | New optimization core | High | 🔺 Mandatory |
| **Minor** | New feature added | Added image format support | Medium | ⚡ Recommended |
| **Expand/Fix** | Feature expansion, bug fix, or efficiency tweak | Improved compression | Low | 🟢 Optional |
| **Extra** | Docs, tests, or non-core updates | Updated README / Added tests | None | ⚪ Informational |
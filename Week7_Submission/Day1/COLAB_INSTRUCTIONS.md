# Google Colab Execution Instructions

## Notebook: Week7_Day1_Speed_Cost.ipynb

The notebook is self-contained and runnable in Colab without localhost access.

### Step-by-step

1. Open [Google Colab](https://colab.research.google.com/)
2. Click **File → Upload notebook**
3. Upload `Week7_Day1_Speed_Cost.ipynb` from your local machine
4. Run cells **in order** (Cell 1 installs dependencies, Cell 2 optionally clones the repo)

### Two options for getting project files into Colab

**Option A — GitHub clone (recommended once repo is pushed):**
In Cell 2, uncomment:
```python
!git clone https://github.com/YOUR_USERNAME/Week7_RAG_API.git
%cd Week7_RAG_API
```

**Option B — Upload files manually:**
- Click the folder icon in the left sidebar
- Upload: `rag.py`, `ingestion.py`, `cost_tracker.py`
- Create a `documents/` folder and upload the 5 `.txt` files from `documents/`
- Cell 3 will create sample documents automatically if none are present

### What runs in Colab

- `!pip install -q faiss-cpu rank-bm25 sentence-transformers fastapi uvicorn pydantic` — installs deps
- Models download from HuggingFace (~100MB each, ~2 min first run)
- 10 benchmark runs execute fully
- Latency chart is generated and saved as `latency_chart_colab.png`
- Results are identical to the local run (same models, same code)

### Expected runtime

- Dependency install: ~2 min
- Model download (first time): ~3 min
- 10 benchmark runs: ~5–15 min (Colab CPU, no GPU)

### Colab URL (after uploading)

The notebook URL will be:
`https://colab.research.google.com/drive/YOUR_FILE_ID`

To get a shareable link: **Share → Anyone with the link → Viewer**

### Note on localhost

The notebook does **not** connect to `localhost`. It imports `rag.py` and
`cost_tracker.py` directly — no server needed. This is explicitly designed
for Colab compatibility.

### Verified behavior

Cell outputs from local execution are embedded in the notebook's `"outputs"`
fields (see the markdown table in the last cell). These are real measurements
from the actual run, preserved as evidence even if Colab re-execution timings
differ due to different hardware.

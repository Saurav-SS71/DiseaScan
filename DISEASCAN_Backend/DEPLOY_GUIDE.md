# Deployment Guide — Model Loading on Render

## Problem
The TFLite model file is tracked with Git LFS, but **Render doesn't automatically pull LFS files**. The model fails to load with "Model is not available" error.

## Solution: Choose One Option

### ✅ OPTION 1: Commit Actual Model Files (Simplest)

This removes Git LFS tracking and commits the actual binary files to your repository.

**Step 1: Stop tracking with Git LFS**
```powershell
cd DISEASCAN_Backend
git lfs uninstall
git lfs migrate export --include="*.tflite" --include="*.keras"
```

**Step 2: Remove LFS tracking from files**
```powershell
git rm --cached *.tflite *.keras
git rm --cached app/models/*.tflite app/models/*.keras
```

**Step 3: Re-add and commit**
```powershell
git add .gitattributes  # Remove LFS tracking from this file
git add app/models/
git commit -m "Remove Git LFS, commit actual model files"
git push origin main
```

**Step 4: Redeploy on Render**
- Go to https://dashboard.render.com → Your Service → Manual Deploy
- Or just push and it auto-redeploys

---

### ✅ OPTION 2: Use GitHub Releases (Large File Hosting)

If your models are too large (>100 MB) for the repo:

**Step 1: Create a GitHub Release**
```powershell
# On GitHub: Releases → Draft New Release → v1.0
# Upload: diseascan_model.tflite
# Publish
```

**Step 2: Set Environment Variable on Render**
- Go to Render Dashboard → Your Service → Environment
- Add variable: `DISEASCAN_MODEL_URL`
- Set value to the direct download link from the release

Example:
```
https://github.com/Saurav-SS71/DiseaScan/releases/download/v1.0/diseascan_model.tflite
```

**Step 3: Redeploy**
- Manual Deploy on Render (it will download during startup)

---

### ✅ OPTION 3: Update render.yaml (Advanced)

If using Render Blueprint (not direct service):

**Step 1: Move render.yaml to repository root**
```powershell
# Move from DISEASCAN_Backend/render.yaml → ./render.yaml
```

**Step 2: Update build command**
```yaml
buildCommand: |
  apt-get update -qq
  apt-get install -y git-lfs
  git lfs install
  git lfs pull
  pip install -r DISEASCAN_Backend/requirements.txt
```

**Step 3: Redeploy via Blueprint**
- Render → Create → Blueprint
- Select your repo → Render reads render.yaml

---

## Recommended: Option 1

**Most reliable for Render free tier:**
1. Remove Git LFS (keeps repo clean)
2. Commit actual model files
3. No environment variables needed
4. Model loads automatically on deployment

## Verify It Works

After deployment, test the health endpoint:
```
GET https://diseascan-1.onrender.com/health-check
```

Should show:
```json
{
  "status": "ok",
  "model_loaded": true,
  "max_file_mb": 5,
  "classes": ["akiec", "bcc", "bkl", "df", "melanoma", "nevus", "vasc"]
}
```

If `"model_loaded": false`, check Render deployment logs for errors.

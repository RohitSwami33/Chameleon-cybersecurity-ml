# 🔧 Render Deployment Fix

## ❌ Issue
```
bash: line 1: uvicorn: command not found
```

## ✅ Solution

The issue is that `uvicorn` command is not in PATH. Use `python -m uvicorn` instead.

---

## 🎯 Correct Configuration for Render

### Backend Service

**Build Command:**
```bash
pip install --upgrade pip && pip install -r Backend/requirements.txt
```

**Start Command:**
```bash
cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Important:** Use `python -m uvicorn` NOT just `uvicorn`

---

### Frontend Service

**Build Command:**
```bash
cd frontend && npm install && npm run build
```

**Start Command:**
```bash
cd frontend && npm start
```

---

## 📋 Step-by-Step Fix

### If Already Deployed:

1. **Go to Backend Service Settings**
   - Dashboard → Your Backend Service → Settings

2. **Update Start Command**
   - Find "Start Command" field
   - Change from:
     ```bash
     cd Backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - To:
     ```bash
     cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Save Changes**
   - Click "Save Changes"
   - Render will automatically redeploy

4. **Wait for Deployment**
   - Check logs for successful startup
   - Should see: "Uvicorn running on http://0.0.0.0:PORT"

---

## 🆕 For New Deployment:

### Backend Configuration

```yaml
Name: chameleon-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main

Build Command:
pip install --upgrade pip && pip install -r Backend/requirements.txt

Start Command:
cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT

Environment Variables:
PYTHON_VERSION=3.12.0
GEMINI_API_KEY=AIzaSyB7w5tQXvg1D7cVuqpeR6cZ5OMzNKCqguY
MONGODB_URL=<your_mongodb_atlas_url>
JWT_SECRET_KEY=<your_secret_key>
```

---

## 🧪 Test Locally

Before deploying, test the command locally:

```bash
cd Backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Should work without errors.

---

## 🔍 Why This Happens

**Issue:** When you run `uvicorn` directly, it looks for the command in PATH.

**Solution:** Using `python -m uvicorn` runs uvicorn as a Python module, which always works when uvicorn is installed via pip.

**Comparison:**
```bash
# ❌ May not work (PATH issues)
uvicorn main:app

# ✅ Always works (Python module)
python -m uvicorn main:app
```

---

## 📊 Complete Render Configuration

### Backend

| Setting | Value |
|---------|-------|
| **Name** | chameleon-backend |
| **Environment** | Python 3 |
| **Build Command** | `pip install --upgrade pip && pip install -r Backend/requirements.txt` |
| **Start Command** | `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Frontend

| Setting | Value |
|---------|-------|
| **Name** | chameleon-frontend |
| **Environment** | Node |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Start Command** | `cd frontend && npm start` |

---

## ✅ Verification

After fixing, check logs for:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
✅ Loaded ML model from chameleon_char_cnn_gru.keras
✅ Connected to MongoDB successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
```

---

## 🚀 Quick Fix Commands

**For Render Dashboard:**

1. Backend Start Command:
   ```
   cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Backend Build Command:
   ```
   pip install --upgrade pip && pip install -r Backend/requirements.txt
   ```

3. Frontend Start Command:
   ```
   cd frontend && npm start
   ```

4. Frontend Build Command:
   ```
   cd frontend && npm install && npm run build
   ```

---

## 📝 Updated render.yaml

The `render.yaml` file has been updated with the correct commands:

```yaml
services:
  - type: web
    name: chameleon-backend
    env: python
    buildCommand: pip install --upgrade pip && pip install -r Backend/requirements.txt
    startCommand: cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 🎯 Summary

**Problem:** `uvicorn: command not found`

**Solution:** Use `python -m uvicorn` instead of `uvicorn`

**Fixed Start Command:**
```bash
cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Status:** ✅ Fixed and ready to deploy!

---

## 🆘 If Still Not Working

1. **Check Python Version**
   - Ensure `PYTHON_VERSION=3.12.0` is set

2. **Check Build Logs**
   - Verify pip install completed successfully
   - Look for "Successfully installed uvicorn"

3. **Check Requirements.txt**
   - Ensure `uvicorn==0.24.0` is in Backend/requirements.txt

4. **Manual Redeploy**
   - Go to Render Dashboard
   - Click "Manual Deploy" → "Clear build cache & deploy"

---

**Quick Fix:** Just update the start command to use `python -m uvicorn` and redeploy! 🚀

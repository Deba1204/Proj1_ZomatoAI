# Fix: "npm is not recognized" after installing Node.js

You installed [Node.js LTS](https://nodejs.org/) but the terminal still says **npm is not recognized**. That usually means Node’s folder is not on your **PATH**.

## Quick fix: Use the run script (no PATH change)

From the **frontend** folder, double‑click or run:

```
run-frontend.bat
```

That script adds `C:\Program Files\nodejs` to PATH for that window and runs `npm install` and `npm run dev`. Use this if you don’t want to change PATH permanently.

---

## Permanent fix: Add Node.js to your PATH

### Option A: Restart your terminal (try first)

1. **Close all** PowerShell/Command Prompt/Cursor terminals.
2. Open a **new** terminal.
3. Run: `node -v` and `npm -v`.

If they work, PATH was set by the installer and the old terminals just didn’t have it.

---

### Option B: Add Node.js to PATH manually

1. Press **Win + R**, type `sysdm.cpl`, Enter.
2. **Advanced** tab → **Environment Variables**.
3. Under **System variables** (or **User variables**), select **Path** → **Edit**.
4. **New** → add:  
   `C:\Program Files\nodejs`  
   (If you installed Node somewhere else, use that folder.)
5. **OK** on all windows.
6. **Close and reopen** any terminal (and Cursor if you use its terminal).
7. Run: `npm -v`

---

### Option C: Use full path in this project only

In any terminal, from the **frontend** folder:

```bat
set "PATH=C:\Program Files\nodejs;%PATH%"
npm install
npm run dev
```

Then open **http://localhost:5173**.

---

## If Node is installed in a different folder

- Common locations:  
  `C:\Program Files\nodejs`  
  `C:\Program Files (x86)\nodejs`  
  `%LOCALAPPDATA%\Programs\nodejs`
- Use that folder in the script or in PATH instead of `C:\Program Files\nodejs`.

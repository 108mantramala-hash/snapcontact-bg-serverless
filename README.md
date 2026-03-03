# SnapContact BG Remover (RunPod Serverless)

RunPod serverless worker that removes image backgrounds and returns PNG base64.

Input: { "input": { "image_base64": "<...>" } }
Output: { "ok": true, "output_base64": "<...>", "meta": {...} }

## Local Test (Windows)

Run from repo root in PowerShell:

```powershell
.\scripts\test_windows.ps1
```

Optional Docker smoke test (import only, no blocking worker start):

```powershell
.\scripts\docker_smoke.ps1
```

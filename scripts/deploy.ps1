param(
    [string]$AppDir = "C:\deploy\WmPrediction",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/EinSchokomuffin/WmPrediction.git"

if (-not (Test-Path (Join-Path $AppDir ".git"))) {
    Write-Host "Cloning repository into $AppDir..."
    New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
    git clone $repoUrl $AppDir
}

Set-Location $AppDir

Write-Host "Updating source code..."
git fetch origin $Branch
git checkout $Branch
git pull --ff-only origin $Branch

Write-Host "Restarting Docker services..."
docker compose down
docker compose up -d --build

Write-Host "Deployment complete."

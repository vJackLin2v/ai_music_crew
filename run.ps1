# 绕过 Windows Defender 拦截 uv trampoline
$env:TEMP = "H:\ai_music_crew\.tmp"
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
crewai run

$ErrorActionPreference='SilentlyContinue'
Set-Location 'H:\ai_music_crew'
$env:SONG_NAME='雨爱'
$env:SONG_TOPIC=(Get-Content 'H:\ai_music_crew\work\songs\雨爱.topic.txt' -Raw -Encoding UTF8)
& 'H:\ai_music_crew\.musicenv\Scripts\python.exe' -u 'H:\ai_music_crew\tools\run_crews.py' *> 'H:\ai_music_crew\work\_yuai6.log'
Write-Output 'runner done'

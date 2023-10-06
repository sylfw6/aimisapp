cd "%USERPROFILE%\Documents\reader2"

pyinstaller main.py --onefile --icon=orb.ico -n aimisappwconsole

pyinstaller main.py --onefile --icon=orb.ico -w -n aimisapp

cd ..

copy /y "reader2\dist\aimisapp.exe" "reader2\"

copy /y "reader2\dist\aimisappwconsole.exe" "reader2\"

pause
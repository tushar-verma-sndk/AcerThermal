@echo off
@REM pyinstaller.exe --onefile --clean --hidden-import=pywin32 --name "Acer Thermal Parser" --uac-admin --icon=resources\icon.ico .\main.py
pyinstaller.exe --onedir --clean --hidden-import=pandas --hidden-import=matplotlib --name "Acer Thermal Parser" --uac-admin --icon=resources\icon.ico .\main.py --noconfirm

@REM Build cleanup
echo "Cleaning-up CWD"
@REM rd build /s /q
del "Acer Thermal Parser.spec" /f /q
@REM move /y dist\"Acer Thermal Parser" .
@REM rd dist /s /q
@REM rd __pycache__ /s /q
@REM timeout 2 /nobreak

@REM # Compress to ZIP
echo Creating ZIP
tar -a -c -C "dist\Acer Thermal Parser" -f "Acer Thermal Parser.zip" "*"
@REM timeout 2 /nobreak
@REM del "Acer Thermal Parser.spec"
@REM rd "Acer Thermal Parser" /s /q


echo Build Success
pause
@echo on
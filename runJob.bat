SET SCRIPT_DIR=%~dp0

python3 %SCRIPT_DIR%\src\fetchPages.py --rootOutputFolder "out" ^
--urls ^
"your_url1" ^
"your_url2" ^" 
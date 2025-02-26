:: Check for Python Installation
python --version 2>NUL
if errorlevel 1 goto errorNoPython

python.exe %1

:: Once done, exit the batch file -- skips executing the errorNoPython section
goto:eof

:errorNoPython
echo.
echo Error^: Python not installed
pause

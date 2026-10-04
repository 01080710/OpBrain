@echo off
cd /d "%~dp0"

set /p START_DATE=Start date (YYYY-MM-DD):
set /p END_DATE=End date (YYYY-MM-DD):

echo.
echo A browser window will open for you to log into Power BI manually.
echo Please complete login (including 2FA) when it appears.
echo.

.venv\Scripts\python.exe -m src.workflows.pbi_workflow %START_DATE% %END_DATE%

echo.
pause

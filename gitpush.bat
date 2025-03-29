@echo off
setlocal

:: Set Git Project Directory
cd /d "C:\SAS Solutions\DockerEnv\Dev\DEV\application\appservice"

:: Prompt user for commit message
set /p commit_msg="Enter commit message: "

:: Prompt user for tag name
set /p tag_name="Enter tag name (e.g., CONFIG_NEW_10): "

:: Show Git Status
git status

:: Stage all changes
git add .

:: Verify if files were staged
git status

:: Commit the changes with user input message
git commit -m "%commit_msg%"

:: Ensure we are on 'main' branch
git checkout main

:: Push changes to GitHub
git push origin main

:: Create and push the tag
git tag %tag_name%
git push origin --tags

:: Verify tag exists remotely
git ls-remote --tags origin

echo.
echo ✅ Git operations completed successfully!
pause

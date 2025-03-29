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

:: Commit the changes with user input message
git commit -m "%commit_msg%"

:: Switch to the 'dev' branch
git checkout main

:: Push changes to GitHub
git push origin main

:: Create a Git tag with user input tag name
git tag %tag_name%

:: Push the tag to GitHub
git push origin --tags

:: Show commit history with tags
git log --oneline --decorate --graph --all

:: Verify if the tag exists in the remote repository
git ls-remote --tags origin

echo.
echo ✅ Git operations completed successfully!
pause

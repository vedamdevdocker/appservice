@echo off
setlocal

:: Set Git Project Directory
cd /d "C:\SAS Solutions\DockerEnv\Dev\DEV\application\appservice"

:: Prompt user for commit message
set /p commit_msg="Enter commit message: "

:: Prompt user for tag name
set /p tag_name="Enter tag name (e.g., CONFIG_NEW_10): "

:: Show current Git status
echo.
echo === Checking Git Status ===
git status

:: Ensure all changes are staged
echo.
echo === Staging All Changes ===
git add --all

:: Verify if files were staged properly
echo.
echo === Verifying Staged Changes ===
git status

:: Commit the changes
echo.
echo === Committing Changes ===
git commit -m "%commit_msg%"

:: Ensure we are on the 'main' branch
echo.
echo === Switching to Main Branch ===
git checkout main

:: Push changes to GitHub
echo.
echo === Pushing Changes to Remote Repository ===
git push origin main

:: Create a Git tag
echo.
echo === Creating Tag: %tag_name% ===
git tag %tag_name%

:: Push the tag to GitHub
echo.
echo === Pushing Tags to Remote Repository ===
git push origin --tags

:: Verify tag exists in the remote repository
echo.
echo === Verifying Remote Tags ===
git ls-remote --tags origin

:: Show commit history
echo.
echo === Recent Commit History ===
git log --oneline --decorate --graph --all

echo.
echo ✅ Git operations completed successfully!
pause

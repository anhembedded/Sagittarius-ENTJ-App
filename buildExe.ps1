# Set the path to PyInstaller
$nameApp = "Sagittarius-ENTJ"
# Run PyInstaller with --add-data option
Remove-Item -Recurse -Path dist,build
& pyinstaller.exe --noconfirm --name $nameApp --windowed "./Sagittarius-ENTJ.py"
Copy-Item -Recurse -Path "./dist/Sagittarius-ENTJ" -Destination "./executable/" -Force
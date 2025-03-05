@echo off

call run_python.bat sync_compras.py

PowerShell -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('All cards have been updated successfully!', 'Update Notification')"

exit
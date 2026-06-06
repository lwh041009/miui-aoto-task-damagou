@echo off
setlocal EnableExtensions
chcp 65001 >nul

cd /d "%~dp0"

set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
set NO_PROXY=*
set no_proxy=*

py -3.12 miuitask.py


pause

@echo off
chcp 65001 > nul
title Đồng Bộ Mã Nguồn Lên GitHub (Git Push)

echo ============================================================
echo         ĐỒNG BỘ MÃ NGUỒN LÊN GITHUB (GIT PUSH)
echo   Repo: https://github.com/hongquang699/Translate-language
echo ============================================================
echo.

set /p "commit_msg=Nhập ghi chú commit (hoặc nhấn Enter để dùng mặc định): "

echo.
if "%commit_msg%"=="" (
    echo Đang đồng bộ với ghi chú tự động...
    python github_service.py
) else (
    echo Đang đồng bộ với ghi chú: "%commit_msg%"...
    python github_service.py "%commit_msg%"
)

echo.
echo ============================================================
echo Hoàn tất! Nhấn phím bất kỳ để thoát...
echo ============================================================
pause > nul

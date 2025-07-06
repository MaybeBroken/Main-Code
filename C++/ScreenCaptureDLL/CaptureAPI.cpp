#include "pch.h"
#include <Windows.h>
#include <iostream>

HDC hWindowDC = nullptr;
HDC hMemDC = nullptr;
HBITMAP hBitmap = nullptr;
BITMAPINFO bmi;
HWND targetHwnd = nullptr;
BYTE* frameBuffer = nullptr;
int width = 0;
int height = 0;

extern "C"
{
    __declspec(dllexport) bool start_capture(const wchar_t* windowTitle)
    {
        targetHwnd = FindWindowW(NULL, windowTitle);
        if (!targetHwnd)
        {
            MessageBoxA(NULL, "Window not found", "Error", MB_OK);
            return false;
        }

        RECT rc;
        GetClientRect(targetHwnd, &rc);
        width = rc.right - rc.left;
        height = rc.bottom - rc.top;

        hWindowDC = GetDC(targetHwnd);
        hMemDC = CreateCompatibleDC(hWindowDC);

        hBitmap = CreateCompatibleBitmap(hWindowDC, width, height);
        SelectObject(hMemDC, hBitmap);

        // setup BITMAPINFO for easy copying
        ZeroMemory(&bmi, sizeof(BITMAPINFO));
        bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmi.bmiHeader.biWidth = width;
        bmi.bmiHeader.biHeight = -height; // top-down
        bmi.bmiHeader.biPlanes = 1;
        bmi.bmiHeader.biBitCount = 32;
        bmi.bmiHeader.biCompression = BI_RGB;

        frameBuffer = new BYTE[width * height * 4];

        MessageBoxA(NULL, "GDI Window Capture Init OK", "Info", MB_OK);
        return true;
    }

    __declspec(dllexport) bool get_frame(uint8_t* buffer, int* out_w, int* out_h)
    {
        if (!targetHwnd) return false;

        BitBlt(hMemDC, 0, 0, width, height, hWindowDC, 0, 0, SRCCOPY);

        // copy bits to our buffer
        GetDIBits(hMemDC, hBitmap, 0, height, frameBuffer, &bmi, DIB_RGB_COLORS);

        memcpy(buffer, frameBuffer, width * height * 4);
        *out_w = width;
        *out_h = height;

        return true;
    }

    __declspec(dllexport) void stop_capture()
    {
        if (hWindowDC) ReleaseDC(targetHwnd, hWindowDC);
        if (hMemDC) DeleteDC(hMemDC);
        if (hBitmap) DeleteObject(hBitmap);
        if (frameBuffer) delete[] frameBuffer;
        frameBuffer = nullptr;
        targetHwnd = nullptr;

        MessageBoxA(NULL, "GDI Window Capture Done", "Info", MB_OK);
    }
}


@echo off
echo Installing F1 Circuit AI Bot Dependencies...
echo.

echo Installing OpenCV for image processing...
pip install opencv-python==4.8.1.78

echo Installing Pillow for image handling...
pip install pillow==10.0.1

echo Installing NumPy for numerical operations...
pip install numpy==1.24.3

echo.
echo All dependencies installed successfully!
echo You can now run the F1 Circuit AI Bot with: python f1_circuit_gui.py
pause
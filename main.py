import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from frontend.login import LoginWindow

def main():
    app = QApplication(sys.argv)
    
    # Aplicar estilos (opcional)
    try:
        with open('frontend/styles/style.qss', 'r') as f:
            style = f.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print("Archivo de estilos no encontrado")
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
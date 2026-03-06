import sys
import numpy as np
import pandas as pd

from PySide6.QtWidgets import (QApplication, QComboBox, QMainWindow, QVBoxLayout, QMessageBox, QFileDialog)
from PySide6.QtCore import QThread, Signal
import serial
import serial.tools.list_ports
import pyqtgraph as pg
from tensorflow.keras.models import load_model
import joblib

from ui_main import Ui_MainWindow

class SerialThread(QThread):
    data_received = Signal(str)

    def __init__(self, port, baudrate=9600, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.running = False

    def run(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
        except serial.SerialException as e:
            print(f"Gagal membuka port: {e}")
            self.running = False
            return

        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        self.data_received.emit(line)
            except Exception as e:
                print(f"Error baca data serial: {e}")
                self.running = False

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        try:
            self.model = load_model('model_ann.h5')
            self.scaler = joblib.load('scaler.pkl')
        except Exception as e:
            QMessageBox.critical(self, "Model Load Error", f"Gagal memuat model atau scaler:\n{e}")
            sys.exit(1)

        self.serial_thread = None
        self.serial_connected = False
        
        self.is_standby = True 
        self.data_history = []
        
        self.ui.Button_Start.clicked.connect(self.toggle_connection)
        self.ui.Button_Export.clicked.connect(self.export_to_excel)
        self.ui.Button_Standby.clicked.connect(self.toggle_standby)
        self.set_standby_ui()

        self.ui.Box_port.showPopup = self.update_port_list_then_show

        self.setup_plots()
        self.update_port_list()

    def setup_plots(self):
        #PLOT R (Tegangan & Arus)
        self.plot_r = pg.PlotWidget(title="Fasa R (Tegangan & Arus)")
        self.plot_r.setBackground('k')
        self.plot_r.showGrid(x=True, y=True)
        # Sumbu Kiri (Tegangan)
        self.plot_r.getPlotItem().getAxis('left').setPen('w')
        self.plot_r.getPlotItem().getAxis('left').setTextPen('w')
        self.plot_r.getPlotItem().setLabel('left', 'Tegangan', units='V')
        # Sumbu Bawah
        self.plot_r.getPlotItem().getAxis('bottom').setPen('w')
        self.plot_r.getPlotItem().getAxis('bottom').setTextPen('w')
        
        # Sumbu Kanan (Arus) - Menggunakan ViewBox terpisah
        self.plot_r.showAxis('right')
        self.view_arus_r = pg.ViewBox()
        self.plot_r.scene().addItem(self.view_arus_r)
        self.plot_r.getAxis('right').linkToView(self.view_arus_r)
        self.view_arus_r.setXLink(self.plot_r.plotItem.vb)
        self.plot_r.getAxis('right').setPen('c')
        self.plot_r.getAxis('right').setTextPen('c')
        self.plot_r.getPlotItem().setLabel('right', 'Arus', units='A')
        # Sync geometry
        self.plot_r.plotItem.vb.sigResized.connect(lambda: self.view_arus_r.setGeometry(self.plot_r.plotItem.vb.sceneBoundingRect()))

        #PLOT S (Tegangan & Arus)
        self.plot_s = pg.PlotWidget(title="Fasa S (Tegangan & Arus)")
        self.plot_s.setBackground('k')
        self.plot_s.showGrid(x=True, y=True)
        self.plot_s.getPlotItem().getAxis('left').setPen('w')
        self.plot_s.getPlotItem().getAxis('left').setTextPen('w')
        self.plot_s.getPlotItem().setLabel('left', 'Tegangan', units='V')
        self.plot_s.getPlotItem().getAxis('bottom').setPen('w')
        self.plot_s.getPlotItem().getAxis('bottom').setTextPen('w')

        self.plot_s.showAxis('right')
        self.view_arus_s = pg.ViewBox()
        self.plot_s.scene().addItem(self.view_arus_s)
        self.plot_s.getAxis('right').linkToView(self.view_arus_s)
        self.view_arus_s.setXLink(self.plot_s.plotItem.vb)
        self.plot_s.getAxis('right').setPen('c')
        self.plot_s.getAxis('right').setTextPen('c')
        self.plot_s.getPlotItem().setLabel('right', 'Arus', units='A')
        self.plot_s.plotItem.vb.sigResized.connect(lambda: self.view_arus_s.setGeometry(self.plot_s.plotItem.vb.sceneBoundingRect()))

        #PLOT T (Tegangan & Arus)
        self.plot_t = pg.PlotWidget(title="Fasa T (Tegangan & Arus)")
        self.plot_t.setBackground('k')
        self.plot_t.showGrid(x=True, y=True)
        self.plot_t.getPlotItem().getAxis('left').setPen('w')
        self.plot_t.getPlotItem().getAxis('left').setTextPen('w')
        self.plot_t.getPlotItem().setLabel('left', 'Tegangan', units='V')
        self.plot_t.getPlotItem().getAxis('bottom').setPen('w')
        self.plot_t.getPlotItem().getAxis('bottom').setTextPen('w')

        self.plot_t.showAxis('right')
        self.view_arus_t = pg.ViewBox()
        self.plot_t.scene().addItem(self.view_arus_t)
        self.plot_t.getAxis('right').linkToView(self.view_arus_t)
        self.view_arus_t.setXLink(self.plot_t.plotItem.vb)
        self.plot_t.getAxis('right').setPen('c')
        self.plot_t.getAxis('right').setTextPen('c')
        self.plot_t.getPlotItem().setLabel('right', 'Arus', units='A')
        self.plot_t.plotItem.vb.sigResized.connect(lambda: self.view_arus_t.setGeometry(self.plot_t.plotItem.vb.sceneBoundingRect()))

        #PLOT RST (Gabungan Tegangan Saja)
        self.plot_rst = pg.PlotWidget(title="Gabungan Tegangan R, S, T")
        self.plot_rst.setBackground('k')
        self.plot_rst.showGrid(x=True, y=True)
        self.plot_rst.getPlotItem().getAxis('left').setPen('w')
        self.plot_rst.getPlotItem().getAxis('bottom').setPen('w')
        self.plot_rst.getPlotItem().getAxis('left').setTextPen('w')
        self.plot_rst.getPlotItem().getAxis('bottom').setTextPen('w')

        # Set Range
        for plot in [self.plot_r, self.plot_s, self.plot_t, self.plot_rst]:
            plot.setYRange(220, 250) # Range Tegangan
        
        # Range untuk Arus (Sumur Kanan) - Set manual agar garis terlihat jelas
        self.view_arus_r.setYRange(0, 5) 
        self.view_arus_s.setYRange(0, 5)
        self.view_arus_t.setYRange(0, 5)

        # Layouts
        layout_r = QVBoxLayout(self.ui.widget_R)
        layout_r.setContentsMargins(0, 0, 0, 0)
        layout_r.addWidget(self.plot_r)

        layout_s = QVBoxLayout(self.ui.widget_S)
        layout_s.setContentsMargins(0, 0, 0, 0)
        layout_s.addWidget(self.plot_s)

        layout_t = QVBoxLayout(self.ui.widget_T)
        layout_t.setContentsMargins(0, 0, 0, 0)
        layout_t.addWidget(self.plot_t)

        layout_rst = QVBoxLayout(self.ui.widget_RST)
        layout_rst.setContentsMargins(0, 0, 0, 0)
        layout_rst.addWidget(self.plot_rst)

        # Inisialisasi Kurva Tegangan
        self.data_r, self.data_s, self.data_t = [], [], []
        self.curve_r = self.plot_r.plot(pen=pg.mkPen('r', width=2))
        self.curve_s = self.plot_s.plot(pen=pg.mkPen('g', width=2))
        self.curve_t = self.plot_t.plot(pen=pg.mkPen('b', width=2))

        # Inisialisasi Kurva Arus (Linked ke ViewBox Kanan)
        self.data_arus_r, self.data_arus_s, self.data_arus_t = [], [], []
        self.curve_arus_r = pg.PlotCurveItem(pen=pg.mkPen('c', width=2)) # Cyan
        self.view_arus_r.addItem(self.curve_arus_r)
        
        self.curve_arus_s = pg.PlotCurveItem(pen=pg.mkPen('c', width=2))
        self.view_arus_s.addItem(self.curve_arus_s)
        
        self.curve_arus_t = pg.PlotCurveItem(pen=pg.mkPen('c', width=2))
        self.view_arus_t.addItem(self.curve_arus_t)

        # Kurva Gabungan RST
        self.curve_rst_r = self.plot_rst.plot(pen=pg.mkPen('r', width=2))
        self.curve_rst_s = self.plot_rst.plot(pen=pg.mkPen('g', width=2))
        self.curve_rst_t = self.plot_rst.plot(pen=pg.mkPen('b', width=2))

        self.max_points = 50

        for lineedit in [self.ui.line_R, self.ui.line_S, self.ui.line_T,
                         self.ui.line_arus_R, self.ui.line_arus_S, self.ui.Line_arus_T,
                         self.ui.line_Status_T, self.ui.line_status_A]:
            lineedit.setReadOnly(True)

    def set_standby_ui(self):
        if self.is_standby:
            self.ui.Button_Standby.setText("SYSTEM RUN")
            self.ui.Button_Standby.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        else:
            self.ui.Button_Standby.setText("STANDBY")
            self.ui.Button_Standby.setStyleSheet("background-color: #FF9800; color: black; font-weight: bold;")

    def toggle_standby(self):
        self.is_standby = not self.is_standby
        self.set_standby_ui()
        status_mode = "STANDBY" if self.is_standby else "RUN"
        
        if self.serial_thread and self.serial_thread.serial_port and self.serial_thread.serial_port.is_open:
            try:
                message = f"{status_mode}\n".encode('utf-8')
                self.serial_thread.serial_port.write(message)
            except Exception as e:
                print(f"Error saat mengirim mode ke Arduino: {e}")

        QMessageBox.information(self, "Mode Diubah", f"Sistem dalam mode: {status_mode}")

    def update_port_list_then_show(self):
        self.update_port_list()
        QComboBox.showPopup(self.ui.Box_port)

    def update_port_list(self):
        self.ui.Box_port.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.ui.Box_port.addItem(port.device)

    def toggle_connection(self):
        if not self.serial_connected:
            self.start_serial_thread()
        else:
            self.stop_serial_thread()

    def start_serial_thread(self):
        port = self.ui.Box_port.currentText()
        if not port:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih port terlebih dahulu.")
            return

        self.serial_thread = SerialThread(port)
        self.serial_thread.data_received.connect(self.on_data_received)
        self.serial_thread.start()

        self.ui.Button_Start.setText("Stop")
        self.serial_connected = True
        QMessageBox.information(self, "Info", f"Koneksi berhasil ke {port}")

    def stop_serial_thread(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None
        self.ui.Button_Start.setText("Start")
        self.serial_connected = False
        QMessageBox.information(self, "Info", "Koneksi serial dihentikan.")

    def on_data_received(self, line):
        if self.serial_connected:
            parts = line.split(",")
            if len(parts) == 6:
                self.ui.line_R.setText(parts[0])
                self.ui.line_S.setText(parts[1])
                self.ui.line_T.setText(parts[2])
                self.ui.line_arus_R.setText(parts[3])
                self.ui.line_arus_S.setText(parts[4])
                self.ui.Line_arus_T.setText(parts[5])
                
                self.data_history.append(parts)
                
                self.evaluate_voltage(parts)
                self.update_plot(parts)

    def evaluate_voltage(self, parts):
        try:
            r = float(parts[0])
            s = float(parts[1])
            t = float(parts[2])
            i_r = float(parts[3])
            i_s = float(parts[4])
            i_t = float(parts[5])

            input_data = np.array([[r, s, t, i_r, i_s, i_t]])
            input_scaled = self.scaler.transform(input_data)

            prediction = self.model.predict(input_scaled)[0][0]
            predicted_class = int(prediction > 0.5)
            confidence = prediction if predicted_class == 1 else 1 - prediction

            kondisi = "UNBALANCE" if predicted_class == 1 else "BALANCE"
            
            self.ui.line_Status_T.setText(f"{kondisi}")
            self.ui.line_status_A.setText(f"{confidence*100:.2f}")
            
            if not self.is_standby:
                if self.serial_thread and self.serial_thread.serial_port and self.serial_thread.serial_port.is_open:
                    try:
                        message = f"{kondisi}\n".encode('utf-8')
                        self.serial_thread.serial_port.write(message)
                    except Exception as e:
                        print(f"Error saat mengirim data ke Arduino: {e}")
            
        except Exception as e:
            print(f"Error saat evaluasi ANN: {e}")
            self.ui.line_Status_T.setText("Error ANN")

    def update_plot(self, parts):
        try:
            r = float(parts[0])
            s = float(parts[1])
            t = float(parts[2])
            i_r = float(parts[3])
            i_s = float(parts[4])
            i_t = float(parts[5])

            # Update Data Tegangan
            self.data_r.append(r)
            self.data_s.append(s)
            self.data_t.append(t)

            # Update Data Arus
            self.data_arus_r.append(i_r)
            self.data_arus_s.append(i_s)
            self.data_arus_t.append(i_t)

            # Batasi jumlah titik (Sliding Window)
            if len(self.data_r) > self.max_points:
                self.data_r = self.data_r[-self.max_points:]
                self.data_s = self.data_s[-self.max_points:]
                self.data_t = self.data_t[-self.max_points:]
                
                self.data_arus_r = self.data_arus_r[-self.max_points:]
                self.data_arus_s = self.data_arus_s[-self.max_points:]
                self.data_arus_t = self.data_arus_t[-self.max_points:]

            x_data = list(range(len(self.data_r)))

            # Update Plot Tegangan
            self.curve_r.setData(x_data, self.data_r)
            self.curve_s.setData(x_data, self.data_s)
            self.curve_t.setData(x_data, self.data_t)

            # Update Plot Arus
            self.curve_arus_r.setData(x_data, self.data_arus_r)
            self.curve_arus_s.setData(x_data, self.data_arus_s)
            self.curve_arus_t.setData(x_data, self.data_arus_t)

            # Update Plot Gabungan RST (Hanya Tegangan)
            self.curve_rst_r.setData(x_data, self.data_r)
            self.curve_rst_s.setData(x_data, self.data_s)
            self.curve_rst_t.setData(x_data, self.data_t)
        except ValueError:
            pass

    def export_to_excel(self):
        if not self.data_history:
            QMessageBox.warning(self, "Export Gagal", "Tidak ada data untuk diekspor.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan File Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)

        if file_path:
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
                
            try:
                headers = ["Tegangan R", "Tegangan S", "Tegangan T", "Arus R", "Arus S", "Arus T"]
                df = pd.DataFrame(self.data_history, columns=headers)
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Sukses", f"Data berhasil disimpan di:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan file:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


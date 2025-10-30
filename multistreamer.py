import os
import sys
import subprocess
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QTextEdit, QGridLayout, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class MultiStreamBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Multistream de Kick v1.0.0")
        self.keys = []
        self.file_path = None
        self.music_path = None
        self.timer = None
        self._build_ui()
        self.load_keys()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        grid = QGridLayout()
        grid.addWidget(QLabel("Duración (HH:MM:SS):"), 0, 0)
        self.duration_edit = QLineEdit("06:00:00")
        self.duration_edit.setPlaceholderText("HH:MM:SS")
        grid.addWidget(self.duration_edit, 0, 1)

        grid.addWidget(QLabel("Calidad:"), 0, 2)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "160p (200 kbps)",
            "240p (350 kbps)",
            "360p (600 kbps)",
            "480p (1500 kbps)",
            "720p (3000 kbps)",
            "1080p (6000 kbps)"
        ])
        grid.addWidget(self.quality_combo, 0, 3)
        layout.addLayout(grid)

        options_layout = QHBoxLayout()
        self.loop_cb = QCheckBox("Repetir reproducción")
        options_layout.addWidget(self.loop_cb)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        file_layout = QHBoxLayout()
        self.select_btn = QPushButton("Seleccionar video")
        self.select_btn.setStyleSheet("background-color:#1be354; color:black;")
        self.select_btn.clicked.connect(self.choose_file)
        file_layout.addWidget(self.select_btn)
        self.file_label = QLabel("Ningún archivo seleccionado")
        self.file_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        music_layout = QHBoxLayout()
        self.select_music_btn = QPushButton("Seleccionar música (opcional)")
        self.select_music_btn.setStyleSheet("background-color:#1db548; color:black;")
        self.select_music_btn.clicked.connect(self.choose_music)
        music_layout.addWidget(self.select_music_btn)

        self.mute_button = QPushButton("🔇 Mute")
        self.mute_button.setStyleSheet("background-color:#555; color:black;")
        self.mute_button.clicked.connect(self.toggle_mute)
        music_layout.addWidget(self.mute_button)

        self.music_label = QLabel("Ningún archivo seleccionado")
        self.music_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        music_layout.addWidget(self.music_label)
        layout.addLayout(music_layout)

        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget(self)
        self.video_widget.setStyleSheet("background-color: #2d2d2d;")
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)

        ss_layout = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar transmisiones")
        self.start_btn.setStyleSheet("background-color:#33d624; color:black;")
        self.start_btn.clicked.connect(self.start_streams)
        self.stop_btn = QPushButton("Detener todo")
        self.stop_btn.setStyleSheet("background-color:#33d624; color:black;")
        self.stop_btn.clicked.connect(self.stop_streams)
        ss_layout.addWidget(self.start_btn)
        ss_layout.addWidget(self.stop_btn)
        layout.addLayout(ss_layout)

        layout.addWidget(QLabel("Registro de actividad:"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

    def log(self, message: str):
        self.log_view.append(message)

    def load_keys(self):
        try:
            with open('stream_keys.txt', 'r') as f:
                self.keys = [line.strip() for line in f if line.strip()]
            self.log("✅ Claves cargadas automáticamente")
        except FileNotFoundError:
            self.keys = []
            self.log("❌ Error: stream_keys.txt no encontrado!")

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar video", os.getcwd(),
            "Archivos de video (*.mp4 *.mov *.avi *.mkv *.flv *.gif)"
        )
        if path:
            self.file_path = path
            self.file_label.setText(os.path.basename(path))
            self.log(f"📁 Video seleccionado: {os.path.basename(path)}")
            self.media_player.setSource(QUrl.fromLocalFile(path))
            loops = QMediaPlayer.Loops.Infinite if self.loop_cb.isChecked() else 1
            self.media_player.setLoops(loops)
            self.media_player.play()

    def choose_music(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar música", os.getcwd(),
            "Archivos de audio (*.mp3 *.wav *.aac *.ogg)"
        )
        if path:
            self.music_path = path
            self.music_label.setText(os.path.basename(path))
            self.log(f"🎵 Música seleccionada: {os.path.basename(path)}")
        else:
            self.music_path = None
            self.music_label.setText("Ningún archivo seleccionado")
            self.log("🎵 Música no seleccionada (opcional)")

    def toggle_mute(self):
        is_muted = self.audio_output.isMuted()
        self.audio_output.setMuted(not is_muted)
        if not is_muted:
            self.mute_button.setText("🔊 Unmute")
            self.log("🔇 Audio silenciado")
        else:
            self.mute_button.setText("🔇 Mute")
            self.log("🔊 Audio activado")


    def start_streams(self):
        if not self.file_path:
            self.log("❌ Error: No se seleccionó ningún archivo de video!")
            return
        dur = self.duration_edit.text().strip()
        parts = dur.split(':')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            self.log("❌ Formato de duración inválido. Usa HH:MM:SS")
            return

        calidad = self.quality_combo.currentText()
        bitrate_map = {
            "160p (200 kbps)": "200k",
            "240p (350 kbps)": "350k",
            "360p (600 kbps)": "600k",
            "480p (1500 kbps)": "1500k",
            "720p (3000 kbps)": "3000k",
            "1080p (6000 kbps)": "6000k"
        }
        bitrate = bitrate_map.get(calidad, "3000k")

        if not self.keys:
            self.log("❌ Error: No hay claves configuradas")
            return

        for k in self.keys:
            thread = threading.Thread(
                target=self._stream_thread,
                args=(k, dur, bitrate),
                daemon=True
            )
            thread.start()
        self.log("▶️ Iniciando transmisiones...")

        self.start_timer_for_duration(dur)

    def start_timer_for_duration(self, dur_str):
        try:
            h, m, s = map(int, dur_str.split(":"))
            total_seconds = h * 3600 + m * 60 + s
        except Exception:
            self.log("❌ No se pudo programar el temporizador por formato inválido.")
            return

        if self.timer:
            self.timer.stop()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.auto_stop_and_close)
        self.timer.start(total_seconds * 1000)
        self.log(f"⏳ El programa se cerrará automáticamente en {total_seconds} segundos")

    def auto_stop_and_close(self):
        self.stop_streams()
        self.log("🔔 Tiempo completado. Cerrando programa...")
        QApplication.quit()

    def _stream_thread(self, key: str, duration: str, bitrate: str):
        buf = str(int(bitrate.replace('k', '')) * 2) + 'k'
        cmd = [
            'ffmpeg', '-stream_loop', '-1', '-re', '-t', duration,
            '-i', self.file_path
        ]
        if self.music_path:
            cmd += ['-stream_loop', '-1', '-i', self.music_path]
            cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-b:v', bitrate,
                    '-maxrate', bitrate, '-bufsize', buf, '-pix_fmt', 'yuv420p',
                    '-g', '50', '-c:a', 'aac', '-b:a', '160k', '-ac', '2', '-ar', '44100',
                    '-f', 'flv', '-shortest', f"rtmps://fa723fc1b171.global-contribute.live-video.net/rtmp/{key}"]
        else:
            cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-b:v', bitrate,
                    '-maxrate', bitrate, '-bufsize', buf, '-pix_fmt', 'yuv420p',
                    '-g', '50', '-an',
                    '-f', 'flv', f"rtmps://fa723fc1b171.global-contribute.live-video.net/rtmp/{key}"]

        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log(f"🟢 [EN VIVO] {key} @ {bitrate}")
        except Exception as e:
            self.log(f"❌ Error al iniciar {key}: {e}")

    def stop_streams(self):
        subprocess.run(['taskkill', '/f', '/im', 'ffmpeg.exe'], stdout=subprocess.DEVNULL)
        self.log("⏹️ Todas las transmisiones detenidas")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiStreamBotGUI()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

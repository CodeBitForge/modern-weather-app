from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QGridLayout,
    QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from src.services.weather_service import WeatherService
from src.utils.weather_parser import parse_weather_data
from src.models.weather import WeatherData


class WeatherWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, city: str):
        super().__init__()
        self.city = city
        self.service = WeatherService()

    def run(self):
        try:
            raw_data = self.service.get_weather_data(self.city)
            weather_data = parse_weather_data(raw_data["current"], raw_data["forecast"])
            self.finished.emit(weather_data)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")
        self.setWindowIcon(qta.icon("fa5s.cloud-sun"))
        self.resize(900, 700)

        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        
        header = QLabel("وضعیت آب و هوا")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        search_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("نام شهر را وارد کنید (مثال: تهران)")
        self.city_input.setFont(QFont("Segoe UI", 12))
        self.city_input.returnPressed.connect(self.search_weather)

        search_btn = QPushButton("جستجو")
        search_btn.setIcon(qta.icon("fa5s.search"))
        search_btn.setFixedWidth(120)
        search_btn.clicked.connect(self.search_weather)

        search_layout.addWidget(self.city_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        self.current_frame = QFrame()
        self.current_frame.setFrameShape(QFrame.StyledPanel)
        current_layout = QGridLayout(self.current_frame)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.city_label = QLabel("شهر: -")
        self.temp_label = QLabel("دما: -")
        self.feels_label = QLabel("احساس می‌شود: -")
        self.desc_label = QLabel("وضعیت: -")
        self.humidity_label = QLabel("رطوبت: -")
        self.wind_label = QLabel("باد: -")
        self.sunrise_label = QLabel("طلوع: -")
        self.sunset_label = QLabel("غروب: -")

        for label in [
            self.city_label, self.temp_label, self.feels_label, self.desc_label,
            self.humidity_label, self.wind_label, self.sunrise_label, self.sunset_label
        ]:
            label.setFont(QFont("Segoe UI", 12))

        current_layout.addWidget(self.icon_label, 0, 0, 4, 1)
        current_layout.addWidget(self.city_label, 0, 1)
        current_layout.addWidget(self.temp_label, 1, 1)
        current_layout.addWidget(self.feels_label, 2, 1)
        current_layout.addWidget(self.desc_label, 3, 1)
        current_layout.addWidget(self.humidity_label, 4, 1)
        current_layout.addWidget(self.wind_label, 5, 1)
        current_layout.addWidget(self.sunrise_label, 6, 1)
        current_layout.addWidget(self.sunset_label, 7, 1)

        layout.addWidget(self.current_frame)

        # Forecast section
        forecast_title = QLabel("پیش‌بینی ۵ روز آینده")
        forecast_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(forecast_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.forecast_container = QWidget()
        self.forecast_layout = QHBoxLayout(self.forecast_container)
        self.forecast_layout.setAlignment(Qt.AlignLeft)
        self.scroll.setWidget(self.forecast_container)

        layout.addWidget(self.scroll)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.status_label)

        footer = QLabel("Developed by CodeBitForge")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(footer)

    def search_weather(self):
        city = self.city_input.text().strip()
        if not city:
            self.status_label.setText("لطفاً نام شهر را وارد کنید")
            return

        self.status_label.setText("در حال دریافت اطلاعات...")
        self.city_input.setEnabled(False)

        self.worker = WeatherWorker(city)
        self.worker.finished.connect(self.on_weather_received)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_weather_received(self, weather: WeatherData):
        self.city_input.setEnabled(True)
        self.status_label.setText("")
        self.display_current(weather.current)
        self.display_forecast(weather.forecast)

    def on_error(self, message: str):
        self.city_input.setEnabled(True)
        self.status_label.setText(f"خطا: {message}")

    def display_current(self, current):
        self.city_label.setText(f"شهر: {current.city}, {current.country}")
        self.temp_label.setText(f"دما: {current.temperature:.1f} °C")
        self.feels_label.setText(f"احساس می‌شود: {current.feels_like:.1f} °C")
        self.desc_label.setText(f"وضعیت: {current.description}")
        self.humidity_label.setText(f"رطوبت: {current.humidity}%")
        self.wind_label.setText(f"سرعت باد: {current.wind_speed} m/s")
        self.sunrise_label.setText(f"طلوع: {current.sunrise.strftime('%H:%M')}")
        self.sunset_label.setText(f"غروب: {current.sunset.strftime('%H:%M')}")

        icon = self.get_weather_icon(current.icon, size=96)
        self.icon_label.setPixmap(icon.pixmap(96, 96))

    def display_forecast(self, forecast_list):
        while self.forecast_layout.count():
            item = self.forecast_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for day in forecast_list:
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFixedWidth(140)
            v_layout = QVBoxLayout(frame)

            day_label = QLabel(f"{day.day_name}\n{day.date[5:]}")
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

            icon = self.get_weather_icon(day.icon, size=48)
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(48, 48))
            icon_label.setAlignment(Qt.AlignCenter)

            temp_label = QLabel(f"{day.temp_max:.0f}° / {day.temp_min:.0f}°")
            temp_label.setAlignment(Qt.AlignCenter)

            v_layout.addWidget(day_label)
            v_layout.addWidget(icon_label)
            v_layout.addWidget(temp_label)

            self.forecast_layout.addWidget(frame)

    def get_weather_icon(self, condition: str, size: int = 64):
        icons = {
            "Thunderstorm": "fa5s.bolt",
            "Snow": "fa5s.snowflake",
            "Rain": "fa5s.cloud-rain",
            "Drizzle": "fa5s.cloud-showers-heavy",
            "Clouds": "fa5s.cloud",
            "Clear": "fa5s.sun",
            "Mist": "fa5s.smog",
            "Fog": "fa5s.smog",
        }
        icon_name = icons.get(condition, "fa5s.cloud-sun")
        return qta.icon(icon_name, color="white", scale_factor=1.0)
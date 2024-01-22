import serial
import pynmea2
import tkinter as tk
from tkinter import scrolledtext

class GPSReaderApp:
    def __init__(self, master):
        self.master = master
        master.title("GPS Data Reader")

        self.serial_port_label = tk.Label(master, text="Serial Port:")
        self.serial_port_label.pack()

        self.serial_port_entry = tk.Entry(master)
        self.serial_port_entry.insert(0, "COM8")
        self.serial_port_entry.pack()

        self.start_button = tk.Button(master, text="Start Reading GPS Data", command=self.start_reading)
        self.start_button.pack()

        self.log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=100, height=25)
        self.log_text.pack()

        self.stop_button = tk.Button(master, text="Stop Reading", command=self.stop_reading)
        self.stop_button.pack()

        self.serial_port = None
        self.reading_gps = False

    def parse_nmea_sentence(self, sentence):
        try:
            data = pynmea2.parse(sentence)
            log_message = f"Latitude: {data.latitude}, Longitude: {data.longitude}\n"
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        except pynmea2.ParseError as e:
            log_message = f"Error parsing NMEA sentence: {e}\n"
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)

    def read_gps_data(self):
        try:
            with serial.Serial(self.serial_port, baudrate=9600, timeout=1) as ser:
                self.log_text.insert(tk.END, f"Reading GPS data from {self.serial_port}...\n")
                self.log_text.see(tk.END)
                while self.reading_gps:
                    try:
                        sentence = ser.readline().decode('utf-8').strip()
                        log_message = f"Raw NMEA sentence: {sentence}\n"
                        self.log_text.insert(tk.END, log_message)
                        self.log_text.see(tk.END)
                        if sentence.startswith('$GPGGA') or sentence.startswith('$GPRMC') or sentence.startswith("$G"):
                            self.parse_nmea_sentence(sentence)
                    except Exception as e:
                        pass
        except serial.SerialException as e:
            log_message = f"Error opening or reading from serial port: {e}\n"
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)

    def start_reading(self):
        if not self.reading_gps:
            self.serial_port = self.serial_port_entry.get()
            self.reading_gps = True
            self.start_button.config(state=tk.DISABLED)
            self.serial_port_entry.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)  # Clear previous log
            self.read_gps_data()

    def stop_reading(self):
        if self.reading_gps:
            self.reading_gps = False
            self.start_button.config(state=tk.NORMAL)
            self.serial_port_entry.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_text.insert(tk.END, "Stopping GPS data reading.\n")
            self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSReaderApp(root)
    root.mainloop()

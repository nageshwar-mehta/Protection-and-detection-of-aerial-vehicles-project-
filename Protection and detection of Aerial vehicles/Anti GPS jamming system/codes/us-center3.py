import serial
import pynmea2
import tkinter as tk
from tkinter import scrolledtext, filedialog
import csv
import cv2
from threading import Thread

class GPSReaderApp:
    def __init__(self, master):
        self.master = master
        master.title("GPS Data Reader(developed by PDD Lab Team)")

        self.serial_port_label = tk.Label(master, text="Serial Port:")
        self.serial_port_label.pack()

        self.serial_port_entry = tk.Entry(master)
        self.serial_port_entry.insert(0, "COM8")
        self.serial_port_entry.pack()

        self.start_button = tk.Button(master, text="Start Reading GPS Data", command=self.start_reading)
        self.start_button.pack()

        self.log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=15)
        self.log_text.pack()

        self.stop_button = tk.Button(master, text="Stop Reading", command=self.stop_reading)
        self.stop_button.pack()

        self.save_button = tk.Button(master, text="Save Data", command=self.save_data)
        self.save_button.pack()

        self.record_button = tk.Button(master, text="Record Video", command=self.toggle_record)
        self.record_button.pack()

        self.serial_port = None
        self.reading_gps = False
        self.latitude_data = []
        self.longitude_data = []
        self.recording = False
        self.video_writer = None

    def parse_nmea_sentence(self, sentence):
        try:
            data = pynmea2.parse(sentence)
            log_message = f"Latitude: {data.latitude}, Longitude: {data.longitude}\n"
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.latitude_data.append(data.latitude)
            self.longitude_data.append(data.longitude)
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
            self.save_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)  # Clear previous log
            self.read_gps_data()

    def stop_reading(self):
        if self.reading_gps:
            self.reading_gps = False
            self.start_button.config(state=tk.NORMAL)
            self.serial_port_entry.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.record_button.config(state=tk.DISABLED)
            self.log_text.insert(tk.END, "Stopping GPS data reading.\n")
            self.log_text.see(tk.END)

    def save_data(self):
        if self.latitude_data and self.longitude_data:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                with open(file_path, mode="w", newline="") as csvfile:
                    fieldnames = ["Latitude", "Longitude"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for lat, lon in zip(self.latitude_data, self.longitude_data):
                        writer.writerow({"Latitude": lat, "Longitude": lon})
                self.log_text.insert(tk.END, f"Data saved to {file_path}\n")
                self.log_text.see(tk.END)
        else:
            self.log_text.insert(tk.END, "No data to save.\n")
            self.log_text.see(tk.END)

    def toggle_record(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI Files", "*.avi")])
        if file_path:
            self.recording = True
            self.record_button.config(text="Stop Recording")
            self.video_writer = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
            self.log_text.insert(tk.END, f"Recording video to {file_path}\n")
            self.log_text.see(tk.END)
            # Start a thread for video recording
            self.video_thread = Thread(target=self.record_video)
            self.video_thread.start()
        else:
            self.log_text.insert(tk.END, "Video recording canceled.\n")
            self.log_text.see(tk.END)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.record_button.config(text="Record Video")
            self.log_text.insert(tk.END, "Video recording stopped.\n")
            self.log_text.see(tk.END)
            self.video_thread.join()
            self.video_writer.release()

    def record_video(self):
        try:
            with serial.Serial(self.serial_port, baudrate=9600, timeout=1) as ser:
                while self.recording:
                    try:
                        sentence = ser.readline().decode('utf-8').strip()
                        if sentence.startswith('$GPGGA') or sentence.startswith('$GPRMC') or sentence.startswith("$G"):
                            self.parse_nmea_sentence(sentence)
                    except Exception as e:
                        pass
                    # Dummy frame for now, you need to replace it with actual frames from your interface
                    dummy_frame = cv2.imread("codergps.jfif")  # Replace with the actual frame
                    if dummy_frame is not None:
                        self.video_writer.write(dummy_frame)
        except serial.SerialException as e:
            log_message = f"Error opening or reading from serial port: {e}\n"
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSReaderApp(root)
    root.mainloop()

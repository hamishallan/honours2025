import os
import socket
import struct
import time
import uuid
import sqlite3
import logging
import requests
from datetime import datetime, timezone


AODAQ_HOST = "127.0.0.1"
AODAQ_PORT = 1242
DB_FILE = "spectra.db"
HEADER_SIZE = 256


class AoDAQClient:
    def __init__(self, ip=AODAQ_HOST, port=AODAQ_PORT, db_file=DB_FILE):
        self.ip = ip
        self.port = port
        self.sock = None
        self.conn = sqlite3.connect(db_file)
        self._init_db()
        self.recv_buffer = b""  # persistent buffer


    # --- DB Methods ---
    def _init_db(self):
        cur = self.conn.cursor()
        
        # Drop existing tables if they exist
        cur.execute("DROP TABLE IF EXISTS core_spectrumdatapoint")
        cur.execute("DROP TABLE IF EXISTS core_spectrum")
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS core_spectrum (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            device_id TEXT NOT NULL,
            accuracy_m REAL,
            altitude_m REAL,
            latitude REAL,
            longitude REAL
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS core_spectrumdatapoint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wavelength REAL NOT NULL,
            intensity REAL NOT NULL,
            spectrum_id TEXT NOT NULL,
            FOREIGN KEY (spectrum_id) REFERENCES core_spectrum(id)
        )
        """)
        self.conn.commit()


    def save_spectrum(self, spectrum, device_id="tractor_probe_1"):
        spectrum_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO core_spectrum (id, timestamp, device_id)
            VALUES (?, ?, ?)
        """, (spectrum_id, timestamp, device_id))

        cur.executemany("""
            INSERT INTO core_spectrumdatapoint (wavelength, intensity, spectrum_id)
            VALUES (?, ?, ?)
        """, [(w, i, spectrum_id) for w, i in spectrum])

        self.conn.commit()
        logging.info("[AoDAQ_Client] Saved spectrum {} with {} points".format(spectrum_id, len(spectrum)))

    def close_db(self):
        self.conn.close()


    # --- AoDAQ TCP Methods ---
    def connect(self):
        self.sock = socket.create_connection((self.ip, self.port))
        logging.info(f"[AoDAQ_Client] {self.send_cmd('*IDN?')}")
        self.wait_for_initialisation()
        
        # Initialisation commands
        self.send_cmd("TRAN:BIN 1")
        self.send_cmd("SPEC:WLG 1")
        
        # --- Flush any extra bytes so we don't block later ---
        self.sock.settimeout(0.1)
        try:
            while True:
                leftover = self.sock.recv(4096)
                if not leftover:
                    break
        except Exception:
            pass
        self.sock.settimeout(None)
        logging.info("[AoDAQ_Client] Connection ready, buffer flushed.")


    def close(self):
        if self.sock:
            try:
                self.send_cmd("EXIT")
            except Exception:
                pass
            self.sock.close()
        self.close_db()


    def send_cmd(self, cmd):
        self.sock.sendall((cmd + "\n").encode("ascii"))
        data = b""
        while not data.endswith(b"\xfe\xfe\n"):
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return data.decode(errors="ignore")


    def wait_for_initialisation(self, poll_interval=2):
        logging.info("[AoDAQ_Client] Waiting for spectrometer initialisation...")
        while True:
            resp = self.send_cmd("STAT:INIT?")
            if "0" in resp.split():
                logging.info("[AoDAQ_Client] Spectrometer is ready.")
                break
            time.sleep(poll_interval)


    def start_stream(self):
        self.send_cmd("SPEC:STREAM 1")
        logging.info("[AoDAQ_Client] Streaming started.")


    def stop_stream(self):
        self.send_cmd("SPEC:STREAM 0")
        logging.info("[AoDAQ_Client] Streaming stopped.")
        

    def receive_spectrum(self):
        terminator = b"\xfe\xfe\n"

        # Keep reading until we have at least one terminator
        while terminator not in self.recv_buffer:
            chunk = self.sock.recv(8192)
            if not chunk:
                return None
            self.recv_buffer += chunk

        while terminator in self.recv_buffer:
            frame, self.recv_buffer = self.recv_buffer.split(terminator, 1)
            frame += terminator  # put terminator back

            # Skip empty / too-short frames
            if len(frame) < HEADER_SIZE + 3:
                logging.debug(f"[AoDAQ_Client] Skipping short frame of {len(frame)} bytes")
                continue

            return self.parse_binary_spectrum(frame)

        return None


    def parse_binary_spectrum(self, raw):
        raw = raw[:-3]  # strip terminator

        if len(raw) < HEADER_SIZE:
            raise ValueError(f"[AoDAQ_Client] Frame too short: {len(raw)} bytes")

        header = raw[:HEADER_SIZE]
        data_bytes = raw[HEADER_SIZE:]

        # Number of points from header
        num_points = struct.unpack(">I", header[55:59])[0]
        expected_len = num_points * 8

        if len(data_bytes) < expected_len:
            logging.warning(f"[AoDAQ_Client] Got {len(data_bytes)} data bytes, expected {expected_len}")
            return []

        data_bytes = data_bytes[:expected_len]
        floats = struct.unpack("<" + "f" * (len(data_bytes) // 4), data_bytes)

        # Correct order: wavelength first, then intensity
        spectrum = [(floats[i], floats[i+1]) for i in range(0, len(floats), 2)]

        if len(spectrum) != num_points:
            logging.warning(f"[AoDAQ_Client] Expected {num_points} points, got {len(spectrum)}")

        return spectrum
    
    
    def upload_spectra(self, api_url, default_device_id="tractor_probe_1", limit=None):
        """
        Upload spectra from the local SQLite DB to the remote API.

        Args:
            api_url (str): Endpoint for uploads.
            default_device_id (str): Device ID if missing in DB.
            limit (int, optional): Max number of spectra to upload (most recent first).
        """
        cur = self.conn.cursor()

        query = """
            SELECT id, timestamp, device_id, accuracy_m, altitude_m, latitude, longitude
            FROM core_spectrum
            ORDER BY timestamp DESC
        """
        if limit:
            query += f" LIMIT {limit}"

        cur.execute(query)
        spectra = cur.fetchall()

        for spectrum in spectra:
            spectrum_id, timestamp, device_id, accuracy_m, altitude_m, lat, lon = spectrum

            # Fetch datapoints
            cur.execute("""
                SELECT wavelength, intensity
                FROM core_spectrumdatapoint
                WHERE spectrum_id = ?
                ORDER BY id ASC
            """, (spectrum_id,))
            datapoints = cur.fetchall()

            payload = {
                "device_id": device_id or default_device_id,
                "wavelengths": [w for w, _ in datapoints],
                "intensities": [i for _, i in datapoints],
            }

            # Optional fields
            if lat is not None and lon is not None:
                payload["latitude"] = lat
                payload["longitude"] = lon
            if altitude_m is not None:
                payload["altitude_m"] = altitude_m
            if accuracy_m is not None:
                payload["accuracy_m"] = accuracy_m

            try:
                resp = requests.post(api_url, json=payload, timeout=30)
                if resp.status_code == 201:
                    logging.info("Uploaded spectrum %s (%d points)",
                                 spectrum_id, len(payload["wavelengths"]))
                else:
                    logging.error("Failed to upload %s: %s - %s",
                                  spectrum_id, resp.status_code, resp.text)
            except Exception as e:
                logging.error("Error uploading %s: %s", spectrum_id, e)

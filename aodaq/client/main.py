from classes import AoDAQClient
import logging

# --- Configuration ---
AODAQ_HOST = "192.168.64.2"
AODAQ_PORT = 1242

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    client = AoDAQClient(AODAQ_HOST, AODAQ_PORT)
    try:
        client.connect()        
        client.run_full_matlab_equivalent(
            gain_level="Low",
            apodization="NortonBeerStrong",
            num_averages=5,
            is_igm_avg=False
        )
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()

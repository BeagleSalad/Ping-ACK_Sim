import multiprocessing
import time

# Ping interval and waiting timeout
PING_INTERVAL = 1  # seconds
ACK_TIMEOUT = 2  # seconds

def detector(queue_send, queue_recv):
    """
    Detector process sends pings and expects ACKs. It detects if the other process crashes.
    """
    print("Detector process started.")
    while True:
        # Send a ping
        queue_send.put("PING")
        print("[Detector] Sent: PING")
        
        # Wait for an ACK
        try:
            ack = queue_recv.get(timeout=ACK_TIMEOUT)
            if ack == "ACK":
                print("[Detector] Received: ACK")
        except Exception:
            print("[Detector] No ACK received. Process crashed!")
            break  # Exit on detecting crash
        
        time.sleep(PING_INTERVAL)

def crash_process(queue_send, queue_recv, crash_after):
    """
    'Crash' process responds to PING with ACK and simulates a crash after a certain time.
    """
    print("Crash process started.")
    start_time = time.time()
    
    while True:
        # Simulate crash after `crash_after` seconds
        if time.time() - start_time > crash_after:
            print("[Crash Process] Crashing now!")
            break
        
        try:
            # Wait for a ping
            ping = queue_recv.get(timeout=PING_INTERVAL)
            if ping == "PING":
                print("[Crash Process] Received: PING")
                # Respond with ACK
                queue_send.put("ACK")
                print("[Crash Process] Sent: ACK")
        except Exception:
            pass  # No PING received, loop back to wait

if __name__ == "__main__":
    # Create queues for bidirectional communication
    detector_to_crash = multiprocessing.Queue()
    crash_to_detector = multiprocessing.Queue()

    # Time after which the crash process will crash (in seconds)
    CRASH_AFTER = 5

    # Create processes
    detector_process = multiprocessing.Process(target=detector, args=(detector_to_crash, crash_to_detector))
    crash_process_instance = multiprocessing.Process(target=crash_process, args=(crash_to_detector, detector_to_crash, CRASH_AFTER))

    # Start processes
    detector_process.start()
    crash_process_instance.start()

    # Wait for processes to complete
    detector_process.join()
    crash_process_instance.join()

    print("Simulation finished.")

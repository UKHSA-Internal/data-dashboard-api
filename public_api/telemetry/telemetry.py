import time
import threading
import atexit
from contextlib import contextmanager

import requests


class Telemetry:

    def __init__(self):

        self.service = None
        self.environment = None
        self.endpoint = None

        self.session = requests.Session()

        # batching
        self.queue = []
        self.batch_size = 1
        self.flush_interval = 2

        self.lock = threading.Lock()
        self.running = False

    # --------------------------------------------------------
    # Init
    # --------------------------------------------------------

    def init(self, service, endpoint=None, environment="dev"):
        if self.running:
            return  # prevent double init (Django reload etc.)

        self.service = service
        self.environment = environment
        self.endpoint = endpoint

        self.running = True

        threading.Thread(target=self._worker, daemon=True).start()

        atexit.register(self._flush)

        print(f"[telemetry] initialized for {service} ({environment})")

    # --------------------------------------------------------
    # Background worker
    # --------------------------------------------------------

    def _worker(self):

        while self.running:

            time.sleep(self.flush_interval)

            with self.lock:
                if self.queue:
                    self._flush()

    # --------------------------------------------------------
    # Flush batch
    # --------------------------------------------------------

    def _flush(self):

        if not self.queue:
            return

        batch = self.queue
        self.queue = []

        if not self.endpoint:
            # demo mode: just print signals
            for signal in batch:
                print(signal)
            return

        try:

            self.session.post(
                self.endpoint,
                json=batch,
                timeout=2
            )

        except Exception as e:
            print(f"[telemetry] failed to send: {e}")

    # --------------------------------------------------------
    # Internal enqueue
    # --------------------------------------------------------

    def _enqueue(self, signal):

        signal["service"] = self.service
        signal["environment"] = self.environment
        signal["timestamp"] = time.time()

        with self.lock:

            self.queue.append(signal)

            if len(self.queue) >= self.batch_size:
                self._flush()

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def track(self, name, **metadata):

        signal = {
            "type": "event",
            "name": name,
            "metadata": metadata
        }

        self._enqueue(signal)

    def metric(self, name, value, **metadata):

        signal = {
            "type": "metric",
            "name": name,
            "value": value,
            "metadata": metadata
        }

        self._enqueue(signal)

    # --------------------------------------------------------
    # Operation wrapper
    # --------------------------------------------------------

    @contextmanager
    def operation(self, name, **metadata):

        start = time.time()

        self.track(f"{name}_start", **metadata)

        try:

            yield

            self.track(f"{name}_success", **metadata)

        except Exception:

            self.track(f"{name}_error", **metadata)
            raise

        finally:

            duration = time.time() - start

            self.metric(
                f"{name}_duration",
                duration,
                **metadata
            )


# singleton instance
telemetry = Telemetry()
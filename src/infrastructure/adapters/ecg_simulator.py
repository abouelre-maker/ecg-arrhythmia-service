import neurokit2 as nk
import numpy as np


class ECGDataSimulator:
    """محاكي إشارات ECG لغرض الاختبار والتحقق السريري (V&V) وفق معيار IEC 62304"""

    def __init__(self, sampling_rate: int = 500):
        self.sampling_rate = sampling_rate

    def generate_normal_ecg(self, duration_sec: int = 10, heart_rate: int = 75) -> np.ndarray:
        """توليد إشارة ECG طبيعية محاكاة للمحيط السريري"""
        signal = nk.ecg_simulate(
            duration=duration_sec,
            sampling_rate=self.sampling_rate,
            heart_rate=heart_rate,
            noise=0.01,
        )
        return np.array(signal)


if __name__ == "__main__":
    simulator = ECGDataSimulator()
    signal = simulator.generate_normal_ecg(duration_sec=5)
    print(
        f"تم توليد إشارة بنجاح! عدد النقاط: {len(signal)} نقطة بمعدل عينات {simulator.sampling_rate}Hz"
    )

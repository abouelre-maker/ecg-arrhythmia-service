import pytest
from fastapi import HTTPException
from unittest.mock import patch

from src.api.v1.analyze import analyze_ecg
from src.domain.entities.ecg_signal import ECGSignal


def test_analyze_ecg_success():
    """اختبار نجاح معالجة الإشارة عبر الـ API"""
    # إنشاء إشارة وهمية سليمة
    signal = ECGSignal(
        patient_id="PAT-999",
        sampling_rate_hz=500.0,
        samples=[0.0] * 1000  # 1000 نقطة لتجاوز الفلترة
    )
    
    # استدعاء الدالة مباشرة
    response = analyze_ecg(signal)
    
    assert "alert" in response
    assert "fhir_observation" in response
    assert response["fhir_observation"]["resourceType"] == "Observation"


@patch("src.api.v1.analyze.RuleBasedDetector.analyze")
def test_analyze_ecg_exception(mock_analyze):
    """اختبار التعامل مع الأخطاء (Exceptions) في الـ API"""
    # إجبار الخوارزمية على إرجاع خطأ وهمي
    mock_analyze.side_effect = Exception("System Down")
    signal = ECGSignal(
        patient_id="PAT-456",
        sampling_rate_hz=500.0,
        samples=[0.0, 1.0]
    )
    
    # التأكد من أن الـ API يكتشف الخطأ ويرجع 500
    with pytest.raises(HTTPException) as excinfo:
        analyze_ecg(signal)
        
    assert excinfo.value.status_code == 500
    assert "System Down" in excinfo.value.detail
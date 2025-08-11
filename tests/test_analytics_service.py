import pytest
from unittest.mock import Mock, MagicMock
from bot.services.analytics_service import AnalyticsService

# Pytest bizga testlarni sodda funksiyalar sifatida yozish imkonini beradi.
# "fixture" - bu testlar uchun kerakli bo'lgan obyektlarni oldindan tayyorlab beruvchi funksiya.
@pytest.fixture
def mock_analytics_repo() -> MagicMock:
    """
    AnalyticsRepository'ning soxta (mock) obyektini yaratadi.
    Bu obyekt haqiqiy ma'lumotlar bazasiga ulanmaydi.
    """
    return MagicMock()

@pytest.fixture
def analytics_service(mock_analytics_repo: MagicMock) -> AnalyticsService:
    # Parametr nomini "analytics_repository" ga o'zgartiramiz
    return AnalyticsService(analytics_repository=mock_analytics_repo)


# === BIRINCHI TESTIMIZ ===
def test_get_total_users_count(
    analytics_service: AnalyticsService,
    mock_analytics_repo: MagicMock
):
    """
    get_total_users_count metodi to'g'ri ishlashini tekshiradi.
    """
    # 1. TAYYORGARLIK (Arrange)
    # Biz mock_analytics_repo'ga aytamiz: "Agar kimdir sendan
    # get_total_count metodini chaqirsa, 123 degan sonni qaytar"
    expected_user_count = 123
    mock_analytics_repo.get_total_count.return_value = expected_user_count

    # 2. HARAKAT (Act)
    # Biz test qilmoqchi bo'lgan servis metodini chaqiramiz.
    actual_user_count = analytics_service.get_total_users_count()

    # 3. TASDIQLASH (Assert)
    # Natija biz kutgan qiymatga teng ekanligini tekshiramiz.
    assert actual_user_count == expected_user_count

    # Bonus: Repozitoriyning kerakli metodi rostdan ham bir marta chaqirilganini tekshiramiz.
    mock_analytics_repo.get_total_count.assert_called_once()

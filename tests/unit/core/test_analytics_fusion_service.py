"""
Unit tests for AnalyticsFusionService
Focus on z-score trending detection with synthetic data spike scenarios
"""

import math
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from core.services.analytics_fusion_service import AnalyticsFusionService


class TestAnalyticsFusionServiceTrending:
    """Test trending z-score calculations with synthetic data patterns"""

    @pytest.fixture
    def mock_repos(self):
        """Mock all required repositories"""
        return {
            "channel_daily": AsyncMock(),
            "post_repo": AsyncMock(),
            "metrics_repo": AsyncMock(),
            "edges_repo": AsyncMock(),
            "stats_raw_repo": AsyncMock(),
        }

    @pytest.fixture
    def fusion_service(self, mock_repos):
        """Create service instance with mocked dependencies"""
        return AnalyticsFusionService(
            channel_daily_repo=mock_repos["channel_daily"],
            post_repo=mock_repos["post_repo"],
            metrics_repo=mock_repos["metrics_repo"],
            edges_repo=mock_repos["edges_repo"],
            stats_raw_repo=mock_repos["stats_raw_repo"],
        )

    @pytest.fixture
    def baseline_posts(self):
        """Synthetic baseline posts with normal view distribution"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        posts = []

        # Generate 20 posts with normal distribution (mean=1000, std=200)
        normal_views = [
            800,
            950,
            1100,
            1050,
            900,
            1200,
            850,
            1300,
            1150,
            750,
            1000,
            1100,
            950,
            1250,
            800,
            1050,
            900,
            1150,
            1000,
            1100,
        ]

        for i, views in enumerate(normal_views):
            posts.append(
                {
                    "msg_id": i + 1,
                    "date": base_time + timedelta(hours=i),
                    "views": views,
                    "forwards": views // 50,
                    "replies": views // 100,
                    "reactions": {"👍": views // 20, "❤️": views // 30},
                    "title": f"Normal Post {i+1}",
                    "permalink": f"https://t.me/test/{i+1}",
                }
            )

        return posts

    @pytest.fixture
    def spike_posts(self):
        """Synthetic posts with clear trending spikes"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        posts = []

        # Generate posts with 3 clear spikes in a normal distribution
        views_with_spikes = [
            800,
            950,
            1100,
            5000,  # Spike 1: 5x normal
            900,
            1200,
            850,
            1300,
            1150,
            750,
            8500,  # Spike 2: 8.5x normal
            1100,
            950,
            1250,
            800,
            1050,
            6200,  # Spike 3: 6.2x normal
            900,
            1150,
            1000,
            1100,
        ]

        for i, views in enumerate(views_with_spikes):
            posts.append(
                {
                    "msg_id": i + 1,
                    "date": base_time + timedelta(hours=i),
                    "views": views,
                    "forwards": views // 30,  # Trending posts get more forwards
                    "replies": views // 80,
                    "reactions": {"👍": views // 15, "❤️": views // 25, "🔥": views // 40},
                    "title": f"Post {i+1}" + (" - VIRAL!" if views > 3000 else ""),
                    "permalink": f"https://t.me/test/{i+1}",
                }
            )

        return posts

    async def test_zscore_trending_identifies_spikes(self, fusion_service, mock_repos, spike_posts):
        """Test that z-score method correctly identifies synthetic viral spikes"""
        # Setup
        channel_id = 12345
        frm = datetime(2024, 1, 1)
        to = datetime(2024, 1, 2)

        # Mock repository to return our spike posts
        mock_repos["post_repo"].top_by_views.return_value = spike_posts

        # Execute
        trending = await fusion_service.get_trending(channel_id, frm, to, method="zscore")

        # Verify trending posts were identified
        assert len(trending) > 0, "Should identify trending posts from spike data"
        assert len(trending) <= 10, "Should limit results to 10 posts"

        # Extract view counts for manual z-score verification
        all_views = [post["views"] for post in spike_posts]
        mean_views = sum(all_views) / len(all_views)
        variance = sum((x - mean_views) ** 2 for x in all_views) / len(all_views)
        std_dev = math.sqrt(variance)

        # Verify the 3 major spikes (5000, 8500, 6200) are detected
        trending_views = [post["views"] for post in trending]
        assert 5000 in trending_views, "Should detect first spike (5000 views)"
        assert 8500 in trending_views, "Should detect second spike (8500 views)"
        assert 6200 in trending_views, "Should detect third spike (6200 views)"

        # Verify z-scores are calculated correctly
        for post in trending:
            if "trend_score" in post:
                expected_zscore = (post["views"] - mean_views) / std_dev
                assert (
                    abs(post["trend_score"] - expected_zscore) < 0.1
                ), f"Z-score {post['trend_score']} should match calculated {expected_zscore:.2f}"
                assert post["trend_score"] > 1.5, "Trending posts should have z-score > 1.5"

    async def test_zscore_baseline_no_false_positives(
        self, fusion_service, mock_repos, baseline_posts
    ):
        """Test that normal distribution doesn't produce false trending signals"""
        # Setup
        channel_id = 12345
        frm = datetime(2024, 1, 1)
        to = datetime(2024, 1, 2)

        # Mock repository to return baseline posts (normal distribution)
        mock_repos["post_repo"].top_by_views.return_value = baseline_posts

        # Execute
        trending = await fusion_service.get_trending(channel_id, frm, to, method="zscore")

        # Verify minimal or no trending posts from normal distribution
        # In a normal distribution, very few points should exceed z-score > 1.5
        assert (
            len(trending) <= 2
        ), f"Normal distribution should produce minimal trending signals, got {len(trending)}"

        # If any trending posts exist, verify their z-scores
        if trending:
            for post in trending:
                assert (
                    post.get("trend_score", 0) > 1.5
                ), "Any detected trending post should have z-score > 1.5"

    async def test_zscore_edge_cases(self, fusion_service, mock_repos):
        """Test z-score calculation edge cases"""
        # Test case 1: Insufficient data
        mock_repos["post_repo"].top_by_views.return_value = [
            {"msg_id": 1, "views": 100, "date": datetime.now()}
        ]

        trending = await fusion_service.get_trending(12345, datetime.now(), datetime.now())
        assert len(trending) <= 1, "Should handle insufficient data gracefully"

        # Test case 2: Identical values (zero variance)
        identical_posts = []
        for i in range(5):
            identical_posts.append(
                {
                    "msg_id": i + 1,
                    "views": 1000,  # All identical
                    "date": datetime.now() + timedelta(hours=i),
                    "forwards": 20,
                    "replies": 10,
                    "reactions": {},
                    "title": f"Post {i+1}",
                    "permalink": f"https://t.me/test/{i+1}",
                }
            )

        mock_repos["post_repo"].top_by_views.return_value = identical_posts
        trending = await fusion_service.get_trending(12345, datetime.now(), datetime.now())

        # Should handle zero variance gracefully (no posts will be trending)
        assert all(
            post.get("trend_score", 0) == 0 for post in trending
        ), "Identical values should produce zero z-scores"

    async def test_trending_score_sorting(self, fusion_service, mock_repos, spike_posts):
        """Test that trending posts are sorted by trend_score descending"""
        # Setup
        mock_repos["post_repo"].top_by_views.return_value = spike_posts

        # Execute
        trending = await fusion_service.get_trending(12345, datetime.now(), datetime.now())

        # Verify sorting by trend_score descending
        if len(trending) > 1:
            trend_scores = [post.get("trend_score", 0) for post in trending]
            assert trend_scores == sorted(
                trend_scores, reverse=True
            ), "Trending posts should be sorted by trend_score descending"

            # Highest z-score should be the 8500 views post (biggest spike)
            assert (
                trending[0]["views"] == 8500
            ), "Post with most views (biggest spike) should be ranked first"

    async def test_ewma_trending_comparison(self, fusion_service, mock_repos, spike_posts):
        """Test EWMA trending method as comparison to z-score"""
        # Setup
        mock_repos["post_repo"].top_by_views.return_value = spike_posts

        # Execute both methods
        zscore_trending = await fusion_service.get_trending(
            12345, datetime.now(), datetime.now(), method="zscore"
        )
        ewma_trending = await fusion_service.get_trending(
            12345, datetime.now(), datetime.now(), method="ewma"
        )

        # Both methods should detect trending posts
        assert len(zscore_trending) > 0, "Z-score method should detect trending posts"
        assert len(ewma_trending) > 0, "EWMA method should detect trending posts"

        # Both should identify the major spikes
        zscore_views = {post["views"] for post in zscore_trending}
        ewma_views = {post["views"] for post in ewma_trending}

        major_spikes = {5000, 8500, 6200}
        zscore_detections = major_spikes.intersection(zscore_views)
        ewma_detections = major_spikes.intersection(ewma_views)

        assert (
            len(zscore_detections) >= 2
        ), f"Z-score should detect at least 2 major spikes, found {len(zscore_detections)}"
        assert (
            len(ewma_detections) >= 2
        ), f"EWMA should detect at least 2 major spikes, found {len(ewma_detections)}"

    async def test_trending_with_repository_error(self, fusion_service, mock_repos):
        """Test graceful handling of repository errors"""
        # Setup repository to raise exception
        mock_repos["post_repo"].top_by_views.side_effect = Exception("Database connection error")

        # Execute
        trending = await fusion_service.get_trending(12345, datetime.now(), datetime.now())

        # Should return empty list on error
        assert trending == [], "Should return empty list when repository fails"

    def test_zscore_calculation_direct(self, fusion_service):
        """Test the z-score calculation method directly"""
        # Test data with known statistical properties
        posts = [
            {"msg_id": i, "views": views, "date": datetime.now()}
            for i, views in enumerate([100, 200, 300, 1000, 150], 1)  # 1000 is clear outlier
        ]
        view_counts = [100, 200, 300, 1000, 150]

        # Calculate expected values
        mean = sum(view_counts) / len(view_counts)  # 350
        variance = sum((x - mean) ** 2 for x in view_counts) / len(view_counts)
        std_dev = math.sqrt(variance)
        expected_zscore_1000 = (1000 - mean) / std_dev

        # Execute
        trending = fusion_service._calculate_zscore_trending(posts, view_counts, 48)

        # Verify
        assert len(trending) == 1, "Should detect exactly one trending post (1000 views)"
        assert trending[0]["msg_id"] == 4, "Should identify the 1000-view post"
        assert (
            abs(trending[0]["trend_score"] - expected_zscore_1000) < 0.01
        ), f"Z-score should be {expected_zscore_1000:.2f}, got {trending[0]['trend_score']}"
        assert trending[0]["trend_score"] > 1.5, "Outlier should have z-score > 1.5"

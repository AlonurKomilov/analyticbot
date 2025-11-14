/**
 * Daily Recommendation Service
 * Generates posting recommendations for each day based on patterns and historical data
 */

interface WeeklyPattern {
    dayOfWeek: number; // 0-6 (Sunday-Saturday)
    baseScore: number; // 0-100 base recommendation score
    bestTimes: string[]; // Optimal posting times
    confidence: number; // Confidence in this pattern
}

interface HistoricalDayData {
    date: number;
    dayOfWeek: number;
    avgEngagement?: number;
    postCount?: number;
    views?: number;
    reactions?: number;
}

interface DailyRecommendation {
    date: number;
    dayOfWeek: number;
    recommendationScore: number; // 0-100
    recommendedTimes: string[];
    confidence: number;
    reasoning: string;
    isPast: boolean;
    isToday: boolean;
    isFuture: boolean;
    historicalData?: HistoricalDayData;
}

class DailyRecommendationService {
    // Base patterns for different days of the week
    private static weeklyPatterns: WeeklyPattern[] = [
        { dayOfWeek: 0, baseScore: 70, bestTimes: ['12:00', '17:00', '19:00'], confidence: 75 }, // Sunday
        { dayOfWeek: 1, baseScore: 85, bestTimes: ['09:00', '14:00', '18:00'], confidence: 90 }, // Monday
        { dayOfWeek: 2, baseScore: 90, bestTimes: ['10:00', '15:00', '19:00'], confidence: 95 }, // Tuesday
        { dayOfWeek: 3, baseScore: 88, bestTimes: ['09:30', '14:30', '18:30'], confidence: 92 }, // Wednesday
        { dayOfWeek: 4, baseScore: 86, bestTimes: ['10:30', '15:30', '19:30'], confidence: 88 }, // Thursday
        { dayOfWeek: 5, baseScore: 75, bestTimes: ['09:00', '13:00', '17:00'], confidence: 80 }, // Friday
        { dayOfWeek: 6, baseScore: 68, bestTimes: ['11:00', '16:00', '20:00'], confidence: 70 }, // Saturday
    ];

    /**
     * Generate daily recommendations for a specific month
     */
    static generateMonthlyRecommendations(
        year: number,
        month: number, // 0-11 JavaScript month format
        historicalData: HistoricalDayData[] = [],
        bestTimesByDay: Record<number, string[]> = {}
    ): DailyRecommendation[] {
        const today = new Date();
        const lastDay = new Date(year, month + 1, 0);
        const recommendations: DailyRecommendation[] = [];

        // Generate recommendations for each day of the month
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const currentDate = new Date(year, month, day);
            const dayOfWeek = currentDate.getDay();
            const isToday = currentDate.toDateString() === today.toDateString();
            const isPast = currentDate < today && !isToday;
            const isFuture = currentDate > today;

            // Find historical data for this day
            const historicalDayData = historicalData.find(h => h.date === day);
            
            // Get weekly pattern for this day of week
            const weeklyPattern = this.weeklyPatterns.find(p => p.dayOfWeek === dayOfWeek) || 
                { dayOfWeek, baseScore: 70, bestTimes: ['09:00', '14:00', '18:00'], confidence: 60 };

            let recommendationScore: number;
            let confidence: number;
            let reasoning: string;
            let recommendedTimes: string[];

            if (isPast && historicalDayData) {
                // Use historical performance for past days
                recommendationScore = this.calculateHistoricalScore(historicalDayData);
                confidence = Math.min(95, 70 + (historicalDayData.postCount || 0) * 5);
                reasoning = this.generateHistoricalReasoning(historicalDayData);
                recommendedTimes = weeklyPattern.bestTimes;
            } else {
                // Use prediction for future days
                recommendationScore = this.calculatePredictedScore(
                    weeklyPattern,
                    historicalData.filter(h => h.dayOfWeek === dayOfWeek),
                    currentDate
                );
                confidence = this.calculatePredictionConfidence(
                    weeklyPattern,
                    historicalData.filter(h => h.dayOfWeek === dayOfWeek)
                );
                reasoning = this.generatePredictionReasoning(weeklyPattern, dayOfWeek);
                recommendedTimes = bestTimesByDay[dayOfWeek] || weeklyPattern.bestTimes;
            }

            recommendations.push({
                date: day,
                dayOfWeek,
                recommendationScore: Math.max(0, Math.min(100, recommendationScore)),
                recommendedTimes,
                confidence: Math.max(0, Math.min(100, confidence)),
                reasoning,
                isPast,
                isToday,
                isFuture,
                historicalData: historicalDayData
            });
        }

        return recommendations;
    }

    /**
     * Calculate score based on historical performance
     */
    private static calculateHistoricalScore(data: HistoricalDayData): number {
        if (!data.avgEngagement && !data.views) return 30; // Poor if no data

        // Calculate engagement rate
        let engagementRate = 0;
        if (data.avgEngagement && data.views && data.views > 0) {
            engagementRate = (data.avgEngagement / data.views) * 100;
        } else if (data.avgEngagement) {
            // Assume good engagement if views not available
            engagementRate = Math.min(15, data.avgEngagement); // Cap at 15%
        }

        // Convert engagement rate to score (0-100)
        if (engagementRate >= 10) return 95; // Excellent
        if (engagementRate >= 5) return 85;  // Great
        if (engagementRate >= 3) return 70;  // Good
        if (engagementRate >= 1) return 55;  // Average
        return 35; // Poor
    }

    /**
     * Calculate predicted score for future days
     */
    private static calculatePredictedScore(
        weeklyPattern: WeeklyPattern,
        historicalDataForDay: HistoricalDayData[],
        targetDate: Date
    ): number {
        let baseScore = weeklyPattern.baseScore;

        // Adjust based on historical performance for this day of week
        if (historicalDataForDay.length > 0) {
            const avgHistoricalScore = historicalDataForDay.reduce(
                (sum, data) => sum + this.calculateHistoricalScore(data),
                0
            ) / historicalDataForDay.length;
            
            // Blend historical average with weekly pattern (70% historical, 30% pattern)
            baseScore = avgHistoricalScore * 0.7 + weeklyPattern.baseScore * 0.3;
        }

        // Apply seasonal adjustments
        const month = targetDate.getMonth();
        const seasonalMultiplier = this.getSeasonalMultiplier(month);
        baseScore *= seasonalMultiplier;

        // Add some randomness to simulate real-world variation
        const variance = (Math.random() - 0.5) * 20; // ±10 points
        baseScore += variance;

        return baseScore;
    }

    /**
     * Calculate confidence in prediction
     */
    private static calculatePredictionConfidence(
        weeklyPattern: WeeklyPattern,
        historicalDataForDay: HistoricalDayData[]
    ): number {
        let confidence = weeklyPattern.confidence;

        // Higher confidence with more historical data
        if (historicalDataForDay.length > 0) {
            const dataPoints = historicalDataForDay.length;
            const dataBonus = Math.min(20, dataPoints * 2); // Up to 20 points bonus
            confidence += dataBonus;

            // Check consistency of historical data
            if (dataPoints > 1) {
                const scores = historicalDataForDay.map(d => this.calculateHistoricalScore(d));
                const variance = this.calculateVariance(scores);
                if (variance < 10) confidence += 10; // Bonus for consistency
            }
        } else {
            confidence -= 15; // Lower confidence without historical data
        }

        return confidence;
    }

    /**
     * Generate reasoning text for historical performance
     */
    private static generateHistoricalReasoning(data: HistoricalDayData): string {
        const score = this.calculateHistoricalScore(data);
        
        if (score >= 85) {
            return `Excellent historical performance with ${data.postCount || 'multiple'} posts averaging ${data.avgEngagement?.toFixed(2) || 'high'} engagement.`;
        } else if (score >= 70) {
            return `Good historical performance. This day typically sees strong audience engagement.`;
        } else if (score >= 55) {
            return `Average historical performance. Consider optimizing content or timing.`;
        } else {
            return `Below average historical performance. Consider alternative posting times or content types.`;
        }
    }

    /**
     * Generate reasoning text for predictions
     */
    private static generatePredictionReasoning(pattern: WeeklyPattern, dayOfWeek: number): string {
        const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const dayName = dayNames[dayOfWeek];
        
        if (pattern.baseScore >= 85) {
            return `${dayName}s typically show high engagement. Great day for important announcements.`;
        } else if (pattern.baseScore >= 70) {
            return `${dayName}s show good engagement patterns. Suitable for regular posting.`;
        } else {
            return `${dayName}s tend to have lower engagement. Consider lighter content or alternative days.`;
        }
    }

    /**
     * Get seasonal adjustment multiplier
     */
    private static getSeasonalMultiplier(month: number): number {
        // Adjust for seasonal patterns (0 = January, 11 = December)
        const seasonalFactors = [
            0.95, // January - post-holiday low
            1.00, // February - normal
            1.05, // March - spring increase
            1.08, // April - spring peak
            1.10, // May - high activity
            1.00, // June - summer start
            0.90, // July - summer low
            0.88, // August - vacation time
            1.05, // September - back to work
            1.10, // October - fall peak
            1.08, // November - pre-holiday
            0.92, // December - holiday distraction
        ];
        
        return seasonalFactors[month] || 1.0;
    }

    /**
     * Calculate variance of an array of numbers
     */
    private static calculateVariance(numbers: number[]): number {
        if (numbers.length <= 1) return 0;
        
        const mean = numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
        const squaredDifferences = numbers.map(n => Math.pow(n - mean, 2));
        const variance = squaredDifferences.reduce((sum, sq) => sum + sq, 0) / numbers.length;
        
        return Math.sqrt(variance); // Return standard deviation
    }

    /**
     * Generate sample data for demo purposes
     */
    static generateSampleRecommendations(year: number = 2025, month: number = 10): DailyRecommendation[] {
        // Generate some sample historical data
        const sampleHistoricalData: HistoricalDayData[] = [];
        const today = new Date();
        const currentMonth = new Date(year, month);
        
        // Generate historical data for past days in the month
        for (let day = 1; day <= today.getDate() && currentMonth.getMonth() === today.getMonth(); day++) {
            const date = new Date(year, month, day);
            if (date < today) {
                sampleHistoricalData.push({
                    date: day,
                    dayOfWeek: date.getDay(),
                    avgEngagement: Math.random() * 20 + 5, // 5-25 engagement
                    postCount: Math.floor(Math.random() * 3) + 1, // 1-3 posts
                    views: Math.floor(Math.random() * 1000) + 100, // 100-1100 views
                    reactions: Math.floor(Math.random() * 50) + 5 // 5-55 reactions
                });
            }
        }

        // Sample best times by day of week
        const sampleBestTimes: Record<number, string[]> = {
            0: ['12:00', '17:00', '19:00'], // Sunday
            1: ['09:00', '14:00', '18:00'], // Monday
            2: ['10:00', '15:00', '19:00'], // Tuesday
            3: ['09:30', '14:30', '18:30'], // Wednesday
            4: ['10:30', '15:30', '19:30'], // Thursday
            5: ['09:00', '13:00', '17:00'], // Friday
            6: ['11:00', '16:00', '20:00'], // Saturday
        };

        return this.generateMonthlyRecommendations(year, month, sampleHistoricalData, sampleBestTimes);
    }
}

export default DailyRecommendationService;
export type { DailyRecommendation, WeeklyPattern, HistoricalDayData };
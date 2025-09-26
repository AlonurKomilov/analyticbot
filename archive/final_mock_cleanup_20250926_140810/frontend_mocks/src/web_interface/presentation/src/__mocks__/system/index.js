/**
 * System Mock Data Module
 * System status and configuration data for testing and development
 */

export const systemStatusData = {
  botStatus: 'online',
  apiStatus: 'operational',
  analyticsStatus: 'processing',
  lastUpdate: new Date().toISOString()
};

export const apiUtilsData = {
  /**
   * Simulates API delay for realistic loading experience
   */
  mockApiCall: async (data, delay = 300) => {
    await new Promise(resolve => setTimeout(resolve, delay));
    return data;
  },

  /**
   * Get mock storage files for media browser
   */
  getMockStorageFiles: (limit = 20, offset = 0) => {
    const mockFiles = [
      {
        id: 1,
        filename: "sample-image-1.jpg",
        size: 245760,
        type: "image/jpeg",
        uploaded_at: "2025-09-06T10:30:00Z",
        url: "https://picsum.photos/800/600?random=1"
      },
      {
        id: 2,
        filename: "demo-video.mp4",
        size: 15728640,
        type: "video/mp4",
        uploaded_at: "2025-09-06T09:15:00Z",
        url: "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
      },
      {
        id: 3,
        filename: "presentation.pdf",
        size: 1048576,
        type: "application/pdf",
        uploaded_at: "2025-09-05T14:20:00Z",
        url: "#"
      },
      {
        id: 4,
        filename: "chart-data.png",
        size: 156000,
        type: "image/png",
        uploaded_at: "2025-09-05T11:45:00Z",
        url: "https://picsum.photos/600/400?random=2"
      },
      {
        id: 5,
        filename: "audio-clip.mp3",
        size: 3145728,
        type: "audio/mpeg",
        uploaded_at: "2025-09-04T16:30:00Z",
        url: "#"
      }
    ];

    // Simulate pagination
    const total = mockFiles.length;
    const paginatedFiles = mockFiles.slice(offset, offset + limit);

    return {
      files: paginatedFiles,
      total: total,
      limit: limit,
      offset: offset,
      hasMore: offset + limit < total
    };
  }
};

// Combined system export
export const system = {
  systemStatus: systemStatusData,
  apiUtils: apiUtilsData
};
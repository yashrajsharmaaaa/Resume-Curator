// Simple analytics service for production
class AnalyticsService {
  constructor() {
    this.enabled = import.meta.env.VITE_ENABLE_ANALYTICS === 'true';
    this.trackingId = import.meta.env.VITE_GA_TRACKING_ID;
  }

  // Initialize analytics
  init() {
    if (!this.enabled || !this.trackingId) return;

    // Google Analytics 4 setup
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${this.trackingId}`;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag() {
      window.dataLayer.push(arguments);
    }
    window.gtag = gtag;

    gtag('js', new Date());
    gtag('config', this.trackingId);
  }

  // Track page views
  trackPageView(path) {
    if (!this.enabled || !window.gtag) return;
    
    window.gtag('config', this.trackingId, {
      page_path: path,
    });
  }

  // Track events
  trackEvent(eventName, parameters = {}) {
    if (!this.enabled || !window.gtag) return;
    
    window.gtag('event', eventName, parameters);
  }

  // Track resume upload
  trackResumeUpload(fileType, fileSize) {
    this.trackEvent('resume_upload', {
      file_type: fileType,
      file_size: fileSize,
    });
  }

  // Track analysis completion
  trackAnalysisComplete(score, processingTime) {
    this.trackEvent('analysis_complete', {
      compatibility_score: score,
      processing_time: processingTime,
    });
  }

  // Track errors
  trackError(error, context) {
    this.trackEvent('error', {
      error_message: error.message,
      error_context: context,
    });
  }
}

export const analytics = new AnalyticsService();
export default analytics;
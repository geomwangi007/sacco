class StorageKeys {
  // Authentication
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String userId = 'user_id';
  static const String userEmail = 'user_email';
  static const String isLoggedIn = 'is_logged_in';
  static const String loginTimestamp = 'login_timestamp';
  
  // Biometric Authentication
  static const String biometricEnabled = 'biometric_enabled';
  static const String biometricPrompted = 'biometric_prompted';
  
  // PIN Authentication
  static const String pinEnabled = 'pin_enabled';
  static const String pinHash = 'pin_hash';
  static const String pinFailedAttempts = 'pin_failed_attempts';
  static const String pinLockoutTime = 'pin_lockout_time';
  
  // Security Settings
  static const String sessionTimeout = 'session_timeout';
  static const String autoLockEnabled = 'auto_lock_enabled';
  static const String transactionPinRequired = 'transaction_pin_required';
  static const String biometricTransactionEnabled = 'biometric_transaction_enabled';
  
  // Notifications
  static const String fcmToken = 'fcm_token';
  static const String notificationPermissionGranted = 'notification_permission_granted';
  static const String transactionNotificationsEnabled = 'transaction_notifications_enabled';
  static const String loanNotificationsEnabled = 'loan_notifications_enabled';
  static const String securityNotificationsEnabled = 'security_notifications_enabled';
  static const String marketingNotificationsEnabled = 'marketing_notifications_enabled';
  
  // User Preferences
  static const String themeMode = 'theme_mode';
  static const String languageCode = 'language_code';
  static const String currencyCode = 'currency_code';
  static const String dateFormat = 'date_format';
  static const String numberFormat = 'number_format';
  
  // App Settings
  static const String firstTimeUser = 'first_time_user';
  static const String onboardingCompleted = 'onboarding_completed';
  static const String tosAccepted = 'tos_accepted';
  static const String privacyPolicyAccepted = 'privacy_policy_accepted';
  static const String appVersion = 'app_version';
  static const String lastSyncTime = 'last_sync_time';
  
  // Dashboard Settings
  static const String dashboardLayout = 'dashboard_layout';
  static const String hiddenDashboardItems = 'hidden_dashboard_items';
  static const String quickActionsOrder = 'quick_actions_order';
  
  // Cache Settings
  static const String cacheExpiry = 'cache_expiry';
  static const String offlineModeEnabled = 'offline_mode_enabled';
  static const String cacheSize = 'cache_size';
  
  // Feature Flags
  static const String biometricLoginEnabled = 'biometric_login_enabled';
  static const String investmentFeatureEnabled = 'investment_feature_enabled';
  static const String budgetFeatureEnabled = 'budget_feature_enabled';
  static const String advancedAnalyticsEnabled = 'advanced_analytics_enabled';
  
  // Device Information
  static const String deviceId = 'device_id';
  static const String deviceName = 'device_name';
  static const String appInstallId = 'app_install_id';
  static const String lastActiveTime = 'last_active_time';
  
  // Temporary Storage
  static const String tempFormData = 'temp_form_data';
  static const String draftLoanApplication = 'draft_loan_application';
  static const String pendingTransactions = 'pending_transactions';
  
  // Analytics
  static const String analyticsEnabled = 'analytics_enabled';
  static const String crashReportingEnabled = 'crash_reporting_enabled';
  static const String performanceMonitoringEnabled = 'performance_monitoring_enabled';
}
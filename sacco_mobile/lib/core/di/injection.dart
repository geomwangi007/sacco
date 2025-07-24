import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:local_auth/local_auth.dart';
import 'package:logger/logger.dart';

import '../../app/app_config.dart';
import '../network/api_client.dart';
import '../network/interceptors/auth_interceptor.dart';
import '../network/interceptors/logging_interceptor.dart';
import '../network/interceptors/error_interceptor.dart';
import '../storage/secure_storage_service.dart';
import '../storage/local_database_service.dart';
import '../services/auth_service.dart';
import '../services/connectivity_service.dart';
import '../services/biometric_service.dart';
import '../services/notification_service.dart';
import '../services/analytics_service.dart';
import '../services/cache_service.dart';
import '../services/sync_service.dart';

import 'injection.config.dart';

final GetIt getIt = GetIt.instance;

@InjectableInit(
  initializerName: 'init',
  preferRelativeImports: true,
  asExtension: true,
)\nConfigureDependencies configureDependencies() => getIt.init();\n\n@module\nabstract class AppModule {\n  @lazySingleton\n  Logger get logger => Logger(\n    printer: PrettyPrinter(\n      methodCount: 2,\n      errorMethodCount: 8,\n      lineLength: 120,\n      colors: true,\n      printEmojis: true,\n      printTime: true,\n    ),\n  );\n\n  @lazySingleton\n  FlutterSecureStorage get secureStorage => const FlutterSecureStorage(\n    aOptions: AndroidOptions(\n      encryptedSharedPreferences: true,\n    ),\n    iOptions: IOSOptions(\n      accessibility: KeychainAccessibility.first_unlock_this_device,\n    ),\n  );\n\n  @lazySingleton\n  Connectivity get connectivity => Connectivity();\n\n  @lazySingleton\n  LocalAuthentication get localAuth => LocalAuthentication();\n\n  @lazySingleton\n  Dio get dio {\n    final dio = Dio(\n      BaseOptions(\n        baseUrl: AppConfig.baseUrl,\n        connectTimeout: AppConfig.apiTimeout,\n        receiveTimeout: AppConfig.apiTimeout,\n        sendTimeout: AppConfig.apiTimeout,\n        headers: {\n          'Content-Type': 'application/json',\n          'Accept': 'application/json',\n        },\n      ),\n    );\n\n    // Add interceptors in order\n    if (AppConfig.enableLogging) {\n      dio.interceptors.add(LoggingInterceptor(getIt<Logger>()));\n    }\n    \n    dio.interceptors.add(AuthInterceptor(\n      getIt<SecureStorageService>(),\n      getIt<Logger>(),\n    ));\n    \n    dio.interceptors.add(ErrorInterceptor(getIt<Logger>()));\n    \n    return dio;\n  }\n}\n\n/// Initialize all dependencies\nFuture<void> setupDependencies() async {\n  // Initialize Hive for local storage\n  await Hive.initFlutter();\n  \n  // Configure dependencies\n  configureDependencies();\n  \n  // Initialize core services\n  await getIt<LocalDatabaseService>().initialize();\n  await getIt<NotificationService>().initialize();\n  await getIt<AnalyticsService>().initialize();\n  await getIt<CacheService>().initialize();\n  \n  // Start background services\n  getIt<SyncService>().startPeriodicSync();\n}
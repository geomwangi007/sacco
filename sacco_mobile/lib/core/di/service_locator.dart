// lib/core/di/service_locator.dart
import 'package:get_it/get_it.dart';
import 'package:sacco_mobile/core/api/api_client.dart';
import 'package:sacco_mobile/core/services/auth_service.dart';
import 'package:sacco_mobile/core/storage/secure_storage_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:sacco_mobile/core/services/connectivity_service.dart';
import 'package:sacco_mobile/features/auth/repositories/auth_repository.dart';
import 'package:sacco_mobile/features/auth/viewmodels/login_viewmodel.dart';
import 'package:sacco_mobile/features/auth/viewmodels/register_viewmodel.dart';
import 'package:sacco_mobile/features/dashboard/viewmodels/dashboard_viewmodel.dart';
import 'package:sacco_mobile/features/loans/repositories/loan_repository.dart';
import 'package:sacco_mobile/features/loans/viewmodels/loan_list_viewmodel.dart';
import 'package:sacco_mobile/features/loans/viewmodels/loan_application_viewmodel.dart';
import 'package:sacco_mobile/features/loans/viewmodels/loan_repayment_viewmodel.dart';
import 'package:sacco_mobile/features/savings/repositories/savings_repository.dart';
import 'package:sacco_mobile/features/savings/viewmodels/savings_account_viewmodel.dart';
import 'package:sacco_mobile/features/savings/viewmodels/transaction_viewmodel.dart';
import 'package:sacco_mobile/features/profile/repositories/profile_repository.dart';
import 'package:sacco_mobile/features/profile/viewmodels/profile_viewmodel.dart';

// Global instance of GetIt service locator
final GetIt getIt = GetIt.instance;

Future<void> setupServiceLocator() async {
  // Register core services as singletons
  getIt.registerLazySingleton<ConnectivityService>(() => ConnectivityService(Connectivity()));
  getIt.registerLazySingleton<SecureStorageService>(
      () => SecureStorageService(const FlutterSecureStorage()));

  // ApiClient now depends on ConnectivityService for network status
  getIt.registerLazySingleton<ApiClient>(() => ApiClient(
        getIt<ConnectivityService>(),
      ));

  getIt.registerLazySingleton<AuthService>(() => AuthService(
        getIt<ApiClient>(),
        getIt<SecureStorageService>(),
      ));

  // Register repositories
  getIt.registerLazySingleton<AuthRepository>(() => AuthRepository(
        getIt<ApiClient>(),
      ));

  getIt.registerLazySingleton<LoanRepository>(() => LoanRepository(
        getIt<ApiClient>(),
      ));

  getIt.registerLazySingleton<SavingsRepository>(() => SavingsRepository(
        getIt<ApiClient>(),
      ));

  getIt.registerLazySingleton<ProfileRepository>(() => ProfileRepository(
        getIt<ApiClient>(),
      ));

  // Register view models as factories (created anew each time)
  getIt.registerFactory<LoginViewModel>(() => LoginViewModel(
        getIt<AuthRepository>(),
        getIt<AuthService>(),
        getIt<ConnectivityService>(),
      ));

  getIt.registerFactory<RegisterViewModel>(() => RegisterViewModel(
        getIt<AuthRepository>(),
        getIt<AuthService>(),
      ));

  getIt.registerFactory<DashboardViewModel>(() => DashboardViewModel(
        getIt<AuthService>(),
        getIt<SavingsRepository>(),
        getIt<LoanRepository>(),
      ));

  getIt.registerFactory<LoanListViewModel>(() => LoanListViewModel(
        getIt<LoanRepository>(),
      ));

  getIt
      .registerFactory<LoanApplicationViewModel>(() => LoanApplicationViewModel(
            getIt<LoanRepository>(),
          ));

  getIt.registerFactory<LoanRepaymentViewModel>(() => LoanRepaymentViewModel(
        getIt<LoanRepository>(),
      ));

  getIt.registerFactory<SavingsAccountViewModel>(() => SavingsAccountViewModel(
        getIt<SavingsRepository>(),
      ));

  getIt.registerFactory<TransactionViewModel>(() => TransactionViewModel(
        getIt<SavingsRepository>(),
      ));

  getIt.registerFactory<ProfileViewModel>(() => ProfileViewModel(
        getIt<ProfileRepository>(),
      ));
}

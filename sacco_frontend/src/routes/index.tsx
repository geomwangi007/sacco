// AppRoutes.tsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import PrivateRoute from "./PrivateRoute";
import PublicRoute from "./PublicRoute";

// Import our new Dashboard Layout
import SaccoDashboardLayout from "@/layouts/SaccoDashboardLayout";
import AuthLayout from "@/layouts/AuthLayout";

// Auth Pages
import Login from "@/pages/auth/Login";
import Register from "@/pages/auth/Register";
// import ForgotPassword from '@/pages/auth/ForgotPassword';

// Dashboard Pages
import Dashboard from "@/pages/dashboard/Dashboard";

// Member Pages
import MembersList from "@/pages/members/MembersList";
import MemberProfile from '@/pages/members/MemberProfile';
import AddMember from '@/pages/members/AddMember';

// Loan Pages
import LoansList from "@/pages/loans/LoansList";
import LoanDetails from "@/pages/loans/LoanDetails";
import ApplyLoan from "@/pages/loans/ApplyLoan";

// Savings Pages
import SavingsAccounts from '@/pages/savings/SavingsAccounts';
// import AccountDetails from '@/pages/savings/AccountDetails';
// import MakeTransaction from '@/pages/savings/MakeTransaction';

// Transaction Pages
import TransactionHistory from '@/pages/transactions/TransactionHistory';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Authentication Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute restricted>
            <AuthLayout
              title="SACCO Management"
              subtitle="Access your cooperative banking platform"
            >
              <Login />
            </AuthLayout>
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute restricted>
            <AuthLayout
              title="Create an Account"
              subtitle="Join our cooperative banking platform"
              isRegister
            >
              <Register />
            </AuthLayout>
          </PublicRoute>
        }
      />
      {/* <Route
        path="/forgot-password"
        element={
          <PublicRoute restricted>
            <AuthLayout>
              <ForgotPassword />
            </AuthLayout>
          </PublicRoute>
        }
      /> */}

      {/* Protected Routes - Using our SaccoDashboardLayout with Outlet */}
      <Route
        element={
          <PrivateRoute>
            <SaccoDashboardLayout />
          </PrivateRoute>
        }
      >
        {/* Dashboard */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Member Routes */}
        <Route path="/members" element={<MembersList />} />
        <Route path="/members/add" element={<AddMember />} />
        <Route path="/members/:id" element={<MemberProfile />} />

        {/* Loan Routes */}
        <Route path="/loans" element={<LoansList />} />
        <Route path="/loans/apply" element={<ApplyLoan />} />
        <Route path="/loans/:id" element={<LoanDetails />} />

        {/* Savings Routes */}
        <Route path="/savings" element={<SavingsAccounts />} />
        {/* <Route path="/savings/:id" element={<AccountDetails />} /> */}
        {/* <Route path="/savings/:id/transaction" element={<MakeTransaction />} /> */}

        {/* Transaction Routes */}
        <Route path="/transactions" element={<TransactionHistory />} />

        {/* Add placeholder routes for other sections used in the sidebar */}
        <Route path="/reports" element={<ComingSoon title="Reports" />} />
        <Route path="/meetings" element={<ComingSoon title="Meetings" />} />
        <Route path="/documents" element={<ComingSoon title="Documents" />} />
        <Route path="/partners" element={<ComingSoon title="Partners" />} />
        <Route path="/profile" element={<ComingSoon title="Profile" />} />
        <Route path="/settings" element={<ComingSoon title="Settings" />} />
        <Route path="/help" element={<ComingSoon title="Help Center" />} />
      </Route>

      {/* 404 Catch-all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

// Temporary component for routes that haven't been implemented yet
const ComingSoon: React.FC<{ title: string }> = ({ title }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '70vh',
      textAlign: 'center'
    }}>
      <h2 style={{ color: '#1e5631', marginBottom: '16px' }}>{title}</h2>
      <p style={{ color: '#666', fontSize: '18px' }}>This feature is coming soon!</p>
      <div style={{
        marginTop: '24px',
        padding: '16px 32px',
        backgroundColor: 'rgba(30, 86, 49, 0.1)',
        borderRadius: '8px',
        maxWidth: '500px'
      }}>
        <p>We're currently working on building this section to provide you with even more features to manage your SACCO efficiently.</p>
      </div>
    </div>
  );
};

export default AppRoutes;
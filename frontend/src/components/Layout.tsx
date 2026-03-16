import React, { useState } from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import {
  HomeIcon,
  ChartBarIcon,
  ClockIcon,
  CogIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ShieldCheckIcon,
  SunIcon,
  MoonIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';

export const Layout: React.FC = () => {
  const { user, logout, usageInfo } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/app/dashboard', icon: HomeIcon },
    { name: 'Process Audio', href: '/app/process', icon: ChartBarIcon },
    { name: 'History', href: '/app/history', icon: ClockIcon },
    { name: 'Subscription', href: '/app/subscription', icon: CogIcon },
    { name: 'Profile', href: '/app/profile', icon: UserIcon },
    { name: 'About', href: '/app/about', icon: InformationCircleIcon },
  ];

  if (user?.role === 'admin') {
    navigation.push({
      name: 'Admin',
      href: '/app/admin',
      icon: ShieldCheckIcon,
    });
  }

  const isCurrentPath = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and Brand */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">SC</span>
                </div>
                <span className="text-lg font-semibold text-gray-900">Speech Clarity</span>
              </div>
            </div>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex md:items-center md:gap-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isCurrent = isCurrentPath(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
                      transition-colors duration-200
                      ${isCurrent
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>

            {/* Right side - Theme, Usage, User */}
            <div className="flex items-center gap-3">
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors duration-200"
                title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
              >
                {theme === 'light' ? (
                  <MoonIcon className="w-5 h-5" />
                ) : (
                  <SunIcon className="w-5 h-5" />
                )}
              </button>

              {/* Usage indicator - Desktop */}
              {usageInfo && !usageInfo.is_premium && (
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 border border-gray-200">
                  <span className="text-sm text-gray-700">
                    <span className="font-semibold text-gray-900">{usageInfo.remaining_uses}</span> uses left
                  </span>
                </div>
              )}
              
              {/* Premium badge */}
              {usageInfo?.is_premium && (
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-yellow-50 border border-yellow-200">
                  <span className="text-sm font-semibold text-yellow-700">Premium</span>
                </div>
              )}
              
              {/* User menu - Desktop */}
              <div className="hidden md:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-gray-100 border border-gray-200">
                <div className="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center text-white font-semibold text-sm">
                  {user?.name?.charAt(0).toUpperCase()}
                </div>
                <span className="text-sm text-gray-900 font-medium">{user?.name}</span>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-lg text-gray-600 hover:text-red-600 hover:bg-gray-200 transition-colors duration-200"
                  title="Logout"
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5" />
                </button>
              </div>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors duration-200"
              >
                {mobileMenuOpen ? (
                  <XMarkIcon className="w-6 h-6" />
                ) : (
                  <Bars3Icon className="w-6 h-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-4 pt-2 pb-3 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isCurrent = isCurrentPath(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center gap-3 px-4 py-3 rounded-lg text-base font-medium
                      transition-colors duration-200
                      ${isCurrent
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
            
            {/* Mobile user info */}
            <div className="px-4 py-4 border-t border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gray-900 flex items-center justify-center text-white font-semibold">
                    {user?.name?.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-gray-900">{user?.name}</div>
                    <div className="text-xs text-gray-500">{user?.email}</div>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-lg text-gray-600 hover:text-red-600 hover:bg-gray-100 transition-colors duration-200"
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5" />
                </button>
              </div>
              
              {usageInfo && !usageInfo.is_premium && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 border border-gray-200">
                  <span className="text-sm text-gray-700">
                    <span className="font-semibold text-gray-900">{usageInfo.remaining_uses}</span> uses remaining
                  </span>
                </div>
              )}
              
              {usageInfo?.is_premium && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-50 border border-yellow-200">
                  <span className="text-sm font-semibold text-yellow-700">Premium Member</span>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Page content */}
      <main>
        <div className="py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
};

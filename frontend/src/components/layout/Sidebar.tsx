import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar() {
  const location = useLocation();
  const { user } = useAuth();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: '📊',
      roles: ['admin', 'trabajador', 'cliente'],
    },
    {
      name: 'Habitaciones',
      path: '/rooms',
      icon: '🏨',
      roles: ['admin', 'trabajador'],
    },
    {
      name: 'Reservas',
      path: '/bookings',
      icon: '📅',
      roles: ['admin', 'trabajador', 'cliente'],
    },
    {
      name: 'Usuarios',
      path: '/users',
      icon: '👥',
      roles: ['admin'],
    },
  ];

  const filteredNavItems = navItems.filter(item => 
    user && item.roles.includes(user. role)
  );

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold">🏨 Metrics Hotel</h1>
        <p className="text-sm text-gray-400 mt-1">Sistema de Gestión</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {filteredNavItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
              ${isActive(item.path)
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }
            `}
          >
            <span className="text-xl">{item.icon}</span>
            <span className="font-medium">{item.name}</span>
          </Link>
        ))}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
            <span className="text-lg">👤</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.nombre_completo}</p>
            <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
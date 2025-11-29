import { useEffect, useState } from 'react';
import { metricsService } from '../../services/metrics.service';
import type { DashboardMetrics } from '../../types';
import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/ui/Card';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await metricsService. getDashboard();
      setMetrics(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al cargar métricas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Cargando métricas...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Título */}
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Período: {new Date(metrics?.periodo. fecha_inicio || ''). toLocaleDateString()} - {new Date(metrics?.periodo.fecha_fin || '').toLocaleDateString()}
          </p>
        </div>

        {/* Métricas de Habitaciones */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">📊 Habitaciones</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Total Habitaciones</p>
                <p className="text-4xl font-bold text-blue-600 mt-2">
                  {metrics?.habitaciones.total || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Disponibles</p>
                <p className="text-4xl font-bold text-green-600 mt-2">
                  {metrics?.habitaciones.disponibles || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Ocupadas</p>
                <p className="text-4xl font-bold text-orange-600 mt-2">
                  {metrics?.habitaciones. ocupadas || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Tasa de Ocupación</p>
                <p className="text-4xl font-bold text-purple-600 mt-2">
                  {metrics?.habitaciones.tasa_ocupacion. toFixed(1) || 0}%
                </p>
              </div>
            </Card>
          </div>
        </div>

        {/* Métricas de Reservas */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">📅 Reservas</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Total</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  {metrics?.reservas. total || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Pendientes</p>
                <p className="text-3xl font-bold text-yellow-600 mt-2">
                  {metrics?.reservas. pendientes || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Confirmadas</p>
                <p className="text-3xl font-bold text-green-600 mt-2">
                  {metrics?.reservas.confirmadas || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Completadas</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  {metrics?.reservas. completadas || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Canceladas</p>
                <p className="text-3xl font-bold text-red-600 mt-2">
                  {metrics?. reservas.canceladas || 0}
                </p>
              </div>
            </Card>
          </div>
        </div>

        {/* Métricas de Ingresos */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">💰 Ingresos</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Ingresos Totales</p>
                <p className="text-4xl font-bold text-green-600 mt-2">
                  ${metrics?.ingresos.totales. toLocaleString() || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Ingresos Proyectados</p>
                <p className="text-4xl font-bold text-blue-600 mt-2">
                  ${metrics?.ingresos.proyectados.toLocaleString() || 0}
                </p>
              </div>
            </Card>
          </div>
        </div>

        {/* Clientes */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">👥 Clientes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Total Clientes</p>
                <p className="text-4xl font-bold text-blue-600 mt-2">
                  {metrics?.clientes. total || 0}
                </p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <p className="text-sm text-gray-600">Nuevos en el Período</p>
                <p className="text-4xl font-bold text-green-600 mt-2">
                  {metrics?. clientes.nuevos_periodo || 0}
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
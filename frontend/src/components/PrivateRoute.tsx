import { Navigate, Outlet, useLocation } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export const PrivateRoute = () => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Если еще идет проверка токена (loading = true), ничего не рендерим или показываем спиннер
  if (loading) {
    return <p>Загрузка...</p>; 
  }

  return (
    isAuthenticated === true ?
      <Outlet /> :
      <Navigate to="/login" state={{ from: location }} replace />
  );
};

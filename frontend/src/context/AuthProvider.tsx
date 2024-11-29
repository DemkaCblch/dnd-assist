import { createContext, useState, useEffect } from "react";

// Определяем тип контекста
type AuthContextType = {
  isAuthenticated: boolean;
  setAuth: (auth: boolean) => void;
  logout: () => void; // Функция для выхода из системы
};

// Создаем контекст с начальными значениями по умолчанию
const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  setAuth: () => {},
  logout: () => {},
});

// Провайдер авторизации
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Восстанавливаем авторизацию из localStorage при загрузке
  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  // Функция для установки авторизации
  const setAuth = (auth: boolean) => {
    if (auth) {
     // Замените на реальный токен
    } else {
      localStorage.removeItem("authToken");
    }
    setIsAuthenticated(auth);
  };

  // Функция для выхода
  const logout = () => {
    localStorage.removeItem("authToken");
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, setAuth, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

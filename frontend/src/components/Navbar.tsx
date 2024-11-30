import { Link } from 'react-router-dom'
import useAuth from '../hooks/useAuth'
import './Navbar.css'


function Navbar() {
  const { isAuthenticated } = useAuth()
  return (
    <>
      <nav>
      <div className="nav-left">
        {/* Иконка сайта слева */}
        <Link to="/">
          <img src= "/imgs/icon.png" className="site-icon" />
        </Link>
      </div>
      <div className="nav-right">
        <Link to="/admin">
          <img src="/assets/icons/admin-icon.png" className="icon" /> Admin
        </Link>
        <Link to="/characters"> Characters</Link>
        {isAuthenticated ? (
          <Link to="/logout">
            <img src="/assets/icons/logout-icon.png" className="icon" /> Выйти
          </Link>
        ) : (
          <Link to="/login">
            <img src="/assets/icons/login-icon.png" className="icon" /> Войти
          </Link>
        )}
        </div>
      </nav>
    </>
  )
}

export default Navbar
import './Main.css'
import { Link, useNavigate} from 'react-router-dom'
import useAuth from '../hooks/useAuth'

const Main = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth()
  const handleCreateRoom = () => {
    isAuthenticated ?(
      console.log("Создать комнату")
    ):(
    navigate('/login')
  );
    // Навигация на страницу создания комнаты
  };

  const handleJoinRoom = () => {
    isAuthenticated ?(
      console.log("Присоеденится к комнате")
    ):(
    navigate('/login')
  );
    // Навигация на страницу присоединения
  };  
  
  return (
      <div className="MainBase">
        <header className="header">
          <h1 className="title">Добро пожаловать на D&D-Assist</h1>
            <p className="description">
               Создавайте и играйте в Dungeons & Dragons с друзьями онлайн. Быстро, удобно, увлекательно!
            </p>
         </header>
        <div className="buttons-container">
            <button className="btn create-room" onClick={handleCreateRoom}>
                Создать комнату
             </button>
            <button className="btn join-room" onClick={handleJoinRoom}>
                Присоединиться к комнате
              </button>
        </div>  
      </div>
      
    )
  }
  
  export default Main
  
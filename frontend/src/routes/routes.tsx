import { Route, Routes } from 'react-router-dom';
import { PrivateRoute } from '../components/PrivateRoute';
import Main from '../pages/Main';
import Login from '../pages/Login';
import Admin from '../pages/Admin';
import Logout from '../pages/Logout';
import Chars from '../pages/Characters';
import Lobby from '../pages/Lobby';
import GameField from '../pages/GameField';
import Profile from '../pages/Characters';

export const useRoutes = () => {

  return (
    <Routes>
      <Route index element={<Main />} />
      <Route path="/" element={<Main />} />
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Chars />} />
      <Route path="/field" element={<GameField />}/>
      
      <Route element={<PrivateRoute />}>
        <Route path='/admin' element={<Admin />} />
        <Route path='/profile' element={<Profile/>} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/lobby/:id" element={<Lobby />} />
      </Route>

    </Routes>
  )
}

export default useRoutes

import Navbar from './components/Navbar';
import useRoutes from './routes/routes';
import Footer from './components/Footer';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import './App.css'

const App = () => {
  const routes = useRoutes()

  return (
    <div className='Page'>
      <AuthProvider>
        <Navbar />
        {routes}
        <Footer />
      </AuthProvider>
    </div>
   
  )
};

export default App;
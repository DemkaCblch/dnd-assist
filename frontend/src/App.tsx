import Navbar from './components/Navbar';
import useRoutes from './routes/routes';
import Footer from './components/Footer';
import './App.css'

const App = () => {
  const routes = useRoutes()

  return (
    <div className='Page'>
      <Navbar />
      {routes}
      <Footer />
    </div>
   
  )
};

export default App;
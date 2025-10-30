import { Switch, Route } from 'wouter';
import './App.css';
import Navigation from './components/Navigation.tsx';
import Dashboard from './pages/Dashboard.tsx';
import About from './pages/About.tsx';
import NotFound from './pages/not-found.tsx';

function App() {
  return (
    <div className="app">
      <Navigation />
      <main>
        <Switch>
          <Route path="/" component={Dashboard} />
          <Route path="/about" component={About} />
          <Route component={NotFound} />
        </Switch>
      </main>
    </div>
  );
}

export default App;
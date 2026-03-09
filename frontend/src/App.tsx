import { useState } from 'react'
import logo from './assets/logo.png'
import './App.css'
import HelloCard from './components/HelloCard'
import CitiesCard from './components/GetCities'
import CityLookup from './components/CityLookup'
import SalaryCalculator from './components/SalaryCalculator'
import SetPopulation from './components/SetPopulation'
// Main application shell component
function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <img src={logo} className="logo" alt="Site logo" />
      </div>
      <h1>LiveWhere</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <HelloCard />
      <CitiesCard />
      <CityLookup />
      <SalaryCalculator />
      <SetPopulation />
    </>
  )
}

export default App

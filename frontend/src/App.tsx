import { useState } from 'react'
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

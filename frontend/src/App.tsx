import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import HelloCard from './components/HelloCard'
import CitiesCard from './components/GetCities'
import CityLookup from './components/CityLookup'
import SalaryCalculator from './components/SalaryCalculator'

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
     
    </>
  )
}

export default App

<<<<<<< HEAD
import { useState, useEffect } from 'react'
=======
import { useState } from 'react'
import logo from './assets/logo.png'
>>>>>>> 0170bae0847e2a9452040189dc0b66d3e24265e4
import './App.css'
import CityMap from './components/CityMap'
import CityComparison from './components/CityComparison'
import SalaryCalculator from './components/SalaryCalculator'
import CitiesCard from './components/GetCities'
<<<<<<< HEAD

interface City {
  name: string;
  state_code?: string;
  population?: number;
  lat?: number;
  lng?: number;
}

// Main application shell component - LiveWhere Cost of Living Tool
=======
import CityLookup from './components/CityLookup'
import SalaryCalculator from './components/SalaryCalculator'
import SetPopulation from './components/SetPopulation'
// Main application shell component
>>>>>>> 0170bae0847e2a9452040189dc0b66d3e24265e4
function App() {
  const [cities, setCities] = useState<City[]>([]);
  const [selectedCities, setSelectedCities] = useState<City[]>([]);

  // Fetch cities from backend
  useEffect(() => {
    // TODO: Replace with actual API call
    const mockCities: City[] = [
      { name: 'New York', state_code: 'NY', population: 8336817, lat: 40.7128, lng: -74.0060 },
      { name: 'Los Angeles', state_code: 'CA', population: 3979576, lat: 34.0522, lng: -118.2437 },
      { name: 'Chicago', state_code: 'IL', population: 2693976, lat: 41.8781, lng: -87.6298 },
      { name: 'Houston', state_code: 'TX', population: 2320268, lat: 29.7604, lng: -95.3698 },
      { name: 'Austin', state_code: 'TX', population: 978908, lat: 30.2672, lng: -97.7431 },
    ];
    setCities(mockCities);
  }, []);

  const handleCitySelect = (city: City) => {
    // Add city to comparison if not already selected (max 4 cities)
    if (selectedCities.length < 4 && !selectedCities.find(c => c.name === city.name)) {
      setSelectedCities([...selectedCities, city]);
    }
  };

  const clearSelection = () => {
    setSelectedCities([]);
  };

  return (
<<<<<<< HEAD
    <div style={{ padding: '20px' }}>
      <h1>LiveWhere — Cost of Living Comparison Tool</h1>
      <p>Compare cities, calculate salary adjustments, and find your ideal location</p>

      <div style={{ marginBottom: '30px' }}>
        <h2>Interactive City Map</h2>
        <p>Click on markers to select cities for comparison (max 4)</p>
        <CityMap cities={cities} onCitySelect={handleCitySelect} />
        {selectedCities.length > 0 && (
          <button
            onClick={clearSelection}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Clear Selection
          </button>
        )}
      </div>

      <div style={{ marginBottom: '30px' }}>
        <CityComparison cities={selectedCities} />
      </div>

      <div style={{ marginBottom: '30px' }}>
        <SalaryCalculator />
      </div>

      <div style={{ marginBottom: '30px' }}>
        <h2>All Cities Data</h2>
        <CitiesCard />
      </div>
    </div>
=======
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
>>>>>>> 0170bae0847e2a9452040189dc0b66d3e24265e4
  )
}

export default App

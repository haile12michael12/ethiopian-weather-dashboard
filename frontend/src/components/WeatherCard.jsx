import './WeatherCard.css';

const WeatherCard = ({ data }) => {
  const {
    City,
    MinTempD1, MaxTempD1, WeatherConditionD1,
    MinTempD2, MaxTempD2, WeatherConditionD2,
    MinTempD3, MaxTempD3, WeatherConditionD3
  } = data;

  // Simple function to get weather icon based on condition
  const getWeatherIcon = (condition) => {
    if (!condition) return '☀️';
    
    const conditionLower = condition.toLowerCase();
    if (conditionLower.includes('sun')) return '☀️';
    if (conditionLower.includes('cloud')) return '☁️';
    if (conditionLower.includes('rain')) return '🌧️';
    if (conditionLower.includes('hot')) return '🔥';
    return '☀️'; // default
  };

  return (
    <div className="weather-card">
      <h2>{City}</h2>
      <div className="forecast-container">
        <div className="forecast-day">
          <h3>Day 1</h3>
          <div className="weather-icon">{getWeatherIcon(WeatherConditionD1)}</div>
          <div className="temperature">
            <span className="temp-max">{MaxTempD1}°C</span>
            <span className="temp-min">{MinTempD1}°C</span>
          </div>
          <div className="condition">{WeatherConditionD1}</div>
        </div>
        
        <div className="forecast-day">
          <h3>Day 2</h3>
          <div className="weather-icon">{getWeatherIcon(WeatherConditionD2)}</div>
          <div className="temperature">
            <span className="temp-max">{MaxTempD2}°C</span>
            <span className="temp-min">{MinTempD2}°C</span>
          </div>
          <div className="condition">{WeatherConditionD2}</div>
        </div>
        
        <div className="forecast-day">
          <h3>Day 3</h3>
          <div className="weather-icon">{getWeatherIcon(WeatherConditionD3)}</div>
          <div className="temperature">
            <span className="temp-max">{MaxTempD3}°C</span>
            <span className="temp-min">{MinTempD3}°C</span>
          </div>
          <div className="condition">{WeatherConditionD3}</div>
        </div>
      </div>
    </div>
  );
};

export default WeatherCard;
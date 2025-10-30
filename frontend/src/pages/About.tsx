import React from 'react';

const About: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">About Ethiopian Weather Dashboard</h1>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
        <p className="mb-4">
          The Ethiopian Weather Dashboard provides up-to-date weather information for major cities across Ethiopia.
          Our service helps residents and visitors plan their activities based on accurate weather forecasts.
        </p>
        <p className="mb-4">
          Ethiopia's diverse climate zones, from the cool highlands to the hot lowlands, make weather information
          crucial for agriculture, transportation, and daily life.
        </p>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-3">Ethiopian Climate Zones</h2>
        <ul className="list-disc pl-5 mb-4">
          <li className="mb-2"><strong>Dega (Highlands)</strong>: Above 2,400 meters with cool temperatures averaging 10-16°C</li>
          <li className="mb-2"><strong>Weyna Dega (Midlands)</strong>: Between 1,500-2,400 meters with moderate temperatures of 16-25°C</li>
          <li className="mb-2"><strong>Kolla (Lowlands)</strong>: Below 1,500 meters with hot temperatures ranging from 25-35°C</li>
        </ul>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-3">Features</h2>
        <ul className="list-disc pl-5 mb-4">
          <li className="mb-2">Three-day weather forecasts for major Ethiopian cities</li>
          <li className="mb-2">Temperature, humidity, and precipitation data</li>
          <li className="mb-2">Interactive map view showing regional variations</li>
          <li className="mb-2">Seasonal weather patterns information</li>
        </ul>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-3">Understanding Ethiopian Seasons</h2>
        <p className="mb-3">
          Ethiopia experiences distinct seasons that affect agricultural cycles and daily life:
        </p>
        <ul className="list-disc pl-5 mb-4">
          <li className="mb-2"><strong>Bega (Heavy Rains)</strong>: October to January - Heavy rainfall season</li>
          <li className="mb-2"><strong>Belg (Short Rains)</strong>: February to May - Short rainy season</li>
          <li className="mb-2"><strong>Derere (Dry Season)</strong>: June to September - Dry and warm conditions</li>
        </ul>
      </div>
    </div>
  );
};

export default About;
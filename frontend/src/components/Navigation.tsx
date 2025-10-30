import React from 'react';
import { Link } from 'wouter';

const Navigation: React.FC = () => {
  return (
    <nav className="bg-blue-600 dark:bg-blue-800 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/">
          <span className="text-white text-xl font-bold cursor-pointer">Ethiopian Weather</span>
        </Link>
        <div className="space-x-4">
          <Link href="/">
            <span className="text-white hover:text-blue-200 cursor-pointer">Dashboard</span>
          </Link>
          <Link href="/about">
            <span className="text-white hover:text-blue-200 cursor-pointer">About</span>
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
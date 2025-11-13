import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import DomainList from "./components/DomainList";
import GlossaryList from "./components/GlossaryList";

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="max-w-6xl mx-auto p-6 space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-blue-700">
          🏢 Business Glossary Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          Explore business domains and glossary terms extracted from your documents.
        </p>
      </header>
      <DomainList />
      <GlossaryList />
    </div>
    </>
  )
}

export default App

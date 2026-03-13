import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@styles/index3.css'
import App from '@pages/App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter } from 'react-router-dom'
import QueryProvider from './providers/QueryProvider.tsx'
import { AuthProvider } from './providers/AuthProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <QueryProvider>
        {/* <AuthProvider> */}
          <App />

        {/* </AuthProvider> */}
      </QueryProvider>
    </BrowserRouter>
  </StrictMode>
)

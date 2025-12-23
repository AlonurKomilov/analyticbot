import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import PublicLayout from './layouts/PublicLayout'
import HomePage from './pages/HomePage'
import ChannelPage from './pages/ChannelPage'
import CategoryPage from './pages/CategoryPage'
import SearchPage from './pages/SearchPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<PublicLayout />}>
          <Route index element={<HomePage />} />
          <Route path="channel/:username" element={<ChannelPage />} />
          <Route path="category/:slug" element={<CategoryPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </>
  )
}

export default App

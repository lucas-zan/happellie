import { Route, Routes } from 'react-router-dom';
import { AdminPage } from './pages/AdminPage';
import { HomePage } from './pages/HomePage';
import { LessonPage } from './pages/LessonPage';
import { PetPage } from './pages/PetPage';
import { AppLayout } from './layout/AppLayout';

export function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/lesson" element={<LessonPage />} />
        <Route path="/pet" element={<PetPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </AppLayout>
  );
}

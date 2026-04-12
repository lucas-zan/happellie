import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../utils/cn';

const navItems = [
  { to: '/', label: 'Home', caption: 'overview' },
  { to: '/lesson', label: 'Lesson', caption: 'learn' },
  { to: '/pet', label: 'Pet', caption: 'care' },
  { to: '/admin', label: 'Admin', caption: 'measure' },
];

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="app-brand">
          <span className="app-brand__eyebrow">HappyEllie</span>
          <h1 className="app-brand__title">Pet-first English</h1>
          <p className="app-brand__description">
            A tiny learning game with a reusable design system for lesson, pet, and analytics views.
          </p>
        </div>
        <nav className="app-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => cn('app-nav__link', isActive && 'app-nav__link--active')}
            >
              <span className="app-nav__label">{item.label}</span>
              <span className="app-nav__caption">{item.caption}</span>
            </NavLink>
          ))}
        </nav>
        <div className="app-sidebar__footer">
          <strong>Local-first prototype</strong>
          <span>React UI + Python agent + SQLite</span>
        </div>
      </aside>
      <main className="page-shell">{children}</main>
    </div>
  );
}

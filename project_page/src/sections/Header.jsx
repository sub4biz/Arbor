import { useEffect, useState } from 'react';

const NAV = [
  { id: 'method', label: 'Method' },
  { id: 'results', label: 'Results' },
  { id: 'case', label: 'Case Study' },
  { id: 'resources', label: 'Resources' },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState('');

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    const sections = NAV.map((n) => document.getElementById(n.id)).filter(Boolean);
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: '-30% 0px -55% 0px', threshold: [0.08, 0.25, 0.5] }
    );
    sections.forEach((s) => obs.observe(s));
    return () => obs.disconnect();
  }, []);

  return (
    <header className={`site-header${scrolled ? ' scrolled' : ''}`}>
      <a className="brand" href="#top" aria-label="Arbor home">
        <img src="assets/images/arbor-logo.png" alt="Arbor" />
      </a>
      <nav className="nav" aria-label="Sections">
        {NAV.map((n) => (
          <a key={n.id} href={`#${n.id}`} className={active === n.id ? 'active' : undefined}>
            {n.label}
          </a>
        ))}
        <a href="docs/">Docs</a>
      </nav>
      <a className="header-cta" href="https://github.com/RUC-NLPIR/Arbor" target="_blank" rel="noreferrer">
        <span>Star on</span> GitHub
      </a>
    </header>
  );
}

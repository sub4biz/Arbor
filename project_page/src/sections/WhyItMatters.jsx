import SpotlightCard from '../bits/SpotlightCard.jsx';
import Reveal from '../components/Reveal.jsx';

const ITEMS = [
  {
    n: '01',
    t: 'Understanding deepens, not just scores',
    d: 'Early branches test whether a broad mechanism holds; later ones probe where it breaks; ancestor insights compress every finding into constraints that shape the next round of hypotheses.',
  },
  {
    n: '02',
    t: 'Each experiment de-randomizes the next',
    d: "Arbor's best candidates arrive mid-to-late, conditioned on accumulated evidence. The same compute buys a less repetitive, more constrained search — not a longer gamble on stumbling into a result.",
  },
  {
    n: '03',
    t: 'Ideas are evidence-conditioned, not guesses',
    d: 'Each proposal is a local, executable move that answers an earlier failure — turning a half-right result into the next hypothesis instead of a reason to abandon the direction.',
  },
];

export default function WhyItMatters() {
  return (
    <section className="section" aria-label="Why it matters">
      <div className="container">
        <div className="split">
          <Reveal>
            <div>
              <span className="kicker">Why It Matters</span>
              <h2>Autonomous research that compounds.</h2>
              <p className="lead">
                Across Arbor's traces, what gets ruled out, validated, or shown to have
                boundary conditions becomes a prior on the next proposal. The result is a
                process that makes research cumulative — not more attempts, but less
                repetitive, more memory-aware search.
              </p>
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="why-list">
              {ITEMS.map((i) => (
                <SpotlightCard key={i.n} className="tile" spotlightColor="rgba(110, 168, 255, 0.16)">
                  <span className="why-num">{i.n}</span>
                  <div>
                    <h3>{i.t}</h3>
                    <p>{i.d}</p>
                  </div>
                </SpotlightCard>
              ))}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

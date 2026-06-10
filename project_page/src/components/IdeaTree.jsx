import Reveal from './Reveal.jsx';

// Hypothesis-exploration trace from the BrowseComp run (dev-set, 40Q bc_val).
// Scores are dev-set iteration scores; baseline 50%, merged trunk 62.5%.
const BASELINE = 50;

const BRANCHES = [
  {
    id: '1',
    score: 42.5,
    status: 'pruned',
    label: 'Track multiple candidates in a PASS / FAIL constraint table',
  },
  {
    id: '2',
    score: 52.5,
    status: 'done',
    label: "Spawn a devil's-advocate agent to rebut the first answer",
  },
  {
    id: '3',
    score: 45,
    status: 'pruned',
    label: 'Enumerate type-anchored candidate lists up front',
  },
  {
    id: '4',
    score: 25,
    status: 'pruned',
    label: 'Decompose into independent sub-questions, then intersect',
  },
  {
    id: '5',
    score: 55,
    status: 'done',
    label: 'Run four independent trajectories + a selecting judge',
    children: [
      { id: '5.1', score: 47.5, status: 'pruned', label: 'Persona-diversified agents (style per trajectory)' },
      { id: '5.2', score: 57.5, status: 'done', label: 'Give the judge its own 8-call search budget' },
      { id: '5.3', score: 52.5, status: 'done', label: 'Fix the "Candidate N" answer-parser bug' },
      {
        id: '5.4',
        score: 62.5,
        status: 'merged',
        win: true,
        label: 'Let the judge search beyond the candidate set (20-step budget)',
      },
    ],
  },
];

const STATUS_LABEL = { merged: 'Merged ★', done: 'Explored', pruned: 'Pruned' };

function scoreClass(score) {
  if (score > BASELINE) return 'sc-up';
  if (score < BASELINE) return 'sc-down';
  return 'sc-mid';
}

function TreeNode({ node }) {
  return (
    <li className="tree-node">
      <div className={`tnode${node.win ? ' win' : ''}`}>
        <span className="tnode-id">{node.id}</span>
        <div className="tnode-body">
          <p className="tnode-label">{node.label}</p>
          <div className="tnode-meta">
            <span className={`tnode-score ${scoreClass(node.score)}`}>{node.score.toFixed(1)}%</span>
            <span className={`tnode-status st-${node.status}`}>{STATUS_LABEL[node.status]}</span>
          </div>
        </div>
      </div>
      {node.children && (
        <ul className="tree-children">
          {node.children.map((c) => (
            <TreeNode key={c.id} node={c} />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function IdeaTree() {
  return (
    <Reveal delay={0.05}>
      <div className="tree-panel">
        <div className="tree-head">
          <div>
            <span className="tree-title">Hypothesis exploration</span>
            <span className="tree-sub">20-cycle BrowseComp run · dev-set scores (40Q)</span>
          </div>
          <div className="tree-runmeta">
            <span><b>9</b> experiments</span>
            <span><b>1</b> merged</span>
            <span><b>3</b> pruned</span>
          </div>
        </div>

        <div className="tree-root">
          <span className="tnode-id root">ROOT</span>
          <div className="tnode-body">
            <p className="tnode-label">BrowseComp ReAct baseline</p>
            <div className="tnode-meta">
              <span className="tnode-score sc-mid">dev 50.0%</span>
              <span className="tree-arrow">→ merged trunk 62.5%</span>
            </div>
          </div>
        </div>

        <ul className="tree-children root-children">
          {BRANCHES.map((n) => (
            <TreeNode key={n.id} node={n} />
          ))}
        </ul>

        <div className="tree-legend">
          <span><i className="dot sc-up" /> above baseline</span>
          <span><i className="dot sc-mid" /> at baseline</span>
          <span><i className="dot sc-down" /> below baseline</span>
        </div>
      </div>
    </Reveal>
  );
}

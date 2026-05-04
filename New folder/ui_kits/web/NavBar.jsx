// NavBar.jsx — SecureConnect sticky glassmorphism navbar
// Exports: NavBar

function NavBar({ screen, setScreen, unreadMsgs = 0, pendingCount = 0 }) {
  const links = [
    { id: 'feed',     label: 'Feed' },
    { id: 'my-posts', label: 'My Posts' },
    { id: 'discover', label: 'Discover' },
    { id: 'messages', label: 'Messages', badge: unreadMsgs },
    { id: 'network',  label: 'Network',  badge: pendingCount },
    { id: 'profile',  label: 'Profile' },
  ];

  return (
    <nav style={{
      background: 'rgba(24,24,27,0.7)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(255,255,255,0.05)',
      padding: '0.9rem 0',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
    }}>
      <div style={{
        maxWidth: 1100,
        margin: '0 auto',
        padding: '0 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        {/* Brand */}
        <div
          onClick={() => setScreen('feed')}
          style={{
            fontWeight: 800,
            fontSize: '1.35rem',
            letterSpacing: '-0.5px',
            background: 'linear-gradient(135deg,#a78bfa,#3b82f6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            cursor: 'pointer',
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="url(#navGrad)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <defs>
              <linearGradient id="navGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#a78bfa" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          SecureConnect
        </div>

        {/* Links */}
        <div style={{ display: 'flex', gap: 4, alignItems: 'center', flexWrap: 'wrap' }}>
          {links.map(l => (
            <a
              key={l.id}
              onClick={() => setScreen(l.id)}
              style={{
                fontSize: '0.88rem',
                fontWeight: 500,
                color: screen === l.id ? '#f4f4f5' : '#a1a1aa',
                padding: '0.45rem 0.9rem',
                borderRadius: 8,
                background: screen === l.id ? 'rgba(255,255,255,0.05)' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                userSelect: 'none',
              }}
            >
              {l.label}
              {l.badge > 0 && (
                <span style={{
                  background: '#ef4444',
                  color: 'white',
                  borderRadius: 9999,
                  fontSize: '0.65rem',
                  fontWeight: 600,
                  padding: '1px 6px',
                  lineHeight: 1.4,
                }}>
                  {l.badge}
                </span>
              )}
            </a>
          ))}
          <a
            onClick={() => setScreen('login')}
            style={{
              fontSize: '0.88rem',
              fontWeight: 700,
              color: '#f87171',
              padding: '0.45rem 0.9rem',
              borderRadius: 8,
              cursor: 'pointer',
              userSelect: 'none',
            }}
          >
            Logout
          </a>
        </div>
      </div>
    </nav>
  );
}

Object.assign(window, { NavBar });

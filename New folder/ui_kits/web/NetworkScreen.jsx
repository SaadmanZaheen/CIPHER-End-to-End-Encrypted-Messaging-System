// NetworkScreen.jsx — Network (friends), Discover people
// Exports: NetworkScreen, DiscoverScreen

const FRIENDS = [
  { id: 2, username: 'alice', initials: 'A' },
  { id: 3, username: 'bob',   initials: 'B' },
];

const PENDING_IN = [
  { id: 5, username: 'eve',   initials: 'E', reqId: 101 },
];

const PENDING_OUT = [
  { id: 6, username: 'frank', initials: 'F' },
];

const ALL_USERS = [
  { id: 2, username: 'alice',  initials: 'A', role: 'user',  status: 'accepted' },
  { id: 3, username: 'bob',    initials: 'B', role: 'user',  status: 'accepted' },
  { id: 4, username: 'carol',  initials: 'C', role: 'admin', status: null },
  { id: 5, username: 'eve',    initials: 'E', role: 'user',  status: 'pending', isRequester: false },
  { id: 6, username: 'frank',  initials: 'F', role: 'user',  status: 'pending', isRequester: true },
  { id: 7, username: 'grace',  initials: 'G', role: 'user',  status: null },
  { id: 8, username: 'hank',   initials: 'H', role: 'user',  status: 'rejected' },
];

function NetworkScreen({ setScreen, setConvFriend }) {
  const [friends, setFriends] = React.useState(FRIENDS);
  const [pendingIn, setPendingIn] = React.useState(PENDING_IN);

  function acceptRequest(reqId, user) {
    setPendingIn(p => p.filter(r => r.reqId !== reqId));
    setFriends(f => [...f, user]);
  }

  function declineRequest(reqId) {
    setPendingIn(p => p.filter(r => r.reqId !== reqId));
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2 style={{ fontWeight: 800, fontSize: '2rem', letterSpacing: '-1px', margin: 0 }}>Your Network</h2>
        <button onClick={() => setScreen('discover')} style={{
          background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
          border: 'none', borderRadius: 9999, color: 'white',
          fontWeight: 600, padding: '0.5rem 1.4rem', fontSize: '0.9rem',
          cursor: 'pointer', fontFamily: 'Inter, sans-serif',
          boxShadow: '0 4px 12px rgba(124,58,237,0.35)',
        }}>Discover</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 24 }}>
        {/* Left: connections */}
        <div>
          <h5 style={{ fontWeight: 700, marginBottom: 14, fontSize: '1rem' }}>Active Connections ({friends.length})</h5>
          {friends.length > 0 ? (
            <div style={{
              background: 'rgba(24,24,27,0.4)',
              border: '1px solid rgba(255,255,255,0.05)',
              borderRadius: 20, overflow: 'hidden',
              marginBottom: 32,
            }}>
              {friends.map((f, i) => (
                <div key={f.id} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '14px 18px',
                  borderBottom: i < friends.length - 1 ? '1px solid rgba(255,255,255,0.03)' : 'none',
                  background: 'rgba(24,24,27,0.6)',
                  transition: 'background 0.2s',
                }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'rgba(24,24,27,0.6)'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 46, height: 46, borderRadius: '50%',
                      background: 'linear-gradient(135deg,#a78bfa,#3b82f6)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 700, color: 'white', fontSize: '1.1rem',
                    }}>{f.initials}</div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '1rem' }}>{f.username}</div>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: 4,
                        background: 'rgba(16,185,129,0.08)', color: '#34d399',
                        fontSize: '0.68rem', fontWeight: 600, padding: '2px 8px', borderRadius: 4, marginTop: 2,
                      }}>
                        <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                        Secure Channel
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => { setConvFriend(f); setScreen('conversation'); }}
                    style={{
                      background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
                      border: 'none', borderRadius: 9999, color: 'white',
                      fontWeight: 600, padding: '0.4rem 1.2rem', fontSize: '0.85rem',
                      cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                    }}>
                    Message
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)',
              borderRadius: 20, padding: '40px 20px', textAlign: 'center', marginBottom: 32,
            }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#a1a1aa" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 12 }}>
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              <h5 style={{ fontWeight: 700, marginBottom: 6 }}>No connections yet</h5>
              <p style={{ fontSize: '0.85rem', color: '#a1a1aa' }}>Build your network to start sharing securely.</p>
            </div>
          )}
        </div>

        {/* Right: pending */}
        <div>
          <h5 style={{ fontWeight: 700, marginBottom: 14, fontSize: '1rem' }}>Pending Requests</h5>
          {pendingIn.length > 0 ? (
            <div style={{
              background: '#18181b',
              border: '1px solid rgba(16,185,129,0.3)',
              borderRadius: 20, overflow: 'hidden', marginBottom: 24,
              boxShadow: '0 0 15px rgba(16,185,129,0.1)',
            }}>
              <div style={{
                padding: '12px 16px',
                background: 'rgba(16,185,129,0.08)',
                borderBottom: '1px solid rgba(16,185,129,0.15)',
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
                <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Needs Review ({pendingIn.length})</span>
              </div>
              {pendingIn.map(r => (
                <div key={r.reqId} style={{
                  padding: '14px 16px',
                  borderTop: '1px solid rgba(255,255,255,0.04)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: '50%', background: '#374151',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 700, color: 'white', fontSize: '0.85rem',
                    }}>{r.initials}</div>
                    <span style={{ fontWeight: 600, fontSize: '0.92rem' }}>{r.username}</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button
                      onClick={() => acceptRequest(r.reqId, r)}
                      style={{
                        flex: 1, background: '#10b981', border: 'none', borderRadius: 8,
                        color: 'white', fontWeight: 600, padding: '0.4rem', fontSize: '0.82rem',
                        cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                      }}>Accept</button>
                    <button
                      onClick={() => declineRequest(r.reqId)}
                      style={{
                        flex: 1, background: 'transparent',
                        border: '1px solid rgba(239,68,68,0.5)',
                        borderRadius: 8, color: '#f87171', fontWeight: 600,
                        padding: '0.4rem', fontSize: '0.82rem',
                        cursor: 'pointer', fontFamily: 'Inter, sans-serif',
                      }}>Decline</button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              border: '1px dashed rgba(255,255,255,0.1)', borderRadius: 20,
              padding: '20px', textAlign: 'center', marginBottom: 24,
            }}>
              <p style={{ fontSize: '0.82rem', color: '#a1a1aa' }}>No incoming requests.</p>
            </div>
          )}

          {PENDING_OUT.length > 0 && (
            <>
              <h5 style={{ fontWeight: 700, marginBottom: 14, fontSize: '1rem', marginTop: 20 }}>Sent Requests</h5>
              <div style={{
                background: 'rgba(24,24,27,0.4)', border: '1px solid rgba(255,255,255,0.05)',
                borderRadius: 20, overflow: 'hidden',
              }}>
                {PENDING_OUT.map((r, i) => (
                  <div key={r.id} style={{
                    display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px',
                    borderBottom: i < PENDING_OUT.length - 1 ? '1px solid rgba(255,255,255,0.03)' : 'none',
                  }}>
                    <div style={{
                      width: 16, height: 16, borderRadius: '50%',
                      border: '2px solid #a1a1aa', borderTopColor: 'transparent',
                      animation: 'spin 1s linear infinite', flexShrink: 0,
                    }} />
                    <span style={{ fontSize: '0.82rem', color: '#a1a1aa' }}>
                      Waiting for <strong style={{ color: '#f4f4f5' }}>{r.username}</strong>
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function DiscoverScreen({ setScreen }) {
  const [users, setUsers] = React.useState(ALL_USERS);

  function sendRequest(id) {
    setUsers(u => u.map(x => x.id === id ? { ...x, status: 'pending', isRequester: true } : x));
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <h2 style={{ fontWeight: 800, fontSize: '2rem', letterSpacing: '-1px', marginBottom: '2rem' }}>Discover People</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
        {users.map(u => (
          <div key={u.id} style={{
            background: 'rgba(24,24,27,0.8)',
            border: '1px solid rgba(255,255,255,0.05)',
            borderRadius: 20, overflow: 'hidden',
            boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
            transition: 'transform 0.3s, box-shadow 0.3s',
          }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 15px 35px rgba(0,0,0,0.3)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)'; }}
          >
            <div style={{ padding: '24px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%',
                background: 'linear-gradient(135deg,#a78bfa,#3b82f6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, color: 'white', fontSize: '1.4rem', marginBottom: 10,
                boxShadow: '0 4px 15px rgba(139,92,246,0.3)',
              }}>{u.initials}</div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: 6 }}>{u.username}</div>
              <div style={{ marginBottom: 14 }}>
                {u.role === 'admin'
                  ? <span style={{ background: 'rgba(234,179,8,0.15)', color: '#facc15', border: '1px solid rgba(234,179,8,0.3)', fontSize: '0.68rem', fontWeight: 600, padding: '2px 8px', borderRadius: 6 }}>Platform Admin</span>
                  : <span style={{ background: 'rgba(255,255,255,0.05)', color: '#a1a1aa', fontSize: '0.68rem', fontWeight: 600, padding: '2px 8px', borderRadius: 6 }}>Creator</span>
                }
              </div>
              <div style={{ width: '100%' }}>
                {u.status === 'accepted' ? (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <span style={{ flex: 1, background: 'rgba(16,185,129,0.1)', color: '#34d399', borderRadius: 12, padding: '0.35rem 0', fontSize: '0.78rem', fontWeight: 600, textAlign: 'center' }}>Connected</span>
                    <button style={{ flex: 1, background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)', border: 'none', borderRadius: 12, color: 'white', fontWeight: 600, padding: '0.35rem 0', fontSize: '0.78rem', cursor: 'pointer', fontFamily: 'Inter,sans-serif' }}>Message</button>
                  </div>
                ) : u.status === 'pending' && u.isRequester ? (
                  <button disabled style={{ width: '100%', background: 'rgba(255,255,255,0.05)', border: 'none', borderRadius: 12, color: '#a1a1aa', fontWeight: 600, padding: '0.4rem', fontSize: '0.82rem', cursor: 'not-allowed', fontFamily: 'Inter,sans-serif' }}>Request Pending</button>
                ) : u.status === 'pending' && !u.isRequester ? (
                  <button style={{ width: '100%', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 12, color: '#34d399', fontWeight: 600, padding: '0.4rem', fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Inter,sans-serif' }}>Review Request</button>
                ) : u.status === 'rejected' ? (
                  <button disabled style={{ width: '100%', background: 'rgba(239,68,68,0.1)', border: 'none', borderRadius: 12, color: '#f87171', fontWeight: 600, padding: '0.4rem', fontSize: '0.82rem', cursor: 'not-allowed', fontFamily: 'Inter,sans-serif' }}>Declined</button>
                ) : (
                  <button onClick={() => sendRequest(u.id)} style={{ width: '100%', background: 'transparent', border: '2px solid #8b5cf6', borderRadius: 12, color: '#8b5cf6', fontWeight: 600, padding: '0.4rem', fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Inter,sans-serif' }}>Connect 🔒</button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

Object.assign(window, { NetworkScreen, DiscoverScreen });

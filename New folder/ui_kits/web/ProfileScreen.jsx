// ProfileScreen.jsx — Profile view + Key Rotation screen
// Exports: ProfileScreen, KeyRotateScreen

const FAKE_RSA_N = '8342913847293847192834719283...';
const FAKE_ECC_X = '7291837462918374629183746291...';

function ProfileScreen({ setScreen }) {
  const [email, setEmail] = React.useState('you@example.com');
  const [contact, setContact] = React.useState('+1 555-0100');
  const [saved, setSaved] = React.useState(false);

  function handleSave(e) {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <h2 style={{ fontWeight: 800, fontSize: '2rem', letterSpacing: '-1px', marginBottom: '2rem' }}>My Profile</h2>

      {saved && (
        <div style={{
          background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)',
          borderRadius: 12, padding: '12px 18px', marginBottom: 20,
          color: '#34d399', fontSize: '0.9rem', fontWeight: 500,
        }}>
          Profile updated.
        </div>
      )}

      <div style={{
        background: '#18181b', border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 20, overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)', padding: '24px',
      }}>
        {/* User info table */}
        <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 24 }}>
          <tbody>
            {[
              ['Username', <span style={{ fontWeight: 600 }}>you</span>],
              ['Role', <span style={{ background: 'rgba(255,255,255,0.06)', color: '#a1a1aa', fontSize: '0.75rem', fontWeight: 600, padding: '3px 10px', borderRadius: 6 }}>user</span>],
              ['Account Integrity', <span style={{ background: 'rgba(16,185,129,0.15)', color: '#34d399', border: '1px solid rgba(16,185,129,0.3)', fontSize: '0.75rem', fontWeight: 600, padding: '3px 10px', borderRadius: 6 }}>MAC Valid ✔</span>],
              ['RSA Public Key (n, e)', <code style={{ color: '#60a5fa', fontFamily: 'monospace', fontSize: '0.78rem' }}>{FAKE_RSA_N.slice(0, 32)}…</code>],
              ['ECC Public Key (x, y)', <code style={{ color: '#60a5fa', fontFamily: 'monospace', fontSize: '0.78rem' }}>{FAKE_ECC_X.slice(0, 32)}…</code>],
            ].map(([label, val], i) => (
              <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <th style={{ padding: '10px 0', fontSize: '0.85rem', fontWeight: 600, color: '#a1a1aa', textAlign: 'left', width: '36%', paddingRight: 16 }}>{label}</th>
                <td style={{ padding: '10px 0', fontSize: '0.88rem' }}>{val}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <hr style={{ borderColor: 'rgba(255,255,255,0.06)', marginBottom: 20 }} />

        {/* Edit form */}
        <h5 style={{ fontWeight: 700, marginBottom: 16, fontSize: '1rem' }}>Edit Email &amp; Contact</h5>
        <form onSubmit={handleSave}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 500, display: 'block', marginBottom: 6 }}>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 12, color: '#f4f4f5', padding: '0.7rem 1rem',
                fontFamily: 'Inter, sans-serif', fontSize: '0.95rem', width: '100%',
                outline: 'none', boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 500, display: 'block', marginBottom: 6 }}>Contact</label>
            <input
              type="text"
              value={contact}
              onChange={e => setContact(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 12, color: '#f4f4f5', padding: '0.7rem 1rem',
                fontFamily: 'Inter, sans-serif', fontSize: '0.95rem', width: '100%',
                outline: 'none', boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <button type="submit" style={{
              background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
              border: 'none', borderRadius: 12, color: 'white',
              fontWeight: 600, padding: '0.6rem 1.5rem', fontSize: '0.92rem',
              cursor: 'pointer', fontFamily: 'Inter, sans-serif',
              boxShadow: '0 4px 15px rgba(124,58,237,0.4)',
            }}>Save Changes</button>
            <button
              type="button"
              onClick={() => setScreen('key-rotate')}
              style={{
                background: 'transparent', border: '2px solid rgba(255,255,255,0.12)',
                borderRadius: 12, color: '#a1a1aa',
                fontWeight: 600, padding: '0.6rem 1.4rem', fontSize: '0.92rem',
                cursor: 'pointer', fontFamily: 'Inter, sans-serif',
              }}
            >
              Rotate Keys
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function KeyRotateScreen({ setScreen }) {
  const [rotated, setRotated] = React.useState(false);
  const history = [
    { id: 1, rotated_at: '2026-04-01 10:12:00', rsa_pub_preview: '7382918…', ecc_pub_preview: '6291847…' },
    { id: 2, rotated_at: '2026-03-15 08:45:00', rsa_pub_preview: '1234567…', ecc_pub_preview: '9876543…' },
  ];

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: '2rem' }}>
        <button onClick={() => setScreen('profile')} style={{
          background: 'transparent', border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: 8, color: '#a1a1aa', fontSize: '0.82rem',
          padding: '0.35rem 0.9rem', cursor: 'pointer', fontFamily: 'Inter, sans-serif',
        }}>← Back</button>
        <h2 style={{ fontWeight: 800, fontSize: '1.6rem', letterSpacing: '-0.5px', margin: 0 }}>Key Rotation</h2>
      </div>

      {rotated && (
        <div style={{
          background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)',
          borderRadius: 12, padding: '12px 18px', marginBottom: 20,
          color: '#34d399', fontSize: '0.9rem', fontWeight: 500,
        }}>
          Keypairs rotated successfully. New session token issued.
        </div>
      )}

      <div style={{
        background: '#18181b', border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 20, padding: '24px', marginBottom: 24,
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      }}>
        <h5 style={{ fontWeight: 700, marginBottom: 8 }}>Rotate RSA + ECC Keypairs</h5>
        <p style={{ fontSize: '0.88rem', color: '#a1a1aa', lineHeight: 1.6, marginBottom: 20 }}>
          Generate fresh RSA and ECC keypairs. Your old keys will be archived. A new session token will be issued immediately. All future posts and messages will use the new keys.
        </p>
        <button
          onClick={() => setRotated(true)}
          style={{
            background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
            border: 'none', borderRadius: 12, color: 'white',
            fontWeight: 600, padding: '0.6rem 1.5rem', fontSize: '0.92rem',
            cursor: 'pointer', fontFamily: 'Inter, sans-serif',
            boxShadow: '0 4px 15px rgba(124,58,237,0.4)',
          }}>
          Rotate Keys Now
        </button>
      </div>

      <h5 style={{ fontWeight: 700, marginBottom: 14 }}>Key History</h5>
      <div style={{
        background: '#18181b', border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 20, overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      }}>
        {history.map((h, i) => (
          <div key={h.id} style={{
            padding: '14px 20px',
            borderBottom: i < history.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: '0.82rem', color: '#a1a1aa', marginBottom: 4 }}>{h.rotated_at}</div>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.78rem', color: '#60a5fa', fontFamily: 'monospace' }}>RSA: {h.rsa_pub_preview}</span>
                  <span style={{ fontSize: '0.78rem', color: '#60a5fa', fontFamily: 'monospace' }}>ECC: {h.ecc_pub_preview}</span>
                </div>
              </div>
              <span style={{ background: 'rgba(255,255,255,0.05)', color: '#a1a1aa', fontSize: '0.68rem', fontWeight: 600, padding: '3px 8px', borderRadius: 6 }}>Archived</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

Object.assign(window, { ProfileScreen, KeyRotateScreen });

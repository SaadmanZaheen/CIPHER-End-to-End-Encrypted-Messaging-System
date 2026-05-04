// MessagesScreen.jsx — Inbox list + Conversation view
// Exports: MessagesScreen, ConversationScreen

const CONVERSATIONS = [
  { id: 2, username: 'alice',  initials: 'A', unread: 2, lastMsg: 'Hey, did you see my latest post?' },
  { id: 3, username: 'bob',    initials: 'B', unread: 0, lastMsg: 'The ECDH experiment worked!' },
  { id: 4, username: 'carol',  initials: 'C', unread: 0, lastMsg: 'Thanks for connecting.' },
];

const MESSAGES = [
  { id: 1, text: 'Hey, did you see my latest post?',           isMine: false, time: '10:32 AM', macValid: true },
  { id: 2, text: 'Yes! The key rotation note was interesting.',  isMine: true,  time: '10:33 AM', macValid: true },
  { id: 3, text: 'I just rotated mine too. Fresh keypairs.',     isMine: false, time: '10:35 AM', macValid: true },
  { id: 4, text: 'ECDH shared secrets are elegant once you get used to the math.', isMine: true, time: '10:37 AM', macValid: true },
  { id: 5, text: 'Totally. Let me know when you post more!',     isMine: false, time: '10:38 AM', macValid: true },
];

function MessagesScreen({ setScreen, setConvFriend }) {
  return (
    <div style={{ maxWidth: 680, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <h2 style={{ fontWeight: 800, fontSize: '2rem', letterSpacing: '-1px', marginBottom: '2rem' }}>Messages</h2>

      <div style={{
        background: '#18181b',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 20, overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      }}>
        <div style={{
          padding: '14px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
          fontSize: '0.85rem', color: '#a1a1aa', fontWeight: 600,
        }}>
          Active Conversations
        </div>
        {CONVERSATIONS.map(c => (
          <div
            key={c.id}
            onClick={() => { setConvFriend(c); setScreen('conversation'); }}
            style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '14px 20px',
              borderBottom: '1px solid rgba(255,255,255,0.03)',
              cursor: 'pointer',
              transition: 'background 0.2s ease',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 44, height: 44, borderRadius: '50%',
                background: 'linear-gradient(135deg,#4b5563,#1f2937)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, color: 'white', fontSize: '1rem',
              }}>{c.initials}</div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>@{c.username}</span>
                  {c.unread > 0 && (
                    <span style={{
                      background: '#ef4444', color: 'white', borderRadius: 9999,
                      fontSize: '0.65rem', fontWeight: 700, padding: '1px 7px',
                    }}>{c.unread} New</span>
                  )}
                </div>
                <div style={{ fontSize: '0.78rem', color: '#a1a1aa', marginTop: 2 }}>{c.lastMsg}</div>
              </div>
            </div>
            <button style={{
              background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
              border: 'none', borderRadius: 12, color: 'white',
              fontWeight: 600, padding: '0.35rem 1rem', fontSize: '0.82rem',
              cursor: 'pointer', fontFamily: 'Inter, sans-serif',
            }}>
              Open Chat
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function ConversationScreen({ setScreen, friend = CONVERSATIONS[0] }) {
  const [input, setInput] = React.useState('');
  const [msgs, setMsgs] = React.useState(MESSAGES);
  const [encrypt, setEncrypt] = React.useState(true);
  const boxRef = React.useRef(null);

  React.useEffect(() => {
    if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight;
  }, [msgs]);

  function sendMsg(e) {
    e.preventDefault();
    if (!input.trim()) return;
    setMsgs(m => [...m, { id: Date.now(), text: input.trim(), isMine: true, time: 'now', macValid: true }]);
    setInput('');
  }

  return (
    <div style={{ maxWidth: 680, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h5 style={{ fontWeight: 700, fontSize: '1rem', margin: 0 }}>
          Secure Chat: <strong>@{friend.username}</strong>
        </h5>
        <button
          onClick={() => setScreen('messages')}
          style={{
            background: 'transparent', border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: 8, color: '#a1a1aa', fontSize: '0.82rem',
            padding: '0.35rem 0.9rem', cursor: 'pointer', fontFamily: 'Inter, sans-serif', fontWeight: 500,
          }}>
          ← Back
        </button>
      </div>

      <div style={{
        background: '#18181b',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 20, overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      }}>
        {/* Header */}
        <div style={{
          padding: '12px 18px',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span style={{ fontSize: '0.8rem', color: '#a1a1aa', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ color: '#34d399', fontSize: '0.7rem' }}>●</span> End-to-End Encrypted
          </span>
          <span style={{ fontSize: '0.75rem', color: '#a1a1aa', fontFamily: 'monospace' }}>
            ECDH Channel Key: <code style={{ color: '#60a5fa' }}>a3f1b2c4…</code>
          </span>
        </div>

        {/* Message area */}
        <div
          ref={boxRef}
          style={{ height: 380, overflowY: 'auto', padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: 12 }}
        >
          {msgs.map(m => (
            <div key={m.id} style={{ display: 'flex', justifyContent: m.isMine ? 'flex-end' : 'flex-start' }}>
              <div style={{ maxWidth: '75%' }}>
                {!m.isMine && (
                  <div style={{ fontSize: '0.72rem', color: '#a1a1aa', marginBottom: 4, paddingLeft: 4 }}>
                    {friend.username}
                  </div>
                )}
                <div style={{
                  padding: '8px 14px', borderRadius: 14,
                  background: m.isMine ? 'linear-gradient(135deg,#8b5cf6,#3b82f6)' : 'rgba(255,255,255,0.06)',
                  color: 'white', fontSize: '0.9rem', lineHeight: 1.5, wordWrap: 'break-word',
                }}>
                  {m.text}
                </div>
                <div style={{
                  display: 'flex', gap: 8, marginTop: 4,
                  justifyContent: m.isMine ? 'flex-end' : 'flex-start',
                  fontSize: '0.68rem', opacity: 0.6,
                }}>
                  <span>{m.time}</span>
                  <span style={{ color: m.macValid ? '#34d399' : '#f87171' }}>
                    MAC {m.macValid ? '✔' : '✘'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Input area */}
        <div style={{ padding: '12px 18px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <form onSubmit={sendMsg} style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder={`Message @${friend.username}...`}
              style={{
                flex: 1, background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12,
                color: '#f4f4f5', padding: '0.6rem 1rem',
                fontFamily: 'Inter, sans-serif', fontSize: '0.9rem', outline: 'none',
              }}
            />
            <button type="submit" style={{
              background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
              border: 'none', borderRadius: 12, color: 'white',
              fontWeight: 600, padding: '0.6rem 1.2rem', fontSize: '0.88rem',
              cursor: 'pointer', fontFamily: 'Inter, sans-serif',
            }}>
              Send
            </button>
          </form>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => setEncrypt(e => !e)}>
            <div style={{
              width: 36, height: 18, borderRadius: 9999,
              background: encrypt ? '#8b5cf6' : 'rgba(255,255,255,0.1)', position: 'relative',
            }}>
              <div style={{
                position: 'absolute', width: 12, height: 12, background: 'white', borderRadius: '50%', top: 3,
                right: encrypt ? 3 : 'auto', left: encrypt ? 'auto' : 3, transition: '0.3s',
              }} />
            </div>
            <span style={{ fontSize: '0.78rem', color: '#a1a1aa', fontWeight: 600 }}>Enable E2E Encryption</span>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { MessagesScreen, ConversationScreen });

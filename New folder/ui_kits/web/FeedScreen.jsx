// FeedScreen.jsx — Feed with compose card + post cards + locked post
// Exports: FeedScreen, MyPostsScreen

const POSTS = [
  {
    id: 1, author: 'alice', authorId: 2, initials: 'A',
    title: 'Key rotation complete',
    content: 'New RSA + ECC keypairs generated. All future posts encrypted with fresh keys. You can rotate yours in the Profile → Key Rotation section.',
    time: '2 hours ago', macValid: true, eccValid: true, locked: false,
  },
  {
    id: 2, author: 'bob', authorId: 3, initials: 'B',
    title: 'ECDH shared secret experiment',
    content: 'Ran a test of our ECDH key exchange — the shared secrets derived independently match perfectly on both sides. The math works.',
    time: '5 hours ago', macValid: true, eccValid: true, locked: false,
  },
  {
    id: 3, author: 'carol', authorId: 4, initials: 'C',
    title: 'Encrypted research notes',
    content: '',
    time: '1 day ago', macValid: true, eccValid: false, locked: true,
  },
];

function Avatar({ initials, own = false, size = 40 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      background: own
        ? 'linear-gradient(135deg,#a78bfa,#3b82f6)'
        : 'linear-gradient(135deg,#4b5563,#1f2937)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontWeight: 700, color: 'white', fontSize: size * 0.38,
      flexShrink: 0,
    }}>
      {initials}
    </div>
  );
}

function SecurityBadge({ type, valid }) {
  if (valid === null || valid === undefined) return null;
  const colors = {
    mac:  valid ? { bg: 'rgba(16,185,129,0.15)', color: '#34d399', border: 'rgba(16,185,129,0.3)' } : { bg: 'rgba(239,68,68,0.15)', color: '#f87171', border: 'rgba(239,68,68,0.3)' },
    ecc:  valid ? { bg: '#8b5cf6', color: 'white', border: 'transparent' } : { bg: 'rgba(239,68,68,0.15)', color: '#f87171', border: 'rgba(239,68,68,0.3)' },
  };
  const c = colors[type];
  const icons = {
    mac: <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>,
    ecc: <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>,
  };
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 3,
      padding: '0.25em 0.55em', borderRadius: 6,
      fontSize: '0.68rem', fontWeight: 600, letterSpacing: '0.4px',
      background: c.bg, color: c.color, border: `1px solid ${c.border}`,
    }}>
      {icons[type]} {type.toUpperCase()} {valid ? '✔' : '✘'}
    </span>
  );
}

function PostCard({ post, onViewPost, isOwn }) {
  if (post.locked) {
    return (
      <div style={{
        background: '#18181b',
        border: '1px solid rgba(255,255,255,0.04)',
        borderRadius: 20,
        overflow: 'hidden',
        marginBottom: 20,
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
        position: 'relative',
      }}>
        {/* Blurred header */}
        <div style={{ padding: '16px 20px 8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Avatar initials={post.initials} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', filter: 'blur(4px)', opacity: 0.5 }}>{post.author}</div>
              <div style={{ fontSize: '0.72rem', color: '#a1a1aa' }}>{post.time}</div>
            </div>
          </div>
        </div>
        <div style={{ padding: '0 20px 20px', position: 'relative', minHeight: 140 }}>
          <h5 style={{ fontWeight: 700, marginBottom: 8, filter: 'blur(5px)', opacity: 0.5 }}>{post.title}</h5>
          <p style={{ fontSize: '0.88rem', color: '#d4d4d8', lineHeight: 1.6, filter: 'blur(8px)', opacity: 0.3, userSelect: 'none' }}>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
          </p>
          {/* Glass overlay */}
          <div style={{
            position: 'absolute', inset: '0 0 0 0',
            background: 'rgba(24,24,27,0.72)',
            border: '1px solid rgba(255,255,255,0.05)',
            backdropFilter: 'blur(12px)',
            borderRadius: 16,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            textAlign: 'center', padding: 20,
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 10 }}>
              <rect x="3" y="11" width="18" height="11" rx="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <h5 style={{ fontWeight: 700, marginBottom: 6, fontSize: '0.95rem' }}>Encrypted Content</h5>
            <p style={{ fontSize: '0.78rem', color: '#a1a1aa', marginBottom: 14, lineHeight: 1.5 }}>
              Connect with {post.author} to unlock this post securely.
            </p>
            <button style={{
              background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
              border: 'none', borderRadius: 9999, color: 'white',
              fontWeight: 600, padding: '0.4rem 1.3rem', fontSize: '0.85rem',
              cursor: 'pointer', fontFamily: 'Inter, sans-serif',
              boxShadow: '0 4px 12px rgba(124,58,237,0.35)',
            }}>
              Connect to Unlock
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: '#18181b',
      border: isOwn ? '1px solid rgba(139,92,246,0.3)' : '1px solid rgba(255,255,255,0.05)',
      borderRadius: 20, overflow: 'hidden', marginBottom: 20,
      boxShadow: isOwn
        ? '0 10px 30px rgba(0,0,0,0.2), 0 0 20px rgba(139,92,246,0.1)'
        : '0 10px 30px rgba(0,0,0,0.2)',
      transition: 'transform 0.3s ease, box-shadow 0.3s ease',
    }}>
      <div style={{ padding: '16px 20px 8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Avatar initials={post.initials} own={isOwn} />
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{post.author}</div>
            <div style={{ fontSize: '0.72rem', color: '#a1a1aa' }}>{post.time}</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          <SecurityBadge type="mac" valid={post.macValid} />
          <SecurityBadge type="ecc" valid={post.eccValid} />
        </div>
      </div>
      <div style={{ padding: '4px 20px 20px' }}>
        <h4 style={{ fontWeight: 700, marginBottom: 8, fontSize: '1rem' }}>{post.title}</h4>
        <p style={{ fontSize: '0.9rem', color: '#d4d4d8', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{post.content}</p>
        <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', gap: 12, alignItems: 'center' }}>
          <a onClick={() => onViewPost && onViewPost(post)} style={{ fontSize: '0.8rem', color: '#a1a1aa', fontWeight: 600, cursor: 'pointer', textDecoration: 'none' }}>View Details</a>
          {isOwn && <><span style={{ color: '#3f3f46' }}>•</span><a style={{ fontSize: '0.8rem', color: '#a78bfa', fontWeight: 600, cursor: 'pointer' }}>Edit Post</a></>}
        </div>
      </div>
    </div>
  );
}

function ComposeCard({ currentUser }) {
  const [title, setTitle] = React.useState('');
  const [content, setContent] = React.useState('');
  const [encrypt, setEncrypt] = React.useState(true);

  return (
    <div style={{
      background: '#18181b',
      border: '1px solid rgba(139,92,246,0.3)',
      borderRadius: 20, overflow: 'hidden', marginBottom: 24,
      boxShadow: '0 10px 30px rgba(0,0,0,0.2), 0 0 20px rgba(139,92,246,0.1)',
    }}>
      <div style={{ padding: '18px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
          <Avatar initials={currentUser[0].toUpperCase()} own={true} />
          <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Create secure post</span>
        </div>
        <input
          type="text"
          placeholder="Post Title"
          value={title}
          onChange={e => setTitle(e.target.value)}
          style={{
            background: 'transparent', border: 'none', outline: 'none',
            color: '#f4f4f5', fontSize: '1rem', width: '100%',
            fontFamily: 'Inter, sans-serif', marginBottom: 8, display: 'block',
          }}
        />
        <textarea
          placeholder="What's on your mind? This will be end-to-end encrypted..."
          value={content}
          onChange={e => setContent(e.target.value)}
          rows={2}
          style={{
            background: 'transparent', border: 'none', outline: 'none',
            color: '#f4f4f5', fontSize: '0.9rem', width: '100%', resize: 'none',
            fontFamily: 'Inter, sans-serif', lineHeight: 1.6, display: 'block',
          }}
        />
        <hr style={{ borderColor: 'rgba(255,255,255,0.08)', margin: '12px 0' }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => setEncrypt(e => !e)}>
            <div style={{
              width: 40, height: 20, borderRadius: 9999,
              background: encrypt ? '#8b5cf6' : 'rgba(255,255,255,0.1)',
              position: 'relative', transition: '0.3s',
            }}>
              <div style={{
                position: 'absolute', width: 14, height: 14, background: 'white',
                borderRadius: '50%', top: 3,
                right: encrypt ? 3 : 'auto', left: encrypt ? 'auto' : 3,
                transition: '0.3s',
              }} />
            </div>
            <span style={{ fontSize: '0.8rem', color: '#a1a1aa', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ background: 'rgba(139,92,246,0.2)', color: '#a78bfa', fontSize: '0.68rem', fontWeight: 600, padding: '2px 7px', borderRadius: 4 }}>RSA + ECC</span>
              E2E Encryption
            </span>
          </div>
          <button style={{
            background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
            border: 'none', borderRadius: 9999, color: 'white',
            fontWeight: 600, padding: '0.4rem 1.3rem', fontSize: '0.88rem',
            cursor: 'pointer', fontFamily: 'Inter, sans-serif',
            boxShadow: '0 4px 12px rgba(124,58,237,0.35)',
          }}>
            Post securely
          </button>
        </div>
      </div>
    </div>
  );
}

function FeedScreen({ setScreen }) {
  const currentUser = 'you';
  return (
    <div style={{ maxWidth: 680, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <h2 style={{ fontWeight: 800, fontSize: '2rem', letterSpacing: '-1px', marginBottom: '2rem' }}>Your Feed</h2>
      <ComposeCard currentUser={currentUser} />
      {POSTS.map((p, i) => (
        <PostCard key={p.id} post={p} isOwn={i === 0} onViewPost={() => {}} />
      ))}
    </div>
  );
}

function MyPostsScreen({ setScreen }) {
  const myPosts = POSTS.filter(p => !p.locked);
  return (
    <div style={{ maxWidth: 680, margin: '0 auto', padding: '2rem 24px 4rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2 style={{ fontWeight: 800, fontSize: '2rem', letterSpacing: '-1px', margin: 0 }}>My Posts</h2>
        <button
          onClick={() => setScreen('feed')}
          style={{
            background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
            border: 'none', borderRadius: 12, color: 'white',
            fontWeight: 600, padding: '0.5rem 1.2rem', fontSize: '0.88rem',
            cursor: 'pointer', fontFamily: 'Inter, sans-serif',
          }}>
          + New Post
        </button>
      </div>
      {myPosts.map(p => <PostCard key={p.id} post={p} isOwn={true} />)}
    </div>
  );
}

Object.assign(window, { FeedScreen, MyPostsScreen, Avatar, SecurityBadge });

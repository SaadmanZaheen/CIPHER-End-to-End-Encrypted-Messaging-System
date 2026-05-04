// AuthScreens.jsx — Login, Register, OTP Setup, OTP Verify
// Exports: LoginScreen, RegisterScreen, OTPSetupScreen, OTPVerifyScreen

const authCardStyle = {
  background: '#18181b',
  border: '1px solid rgba(255,255,255,0.06)',
  borderRadius: 20,
  boxShadow: '0 10px 30px rgba(0,0,0,0.25)',
  padding: '2.5rem 2rem',
  width: '100%',
  maxWidth: 420,
  margin: '60px auto 0',
};

const inputStyle = {
  background: 'rgba(255,255,255,0.03)',
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: 12,
  color: '#f4f4f5',
  padding: '0.7rem 1rem',
  fontFamily: 'Inter, sans-serif',
  fontSize: '0.95rem',
  width: '100%',
  display: 'block',
  outline: 'none',
  boxSizing: 'border-box',
};

const labelStyle = {
  fontSize: '0.88rem',
  fontWeight: 500,
  color: '#f4f4f5',
  display: 'block',
  marginBottom: 6,
};

function BtnPrimary({ children, onClick, style }) {
  return (
    <button onClick={onClick} style={{
      background: 'linear-gradient(135deg,#8b5cf6,#3b82f6)',
      border: 'none',
      borderRadius: 12,
      color: 'white',
      fontWeight: 600,
      padding: '0.65rem 1.5rem',
      fontSize: '0.95rem',
      width: '100%',
      cursor: 'pointer',
      fontFamily: 'Inter, sans-serif',
      boxShadow: '0 4px 15px rgba(124,58,237,0.4)',
      marginTop: 4,
      ...style,
    }}>{children}</button>
  );
}

function FormGroup({ label, type = 'text', placeholder, value, onChange }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={labelStyle}>{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        style={inputStyle}
      />
    </div>
  );
}

function AuthLink({ text, linkText, onClick }) {
  return (
    <p style={{ textAlign: 'center', marginTop: 20, fontSize: '0.88rem', color: '#a1a1aa' }}>
      {text}{' '}
      <a onClick={onClick} style={{ color: '#a78bfa', cursor: 'pointer', fontWeight: 600 }}>
        {linkText}
      </a>
    </p>
  );
}

// ── Login ──────────────────────────────────────────────────────
function LoginScreen({ setScreen }) {
  const [user, setUser] = React.useState('');
  const [pass, setPass] = React.useState('');

  function handleLogin(e) {
    e.preventDefault();
    setScreen('verify-otp');
  }

  return (
    <div style={authCardStyle}>
      <h4 style={{ textAlign: 'center', fontWeight: 700, marginBottom: 24, fontSize: '1.35rem' }}>Log In</h4>
      <form onSubmit={handleLogin}>
        <FormGroup label="Username" placeholder="your_username" value={user} onChange={e => setUser(e.target.value)} />
        <FormGroup label="Password" type="password" placeholder="••••••••" value={pass} onChange={e => setPass(e.target.value)} />
        <BtnPrimary>Log In</BtnPrimary>
      </form>
      <AuthLink text="No account?" linkText="Register" onClick={() => setScreen('register')} />
    </div>
  );
}

// ── Register ───────────────────────────────────────────────────
function RegisterScreen({ setScreen }) {
  const [form, setForm] = React.useState({ username: '', email: '', contact: '', password: '', confirm: '' });
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  function handleRegister(e) {
    e.preventDefault();
    setScreen('setup-otp');
  }

  return (
    <div style={{ ...authCardStyle, maxWidth: 480 }}>
      <h4 style={{ textAlign: 'center', fontWeight: 700, marginBottom: 24, fontSize: '1.35rem' }}>Create Account</h4>
      <form onSubmit={handleRegister}>
        <FormGroup label="Username" placeholder="your_username" value={form.username} onChange={set('username')} />
        <FormGroup label="Email" type="email" placeholder="you@example.com" value={form.email} onChange={set('email')} />
        <FormGroup label="Contact" placeholder="Phone or other" value={form.contact} onChange={set('contact')} />
        <FormGroup label="Password" type="password" placeholder="••••••••" value={form.password} onChange={set('password')} />
        <FormGroup label="Confirm Password" type="password" placeholder="••••••••" value={form.confirm} onChange={set('confirm')} />
        <BtnPrimary>Register</BtnPrimary>
      </form>
      <AuthLink text="Already have an account?" linkText="Log in" onClick={() => setScreen('login')} />
    </div>
  );
}

// ── OTP Setup ──────────────────────────────────────────────────
function OTPSetupScreen({ setScreen }) {
  const [token, setToken] = React.useState('');
  const fakeSecret = 'JBSWY3DPEHPK3PXP';
  const fakeQR = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=otpauth%3A%2F%2Ftotp%2FCSE447%3Ademo%3Fsecret%3D${fakeSecret}%26issuer%3DCSE447`;

  return (
    <div style={{ ...authCardStyle, maxWidth: 460 }}>
      <h4 style={{ textAlign: 'center', fontWeight: 700, marginBottom: 12, fontSize: '1.2rem' }}>Set Up Two-Factor Authentication</h4>
      <p style={{ fontSize: '0.88rem', color: '#a1a1aa', marginBottom: 16, lineHeight: 1.6 }}>
        Scan this QR code with <strong style={{ color: '#f4f4f5' }}>Google Authenticator</strong> or any TOTP app:
      </p>
      <div style={{ textAlign: 'center', marginBottom: 16 }}>
        <img src={fakeQR} alt="OTP QR" style={{ border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
      </div>
      <p style={{ fontSize: '0.8rem', color: '#a1a1aa', marginBottom: 16 }}>
        Or enter this secret manually:{' '}
        <code style={{ color: '#60a5fa', fontFamily: 'monospace' }}>{fakeSecret}</code>
      </p>
      <hr style={{ borderColor: 'rgba(255,255,255,0.08)', marginBottom: 16 }} />
      <p style={{ fontSize: '0.88rem', color: '#a1a1aa', marginBottom: 12 }}>Enter the 6-digit code shown in your app:</p>
      <input
        type="text"
        maxLength={6}
        placeholder="000000"
        value={token}
        onChange={e => setToken(e.target.value)}
        style={{ ...inputStyle, textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5em', fontFamily: 'monospace', marginBottom: 12 }}
      />
      <button
        onClick={() => setScreen('login')}
        style={{
          background: '#10b981',
          border: 'none',
          borderRadius: 12,
          color: 'white',
          fontWeight: 600,
          padding: '0.65rem',
          fontSize: '0.95rem',
          width: '100%',
          cursor: 'pointer',
          fontFamily: 'Inter, sans-serif',
        }}
      >
        Confirm &amp; Enable 2FA
      </button>
    </div>
  );
}

// ── OTP Verify ─────────────────────────────────────────────────
function OTPVerifyScreen({ setScreen }) {
  const [token, setToken] = React.useState('');

  return (
    <div style={authCardStyle}>
      <h4 style={{ textAlign: 'center', fontWeight: 700, marginBottom: 16, fontSize: '1.2rem' }}>Two-Factor Authentication</h4>
      <p style={{ fontSize: '0.88rem', color: '#a1a1aa', marginBottom: 20, textAlign: 'center', lineHeight: 1.6 }}>
        Enter the 6-digit code from your authenticator app to continue.
      </p>
      <input
        type="text"
        maxLength={6}
        placeholder="000000"
        value={token}
        onChange={e => setToken(e.target.value)}
        style={{ ...inputStyle, textAlign: 'center', fontSize: '1.6rem', letterSpacing: '0.5em', fontFamily: 'monospace', marginBottom: 16 }}
      />
      <BtnPrimary onClick={() => setScreen('feed')}>Verify &amp; Login</BtnPrimary>
      <p style={{ textAlign: 'center', marginTop: 16, fontSize: '0.82rem', color: '#a1a1aa' }}>
        <a onClick={() => setScreen('login')} style={{ color: '#a78bfa', cursor: 'pointer' }}>← Back to login</a>
      </p>
    </div>
  );
}

Object.assign(window, { LoginScreen, RegisterScreen, OTPSetupScreen, OTPVerifyScreen });

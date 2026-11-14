import { useState } from 'react';
import { api } from '../api';
import CameraCapture from './CameraCapture';

const CNIC_PATTERN = /^[0-9]{5}-[0-9]{7}-[0-9]$/;
const STEPS = ['role', 'account', 'otp', 'identity', 'review'];

export default function SecureSignup({ onSuccess, onCancel, addToast, normalizePhone }) {
  const [step, setStep] = useState(0);
  const [role, setRole] = useState('buyer');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [city, setCity] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [cnicNumber, setCnicNumber] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [otpToken, setOtpToken] = useState('');
  const [devOtp, setDevOtp] = useState('');
  const [selfieFile, setSelfieFile] = useState(null);
  const [selfiePreview, setSelfiePreview] = useState('');
  const [cnicFile, setCnicFile] = useState(null);
  const [cnicPreview, setCnicPreview] = useState('');
  const [shopName, setShopName] = useState('');
  const [sellerCategory, setSellerCategory] = useState('Individual');
  const [brandName, setBrandName] = useState('');
  const [trademarkNumber, setTrademarkNumber] = useState('');
  const [certificateFile, setCertificateFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verificationPreview, setVerificationPreview] = useState(null);

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const back = () => setStep((s) => Math.max(s - 1, 0));

  const sendOtp = async () => {
    const p = normalizePhone(phone);
    if (p.length < 10) {
      addToast('Enter a valid phone number.', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/auth/otp/send', { phone: p });
      if (res.data.dev_otp) setDevOtp(res.data.dev_otp);
      addToast('OTP sent to your phone.', 'success');
      next();
    } catch (e) {
      addToast(e.response?.data?.detail || 'Failed to send OTP.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    setLoading(true);
    try {
      const res = await api.post('/auth/otp/verify', {
        phone: normalizePhone(phone),
        code: otpCode,
      });
      setOtpToken(res.data.otp_token);
      addToast('Phone verified successfully.', 'success');
      next();
    } catch (e) {
      addToast(e.response?.data?.detail || 'Invalid OTP.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const submitSignup = async () => {
    if (!selfieFile || !cnicFile) {
      addToast('Live selfie and CNIC photo are required.', 'error');
      return;
    }
    if (!CNIC_PATTERN.test(cnicNumber)) {
      addToast('CNIC format: 12345-1234567-1', 'error');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('name', `${firstName} ${lastName}`.trim());
    formData.append('email', email);
    formData.append('phone', normalizePhone(phone));
    formData.append('password', password);
    formData.append('role', role);
    formData.append('cnic_number', cnicNumber);
    formData.append('otp_token', otpToken);
    formData.append('city', city);
    formData.append('selfie', selfieFile);
    formData.append('cnic_image', cnicFile);
    if (role === 'seller') {
      formData.append('shop_name', shopName);
      formData.append('seller_category', sellerCategory);
      if (cnicFile) formData.append('document', cnicFile);
    }
    if (role === 'brand') {
      formData.append('brand_name', brandName);
      formData.append('brand_category', 'Corporate');
      formData.append('trademark_number', trademarkNumber);
      if (certificateFile) formData.append('certificate', certificateFile);
    }
    try {
      const res = await api.post('/auth/signup/secure', formData);
      setVerificationPreview({
        status: res.data.verification_status,
        score: res.data.biometric_match_score,
        cnic: res.data.cnic_verified,
      });
      const loginRes = await api.post('/auth/login', { email, password });
      localStorage.setItem('trustSellToken', loginRes.data.access_token);
      addToast('Account created with full security verification!', 'success');
      onSuccess?.(loginRes.data.user);
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (typeof detail === 'object' && detail.reasons) {
        addToast(detail.reasons.join(' '), 'error');
      } else {
        addToast(detail || 'Signup failed.', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const validateAccount = () => {
    if (!firstName || !lastName || !email || !phone || !password) {
      addToast('Complete all account fields.', 'error');
      return false;
    }
    if (password !== confirmPassword) {
      addToast('Passwords do not match.', 'error');
      return false;
    }
    if (password.length < 8) {
      addToast('Password must be at least 8 characters.', 'error');
      return false;
    }
    return true;
  };

  return (
    <div className="secure-signup">
      <div className="signup-steps">
        {STEPS.map((s, i) => (
          <span key={s} className={`signup-step ${i <= step ? 'active' : ''}`}>
            {i + 1}. {s}
          </span>
        ))}
      </div>

      {step === 0 && (
        <div>
          <h4>Choose your account type</h4>
          <div className="role-grid">
            {[
              { id: 'buyer', icon: 'fa-shopping-bag', title: 'Buyer', desc: 'Shop with verified trust' },
              { id: 'seller', icon: 'fa-store', title: 'Seller', desc: 'CNIC + shop verification' },
              { id: 'brand', icon: 'fa-certificate', title: 'Brand', desc: 'Trademark certificate audit' },
            ].map((r) => (
              <button
                key={r.id}
                type="button"
                className={`role-card ${role === r.id ? 'selected' : ''}`}
                onClick={() => setRole(r.id)}
              >
                <i className={`fas ${r.icon}`}></i>
                <strong>{r.title}</strong>
                <small>{r.desc}</small>
              </button>
            ))}
          </div>
          <button type="button" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }} onClick={next}>
            Continue
          </button>
        </div>
      )}

      {step === 1 && (
        <div>
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input className="form-control" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input className="form-control" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
            </div>
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" className="form-control" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Phone (OTP verified)</label>
            <input className="form-control" placeholder="03001234567" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>City</label>
            <select className="form-control" value={city} onChange={(e) => setCity(e.target.value)}>
              <option value="">Select city</option>
              {['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Peshawar', 'Quetta'].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          {role === 'seller' && (
            <>
              <div className="form-group">
                <label>Shop Name</label>
                <input className="form-control" value={shopName} onChange={(e) => setShopName(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Seller Category</label>
                <select className="form-control" value={sellerCategory} onChange={(e) => setSellerCategory(e.target.value)}>
                  <option>Individual</option>
                  <option>Retailer</option>
                  <option>Wholesaler</option>
                  <option>Manufacturer</option>
                </select>
              </div>
            </>
          )}
          {role === 'brand' && (
            <>
              <div className="form-group">
                <label>Brand Name</label>
                <input className="form-control" value={brandName} onChange={(e) => setBrandName(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Trademark Number</label>
                <input className="form-control" value={trademarkNumber} onChange={(e) => setTrademarkNumber(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Trademark Certificate (PDF/Image)</label>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  className="form-control"
                  onChange={(e) => setCertificateFile(e.target.files?.[0] || null)}
                />
              </div>
            </>
          )}
          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input type="password" className="form-control" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} />
            </div>
            <div className="form-group">
              <label>Confirm</label>
              <input type="password" className="form-control" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            </div>
          </div>
          <div className="signup-nav">
            <button type="button" className="btn btn-outline" onClick={back}>Back</button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => validateAccount() && sendOtp()}
              disabled={loading}
            >
              Send OTP
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div>
          <h4><i className="fas fa-sms"></i> Verify Phone OTP</h4>
          {devOtp && (
            <p className="dev-otp-hint">Dev OTP: <strong>{devOtp}</strong></p>
          )}
          <div className="form-group">
            <label>Enter 6-digit code</label>
            <input className="form-control" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} maxLength={6} />
          </div>
          <div className="signup-nav">
            <button type="button" className="btn btn-outline" onClick={back}>Back</button>
            <button type="button" className="btn btn-primary" onClick={verifyOtp} disabled={loading}>
              Verify OTP
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h4><i className="fas fa-fingerprint"></i> Biometric & CNIC Verification</h4>
          <div className="form-group">
            <label>CNIC Number</label>
            <input
              className="form-control"
              placeholder="12345-1234567-1"
              value={cnicNumber}
              onChange={(e) => setCnicNumber(e.target.value)}
            />
          </div>
          <CameraCapture
            label="Live Selfie (Biometric Matching)"
            capturedPreview={selfiePreview}
            onCapture={(file, preview) => {
              setSelfieFile(file);
              setSelfiePreview(preview);
            }}
          />
          <div className="form-group" style={{ marginTop: 12 }}>
            <label>CNIC Photo (Front)</label>
            <input
              type="file"
              accept="image/*"
              className="form-control"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (!f) return;
                setCnicFile(f);
                const reader = new FileReader();
                reader.onload = (ev) => setCnicPreview(ev.target.result);
                reader.readAsDataURL(f);
              }}
            />
            {cnicPreview && <img src={cnicPreview} alt="CNIC" className="camera-preview-img" />}
          </div>
          <div className="signup-nav">
            <button type="button" className="btn btn-outline" onClick={back}>Back</button>
            <button type="button" className="btn btn-primary" onClick={() => { next(); }}>Review</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div>
          <h4>Security Review</h4>
          <ul className="security-checklist">
            <li><i className="fas fa-check-circle"></i> Phone OTP verified</li>
            <li><i className="fas fa-check-circle"></i> Live camera selfie captured</li>
            <li><i className="fas fa-check-circle"></i> CNIC uploaded for database cross-check</li>
            <li><i className="fas fa-robot"></i> AI will match face ↔ CNIC before approval</li>
            {role !== 'buyer' && (
              <li><i className="fas fa-user-shield"></i> Admin audit required for {role} accounts</li>
            )}
          </ul>
          {verificationPreview && (
            <div className="verification-result">
              <p>Status: <strong>{verificationPreview.status}</strong></p>
              <p>Biometric score: {(verificationPreview.score * 100).toFixed(0)}%</p>
            </div>
          )}
          <div className="signup-nav">
            <button type="button" className="btn btn-outline" onClick={back}>Back</button>
            <button type="button" className="btn btn-primary" onClick={submitSignup} disabled={loading}>
              {loading ? 'Verifying...' : 'Complete Secure Registration'}
            </button>
          </div>
        </div>
      )}

      <button type="button" className="btn-link-cancel" onClick={onCancel}>Cancel</button>
    </div>
  );
}

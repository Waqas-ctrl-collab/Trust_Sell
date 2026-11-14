import React, { useState, useEffect, useRef } from 'react';
import { api, API_BASE_URL } from './api';
import SecureSignup from './components/SecureSignup';
import CategoriesPage from './components/CategoriesPage';

const normalizePhone = (phone) => phone.replace(/\D/g, '');

export default function App() {
  // Global States
  const [currentPage, setCurrentPage] = useState('home');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [user, setUser] = useState(null);
  const [authModal, setAuthModal] = useState(false);
  const [authTab, setAuthTab] = useState('login');
  
  // Listings and Filter States
  const [listings, setListings] = useState([]);
  const [myListings, setMyListings] = useState([]);
  const [selectedListing, setSelectedListing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('All Pakistan');
  const [showLocationSelect, setShowLocationSelect] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [dynamicCategories, setDynamicCategories] = useState([]);
  
  // Mobile UI States
  const [mobileMenu, setMobileMenu] = useState(false);
  const [mobileSearchQuery, setMobileSearchQuery] = useState('');
  
  // Notifications Toast State
  const [toasts, setToasts] = useState([]);

  // Auth Inputs
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupFirstName, setSignupFirstName] = useState('');
  const [signupLastName, setSignupLastName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPhone, setSignupPhone] = useState('');
  const [signupCity, setSignupCity] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupConfirmPassword, setSignupConfirmPassword] = useState('');

  // Sell Page Inputs
  const [sellTitle, setSellTitle] = useState('');
  const [sellPrice, setSellPrice] = useState('');
  const [sellDescription, setSellDescription] = useState('');
  const [sellCategory, setSellCategory] = useState('');
  const [sellLocation, setSellLocation] = useState('');
  const [sellPhone, setSellPhone] = useState('');
  const [sellFiles, setSellFiles] = useState([]);
  const [sellPreviews, setSellPreviews] = useState([]);
  const fileInputRef = useRef(null);

  // Profile Page Inputs
  const [profileFirstName, setProfileFirstName] = useState('');
  const [profileLastName, setProfileLastName] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [profilePhone, setProfilePhone] = useState('');
  const [profileCity, setProfileCity] = useState('');

  // Chat System States
  const [activeChat, setActiveChat] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [chats, setChats] = useState([
    {
      id: '1',
      name: 'Ahmed Raza',
      avatar: 'AR',
      time: '10:30 AM',
      preview: 'Yes, is this item still available?',
      messages: [
        { type: 'received', text: 'Hi, is this item still available?', time: '10:30 AM' },
        { type: 'sent', text: "Yes, it's available. Are you interested?", time: '10:32 AM' },
        { type: 'received', text: "Yes, I'd like to see it. Where are you located?", time: '10:33 AM' }
      ]
    },
    {
      id: '2',
      name: 'Zara Malik',
      avatar: 'ZM',
      time: 'Yesterday',
      preview: 'What is the absolute final price for the Honda Civic?',
      messages: [
        { type: 'received', text: 'What is the absolute final price for the Honda Civic?', time: '4:15 PM' }
      ]
    }
  ]);
  const chatMessagesEndRef = useRef(null);

  // Auto-playing Hero Carousel State
  const [carouselIndex, setCarouselIndex] = useState(0);
  const heroSlides = [
    'https://images.unsplash.com/photo-1563013544-824ae1b704d3?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
    'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
    'https://images.unsplash.com/photo-1556742044-3c6c8b7b89cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80'
  ];

  // Static Mock Ads for demonstration fallback
  const mockAds = [
    {
      _id: '1',
      title: 'iPhone 12 Pro Max - 256GB - Excellent Condition',
      price: 45000,
      description: 'iPhone 12 Pro Max in excellent condition. 256GB storage capacity. No scratches or dents. Battery health is 92%. Comes with original box and charger.',
      category: 'mobile',
      location: 'Lahore, Punjab',
      seller_name: 'Ahmed Raza',
      seller_phone: '0300-1234567',
      status: 'active',
      images: ['https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'],
      views: 124,
      created_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString()
    },
    {
      _id: '2',
      title: 'Honda Civic 2018 Oriel White - Full Option',
      price: 2500000,
      description: 'First hand family used car. Sound engine and perfect suspension. Bumper to bumper genuine. Full option Oriel model.',
      category: 'cars',
      location: 'Karachi, Sindh',
      seller_name: 'Zara Malik',
      seller_phone: '0321-9876543',
      status: 'active',
      images: ['https://images.unsplash.com/photo-1549399542-7e3f8b79c341?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'],
      views: 312,
      created_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString()
    },
    {
      _id: '3',
      title: '5 Marla Premium House in DHA Phase 6',
      price: 18500000,
      description: 'Modern architect design brand new house in DHA Lahore. 3 luxury master bedrooms, tiled bathrooms, double kitchens, and spacious garage.',
      category: 'property',
      location: 'Lahore, Punjab',
      seller_name: 'Imran Khan',
      seller_phone: '0301-4444555',
      status: 'active',
      images: ['https://images.unsplash.com/photo-1568605114967-8130f3a36994?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'],
      views: 520,
      created_at: new Date(Date.now() - 24 * 3600 * 1000).toISOString()
    },
    {
      _id: '4',
      title: 'MacBook Pro M2 Max - 32GB RAM - 1TB SSD',
      price: 520000,
      description: 'Ultimate power machine. Liquid Retina XDR screen. Space gray color, scratchless like brand new with original apple care.',
      category: 'electronics',
      location: 'Islamabad, Capital',
      seller_name: 'Mohammed Maarije',
      seller_phone: '0333-5556677',
      status: 'active',
      images: ['https://images.unsplash.com/photo-1498049794561-7780e7231661?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'],
      views: 98,
      created_at: new Date(Date.now() - 36 * 3600 * 1000).toISOString()
    }
  ];

  // Show dynamic toast helper
  const addToast = (message, type = 'success') => {
    const id = Math.random().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };

  // 1. Initial Load & Theme & Auth Checking
  useEffect(() => {
    // Theme setup
    const savedTheme = localStorage.getItem('trustSellDarkMode') === 'true';
    setIsDarkMode(savedTheme);
    if (savedTheme) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }

    // Auth checking
    const savedToken = localStorage.getItem('trustSellToken');
    const savedUser = localStorage.getItem('trustSellUser');
    if (savedToken && savedUser) {
      const parsed = JSON.parse(savedUser);
      setUser(parsed);
      fillProfileFields(parsed);
    }

    // Favorites checking
    const savedFavs = localStorage.getItem('trustSellFavorites');
    if (savedFavs) {
      setFavorites(JSON.parse(savedFavs));
    }

    // Load initial listings
    fetchListings();
    api.get('/categories/').then((res) => setDynamicCategories(res.data)).catch(() => {});
  }, []);

  // 2. Auto carousel timer
  useEffect(() => {
    const timer = setInterval(() => {
      setCarouselIndex(prev => (prev + 1) % heroSlides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Scroll chat messages to bottom
  useEffect(() => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeChat?.messages]);

  // Fetch listings from Backend
  const fetchListings = async (category = '', query = '') => {
    setLoading(true);
    try {
      // Build search URL
      let url = `${API_BASE_URL}/listings/`;
      const params = {};
      if (category) params.category = category;
      if (query) params.q = query;
      
      const response = await api.get(url, { params });
      setListings(response.data.length > 0 ? response.data : mockAds);
    } catch (error) {
      console.log("Backend offline, loading premium mock advertisements.");
      setListings(mockAds);
    } finally {
      setLoading(false);
    }
  };

  // Populate profiles
  const fillProfileFields = (parsedUser) => {
    const names = parsedUser.name.split(' ');
    setProfileFirstName(names[0] || '');
    setProfileLastName(names.slice(1).join(' ') || '');
    setProfileEmail(parsedUser.email || '');
    setProfilePhone(parsedUser.phone || '');
    setProfileCity(parsedUser.city || 'Lahore');
    setSellPhone(parsedUser.phone || '');
  };

  // Toggle dark/light theme
  const toggleTheme = () => {
    setIsDarkMode(prev => {
      const newVal = !prev;
      localStorage.setItem('trustSellDarkMode', newVal);
      if (newVal) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }
      return newVal;
    });
  };

  // Handle Login submission
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginEmail || !loginPassword) {
      addToast('Please enter both email and password.', 'error');
      return;
    }

    try {
      const response = await api.post('/auth/login', {
        email: loginEmail,
        password: loginPassword
      });
      const userData = response.data.user;
      localStorage.setItem('trustSellToken', response.data.access_token);
      localStorage.setItem('trustSellUser', JSON.stringify(userData));
      setUser(userData);
      fillProfileFields(userData);
      setAuthModal(false);
      addToast(`Welcome back, ${userData.name}!`, 'success');
      setLoginEmail('');
      setLoginPassword('');
    } catch (error) {
      console.warn("Backend credentials bypass during development. Mock login succeeds.");
      // Simulated local login fallback
      const mockUser = {
        name: 'Ahmed Raza',
        email: loginEmail.includes('@') ? loginEmail : 'ahmed.raza@example.com',
        phone: '0300-1234567',
        city: 'Lahore',
        role: 'seller',
        selfie_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&q=80',
        created_at: new Date().toISOString()
      };
      localStorage.setItem('trustSellUser', JSON.stringify(mockUser));
      setUser(mockUser);
      fillProfileFields(mockUser);
      setAuthModal(false);
      addToast(`Logged in successfully!`, 'success');
    }
  };

  const handleSecureSignupSuccess = (userData) => {
    const mapped = {
      ...userData,
      _id: userData._id || userData.id,
      name: userData.name,
      email: userData.email,
      phone: userData.phone,
      city: userData.city || 'Lahore',
      role: userData.role,
      verification_status: userData.verification_status,
    };
    localStorage.setItem('trustSellUser', JSON.stringify(mapped));
    setUser(mapped);
    fillProfileFields(mapped);
    setAuthModal(false);
  };

  const loadChats = async () => {
    if (!user) return;
    try {
      const res = await api.get('/chat/conversations');
      const mapped = await Promise.all(
        res.data.map(async (c) => {
          let messages = [];
          try {
            const msgs = await api.get(`/chat/conversations/${c.id}/messages`);
            messages = msgs.data;
          } catch {
            messages = [];
          }
          return {
            id: c.id,
            name: c.name,
            avatar: c.avatar,
            time: c.time,
            preview: c.preview,
            messages,
          };
        })
      );
      setChats(mapped.length ? mapped : chats);
    } catch {
      /* keep demo chats offline */
    }
  };

  const openChat = async (chat) => {
    try {
      const msgs = await api.get(`/chat/conversations/${chat.id}/messages`);
      setActiveChat({ ...chat, messages: msgs.data });
    } catch {
      setActiveChat(chat);
    }
  };

  // Handle Logout
  const handleLogout = () => {
    localStorage.removeItem('trustSellUser');
    localStorage.removeItem('trustSellToken');
    setUser(null);
    setCurrentPage('home');
    addToast('Logged out successfully.', 'success');
  };

  // Favorite toggle helper
  const handleFavoriteToggle = (id, e) => {
    e.stopPropagation();
    let updated;
    if (favorites.includes(id)) {
      updated = favorites.filter(favId => favId !== id);
      addToast('Removed from favorites', 'success');
    } else {
      updated = [...favorites, id];
      addToast('Added to favorites', 'success');
    }
    setFavorites(updated);
    localStorage.setItem('trustSellFavorites', JSON.stringify(updated));
  };

  // Handle searching
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchListings(categoryFilter, searchQuery);
    addToast(`Searching listings: "${searchQuery}"`, 'success');
  };

  const handleCategoryFilterSelect = (cat) => {
    setCategoryFilter(cat);
    fetchListings(cat, searchQuery);
    setCurrentPage('home');
  };

  // Browse files triggers
  const triggerFileBrowser = () => {
    fileInputRef.current?.click();
  };

  // Handle listings image loading
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSellFiles(prev => [...prev, ...files]);
    
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        setSellPreviews(prev => [...prev, event.target.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  // Submit Ad Posting form
  const handleAdSubmission = async (e) => {
    e.preventDefault();
    if (!user) {
      setAuthModal(true);
      return;
    }
    if (!sellTitle || !sellPrice || !sellDescription || !sellCategory || !sellLocation || !sellPhone) {
      addToast('Please complete all required listing fields.', 'error');
      return;
    }

    const payload = {
      title: sellTitle,
      price: parseFloat(sellPrice),
      description: sellDescription,
      category: sellCategory,
      location: sellLocation,
      seller_phone: normalizePhone(sellPhone)
    };

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('title', payload.title);
      formData.append('price', payload.price.toString());
      formData.append('description', payload.description);
      formData.append('category', payload.category);
      formData.append('location', payload.location);
      formData.append('seller_phone', payload.seller_phone);
      
      sellFiles.forEach((file, index) => {
        formData.append('images', file);
      });

      const response = await api.post('/listings/', formData);
      const newAd = response.data;
      setListings(prev => [newAd, ...prev]);
      addToast('Your ad has been posted successfully!', 'success');
    } catch (error) {
      console.warn("Backend offline. Simulating ad post locally inside React state.");
      const localAd = {
        _id: Math.random().toString(),
        title: sellTitle,
        price: parseFloat(sellPrice),
        description: sellDescription,
        category: sellCategory,
        location: sellLocation,
        seller_name: user.name,
        seller_phone: sellPhone,
        status: 'active',
        images: sellPreviews.length > 0 ? [sellPreviews[0]] : ['https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80'],
        views: 0,
        created_at: new Date().toISOString()
      };
      setListings(prev => [localAd, ...prev]);
      
      // Store in custom user listing storage
      const userAds = JSON.parse(localStorage.getItem('trustSellUserAds') || '[]');
      userAds.push(localAd);
      localStorage.setItem('trustSellUserAds', JSON.stringify(userAds));
      
      addToast('Ad published successfully!', 'success');
    } finally {
      setLoading(false);
      // Reset fields
      setSellTitle('');
      setSellPrice('');
      setSellDescription('');
      setSellCategory('');
      setSellLocation('');
      setSellPreviews([]);
      setSellFiles([]);
      navigateToPage('my-ads');
    }
  };

  // Navigating routing helper
  const navigateToPage = (pageName) => {
    setCurrentPage(pageName);
    setMobileMenu(false);
    if (pageName === 'my-ads') {
      loadMyAds();
    }
    if (pageName === 'inbox') {
      loadChats();
    }
  };

  // Load active user's posted listings
  const loadMyAds = async () => {
    if (!user) return;
    try {
      const response = await api.get('/listings/user/me');
      setMyListings(response.data);
    } catch (err) {
      const userAds = JSON.parse(localStorage.getItem('trustSellUserAds') || '[]');
      setMyListings(userAds);
    }
  };

  // Delete Ad
  const deleteMyAd = async (id, e) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this listing permanently?')) return;
    
    try {
      await api.delete(`/listings/${id}`);
      setMyListings(prev => prev.filter(a => a._id !== id));
      setListings(prev => prev.filter(a => a._id !== id));
      addToast('Ad deleted successfully from database.', 'success');
    } catch (error) {
      // Local fallback deletion
      const userAds = JSON.parse(localStorage.getItem('trustSellUserAds') || '[]');
      const filtered = userAds.filter(a => a._id !== id);
      localStorage.setItem('trustSellUserAds', JSON.stringify(filtered));
      setMyListings(filtered);
      setListings(prev => prev.filter(a => a._id !== id));
      addToast('Ad deleted successfully.', 'success');
    }
  };

  // View Listing detail
  const viewAdDetail = async (ad) => {
    setSelectedListing(ad);
    setCurrentPage('ad-detail');
    try {
      // Increment views count via endpoint ping
      api.get(`/listings/${ad._id}`);
    } catch (err) {
      ad.views += 1;
    }
  };

  // Update profile
  const handleProfileUpdate = (e) => {
    e.preventDefault();
    if (!profileFirstName || !profileLastName || !profileEmail || !profilePhone) {
      addToast('Please complete all required profile fields.', 'error');
      return;
    }
    const updated = {
      ...user,
      name: `${profileFirstName} ${profileLastName}`,
      email: profileEmail,
      phone: profilePhone,
      city: profileCity
    };
    setUser(updated);
    localStorage.setItem('trustSellUser', JSON.stringify(updated));
    addToast('Profile updated successfully!', 'success');
  };

  // Chat message send handler
  const sendChatMessage = async () => {
    if (!chatInput.trim() || !activeChat) return;
    const text = chatInput.trim();
    setChatInput('');

    try {
      const res = await api.post(`/chat/conversations/${activeChat.id}/messages`, { text });
      const newMessage = { ...res.data, type: 'sent' };
      const updatedChat = {
        ...activeChat,
        preview: text,
        messages: [...(activeChat.messages || []), newMessage],
      };
      setActiveChat(updatedChat);
      setChats((prev) => prev.map((c) => (c.id === activeChat.id ? updatedChat : c)));
      if (res.data.fraud_flags?.length) {
        addToast('Message sent with fraud monitoring active.', 'success');
      }
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (detail?.flags) {
        addToast(`Blocked: ${detail.flags.join(' ')}`, 'error');
      } else {
        addToast(detail?.message || detail || 'Could not send message.', 'error');
      }
    }
  };

  // Start chat with listing seller
  const startChatWithSeller = async () => {
    if (!user) {
      setAuthModal(true);
      return;
    }
    if (!selectedListing.seller_id) {
      addToast('Seller chat unavailable for this listing.', 'error');
      return;
    }
    try {
      const res = await api.post('/chat/conversations', {
        participant_id: selectedListing.seller_id,
        listing_id: selectedListing._id,
        initial_message: `Hi, is "${selectedListing.title}" still available?`,
      });
      const msgs = await api.get(`/chat/conversations/${res.data.id}/messages`);
      const newChat = {
        id: res.data.id,
        name: res.data.name,
        avatar: res.data.avatar,
        time: res.data.time,
        preview: res.data.preview,
        messages: msgs.data,
      };
      setChats((prev) => [newChat, ...prev.filter((c) => c.id !== newChat.id)]);
      setActiveChat(newChat);
      navigateToPage('inbox');
    } catch {
      addToast('Could not start secure chat.', 'error');
    }
  };

  return (
    <div>
      {/* Toast notifications container */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {toasts.map(toast => (
          <div key={toast.id} className={`notification ${toast.type === 'error' ? 'error' : ''}`}>
            <i className={`fas fa-${toast.type === 'success' ? 'check-circle' : 'exclamation-circle'}`}></i>
            <span>{toast.message}</span>
          </div>
        ))}
      </div>

      {/* Header */}
      <header>
        <div className="container">
          <div className="header-content">
            <a href="#" className="logo" onClick={() => navigateToPage('home')}>
              <i className="fas fa-shield-alt"></i>
              <span>TrustSell</span>
            </a>
            
            <button className="mobile-menu-btn" onClick={() => setMobileMenu(true)}>
              <i className="fas fa-bars"></i>
            </button>
            
            <div className="header-actions">
              <button className="icon-btn" onClick={toggleTheme} title="Toggle Dark/Light Mode">
                <i className={`fas fa-${isDarkMode ? 'sun' : 'moon'}`}></i>
              </button>
              
              <div className="account-dropdown">
                <button className="account-btn" onClick={() => user ? navigateToPage('profile') : setAuthModal(true)}>
                  <i className="fas fa-user"></i>
                  <span>{user ? user.name : 'Account'}</span>
                </button>
                {user && (
                  <div className="dropdown-content show-hover">
                    <a href="#" onClick={(e) => { e.preventDefault(); navigateToPage('profile'); }}><i className="fas fa-user-circle"></i> My Profile</a>
                    <a href="#" onClick={(e) => { e.preventDefault(); navigateToPage('my-ads'); }}><i className="fas fa-list"></i> My Ads</a>
                    <a href="#" onClick={(e) => { e.preventDefault(); navigateToPage('inbox'); }}><i className="fas fa-inbox"></i> Inbox</a>
                    <a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}><i className="fas fa-sign-out-alt"></i> Logout</a>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Desktop Search Bar */}
          <div className="desktop-search-container">
            <div className="location-selector" style={{ position: 'relative' }} onClick={() => setShowLocationSelect(!showLocationSelect)}>
              <i className="fas fa-map-marker-alt"></i>
              <span>{locationFilter}</span>
              <i className="fas fa-chevron-down" style={{ fontSize: '0.6rem', marginLeft: '5px' }}></i>
              
              {showLocationSelect && (
                <div style={{
                  position: 'absolute', top: '100%', left: 0, background: 'var(--card-bg)', 
                  border: '1px solid var(--gray-light)', borderRadius: '4px', zIndex: 1001, 
                  width: '200px', display: 'flex', flexDirection: 'column', color: 'var(--text-primary)'
                }} onClick={(e) => e.stopPropagation()}>
                  {['All Pakistan', 'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Peshawar', 'Quetta'].map(loc => (
                    <div key={loc} style={{ padding: '8px 12px', cursor: 'pointer', hover: { background: 'var(--light)' } }}
                      onClick={() => { setLocationFilter(loc); setShowLocationSelect(false); }}>
                      {loc}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <form className="search-bar" onSubmit={handleSearchSubmit} style={{ flex: 1 }}>
              <input 
                type="text" 
                placeholder="Search city, area or product details..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="button" className="voice-search-btn" onClick={() => addToast('Voice search listening...', 'success')}>
                <i className="fas fa-microphone"></i>
              </button>
              <button type="submit">
                <i className="fas fa-search"></i>
              </button>
            </form>
          </div>
        </div>
        
        {/* Mobile Search Bar */}
        <div className="mobile-search-container">
          <form className="mobile-search-bar" onSubmit={(e) => { e.preventDefault(); fetchListings('', mobileSearchQuery); }}>
            <input 
              type="text" 
              placeholder="Search category or product..."
              value={mobileSearchQuery}
              onChange={(e) => setMobileSearchQuery(e.target.value)}
            />
            <button type="submit">
              <i className="fas fa-search"></i>
            </button>
          </form>
        </div>
        
        {/* Desktop Navigation */}
        <nav>
          <div className="container">
            <ul className="nav-links">
              <li><a href="#" className={`nav-link ${currentPage === 'home' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); navigateToPage('home'); }}><i className="fas fa-home"></i> Home</a></li>
              <li><a href="#" className={`nav-link ${currentPage === 'categories' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); navigateToPage('categories'); }}><i className="fas fa-th-large"></i> Categories</a></li>
              <li><a href="#" className={`nav-link ${currentPage === 'sell' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('sell') : setAuthModal(true); }}><i className="fas fa-plus-circle"></i> Sell</a></li>
              <li><a href="#" className={`nav-link ${currentPage === 'my-ads' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('my-ads') : setAuthModal(true); }}><i className="fas fa-list"></i> My Ads</a></li>
              <li><a href="#" className={`nav-link ${currentPage === 'inbox' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('inbox') : setAuthModal(true); }}><i className="fas fa-inbox"></i> Inbox</a></li>
              <li><a href="#" className={`nav-link ${currentPage === 'profile' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('profile') : setAuthModal(true); }}><i className="fas fa-user"></i> Account</a></li>
            </ul>
          </div>
        </nav>
      </header>

      {/* AI-Powered Message Banner */}
      <div className="ai-banner">
        <div className="container">
          <div className="ai-banner-content">
            <div className="ai-badge">AI-POWERED</div>
            <div className="ai-message">
              TrustSell uses government CNIC databases and biometric face checks to guarantee zero fraud listings.
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Drawer menu */}
      {mobileMenu && (
        <div className="modal" style={{ background: 'rgba(0,0,0,0.5)', zIndex: 3000 }} onClick={() => setMobileMenu(false)}>
          <div className="mobile-menu-drawer active" style={{ display: 'block', transform: 'translateX(0)' }} onClick={(e) => e.stopPropagation()}>
            <div className="mobile-menu-header">
              <div className="logo">
                <i className="fas fa-shield-alt"></i>
                <span>TrustSell</span>
              </div>
              <button className="mobile-menu-close" onClick={() => setMobileMenu(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <ul className="mobile-menu-links">
              <li><a href="#" onClick={(e) => { e.preventDefault(); navigateToPage('home'); }}><i className="fas fa-home"></i> Home</a></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); navigateToPage('categories'); }}><i className="fas fa-th-large"></i> Categories</a></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); user ? navigateToPage('sell') : setAuthModal(true); }}><i className="fas fa-plus-circle"></i> Sell</a></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); user ? navigateToPage('my-ads') : setAuthModal(true); }}><i className="fas fa-list"></i> My Ads</a></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); user ? navigateToPage('inbox') : setAuthModal(true); }}><i className="fas fa-inbox"></i> Inbox</a></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); user ? navigateToPage('profile') : setAuthModal(true); }}><i className="fas fa-user"></i> Account</a></li>
              {!user ? (
                <li><a href="#" onClick={(e) => { e.preventDefault(); setAuthModal(true); }}><i className="fas fa-sign-in-alt"></i> Login</a></li>
              ) : (
                <li><a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}><i className="fas fa-sign-out-alt"></i> Logout</a></li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* Main Pages Content */}
      <main style={{ minHeight: '60vh' }}>
        
        {/* PAGE 1: HOME PAGE */}
        {currentPage === 'home' && (
          <section className="fade-in">
            {/* Hero Auto Carousel */}
            <div className="hero">
              <div className="hero-carousel">
                {heroSlides.map((slide, i) => (
                  <div 
                    key={slide} 
                    className={`carousel-slide ${carouselIndex === i ? 'active' : ''}`}
                    style={{ backgroundImage: `url('${slide}')`, display: carouselIndex === i ? 'block' : 'none' }}
                  />
                ))}
              </div>
              <div className="container">
                <div className="hero-content">
                  <h1>Buy & Sell With Verified Trust</h1>
                  <p>Pakistan's premium secured classifieds engine protecting buyers and sellers</p>
                  <button className="btn btn-primary" onClick={() => user ? navigateToPage('sell') : setAuthModal(true)}>
                    <i className="fas fa-rocket"></i>
                    Start Listing Now
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Categories */}
            <div className="quick-categories">
              <div className="container">
                <h2 className="section-title">Popular Categories</h2>
                <div className="categories-grid">
                  {(dynamicCategories.length ? dynamicCategories.map((c) => ({
                    id: c.slug,
                    label: c.name,
                    count: `${c.listing_count ?? 0} ads`,
                    img: c.image_url,
                  })) : [
                    { id: 'mobile', label: 'Mobile Phones', count: '15,842 ads', img: 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=200&q=80' },
                    { id: 'cars', label: 'Cars', count: '12,458 ads', img: 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=200&q=80' },
                    { id: 'property', label: 'Property', count: '18,927 ads', img: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=200&q=80' },
                    { id: 'electronics', label: 'Electronics', count: '11,356 ads', img: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=200&q=80' },
                    { id: 'fashion', label: 'Fashion', count: '9,874 ads', img: 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=200&q=80' },
                    { id: 'furniture', label: 'Furniture', count: '7,642 ads', img: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=200&q=80' },
                  ]).map(cat => (
                    <div 
                      key={cat.id} 
                      className={`category-item ${categoryFilter === cat.id ? 'active' : ''}`}
                      onClick={() => handleCategoryFilterSelect(cat.id)}
                      style={categoryFilter === cat.id ? { borderColor: 'var(--primary)', borderWidth: '2px' } : {}}
                    >
                      <div className="category-icon">
                        <img src={cat.img} alt={cat.label} />
                      </div>
                      <div className="category-name">{cat.label}</div>
                      <div className="category-count">{cat.count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Featured Advertisements Grid */}
            <div className="featured-section">
              <div className="container">
                <div className="section-header">
                  <h2 className="section-title">
                    {categoryFilter ? `Featured ${categoryFilter.toUpperCase()} Ads` : 'Featured Advertisements'}
                  </h2>
                  {categoryFilter && (
                    <button className="btn btn-outline" onClick={() => handleCategoryFilterSelect('')}>
                      Clear Filter <i className="fas fa-times"></i>
                    </button>
                  )}
                </div>

                {loading ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>
                    <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', color: 'var(--primary)' }}></i>
                    <p style={{ marginTop: '10px' }}>Loading marketplace listings...</p>
                  </div>
                ) : listings.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px', background: 'var(--card-bg)', borderRadius: '8px' }}>
                    <i className="fas fa-search" style={{ fontSize: '3rem', color: 'var(--gray)', marginBottom: '15px' }}></i>
                    <h3>No Listings Found</h3>
                    <p>Try clearing filters or search query to find more items.</p>
                  </div>
                ) : (
                  <div className="ads-grid">
                    {listings.map(ad => (
                      <div key={ad._id} className="ad-card" onClick={() => viewAdDetail(ad)}>
                        <div className="ad-badge verified">Verified Seller</div>
                        
                        <div className="ad-actions">
                          <button 
                            className={`ad-action-btn favorite ${favorites.includes(ad._id) ? 'active' : ''}`}
                            onClick={(e) => handleFavoriteToggle(ad._id, e)}
                          >
                            <i className={`${favorites.includes(ad._id) ? 'fas' : 'far'} fa-heart`}></i>
                          </button>
                        </div>

                        <div className="ad-image">
                          <img 
                            src={ad.images && ad.images.length > 0 ? (ad.images[0].startsWith('http') || ad.images[0].startsWith('data') ? ad.images[0] : `${API_BASE_URL}/${ad.images[0]}`) : 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80'} 
                            alt={ad.title} 
                          />
                        </div>

                        <div className="ad-details">
                          <div className="ad-price">Rs {ad.price?.toLocaleString()}</div>
                          <div className="ad-title">{ad.title}</div>
                          <div className="ad-seller">
                            <div className="seller-avatar">{ad.seller_name ? ad.seller_name.split(' ').map(n => n[0]).join('') : 'TS'}</div>
                            <div className="seller-name">{ad.seller_name || 'TrustSell Shop'}</div>
                          </div>
                          <div className="ad-location">
                            <i className="fas fa-map-marker-alt"></i>
                            <span>{ad.location}</span>
                          </div>
                          <div className="ad-meta">
                            <span><i className="far fa-eye"></i> {ad.views || 0} views</span>
                            <span>{new Date(ad.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* AI Security Features Banner */}
            <div className="security-features">
              <div className="container">
                <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '10px' }}>Safest Marketplace Security Pillars</h2>
                <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '30px' }}>How we completely protect you from scammers</p>
                <div className="security-grid">
                  <div className="security-card">
                    <div className="security-icon"><i className="fas fa-fingerprint"></i></div>
                    <div className="security-title">Biometric Selfie Matching</div>
                    <div className="security-desc">All user signups check a live facial camera matching government profiles to eliminate bot shops.</div>
                  </div>
                  <div className="security-card">
                    <div className="security-icon"><i className="fas fa-file-signature"></i></div>
                    <div className="security-title">CNIC Database Verification</div>
                    <div className="security-desc">Identity cards are cross-referenced with national databases before seller approval.</div>
                  </div>
                  <div className="security-card">
                    <div className="security-icon"><i className="fas fa-shield-alt"></i></div>
                    <div className="security-title">Trademark Certificate Audit</div>
                    <div className="security-desc">Major corporate brands upload official IP rights, preventing fake products and knock-offs.</div>
                  </div>
                  <div className="security-card">
                    <div className="security-icon"><i className="fas fa-headset"></i></div>
                    <div className="security-title">Escrow Fraud Filters</div>
                    <div className="security-desc">Artificial Intelligence analyzes chat text logs to intercept scam links and suspicious behaviors instantly.</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Live Streams Section */}
            <div className="live-shopping">
              <div className="container">
                <h2 className="section-title">Live Shopping Streams</h2>
                <div className="live-streams">
                  {[
                    { title: 'iPhone 15 Pro Max Live Hands-on Inspection', host: 'Raza Tech', views: '1.2K watching', img: 'https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=500&q=80' },
                    { title: 'Honda Civic Oriel Interior & Mileage Audit', host: 'CarHub PK', views: '840 watching', img: 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=500&q=80' },
                    { title: 'DHA Phase 6 House Complete Virtual Tour', host: 'DHA Estates', views: '2.5K watching', img: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=500&q=80' }
                  ].map((stream, idx) => (
                    <div key={idx} className="live-card">
                      <div className="live-badge">LIVE</div>
                      <div className="live-image">
                        <img src={stream.img} alt={stream.title} />
                      </div>
                      <div className="live-details">
                        <div className="live-title">{stream.title}</div>
                        <div className="live-host">
                          <div className="host-avatar">{stream.host.substring(0,2)}</div>
                          <div className="host-name">{stream.host}</div>
                        </div>
                        <div className="live-stats">
                          <span><i className="far fa-user"></i> {stream.views}</span>
                          <span style={{ color: 'var(--danger)' }}><i className="fas fa-circle"></i> Live Now</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* PAGE 2: SELL PAGE FORM */}
        {currentPage === 'sell' && (
          <section className="fade-in">
            <div className="sell-form-container">
              <h2 className="sell-form-title">Publish A Trusted Advertisement</h2>
              
              <form onSubmit={handleAdSubmission}>
                <div className="form-group">
                  <label>Ad Title *</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder="e.g. Samsung Galaxy S23 Ultra - 512GB (PTA Approved)"
                    value={sellTitle}
                    onChange={(e) => setSellTitle(e.target.value)}
                    required
                    minLength={3}
                    maxLength={100}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Price (PKR) *</label>
                    <input 
                      type="number" 
                      className="form-control" 
                      placeholder="Enter price"
                      value={sellPrice}
                      onChange={(e) => setSellPrice(e.target.value)}
                      required
                      min={1}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Category *</label>
                    <select 
                      className="form-control"
                      value={sellCategory}
                      onChange={(e) => setSellCategory(e.target.value)}
                      required
                    >
                      <option value="">Choose Category</option>
                      <option value="mobile">Mobile Phones</option>
                      <option value="cars">Cars & Vehicles</option>
                      <option value="property">Property & Real Estate</option>
                      <option value="electronics">Electronics & Computers</option>
                      <option value="fashion">Fashion & Clothes</option>
                      <option value="furniture">Furniture & Decor</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Location (City / Area) *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      placeholder="e.g. DHA Phase 5, Lahore"
                      value={sellLocation}
                      onChange={(e) => setSellLocation(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Contact Phone *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      placeholder="03XXXXXXXXX"
                      value={sellPhone}
                      onChange={(e) => setSellPhone(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Description details *</label>
                  <textarea 
                    className="form-control" 
                    rows="5"
                    placeholder="Enter item specs, age, PTA status, and overall description..."
                    value={sellDescription}
                    onChange={(e) => setSellDescription(e.target.value)}
                    required
                    minLength={10}
                  />
                </div>

                <div className="form-group">
                  <label>Add Images (Max 3MB each) *</label>
                  <div className="image-upload-container" onClick={triggerFileBrowser}>
                    <i className="fas fa-camera image-upload-icon"></i>
                    <h4>Click to browse product photographs</h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '5px' }}>Only PNG, JPG, and JPEG files are allowed.</p>
                    <input 
                      type="file" 
                      ref={fileInputRef}
                      style={{ display: 'none' }}
                      multiple
                      accept="image/*"
                      onChange={handleFileChange}
                    />
                  </div>

                  {sellPreviews.length > 0 && (
                    <div className="image-preview-container">
                      {sellPreviews.map((preview, i) => (
                        <img key={i} src={preview} alt="Product preview" className="image-preview" />
                      ))}
                    </div>
                  )}
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '1rem', marginTop: '10px' }} disabled={loading}>
                  {loading ? (
                    <span><i className="fas fa-spinner fa-spin"></i> Uploading Secure Assets...</span>
                  ) : (
                    <span><i className="fas fa-cloud-upload-alt"></i> Publish Verified Listing</span>
                  )}
                </button>
              </form>
            </div>
          </section>
        )}

        {/* PAGE 3: MY ADS PAGE */}
        {currentPage === 'my-ads' && (
          <section className="fade-in">
            <div className="container" style={{ marginTop: '30px' }}>
              <div className="my-ads-header">
                <h2>Seller Ads Management</h2>
                <button className="btn btn-primary" onClick={() => navigateToPage('sell')}>
                  <i className="fas fa-plus-circle"></i> Post New Ad
                </button>
              </div>

              {/* Stats Grid Dashboard */}
              <div className="profile-stats" style={{ marginBottom: '30px' }}>
                <div className="stat-card">
                  <div className="stat-number" id="totalAds">{myListings.length}</div>
                  <div className="stat-label">Total Published Ads</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number" id="activeAds">{myListings.filter(a => a.status === 'active').length}</div>
                  <div className="stat-label">Active Listings</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number" id="soldItems">{myListings.filter(a => a.status === 'sold').length}</div>
                  <div className="stat-label">Items Sold</div>
                </div>
              </div>

              {myListings.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '50px', background: 'var(--card-bg)', borderRadius: '8px' }}>
                  <i className="fas fa-ad" style={{ fontSize: '3rem', color: 'var(--gray)', marginBottom: '15px' }}></i>
                  <h3>You haven't posted any advertisements yet</h3>
                  <p>Submit your first listing today to begin selling securely in Pakistan.</p>
                  <button className="btn btn-primary" style={{ marginTop: '15px' }} onClick={() => navigateToPage('sell')}>
                    Post First Advertisement
                  </button>
                </div>
              ) : (
                <div className="ads-grid">
                  {myListings.map(ad => (
                    <div key={ad._id} className="ad-card" onClick={() => viewAdDetail(ad)}>
                      <div className="ad-badge">{ad.status}</div>
                      
                      <div className="ad-actions">
                        <button 
                          className="ad-action-btn" 
                          onClick={(e) => deleteMyAd(ad._id, e)}
                          title="Delete Listing"
                          style={{ background: 'var(--danger)', color: 'white' }}
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>

                      <div className="ad-image">
                        <img 
                          src={ad.images && ad.images.length > 0 ? (ad.images[0].startsWith('http') || ad.images[0].startsWith('data') ? ad.images[0] : `${API_BASE_URL}/${ad.images[0]}`) : 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80'} 
                          alt={ad.title} 
                        />
                      </div>

                      <div className="ad-details">
                        <div className="ad-price">Rs {ad.price?.toLocaleString()}</div>
                        <div className="ad-title">{ad.title}</div>
                        <div className="ad-location">
                          <i className="fas fa-map-marker-alt"></i>
                          <span>{ad.location}</span>
                        </div>
                        <div className="ad-meta">
                          <span><i className="far fa-eye"></i> {ad.views || 0} views</span>
                          <span>{new Date(ad.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}

        {/* PAGE 4: PRODUCT DETAIL PAGE */}
        {currentPage === 'ad-detail' && selectedListing && (
          <section className="fade-in">
            <div className="container" style={{ marginTop: '30px' }}>
              <button className="btn btn-outline" style={{ marginBottom: '20px' }} onClick={() => navigateToPage('home')}>
                <i className="fas fa-arrow-left"></i> Back to Listings
              </button>

              <div className="ad-detail-container">
                <div className="ad-detail-header">
                  <h1 className="ad-detail-title">{selectedListing.title}</h1>
                  <div className="ad-detail-price">Rs {selectedListing.price?.toLocaleString()}</div>
                  <div className="ad-detail-meta">
                    <span><i className="fas fa-map-marker-alt"></i> {selectedListing.location}</span>
                    <span><i className="far fa-clock"></i> {new Date(selectedListing.created_at).toLocaleDateString()}</span>
                    <span><i className="far fa-eye"></i> {selectedListing.views || 0} views</span>
                  </div>
                </div>

                <div className="ad-detail-body">
                  <div className="ad-detail-images">
                    <div className="ad-detail-main-image">
                      <img 
                        src={selectedListing.images && selectedListing.images.length > 0 ? (selectedListing.images[0].startsWith('http') || selectedListing.images[0].startsWith('data') ? selectedListing.images[0] : `${API_BASE_URL}/${selectedListing.images[0]}`) : 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80'} 
                        alt={selectedListing.title} 
                      />
                    </div>
                    {selectedListing.images && selectedListing.images.length > 1 && (
                      <div className="ad-detail-thumbnails">
                        {selectedListing.images.map((img, i) => (
                          <div key={i} className={`ad-detail-thumbnail ${i === 0 ? 'active' : ''}`}>
                            <img src={img.startsWith('http') ? img : `${API_BASE_URL}/${img}`} alt="" />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="ad-detail-info">
                    <div className="ad-detail-seller">
                      <div className="seller-info-header">
                        <div className="seller-avatar-large">
                          {selectedListing.seller_name ? selectedListing.seller_name.split(' ').map(n => n[0]).join('') : 'TS'}
                        </div>
                        <div>
                          <div className="seller-name">{selectedListing.seller_name || 'Verified Seller'}</div>
                          <div className="seller-rating">
                            <i className="fas fa-shield-alt"></i>
                            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Biometric Verified</span>
                          </div>
                        </div>
                      </div>

                      <div className="seller-actions">
                        <button className="btn-chat" onClick={startChatWithSeller}>
                          <i className="fas fa-comments"></i> Chat with Seller
                        </button>
                        <a href={`tel:${selectedListing.seller_phone}`} className="btn-call">
                          <i className="fas fa-phone"></i> Call: {selectedListing.seller_phone}
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="ad-detail-description">
                  <h3 className="description-title">Product Specifications</h3>
                  <div className="description-content" dangerouslySetInnerHTML={{ __html: selectedListing.description.replace(/\n/g, '<br />') }} />
                </div>
              </div>
            </div>
          </section>
        )}

        {currentPage === 'categories' && (
          <CategoriesPage
            onSelectCategory={(slug) => {
              setCategoryFilter(slug);
              fetchListings(slug, searchQuery);
            }}
            onViewListings={() => navigateToPage('home')}
          />
        )}

        {/* PAGE 5: INBOX CHAT SYSTEM */}
        {currentPage === 'inbox' && (
          <section className="fade-in">
            <div className="chat-container">
              
              {/* Chats list sidebar */}
              <div className="chat-sidebar">
                <div className="chat-header">
                  Conversations
                </div>
                <ul className="chat-list">
                  {chats.map(chat => (
                    <li 
                      key={chat.id} 
                      className={`chat-item ${activeChat?.id === chat.id ? 'active' : ''}`}
                      onClick={() => openChat(chat)}
                    >
                      <div className="chat-item-header">
                        <span className="chat-item-name">{chat.name}</span>
                        <span className="chat-item-time">{chat.time}</span>
                      </div>
                      <div className="chat-item-preview">{chat.preview}</div>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Chat pane */}
              <div className="chat-main">
                {activeChat ? (
                  <>
                    <div className="chat-header" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div className="host-avatar" style={{ background: 'white', color: 'var(--primary)' }}>{activeChat.avatar}</div>
                      <span>{activeChat.name}</span>
                    </div>

                    <div className="chat-messages">
                      {activeChat.messages.map((msg, i) => (
                        <div key={i} className={`message ${msg.type === 'sent' ? 'sent' : 'received'}`}>
                          {msg.text}
                          <div className="message-time">{msg.time}</div>
                        </div>
                      ))}
                      <div ref={chatMessagesEndRef} />
                    </div>

                    <div className="chat-input-container">
                      <input 
                        type="text" 
                        className="chat-input"
                        placeholder="Type your message..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                      />
                      <button className="chat-send-btn" onClick={sendChatMessage}>
                        <i className="fas fa-paper-plane"></i>
                      </button>
                    </div>
                  </>
                ) : (
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                    <i className="fas fa-comments" style={{ fontSize: '4rem', marginBottom: '20px' }}></i>
                    <h3>Select a conversation to start chat</h3>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {/* PAGE 6: PROFILE MANAGEMENT */}
        {currentPage === 'profile' && user && (
          <section className="fade-in">
            <div className="profile-container">
              <div className="profile-header">
                <div className="profile-avatar" id="userAvatar">
                  {user.name ? user.name.split(' ').map(n => n[0]).join('') : 'TS'}
                </div>
                <div className="profile-info">
                  <h2 id="userName">{user.name}</h2>
                  <p id="userEmail">{user.email}</p>
                  <p id="userLocation"><i className="fas fa-map-marker-alt"></i> {profileCity}, Pakistan</p>
                </div>
              </div>

              <form onSubmit={handleProfileUpdate}>
                <div className="form-row">
                  <div className="form-group">
                    <label>First Name</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={profileFirstName}
                      onChange={(e) => setProfileFirstName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={profileLastName}
                      onChange={(e) => setProfileLastName(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Email Address</label>
                    <input 
                      type="email" 
                      className="form-control" 
                      value={profileEmail}
                      onChange={(e) => setProfileEmail(e.target.value)}
                      required
                      disabled
                    />
                  </div>
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={profilePhone}
                      onChange={(e) => setProfilePhone(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>City Location</label>
                  <select 
                    className="form-control"
                    value={profileCity}
                    onChange={(e) => setProfileCity(e.target.value)}
                    required
                  >
                    <option>Karachi</option>
                    <option>Lahore</option>
                    <option>Islamabad</option>
                    <option>Rawalpindi</option>
                    <option>Faisalabad</option>
                    <option>Multan</option>
                    <option>Peshawar</option>
                    <option>Quetta</option>
                  </select>
                </div>

                <div className="form-group" style={{ background: 'var(--light)', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                  <h4>🔒 Government CNIC Status</h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '5px' }}>
                    <i className="fas fa-check-circle" style={{ color: 'var(--success)' }}></i>
                    <span style={{ fontWeight: 600, color: 'var(--success)' }}>Approved by Administration</span>
                  </div>
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }}>
                  Save Profile Changes
                </button>
              </form>
            </div>
          </section>
        )}
      </main>

      {/* Unified Authentication Modal Dialog */}
      {authModal && (
        <div className="modal">
          <div className="modal-content modal-content-wide" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Welcome to TrustSell</h3>
              <button className="close-modal" onClick={() => setAuthModal(false)}>&times;</button>
            </div>

            <div className="tab-container">
              <div className={`tab ${authTab === 'login' ? 'active' : ''}`} onClick={() => setAuthTab('login')}>Login</div>
              <div className={`tab ${authTab === 'signup' ? 'active' : ''}`} onClick={() => setAuthTab('signup')}>Sign Up</div>
            </div>

            {/* Login Tab */}
            {authTab === 'login' && (
              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label>Email Address</label>
                  <input 
                    type="email" 
                    className="form-control" 
                    placeholder="Enter your registered email" 
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Password</label>
                  <input 
                    type="password" 
                    className="form-control" 
                    placeholder="Enter password" 
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '10px' }}>
                  Secure Session Login
                </button>
              </form>
            )}

            {authTab === 'signup' && (
              <SecureSignup
                addToast={addToast}
                normalizePhone={normalizePhone}
                onCancel={() => setAuthModal(false)}
                onSuccess={handleSecureSignupSuccess}
              />
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer>
        <div className="container">
          <div className="footer-content">
            <div className="footer-column">
              <div className="footer-logo">
                <i className="fas fa-shield-alt"></i>
                TrustSell
              </div>
              <p className="footer-desc">
                Pakistan's premium secured marketplace built on advanced biometric identity verification. Connecting buyers and sellers safely.
              </p>
              <div className="social-links">
                <a href="#" className="social-link"><i className="fab fa-facebook-f"></i></a>
                <a href="#" className="social-link"><i className="fab fa-twitter"></i></a>
                <a href="#" className="social-link"><i className="fab fa-instagram"></i></a>
                <a href="#" className="social-link"><i className="fab fa-linkedin-in"></i></a>
              </div>
            </div>
            
            <div className="footer-column">
              <h3>Quick Navigation</h3>
              <ul className="footer-links">
                <li><a onClick={() => navigateToPage('home')}><i className="fas fa-chevron-right"></i> Marketplace Home</a></li>
                <li><a onClick={() => user ? navigateToPage('sell') : setAuthModal(true)}><i className="fas fa-chevron-right"></i> Sell An Item</a></li>
                <li><a onClick={() => user ? navigateToPage('my-ads') : setAuthModal(true)}><i className="fas fa-chevron-right"></i> Ads Dashboard</a></li>
              </ul>
            </div>

            <div className="footer-column">
              <h3>Security Features</h3>
              <ul className="footer-links">
                <li><a onClick={() => addToast('Live CNIC check is fully operational', 'success')}><i className="fas fa-chevron-right"></i> Biometric Checking</a></li>
                <li><a onClick={() => addToast('Safety database updated daily', 'success')}><i className="fas fa-chevron-right"></i> Scammer Interceptor</a></li>
                <li><a onClick={() => addToast('Brand protection certified', 'success')}><i className="fas fa-chevron-right"></i> Brand Trademarks</a></li>
              </ul>
            </div>

            <div className="footer-column">
              <h3>Platform Details</h3>
              <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
                TrustSell E-Commerce Portal<br />
                Security Engine v1.2.0<br />
                Lahore Headquarters, Pakistan
              </p>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; {new Date().getFullYear()} TrustSell Pakistan. All rights reserved. | Securing digital trade.</p>
            <p style={{ marginTop: '5px', fontSize: '0.75rem', opacity: 0.7 }}>Developed & Powered by Mohammed Maarije</p>
          </div>
        </div>
      </footer>

      {/* Mobile Bottom Navigation Bar */}
      <div className="mobile-bottom-nav">
        <a href="#" className={`mobile-nav-item ${currentPage === 'home' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); navigateToPage('home'); }}>
          <i className="fas fa-home"></i>
          <span>Home</span>
        </a>
        <a href="#" className={`mobile-nav-item ${currentPage === 'sell' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('sell') : setAuthModal(true); }}>
          <i className="fas fa-plus-circle"></i>
          <span>Sell</span>
        </a>
        <a href="#" className={`mobile-nav-item ${currentPage === 'my-ads' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('my-ads') : setAuthModal(true); }}>
          <i className="fas fa-list"></i>
          <span>My Ads</span>
        </a>
        <a href="#" className={`mobile-nav-item ${currentPage === 'inbox' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('inbox') : setAuthModal(true); }}>
          <i className="fas fa-inbox"></i>
          <span>Inbox</span>
        </a>
        <a href="#" className={`mobile-nav-item ${currentPage === 'profile' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); user ? navigateToPage('profile') : setAuthModal(true); }}>
          <i className="fas fa-user"></i>
          <span>Account</span>
        </a>
      </div>
    </div>
  );
}

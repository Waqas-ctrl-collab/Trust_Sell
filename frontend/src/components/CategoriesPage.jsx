import { useEffect, useState } from 'react';
import { api } from '../api';

export default function CategoriesPage({ onSelectCategory, onViewListings }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/categories/')
      .then((res) => setCategories(res.data))
      .catch(() => {
        setCategories([
          { slug: 'mobile', name: 'Mobile Phones', description: 'Phones & tablets', icon: 'fa-mobile-alt', image_url: 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400&q=80', listing_count: 0 },
          { slug: 'cars', name: 'Cars', description: 'Vehicles', icon: 'fa-car', image_url: 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=400&q=80', listing_count: 0 },
          { slug: 'property', name: 'Property', description: 'Real estate', icon: 'fa-home', image_url: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400&q=80', listing_count: 0 },
          { slug: 'electronics', name: 'Electronics', description: 'Gadgets', icon: 'fa-laptop', image_url: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&q=80', listing_count: 0 },
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', color: 'var(--primary)' }}></i>
      </div>
    );
  }

  return (
    <section className="categories-page fade-in">
      <div className="container" style={{ marginTop: 30 }}>
        <h1 className="section-title">All Categories</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
          Browse Pakistan&apos;s most popular marketplace categories — dynamically updated from TrustSell.
        </p>
        <div className="categories-grid categories-page-grid">
          {categories.map((cat) => (
            <div
              key={cat.slug}
              className="category-item category-page-card"
              onClick={() => {
                onSelectCategory?.(cat.slug);
                onViewListings?.();
              }}
            >
              <div className="category-icon">
                <img src={cat.image_url || 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=200&q=80'} alt={cat.name} />
              </div>
              <div className="category-name">
                <i className={`fas ${cat.icon || 'fa-tag'}`}></i> {cat.name}
              </div>
              <div className="category-count">{cat.listing_count ?? 0} active ads</div>
              <p className="category-desc">{cat.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}


import { useState } from 'react';
import { Dashboard } from '@/components/Dashboard';
import { Header } from '@/components/Header';
import { AuthModal } from '@/components/AuthModal';

const Index = () => {
  const [user, setUser] = useState<{ email: string; name?: string } | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const handleLogin = (email: string) => {
    setUser({ email, name: email.split('@')[0] });
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg via-dark-surface to-dark-card">
      <Header 
        user={user}
        onLogin={() => setShowAuthModal(true)}
        onLogout={handleLogout}
      />
      
      {user ? (
        <Dashboard />
      ) : (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-6">
          <div className="text-center max-w-2xl mx-auto">
            <div className="mb-8 animate-float">
              <div className="w-24 h-24 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center mx-auto mb-6">
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                  <div className="w-6 h-6 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full"></div>
                </div>
              </div>
            </div>
            
            <h1 className="text-6xl font-bold mb-6 glow-text bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent">
              Clip-It-Now
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
              Transform your YouTube videos into perfect clips with AI. 
              Extract the most engaging moments automatically and share them with the world.
            </p>
            
            <div className="space-y-4">
              <button
                onClick={() => setShowAuthModal(true)}
                className="bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink text-white font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-blue/25 animate-glow"
              >
                Get Started - It's Free
              </button>
              
              <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground mt-8">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse"></div>
                  AI-Powered Clipping
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-neon-purple rounded-full animate-pulse"></div>
                  Instant Processing
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-neon-pink rounded-full animate-pulse"></div>
                  HD Quality Export
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLogin={handleLogin}
      />
    </div>
  );
};

export default Index;

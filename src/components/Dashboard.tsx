
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Upload, Play, Download, Trash2, Eye } from 'lucide-react';
import { JobQueue } from './JobQueue';
import { VideoPlayer } from './VideoPlayer';
import { ProgressTracker } from './ProgressTracker';

interface Job {
  id: string;
  title: string;
  thumbnail: string;
  status: 'processing' | 'completed' | 'failed';
  progress: number;
  clips: Array<{
    id: string;
    title: string;
    duration: string;
    timeframe: string;
    url: string;
  }>;
  createdAt: Date;
}

export const Dashboard = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [instructions, setInstructions] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [jobs, setJobs] = useState<Job[]>([
    {
      id: '1',
      title: 'AI Revolution in 2024',
      thumbnail: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=300&h=200&fit=crop&crop=center',
      status: 'completed',
      progress: 100,
      clips: [
        { id: '1', title: 'AI Breakthrough Moment', duration: '2:30', timeframe: '5:20-7:50', url: '#' },
        { id: '2', title: 'Future Predictions', duration: '1:45', timeframe: '12:10-13:55', url: '#' }
      ],
      createdAt: new Date('2024-01-15')
    },
    {
      id: '2',
      title: 'Tech Startup Journey',
      thumbnail: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop&crop=center',
      status: 'processing',
      progress: 65,
      clips: [],
      createdAt: new Date('2024-01-16')
    }
  ]);

  const handleSubmit = () => {
    if (!youtubeUrl) return;
    
    setIsSubmitting(true);
    
    // Simulate job creation
    const newJob: Job = {
      id: Date.now().toString(),
      title: 'Processing new video...',
      thumbnail: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=300&h=200&fit=crop&crop=center',
      status: 'processing',
      progress: 0,
      clips: [],
      createdAt: new Date()
    };
    
    setJobs(prev => [newJob, ...prev]);
    setCurrentJob(newJob);
    
    // Reset form
    setYoutubeUrl('');
    setInstructions('');
    setIsSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg via-dark-surface to-dark-card">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 glow-text bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent">
            Clip-It-Now
          </h1>
          <p className="text-xl text-muted-foreground">
            Transform your YouTube videos into perfect clips with AI
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Input Section */}
          <div className="lg:col-span-2 space-y-8">
            {/* URL Input Card */}
            <Card className="glass-effect border-0 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl text-neon-blue">Create New Clip</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">YouTube URL</label>
                  <Input
                    placeholder="https://youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="bg-dark-card/50 border-neon-blue/30 focus:border-neon-blue text-foreground placeholder:text-muted-foreground"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Instructions (Optional)</label>
                  <Textarea
                    placeholder="e.g., Only parts where the speaker mentions AI, or highlight emotional moments..."
                    value={instructions}
                    onChange={(e) => setInstructions(e.target.value)}
                    className="bg-dark-card/50 border-neon-blue/30 focus:border-neon-blue text-foreground placeholder:text-muted-foreground min-h-[100px]"
                  />
                </div>

                <Button
                  onClick={handleSubmit}
                  disabled={!youtubeUrl || isSubmitting}
                  className="w-full bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-blue/25"
                >
                  <Upload className="mr-2 h-5 w-5" />
                  {isSubmitting ? 'Processing...' : 'Create Clips'}
                </Button>
              </CardContent>
            </Card>

            {/* Progress Tracker */}
            {currentJob && currentJob.status === 'processing' && (
              <ProgressTracker job={currentJob} />
            )}

            {/* Video Player & Clips */}
            {currentJob && currentJob.status === 'completed' && (
              <VideoPlayer job={currentJob} />
            )}
          </div>

          {/* Job Queue Sidebar */}
          <div className="lg:col-span-1">
            <JobQueue 
              jobs={jobs} 
              currentJob={currentJob}
              onJobSelect={setCurrentJob}
              onJobDelete={(jobId) => setJobs(prev => prev.filter(j => j.id !== jobId))}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

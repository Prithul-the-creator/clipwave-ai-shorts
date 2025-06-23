
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Play, Download, Share, Clock, Scissors } from 'lucide-react';

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

interface VideoPlayerProps {
  job: Job;
}

export const VideoPlayer = ({ job }: VideoPlayerProps) => {
  return (
    <div className="space-y-6">
      {/* Original Video Info */}
      <Card className="glass-effect border-0 shadow-2xl">
        <CardHeader>
          <CardTitle className="text-xl text-neon-purple flex items-center gap-2">
            <Play className="h-5 w-5" />
            {job.title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="aspect-video bg-dark-card rounded-lg overflow-hidden mb-4">
            <img 
              src={job.thumbnail} 
              alt={job.title}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex items-center justify-between">
            <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
              {job.clips.length} clips generated
            </Badge>
            <Button variant="outline" size="sm" className="border-neon-blue/30 text-neon-blue hover:bg-neon-blue/10">
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Generated Clips */}
      <Card className="glass-effect border-0 shadow-2xl">
        <CardHeader>
          <CardTitle className="text-xl text-neon-cyan flex items-center gap-2">
            <Scissors className="h-5 w-5" />
            Generated Clips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {job.clips.map((clip) => (
              <div key={clip.id} className="bg-dark-card/50 rounded-lg p-4 border border-dark-surface">
                <div className="aspect-video bg-dark-bg rounded-lg overflow-hidden mb-3">
                  <img 
                    src={job.thumbnail} 
                    alt={clip.title}
                    className="w-full h-full object-cover opacity-80"
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Button 
                      size="sm"
                      className="bg-neon-blue/80 hover:bg-neon-blue text-dark-bg border-0 shadow-lg"
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <h3 className="font-medium text-foreground mb-2 line-clamp-2">
                  {clip.title}
                </h3>
                
                <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {clip.duration}
                  </div>
                  <div className="flex items-center gap-1">
                    <Scissors className="h-3 w-3" />
                    {clip.timeframe}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    className="flex-1 bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink text-xs"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="border-neon-blue/30 text-neon-blue hover:bg-neon-blue/10 text-xs"
                  >
                    <Share className="h-3 w-3 mr-1" />
                    Share
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

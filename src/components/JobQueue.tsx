
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Trash2, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

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

interface JobQueueProps {
  jobs: Job[];
  currentJob: Job | null;
  onJobSelect: (job: Job) => void;
  onJobDelete: (jobId: string) => void;
}

export const JobQueue = ({ jobs, currentJob, onJobSelect, onJobDelete }: JobQueueProps) => {
  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'processing':
        return <Clock className="h-4 w-4 text-neon-blue animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'processing':
        return 'bg-neon-blue/20 text-neon-blue border-neon-blue/30';
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
    }
  };

  return (
    <Card className="glass-effect border-0 shadow-2xl h-fit">
      <CardHeader>
        <CardTitle className="text-xl text-neon-purple flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Job Queue
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {jobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No jobs yet</p>
              <p className="text-sm">Submit a YouTube URL to get started</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                  currentJob?.id === job.id
                    ? 'bg-neon-blue/10 border border-neon-blue/30'
                    : 'bg-dark-card/50 hover:bg-dark-card/70 border border-transparent'
                }`}
                onClick={() => onJobSelect(job)}
              >
                <div className="flex items-start gap-3">
                  <img
                    src={job.thumbnail}
                    alt={job.title}
                    className="w-16 h-12 rounded object-cover flex-shrink-0"
                  />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-medium text-sm truncate text-foreground">
                        {job.title}
                      </h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onJobDelete(job.id);
                        }}
                        className="text-muted-foreground hover:text-red-400 p-1 h-auto"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center gap-2 mt-2">
                      {getStatusIcon(job.status)}
                      <Badge className={`text-xs ${getStatusColor(job.status)}`}>
                        {job.status}
                      </Badge>
                    </div>

                    {job.status === 'processing' && (
                      <div className="mt-2">
                        <Progress value={job.progress} className="h-1" />
                        <p className="text-xs text-muted-foreground mt-1">
                          {job.progress}% complete
                        </p>
                      </div>
                    )}

                    {job.status === 'completed' && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {job.clips.length} clips generated
                      </p>
                    )}
                    
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(job.createdAt, { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
